# manage_args.py

import argparse
from enum import Enum
from typing import Any, Optional, Sequence, Dict, Tuple, List
import sys


# define a list of special characters to be used prefix chars for dummy arguments
SPECIAL_CHARACTERS = list("?!#$%&()*+,-./:;<=>@[]^_{|}")


class NargsOption(Enum):
    COLLECT_UNTIL_NEXT_KNOWN = ""


class ArgumentParser(argparse.ArgumentParser):
    """
    Extend argparse.ArgumentParser to accept arguments that collect all unkown arguments
    until the next known argument when supplying
    `nargs=NargsOption.COLLECT_UNTIL_NEXT_KNOWN` to `add_argument`.
    It relies on native `argparse` as much as possible in order to remain functional as
    long as `argparse`'s output does not change. It achieves this by manipulating the
    argument list before parsing it instead of changing how it is parsed. In short, it
    first injects dummy arguments (with a different prefix char) into the args list,
    then parses the knownarguments, and finally parses the unrecognized arguments a
    second time using the the dummy prefix char.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # initialize parent
        super().__init__(*args, **kwargs)
        # we need to keep track of the dummy arguments
        self.dummy_args: Dict[str, str] = {}
        # the dummy prefix char needs to be different from the actual prefix char (which
        # is usually '-') --> loop over all special characters until one is found that
        # is not present in `self.prefix_chars`.
        self.dummy_prefix_char: str
        for char in SPECIAL_CHARACTERS:
            if char not in self.prefix_chars:
                self.dummy_prefix_char = char
                break
        else:
            raise ValueError(
                "Could not find suitable prefix character for dummy arguments"
            )

    def add_argument(
        self,
        *name_or_flags: Any,
        **kwargs: Any,
    ) -> argparse.Action:
        """
        If this argument should collect all unknown arguments until the next known
        argument, define a dummy argument starting with the dummy prefix char, set
        `nargs` to `1` and call the parent function.
        """
        if (
            "nargs" in kwargs
            and kwargs["nargs"] == NargsOption.COLLECT_UNTIL_NEXT_KNOWN
        ):
            for arg in name_or_flags:
                self.dummy_args[arg] = f"{self.dummy_prefix_char}dummy{arg}"
            kwargs["nargs"] = 1
        return super().add_argument(*name_or_flags, **kwargs)

    def parse_known_args(
        self,
        args: Optional[Sequence[str]] = None,
        namespace: Any = None,
    ) -> Tuple[argparse.Namespace, List[str]]:
        """
        Parse the argument list after injecting dummy arguments after the "special"
        arguments. Add each dummy argument twice, so that it is collected as the value
        for the special argument and also remains in the list of unrecognized arguments
        returned by `parse_known_args()`. After parsing the manipulated argument list,
        parse the unrecognized arguments another time looking for arguments starting
        with the dummy prefix char. This collects all arguments until the next string
        starting with the dummy prefix char. Finally, replace the values for the special
        arguments in the original result with the lists of arguments found in the second
        round of parsing.
        """
        # get the arguments
        args = sys.argv[1:] if args is None else list(args)
        # create a new list of arguments and inject the dummy arguments after the
        # special arguments
        manipulated_args: List[str] = []
        for arg in args:
            manipulated_args.append(arg)
            if arg in self.dummy_args:
                # add dummy arg twice since it will be consumed by the first parser
                manipulated_args.append(self.dummy_args[arg])
                manipulated_args.append(self.dummy_args[arg])
        parsed_args, unknown = super().parse_known_args(manipulated_args, namespace)
        # parse the unrecognized arguments again using the dummy prefix:
        # create the parser first and then add the dummy arguments
        dummy_parser = argparse.ArgumentParser(prefix_chars=self.dummy_prefix_char)
        for arg, dummy_arg in self.dummy_args.items():
            dummy_parser.add_argument(dummy_arg, dest=dummy_arg, nargs="+")
        parsed_dummy_args, still_unknown = dummy_parser.parse_known_args(unknown)
        # replace the dummy args in the originally parsed arguments. The "special"
        # arguments hold lists with exactly one value (the corresponding dummy argument)
        # in the original `Namespace`
        for dest, arg in vars(parsed_args).items():
            if (
                isinstance(arg, list)
                and len(arg) == 1
                and arg[0] in self.dummy_args.values()
            ):
                vars(parsed_args)[dest] = vars(parsed_dummy_args)[arg[0]]
        return parsed_args, still_unknown


def parse_exec(required_config_keys):
    """
    Uses argparse to check the cli parameters and prepare them as arguments for chamber.


    There are two arguements supported by this function.
    1. --get_params which takes one or many paths to the SSM parameter store. These paths
    are inspected by the main program, each entry under the path is turned into an 
    environment variable.
    
    2. --exec this is the command line utility to be called after the environment variables
    are persisted.
    """
    
    parser = ArgumentParser()
    
    parser.add_argument(
        '-get_params', '--get_params',
        help='SSM Parameter Store Path',
        nargs='+',
        default=[],
        required=True
    )
        
    parser.add_argument(
        '-exec', '--exec',
        help='Execution Program to run',
        nargs=NargsOption.COLLECT_UNTIL_NEXT_KNOWN,
        default=[],
        required=True
    )
        
    args = parser.parse_args()
    
    return args


def check_config(config, required_keys):
    '''
    Checks that all required parameters are in the config file.
    '''
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise Exception("Config is missing required keys: {}".format(missing_keys))

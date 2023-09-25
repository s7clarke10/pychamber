import os
import subprocess

from pychamber.utils.ssm_parameter_store import SSMParameterStore
from pychamber.utils.manage_args import (
    parse_exec,
    check_config
)
 
# define a main function


def main():

    REQUIRED_CONFIG_KEYS = [
        'get_params',
        'exec',
        'override_env_vars'
     ]

    args = parse_exec(REQUIRED_CONFIG_KEYS)

    my_env = os.environ
    for arg in args.get_params:
        store = SSMParameterStore(prefix = arg)

        ssm_params = store.keys()

        if len(ssm_params) == 0:
            print(f"Warning: no parameters discovered for {arg}")

        for ssm_param in ssm_params:
            param = ssm_param.upper()
  
            # Check to see if the parameter already exists in the env
            env_var_exists = os.environ.get(param)

            if env_var_exists:
                if args.priority_env_vars:
                    print(f"Warning: SSM variable {param} ignored, ",
                            "using existing environment variable")
                else:
                    print(f"Warning: environment variable {param} will be ",
                            "overwritten by SSM Parameter")
                    my_env[param] = store[ssm_param]
            else:
                my_env[param] = store[ssm_param]

    my_command = args.exec
    subprocess.run(my_command, env = my_env)

# run the main function only if this module is executed as the
# main script. (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()

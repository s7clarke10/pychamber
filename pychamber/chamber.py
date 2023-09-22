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
        'get_params'
        'exec'
    ]
    
    args = parse_exec(REQUIRED_CONFIG_KEYS)
    
    my_env = os.environ
    for arg in args.get_params:
        store = SSMParameterStore(prefix=arg)
        
        ssm_params = store.keys()
        
        for ssm_param in ssm_params:
            param = ssm_param.upper()
            
            my_env[param] = store[ssm_param]

    my_command = args.exec
    subprocess.Popen(my_command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()

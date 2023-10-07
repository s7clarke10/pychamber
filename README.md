# pychamber
Chamber is a tool for managing secrets.

It's current implementation, hydrates secrets from AWS Systems Manager Parameter Store as environment variables for use in a callable program.

# Installing

pip install .

# Authentication

Chamber uses the AWS boto3 library for authentication to obtain the secrets from the AWS SSM Parameter Store.

You can use environment variables such as `aws_access_key_id`, `aws_secret_access_key`, and `aws_session_token` or AWS config files. Please ref to https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html 

# Authorization
It is a best practice to manage access the SSM parameter store via IAM Policies.

Please refer to the following page for more details around SSM access policies.
https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html

# Usage

To retrieve secrets from the SSM parameter store use the get_params switch which allows one or many parameters to be supplied and then pass them to an executing program.

Example:

```bash
chamber -get_params /meltano/tap-rest-api-msdk /meltano/target-snowflake -exec meltano run tap-rest-api-msdk target-snowflake

chamber -get_params /meltano/tap-rest-api-msdk /meltano/target-snowflake -priority_env_vars -exec meltano run tap-rest-api-msdk target-snowflake
```

## get_params switch
You may supply one or many valid SSM Parameter store paths (each level of the hierarchy is separated by a slash).
When specifying more that one path to parameters, separate each path by a space.

Note: The environment variables are not persisted in the shell. They are only available to the calling program minimising discovery.

## priority_env_vars switch
Optional: Use existing env variables if they exist rather than incoming SSM Parameters. Default False

## exec switch
Calls a sub-process to execute the given program. Chamber expects that the given program call is available in the PATH or is a fully qualified location to the executable.

Note: Chamber will capture the return result from the program which is executed and will return the result of the execution back to the shell.

# Credits

The following people / projects are credited for pychamber project.

1. [segmentio](https://github.com/segmentio/chamber) . The authors of a full implementation of chamber in the Go language.

2. [Julian Libiseller-Egger](https://github.com/julibeg) for enhanced argpass features to allow all parameters to be passed to the executing program (even when they are switches). [argpass](https://github.com/julibeg/argpass).

3. [Bao Ngugen](https://github.com/nqbao) . Bao has a good [medium article](https://nqbao.medium.com/how-to-use-aws-ssm-parameter-store-easily-in-python-94fda04fea84) and code [gist](https://gist.github.com/nqbao/9a9c22298a76584249501b74410b8475) for retrieving parameters by a path in the AWS SSM Parameter Store.

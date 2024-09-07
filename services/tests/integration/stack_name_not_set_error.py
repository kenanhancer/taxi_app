class StackNameNotSetError(Exception):
    def __init__(self):
        super().__init__(
            "The AWS_SAM_STACK_NAME environment variable is not set. "
            "Please set this variable to the name of your stack."
        )

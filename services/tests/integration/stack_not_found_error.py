class StackNotFoundError(Exception):
    def __init__(self, stack_name):
        super().__init__(
            f"Cannot find stack '{stack_name}'. "
            "Please make sure a stack with this name exists."
        )
        self.stack_name = stack_name

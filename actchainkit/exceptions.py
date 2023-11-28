import better_exceptions

better_exceptions.hook()


class ActchainKitError(Exception):
    """Base class for exceptions in actchain."""

    pass


class ActchainKitImportError(ActchainKitError):
    """Raised when an import error occurs."""

    def __init__(self, module_name: str, *args: object) -> None:
        self.module_name = module_name
        super().__init__("Missing installation: " + module_name, *args)

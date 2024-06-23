class AppError(Exception):
    def __init__(self, message=None, **metadata):
        self.message = message or self.__doc__.strip() or ''
        self.metadata = metadata

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.__class__.__name__}<{self.message}>'


class SlugInvalidTimeError(AppError):
    """Slug was used outside of its validity period"""


class SlugNotFoundError(AppError):
    """Slug was valid, but unable to find its corresponding Record"""

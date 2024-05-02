class Singleton(type):
    '''
    Implement the Singleton pattern by overriding the __call__ method of the metaclass
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

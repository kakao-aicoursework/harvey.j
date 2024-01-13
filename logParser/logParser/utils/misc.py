import logging
from argparse import ArgumentTypeError

try:
    import ujson as json
except ModuleNotFoundError:
    import json
from retry import retry


def str2bool(val: str) -> bool:
    """
    convert string to boolean

    Args:
        val: string value

    Returns:
        boolean value
    """
    if val.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if val.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise ArgumentTypeError("Boolean value expected.")


def get_logger(name: str = __file__, level: str = "debug") -> logging.Logger:
    """
    Get logger.

    Args:
        name: Name of logger. It uses name of file as default. (default: ``__file__``)

    Returns:
        Logger with logging level, time, filename, function, line number as prefix.
    """
    import logging.handlers

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    if level == "debug" or level == logging.DEBUG:
        logger.setLevel(logging.DEBUG)
    elif level == "warning" or level == logging.WARNING:
        logger.setLevel(logging.WARNING)
    elif level == "info" or level == logging.INFO:
        logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(levelname)-8s] %(asctime)s [%(filename)s] [%(funcName)s:%(lineno)d] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    return logger


class Option(dict):
    def __init__(self, *args, **kwargs) -> None:
        """
        Config handling object for aurochs.

        If config file name (supported formats: json, yaml) is given, it reads the config file and converts to config.
        If python dictionary is given, it converts dictionary to config.
        Instances of Option class can be treated as python dictionary.
        """

        def read(fname):
            with open(fname, "r") as f:
                return f.read()

        if kwargs.get("yaml", False):
            import yaml

            args = [yaml.load(read(arg), yaml.FullLoader) for arg in args]
            del kwargs["yaml"]
        else:
            import json

            args = [arg if isinstance(arg, dict) else json.loads(read(arg)) for arg in args]
        super(Option, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = Option(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = Option(v)
                else:
                    self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Option, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Option, self).__delitem__(key)
        del self.__dict__[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

import os


def return_msg(msg):
    return msg


def add_two(x, y):
    """adds two numbers together"""
    try:
        return x + y
    except Exception as e:
        return e


def return_path():
    return os.path.normpath(__name__)


if __name__ == '__main__':
    pass

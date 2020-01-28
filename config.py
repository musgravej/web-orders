import os
# from dotenv import load_dotenv

# basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.urandom(24)


class ProductionConfig(Config):
    DEBUG = False,
    TEMPLATES_AUTO_RELOAD = True,


class DevelopConfig(Config):
    DEBUG = True,
    TEMPLATES_AUTO_RELOAD = True,


config = {
    'default': Config,
    'development': DevelopConfig,
    'production': ProductionConfig,
}


if __name__ == '__main__':
    pass

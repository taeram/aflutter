from os import getenv, \
               path
from time import time
from datetime import timedelta


class Config(object):
    AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
    AWS_REGION = getenv('AWS_REGION')
    AWS_S3_BUCKET = getenv('AWS_S3_BUCKET')
    AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')
    CACHE_BUSTER = int(path.getmtime(__file__))
    GOOGLE_ANALYTICS_ID = getenv('GOOGLE_ANALYTICS_ID', False)
    MAX_UPLOAD_SIZE = getenv('MAX_UPLOAD_SIZE')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SECRET_KEY = getenv('SECRET_KEY')
    SITE_NAME = getenv('SITE_NAME', 'Aflutter')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL').replace('mysql2:', 'mysql:')
    SQLALCHEMY_ECHO = getenv('SQLALCHEMY_ECHO', False)
    SQLALCHEMY_POOL_RECYCLE = 60
    FILES_PROTECTED = getenv('FILES_PROTECTED', False)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    CACHE_BUSTER = int(time())
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.dirname(__file__) + '/app/app.db'


class TestingConfig(Config):
    TESTING = True

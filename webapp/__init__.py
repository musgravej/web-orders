from flask import Flask
from config import Config, DevelopConfig, ProductionConfig
import os
import datetime

from dateutil.parser import parse

app = Flask(__name__)
app.config.from_object(DevelopConfig)

from webapp import routes
from webapp import pkg
from webapp import web_api_transactions
from webapp import web_database_transactions
from webapp import settings

import urllib
import os
from unicodedata import name
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_session import Session
from tempfile import mkdtemp
from flask_bcrypt import Bcrypt
import re
import pymysql
from dotenv import load_dotenv
import boto3
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Configure application
load_dotenv()
application = Flask(__name__)
bcrypt = Bcrypt(application)

#Azure Setup
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = os.getenv(os.getenv('AZURE_CONTAINER_NAME'))

# s3 = boto3.client('s3',
#                     aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
#                     aws_secret_access_key= os.getenv("ACCESS_SECRET_KEY")
#                      )

application.config["TEMPLATES_AUTO_RELOAD"] = True
# params = urllib.parse.quote_plus(os.getenv('DATABASE_URI'))
# conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
# application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(application)
@application.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter


# Configure session to use filesystem (instead of signed cookies)
application.config["SESSION_FILE_DIR"] = mkdtemp()
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
Session(application)
from vault import routes
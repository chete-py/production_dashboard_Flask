from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb

connection = MySQLdb.connect(
  host= os.getenv("DB_HOST"),
  user=os.getenv("DB_USERNAME"),
  passwd= os.getenv("DB_PASSWORD"),
  db= os.getenv("DB_NAME"),
  autocommit = True,
  ssl_disabled=True,
   ssl_mode = "VERIFY_IDENTITY",
  sslca    = {
    "ca": "/etc/ssl/cert.pem"
  }
)
  
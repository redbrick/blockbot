import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN") # required
DEBUG = os.environ.get("DEBUG", False)

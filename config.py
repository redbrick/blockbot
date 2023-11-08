import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN") # required

DEV_GUILD = os.environ.get("DEV_GUILD", 0)
DEBUG = os.environ.get("DEBUG", False)

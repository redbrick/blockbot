import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")  # required
DEBUG = os.environ.get("DEBUG", False)

ROLE_IDS = [
  ("Webgroup", "1166751688598761583"),
  ("Gamez", "1089204642241581139"),
  ("Croomer", "1172696659097047050")
  ]

CHANNEL_IDS = {"lobby": 627542044390457350}

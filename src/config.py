import os
import sys

from dotenv import load_dotenv

load_dotenv()

def get_required_var(var: str) -> str:
    env = os.environ.get(var)
    if env is None:
        print(f"{var} environment variable not set. Exiting.")
        sys.exit(1)
    return env

TOKEN = get_required_var("TOKEN")
DEBUG = os.environ.get("DEBUG", False)
POSTGRES_USER = get_required_var("POSTGRES_USER")
POSTGRES_PASSWORD = get_required_var("POSTGRES_PASSWORD")
POSTGRES_HOST = get_required_var("POSTGRES_HOST")
POSTGRES_PORT = get_required_var("POSTGRES_PORT")
POSTGRES_DB_NAME = get_required_var("POSTGRES_DB_NAME")

CHANNEL_IDS: dict[str, int] = {"lobby": 627542044390457350}

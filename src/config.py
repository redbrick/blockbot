import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")  # required
DEBUG = os.environ.get("DEBUG", False)
UID_MAP = os.environ.get("UID_MAP")

CHANNEL_IDS: dict[str, int] = {
    "lobby": 627542044390457350,
    "bot-private": 853071983452225536,
    "bots-cmt": 1162038557922312312,
    "action-items": 1029132014210793513,
}

ROLE_IDS: dict[str, int] = {
    "all": 568762266992902179,
    "everyone": 568762266992902179,
    "committee": 568762266992902179,
    "cmt": 568762266992902179,
    "events": 807389174009167902,
    "admins": 585512338728419341,
    "helpdesk": 1194683307921772594,
}

UID_MAPS = dict(item.split("=") for item in UID_MAP.split(","))

LDAP_USERNAME = os.environ.get("LDAP_USERNAME")
LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD")

import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")  # required
DEBUG = os.environ.get("DEBUG", False)
DISCORD_UID_MAP = os.environ.get("DISCORD_UID_MAP")

CHANNEL_IDS: dict[str, int] = {
    "lobby": 627542044390457350,
    "bot-private": 853071983452225536,
    "bots-cmt": 1162038557922312312,
    "action-items": 1029132014210793513,
    "cowboys-and-cowgirls-committee": 578712722330353684,
    "committee-announcements": 763113612340363304,
}

# TODO: query API/LDAP for these
ROLE_IDS: dict[str, int] = {
    "all": 568762266992902179,
    "everyone": 568762266992902179,
    "committee": 568762266992902179,
    "cmt": 568762266992902179,
    "events": 807389174009167902,
    "admins": 585512338728419341,
    "helpdesk": 1194683307921772594,
}

UID_MAPS = dict(item.split("=") for item in DISCORD_UID_MAP.split(","))

LDAP_USERNAME = os.environ.get("LDAP_USERNAME")
LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD")

AGENDA_TEMPLATE_URL = os.environ.get("AGENDA_TEMPLATE_URL")

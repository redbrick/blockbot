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


TOKEN = get_required_var("TOKEN")  # required
DEBUG = os.environ.get("DEBUG") or False

DISCORD_UID_MAP = get_required_var("DISCORD_UID_MAP")

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

CHANNEL_IDS: dict[str, int] = {
    "lobby": 627542044390457350,
    "bot-private": 853071983452225536,
    "bots-cmt": 1162038557922312312,
    "action-items": 1029132014210793513,
    "cowboys-and-cowgirls-committee": 578712722330353684,
    "committee-announcements": 763113612340363304,
    "instructions": 892521597276139603,
    "rules": 578713759263096842,
    "waiting-room": 627548568613552138,
}

# TODO: query API/LDAP for these
ROLE_IDS: dict[str, int] = {
    "all": 568762266992902179,
    "brickie": 627549740170608660,
    "croomer": 1172696659097047050,
    "everyone": 568762266992902179,
    "external events": 1299487948206768138,
    "gamez": 1089204642241581139,
    "webgroup": 1166751688598761583,
    "committee": 568762266992902179,
    "cmt": 568762266992902179,
    "events": 807389174009167902,
    "admins": 585512338728419341,
    "helpdesk": 1194683307921772594,
}

ASSIGNABLE_ROLES: dict[str, int] = {
    role: role_id
    for role, role_id in ROLE_IDS.items()
    if role in {"webgroup", "gamez", "croomer", "external events"}
}

UID_MAPS = dict(item.split("=") for item in DISCORD_UID_MAP.split(","))

LDAP_USERNAME = get_required_var("LDAP_USERNAME")
LDAP_PASSWORD = get_required_var("LDAP_PASSWORD")

AGENDA_TEMPLATE_URL = get_required_var("AGENDA_TEMPLATE_URL")

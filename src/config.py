import os
import sys
import typing
from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()

T = typing.TypeVar("T", bound=int | str | bool)


def convert_to_bool(value: str) -> bool:
    value = value.strip().lower()
    if value in ("1", "true"):
        return True
    if value in ("0", "false"):
        return False

    raise RuntimeError(f"{value} cannot be converted to a bool")


@typing.overload
def get_env_var(
    name: str,
    *,
    required: typing.Literal[True],
    conv: typing.Callable[[str], T] = str,
) -> T: ...


@typing.overload
def get_env_var(
    name: str,
    *,
    required: typing.Literal[False],
    conv: typing.Callable[[str], T] = str,
    default: T,
) -> T: ...


@typing.overload
def get_env_var(
    name: str,
    *,
    required: typing.Literal[False],
    conv: typing.Callable[[str], T] = str,
    default: None = None,
) -> T | None: ...


def get_env_var(
    name: str,
    *,
    required: bool,
    conv: typing.Callable[[str], T] = str,
    default: T | None = None,
) -> T | None:
    env = os.environ.get(name, "").strip() or None

    if required and env is None:
        print(f"{name} environment variable not set. Exiting.")
        sys.exit(1)

    if env is None:
        assert not required
        return default

    return conv(env)


TOKEN = get_env_var("TOKEN", required=True)
DEBUG = get_env_var("DEBUG", required=False, conv=convert_to_bool, default=False)

DISCORD_UID_MAP = get_env_var("DISCORD_UID_MAP", required=True)

DB_ENABLED = get_env_var(
    "DB_ENABLED", required=False, conv=convert_to_bool, default=True
)

DB_HOST = get_env_var("DB_HOST", required=False)
DB_NAME = get_env_var("DB_NAME", required=False)
DB_USER = get_env_var("DB_USER", required=False)
DB_PASSWORD = get_env_var("DB_PASSWORD", required=False)

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


class Colour(StrEnum):
    REDBRICK_RED = "#DC2B31"
    BRICKIE_BLUE = "#3498DB"
    GERRY_YELLOW = "#FFC753"
    ROOTHOLDER_YELLOW = "#F1C40F"
    OLDMITTEE_PINK = "#FF5D9D"
    ASSOCIATE_GREEN = "#1A7939"
    WEBGROUP_ORANGE = "#E67E22"
    GAMEZ_YELLOW = "#F1C40F"
    EXTERNAL_EVENTS_ORANGE = "#A84300"
    GUEST_RED = "#992D22"
    HELP_GREEN = "#00FF00"


UID_MAPS: dict[str, str] = dict(item.split("=") for item in DISCORD_UID_MAP.split(","))

LDAP_USERNAME = get_env_var("LDAP_USERNAME", required=False)
LDAP_PASSWORD = get_env_var("LDAP_PASSWORD", required=False)

AGENDA_TEMPLATE_URL = get_env_var("AGENDA_TEMPLATE_URL", required=False)

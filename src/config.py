import logging
import os
import sys
import typing
from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

T = typing.TypeVar("T", bound=int | str | bool)


class Feature(StrEnum):
    # the enum value should be the environment variable
    DATABASE = "DB_ENABLED"
    LDAP = "LDAP_ENABLED"
    PERMISSION_HOOKS = "PERMS_ENABLED"
    RCON = "RCON_ENABLED"
    MISC = "MISC_ENABLED"

    @property
    def enabled(self) -> bool:
        return get_env_var(
            self.value, required=False, conv=convert_to_bool, default=True
        )

    @enabled.setter
    def enabled(self, value: bool) -> None:
        set_env_var(self.value, "true" if value else "false")


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
    required: typing.Literal[True] = True,
    conv: typing.Callable[[str], T] = str,
) -> T: ...


@typing.overload
def get_env_var(
    name: str,
    *,
    required: typing.Literal[False] = False,
    required_features: typing.Sequence[Feature] | None = None,
    conv: typing.Callable[[str], T] = str,
    default: T,
) -> T: ...


@typing.overload
def get_env_var(
    name: str,
    *,
    required: typing.Literal[False] = False,
    required_features: typing.Sequence[Feature] | None = None,
    conv: typing.Callable[[str], T] = str,
    default: None = None,
) -> T | None: ...


def get_env_var(
    name: str,
    *,
    required: bool = False,
    required_features: typing.Sequence[Feature] | None = None,
    conv: typing.Callable[[str], T] = str,
    default: T | None = None,
) -> T | None:
    env = os.environ.get(name, "").strip() or None

    if required and env is None:
        logger.error(f"'{name}' environment variable not set. Exiting.")
        sys.exit(1)

    if required_features:
        for feature in required_features:
            if feature.enabled and env is None:
                # feature is enabled, but the env var is not set!
                logger.error(
                    f"Disabling feature '{feature.name}' as environment variable '{name}' not set"
                )
                feature.enabled = False
                return None

    if env is None:
        assert not required
        return default

    return conv(env)


def set_env_var(
    name: str,
    value: str,
) -> str:
    os.environ[name] = value
    return value


TOKEN = get_env_var("TOKEN", required=True)
DEBUG = get_env_var("DEBUG", required=False, conv=convert_to_bool, default=False)

DISCORD_UID_MAP = get_env_var("DISCORD_UID_MAP", required=True)

DB_HOST = get_env_var("DB_HOST", required_features=[Feature.DATABASE])
DB_NAME = get_env_var("DB_NAME", required_features=[Feature.DATABASE])
DB_USER = get_env_var("DB_USER", required_features=[Feature.DATABASE])
DB_PASSWORD = get_env_var("DB_PASSWORD", required_features=[Feature.DATABASE])

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

DEFAULT_ROLES: set[int] = {
    role_id
    for role, role_id in ROLE_IDS.items()
    if role in {"brickie", "external events"}
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

LDAP_USERNAME = get_env_var("LDAP_USERNAME", required_features=[Feature.LDAP])
LDAP_PASSWORD = get_env_var("LDAP_PASSWORD", required_features=[Feature.LDAP])

AGENDA_TEMPLATE_URL = get_env_var(
    "AGENDA_TEMPLATE_URL", required_features=[Feature.LDAP]
)

RCON_HOST = get_env_var("RCON_HOST", required_features=[Feature.RCON])
RCON_PORT = get_env_var("RCON_PORT", required_features=[Feature.RCON], conv=int)
RCON_PASSWORD = get_env_var("RCON_PASSWORD", required_features=[Feature.RCON])

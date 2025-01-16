import os

import nox
from nox import options

PROJECT_PATH = os.path.join(".", "src")
SCRIPT_PATHS = [PROJECT_PATH, "noxfile.py"]

options.sessions = ["format_fix", "pyright"]


@nox.session()
def format_fix(session: nox.Session) -> None:
    session.install("-r", "requirements_dev.txt")
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS)
    session.run("python", "-m", "ruff", "check", *SCRIPT_PATHS, "--fix")


@nox.session()
def format_check(session: nox.Session) -> None:
    session.install("-r", "requirements_dev.txt")
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS, "--check")
    session.run("python", "-m", "ruff", "check", *SCRIPT_PATHS)


@nox.session()
def pyright(session: nox.Session) -> None:
    session.install("-r", "requirements_dev.txt", "-r", "requirements.txt")
    session.run("pyright", *SCRIPT_PATHS)

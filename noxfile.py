import os

import nox
from nox import options

PROJECT_PATH = os.path.join(".", "src")
SCRIPT_PATHS = [PROJECT_PATH, "noxfile.py"]

options.default_venv_backend = "uv"
options.sessions = ["format_fix", "pyright"]


@nox.session()
def format_fix(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--only-dev", "--active")
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS)
    session.run("python", "-m", "ruff", "check", *SCRIPT_PATHS, "--fix")


@nox.session()
def format_check(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--only-dev", "--active")
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS, "--check")
    session.run("python", "-m", "ruff", "check", *SCRIPT_PATHS)


@nox.session()
def pyright(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--dev", "--active")
    session.run("pyright", *SCRIPT_PATHS)

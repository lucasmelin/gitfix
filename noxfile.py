"""Nox sessions."""

import tempfile
from pathlib import Path

import nox

package = "py_gitfix"
nox.options.sessions = "lint", "safety", "tests"
locations = "src", "tests", "noxfile.py"


def install_with_constraints(session, *args, **kwargs):
    """Install packages constrained by Poetry's lock file."""
    requirements = tempfile.NamedTemporaryFile(delete=False)
    try:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
    finally:
        requirements.close()
        Path(requirements.name).unlink()


@nox.session
def black(session):
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session
def lint(session):
    """Lint using flake8 and isort."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "isort",
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-comprehensions",
        "flake8-docstrings",
        "pep8-naming",
    )
    session.run("isort", "--check", "--diff", "--profile", "black", *args)
    session.run("flake8", *args)


@nox.session
def tests(session):
    """Run the unit tests."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)

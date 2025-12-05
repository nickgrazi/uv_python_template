"""Performs initial repo setup."""

from __future__ import annotations

from pathlib import Path
from subprocess import run
import warnings


def if_none_else(a: any, b: any) -> any:
    """Return second argument if first argument is None.

    Args:
        a: First argument.
        b: Second argument.

    Returns:
         Second argument if first argument is None, else first argument.
    """
    if a is None:
        return b
    return a


def param_from_git(key: str) -> str | None:
    """Query a value from git cofig by key.

    Args:
        key: Key of git config parameter.

    Returns:
        Value of git config parameter. Returns None in case of a non-zero return code.
    """
    process = run(
        ["git", "config", "--global", key],  # noqa: S607
        check=True,
        capture_output=True,
    )

    if process.returncode == 0:
        return process.stdout.decode("utf8", errors="strict").strip()

    return None


def update_placeholders(string: str, project_info: dict[str, str]) -> str:
    """Replaces all instances of `{key}` with `value` in `string`, for each key-value pair in `project_info`.

    Args:
        string: A string of any length.
        project_info: A dictionary where keys are the wildcard to be replaced
            and value is what it is to be replaced with.

    Returns:
        The input string with all wildcards replaced.

    """  # noqa: E501
    for placeholder, value in project_info.items():
        string = string.replace(f"{{{placeholder}}}", value)

    return string


def update_file(filepath: Path | str, project_info: dict) -> None:
    """Updates file in place using key-value pairs in project_info.

    Args:
        filepath: Path to file to update.
        project_info: A dictionary where keys are the wildcard to be replaced
        and value is what it is to be replaced with.
    """
    filepath = Path(filepath)

    with filepath.open() as file:
        filedata = file.read()

    filedata = update_placeholders(filedata, project_info)

    with filepath.open("w") as file:
        file.write(filedata)

def init_repo(
    project_name: str | None = None,
    package_name: str | None = None,
    user_name: str | None = None,
    user_email: str | None = None,
) -> None:
    """Prepares template repo by updating wildcards.

    Args:
        project_name (Optional[str], optional): Desired project name. Defaults to directory title.
        package_name (Optional[str], optional): Desired package name. Defaults to project name.
        user_name (Optional[str], optional): User name. Defaults to global git user.name value.
        user_email (Optional[str], optional): User email address.
            Defaults to global git user.email value.

    """
    path = Path()

    project_info = {}

    # Assign default paramater values.

    project_info["project_name"] = if_none_else(project_name, path.cwd().name.lower())

    project_info["package_name"] = if_none_else(
        package_name,
        project_info["project_name"].replace("-", "_"),
    )

    project_info["user_name"] = if_none_else(
        user_name,
        if_none_else(param_from_git("user.name"), "First Last"),
    )

    project_info["user_email"] = if_none_else(
        user_email,
        if_none_else(param_from_git("user.email"), "name @ email.com"),
    )

    # Loop through files and update contents

    for child in path.rglob("*"):
        if not str(child).startswith(".") and child.is_file() and child.suffix != ".py":
            update_file(child, project_info)

    # Loop through dirs and files and update path

    for child in path.rglob("*"):
        if not str(child).startswith("."):
            target_path = update_placeholders(str(child), project_info)

            if target_path != child:
                child.rename(target_path)

    # Self-destruct

    Path(__file__).unlink()

def main() -> None:
    """Runs prep_repo and self-destructs."""
    init_repo()


if __name__ == "__main__":
    main()

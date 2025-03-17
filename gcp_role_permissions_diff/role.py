import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any

import yaml

from gcp_role_permissions_diff.log import log


class RoleException(Exception):
    """An exception from Role."""


@dataclass
class Role:
    """An expression of the role of Google Cloud."""

    name: str
    includedPermissions: list[str]

    @property
    def permissions(self) -> set[str]:
        return set(self.includedPermissions)

    @classmethod
    def new(cls, name: str, includedPermissions: list[str] = []) -> "Role":
        """Create a new Role."""
        if not name:
            raise RoleException("role has no name!")
        return Role(name=name, includedPermissions=includedPermissions)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Role":
        """Create a new Role from dict."""
        name = d.get("name")
        if not isinstance(name, str):
            raise RoleException("name is not a string")
        includedPermissions = d.get("includedPermissions", [])
        if not isinstance(includedPermissions, list) or not all(isinstance(x, str) for x in includedPermissions):
            raise RoleException("includedPermissions is not a list of string")
        return Role.new(name=name, includedPermissions=includedPermissions)


def gcloud_describe_role(role: str) -> Role:
    """
    Describe role by gcloud.

    See https://cloud.google.com/sdk/gcloud/reference/iam/roles/describe
    """
    log().debug("gcloud iam roles describe %s", role)
    try:
        r = subprocess.run(
            ["gcloud", "iam", "roles", "describe", role],
            check=True,
            capture_output=True,
        ).stdout.decode()
        return Role.from_dict(yaml.safe_load(r))
    except Exception as e:
        e.add_note(f"at gcloud describe role {role}")
        raise


def read_role_from_file(role_file: str) -> Role:
    """Read Role from role_file."""
    parsers = [
        ("yaml", __read_role_from_yaml),
        ("json", __read_role_from_json),
        ("text", __read_role_from_text),
    ]
    excs = []
    for name, f in parsers:
        log().debug("read role from %s file: %s", name, role_file)
        try:
            return f(role_file)
        except Exception as e:
            e.add_note(f"from {name}")
            excs.append(e)
    raise ExceptionGroup(f"at read role from file {role_file}", excs)


def __read_role_from_yaml(role_file: str) -> Role:
    with open(role_file) as f:
        return Role.from_dict(yaml.safe_load(f))


def __read_role_from_json(role_file: str) -> Role:
    with open(role_file) as f:
        return Role.from_dict(json.loads(f.read()))


def __read_role_from_text(role_file: str) -> Role:
    pattern = re.compile(r"^\S+$")
    with open(role_file) as f:
        permissions = []
        for linum, line in enumerate(f, 1):
            p = line.rstrip()
            if len(p) == 0:
                continue
            if not pattern.fullmatch(p):
                raise RoleException(f"at line {linum}, invalid permission line {p}")
            permissions.append(p)
        return Role.new(name=role_file, includedPermissions=permissions)

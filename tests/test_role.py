import textwrap
from tempfile import TemporaryDirectory
from unittest import TestCase

import gcp_role_permissions_diff.role as role


class TestRole(TestCase):
    def test_new(self):
        with self.subTest("require name"):
            with self.assertRaisesRegex(role.RoleException, "no name"):
                role.Role.new(name="", includedPermissions=[])
        with self.subTest("success"):
            got = role.Role.new(name="myrole", includedPermissions=[])
            want = role.Role(name="myrole", includedPermissions=[])
            self.assertEqual(want, got)

    def test_from_dict(self):
        with self.subTest("no name"):
            with self.assertRaisesRegex(role.RoleException, "name is not a string"):
                role.Role.from_dict({})
        with self.subTest("name is not a string"):
            with self.assertRaisesRegex(role.RoleException, "name is not a string"):
                role.Role.from_dict({"name": 1})
        with self.subTest("includedPermissions is not a list"):
            with self.assertRaisesRegex(role.RoleException, "includedPermissions is not a list"):
                role.Role.from_dict({"name": "myrole", "includedPermissions": 1})
        with self.subTest("includedPermissions is not a list of string"):
            with self.assertRaisesRegex(role.RoleException, "includedPermissions is not a list of string"):
                role.Role.from_dict({"name": "myrole", "includedPermissions": [1]})
        with self.subTest("success"):
            got = role.Role.from_dict({"name": "myrole", "includedPermissions": ["p"]})
            want = role.Role(name="myrole", includedPermissions=["p"])
            self.assertEqual(want, got)

    def test_read_role_from_file(self):
        testcases = [
            (
                "yaml",
                "role.yaml",
                textwrap.dedent(
                    """\
                    description: Allows accessing the payload of secrets.
                    etag: AA==
                    includedPermissions:
                    - resourcemanager.projects.get
                    - resourcemanager.projects.list
                    - secretmanager.versions.access
                    name: roles/secretmanager.secretAccessor
                    stage: GA
                    title: Secret Manager Secret Accessor
                    """
                ),
                role.Role(
                    name="roles/secretmanager.secretAccessor",
                    includedPermissions=[
                        "resourcemanager.projects.get",
                        "resourcemanager.projects.list",
                        "secretmanager.versions.access",
                    ],
                ),
            ),
            (
                "json",
                "role.json",
                textwrap.dedent(
                    """\
                    {
                      "name": "roles/secretmanager.secretAccessor",
                      "includedPermissions": [
                        "resourcemanager.projects.get",
                        "resourcemanager.projects.list",
                        "secretmanager.versions.access"
                      ]
                    }
                    """,
                ),
                role.Role(
                    name="roles/secretmanager.secretAccessor",
                    includedPermissions=[
                        "resourcemanager.projects.get",
                        "resourcemanager.projects.list",
                        "secretmanager.versions.access",
                    ],
                ),
            ),
            (
                "text",
                "role.txt",
                textwrap.dedent(
                    """\
                    resourcemanager.projects.get
                    resourcemanager.projects.list
                    secretmanager.versions.access
                    """,
                ),
                role.Role(
                    name="roles/secretmanager.secretAccessor",
                    includedPermissions=[
                        "resourcemanager.projects.get",
                        "resourcemanager.projects.list",
                        "secretmanager.versions.access",
                    ],
                ),
            ),
        ]
        with TemporaryDirectory() as dir:
            for title, name, content, want in testcases:
                with self.subTest(title):
                    with open(f"{dir}/{name}", "w") as f:
                        print(content, file=f)
                    got = role.read_role_from_file(f"{dir}/{name}")
                    self.assertEqual(want.permissions, got.permissions)

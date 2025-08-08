import os
import subprocess
import textwrap
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase


@contextmanager
def cd(p: Path):
    now = Path.cwd()
    try:
        os.chdir(str(p))
        yield
    finally:
        os.chdir(str(now))


def run(cmd: str | list[str], dir: Path, *args, **kwargs) -> subprocess.CompletedProcess:
    with cd(dir):
        return subprocess.run(cmd, check=True, *args, **kwargs)


class TestE2E(TestCase):
    def test_e2e(self):
        pwd = Path.cwd()
        run(["make", "dist"], pwd)
        run(
            [
                "pip",
                "install",
                "dist/gcp_role_permissions_diff-0.1.1.tar.gz",
            ],
            pwd,
        )
        roles = {
            "roles_browser": textwrap.dedent(
                """\
            resourcemanager.folders.get
            resourcemanager.folders.list
            resourcemanager.organizations.get
            resourcemanager.projects.get
            resourcemanager.projects.getIamPolicy
            resourcemanager.projects.list
            """,
            ),
            "roles_recourcemanager.folderViewer": textwrap.dedent(
                """\
            essentialcontacts.contacts.get
            essentialcontacts.contacts.list
            orgpolicy.constraints.list
            orgpolicy.policies.list
            orgpolicy.policy.get
            resourcemanager.folders.get
            resourcemanager.folders.list
            resourcemanager.projects.get
            resourcemanager.projects.list
            """,
            ),
        }

        with TemporaryDirectory() as dir:
            for name, r in roles.items():
                with open(f"{dir}/{name}", "w") as f:
                    print(r, file=f)

            def atom(name: str) -> str:
                return f"@{dir}/{name}"

            browser = atom("roles_browser")
            folder_viewer = atom("roles_recourcemanager.folderViewer")

            testcases = [
                (
                    "only browser",
                    f"{browser} - {folder_viewer}",
                    {
                        "resourcemanager.organizations.get",
                        "resourcemanager.projects.getIamPolicy",
                    },
                ),
                (
                    "common permissions",
                    f"{browser} * {folder_viewer}",
                    {
                        "resourcemanager.folders.get",
                        "resourcemanager.folders.list",
                        "resourcemanager.projects.get",
                        "resourcemanager.projects.list",
                    },
                ),
            ]
            for title, expr, want in testcases:
                with self.subTest(title):
                    r = run(
                        [
                            "python",
                            "-m",
                            "gcp_role_permissions_diff.cli",
                            expr,
                        ],
                        pwd,
                        text=True,
                        capture_output=True,
                    ).stdout
                    got = {x.rstrip() for x in r.split() if len(x.rstrip()) > 0}
                    self.assertEqual(want, got)

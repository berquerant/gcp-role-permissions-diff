from dataclasses import asdict
from tempfile import TemporaryDirectory
from unittest import TestCase

import yaml

import gcp_role_permissions_diff.grammar as grammar
import gcp_role_permissions_diff.role as role


class TestCalculator(TestCase):
    def test_run(self):
        roles = [
            role.Role.new(name="empty"),
            role.Role.new(name="r1", includedPermissions=["p1"]),
            role.Role.new(name="r2", includedPermissions=["p2"]),
            role.Role.new(name="r3", includedPermissions=["p3"]),
            role.Role.new(name="r12", includedPermissions=["p1", "p2"]),
        ]
        with TemporaryDirectory() as dir:
            for r in roles:
                with open(f"{dir}/{r.name}", "w") as f:
                    print(yaml.safe_dump(asdict(r)), file=f)

            def atom(name: str) -> str:
                """Role name to file_expr."""
                return f"@{dir}/{name}"

            empty = atom("empty")
            r1 = atom("r1")
            r2 = atom("r2")
            r3 = atom("r3")
            r12 = atom("r12")
            testcases = [
                ("empty", empty, set()),
                ("single role", r1, {"p1"}),
                ("add", f"{r1}+{r2}", {"p1", "p2"}),
                ("and", f"{r12}*{r2}", {"p2"}),
                ("diff", f"{r12}-{r2}", {"p1"}),
                ("xor", f"{r12} ^ ({r1} + {r3})", {"p2", "p3"}),
            ]
            for title, text, want in testcases:
                with self.subTest(title):
                    got = grammar.parse(text)
                    self.assertEqual(want, got)

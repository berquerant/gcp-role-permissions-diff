"""Entry point of CLI."""

import argparse
import json
import textwrap

import yaml

from gcp_role_permissions_diff import grammar, log


def main() -> int:
    """Entry point of CLI."""
    parser = argparse.ArgumentParser(
        prog="gcp_role_permissions_diff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Compare the permissions of multiple roles in Google Cloud.
            The gcloud command (https://cloud.google.com/sdk/docs/install) is required.

            To perform the comparison, please write the expression according to the following grammar:

            expr = product
              | expr "+" product  // or
              | expr "-" product  // diff
            product = atom
              | product "*" atom  // and
              | product "^" atom  // xor
            atom = "@" NAME       // Read a role from NAME file
              | NAME              // gcloud iam roles describe NAME
              | "(" expr ")"
            NAME: [a-zA-Z-0-9_/.]+

            Examples of expr:
            // Permissions of roles/browser
            roles/browser
            // Permissions included in roles/browser but not in roles/resourcemanager.folderViewer
            roles/browser - roles/resourcemanager.folderViewer
            // Permissions included in both roles/browser and roles/resourcemanager.folderViewer
            roles/browser * roles/resourcemanager.folderViewer

            Examples of role file:
            // yaml
            name: roles/secretmanager.secretAccessor
            includedPermissions:
            - resourcemanager.projects.get
            - resourcemanager.projects.list
            - secretmanager.versions.access
            // json
            {
              "name": "roles/secretmanager.secretAccessor",
              "includedPermissions": [
                "resourcemanager.projects.get",
                "resourcemanager.projects.list",
                "secretmanager.versions.access"
              ]
            }
            // text
            resourcemanager.projects.get
            resourcemanager.projects.list
            secretmanager.versions.access
            """,
        ),
    )
    parser.add_argument("--tree", action="store_true", help="Only parsing, generating Tree")
    parser.add_argument("--debug", action="store_true", help="Enable debug log")
    parser.add_argument(
        "--out", "-o", choices=["json", "yaml", "text"], default="text", help="Output format, default: text"
    )
    parser.add_argument("expr", nargs="+", help="Expressions")
    args = parser.parse_args()

    if args.debug:
        log.debug()

    expr = " ".join(args.expr)
    if args.tree:
        print(grammar.parse_raw(expr))
        return 0

    result = sorted(list(grammar.parse(expr)))
    match args.out:
        case "json":
            print(json.dumps(result, separators=(",", ":")))
        case "yaml":
            print(yaml.safe_dump(result))
        case "text":
            print("\n".join(result))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

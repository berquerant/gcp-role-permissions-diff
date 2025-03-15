# gcp-role-permissions-diff

``` shell
❯ python -m gcp_role_permissions_diff.cli --help
usage: gcp_role_permissions_diff [-h] [--tree] [--debug] [--out {json,yaml,text}] expr [expr ...]

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

positional arguments:
  expr                  Expressions

options:
  -h, --help            show this help message and exit
  --tree                Only parsing, generating Tree
  --debug               Enable debug log
  --out, -o {json,yaml,text}
                        Output format, default: text
```

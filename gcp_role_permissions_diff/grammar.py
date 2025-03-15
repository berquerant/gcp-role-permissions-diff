from typing import Any, cast

from lark import Lark, Transformer, v_args

from gcp_role_permissions_diff.log import log
from gcp_role_permissions_diff.role import gcloud_describe_role, read_role_from_file


def new_parser(**kwargs: dict[str, Any]) -> Lark:
    """Create a new parser."""
    return Lark(
        """
?expr: product
  | expr "+" product -> or_expr
  | expr "-" product -> diff_expr

?product: atom
  | product "*" atom -> and_expr
  | product "^" atom -> xor_expr

?atom: "@" NAME      -> file_expr
  | NAME             -> role_expr
  | "(" expr ")"

%import common.LETTER
%import common.DIGIT
NAME: (LETTER|DIGIT|"_"|"/"|".")+
%import common.WS
%ignore WS
""",
        start="expr",
        parser="lalr",
        propagate_positions=True,
        **kwargs,
    )


def parse_raw(text: str, indent: str = "|") -> str:
    """Parse text and print the tree."""
    return new_parser().parse(text).pretty(indent)


@v_args(inline=True, meta=True)
class Calculator(Transformer):  # type: ignore
    def __debug(self, meta, msg: str):  # type: ignore
        log().debug("[(%02d:%02d)-(%02d:%02d)] %s", meta.line, meta.column, meta.end_line, meta.end_column, msg)

    def or_expr(self, meta, left, right):  # type: ignore
        self.__debug(meta, f"or_expr({left}, {right})")
        return left | right

    def diff_expr(self, meta, left, right):  # type: ignore
        self.__debug(meta, f"diff_expr({left}, {right})")
        return left - right

    def and_expr(self, meta, left, right):  # type: ignore
        self.__debug(meta, f"and_expr({left}, {right})")
        return left & right

    def xor_expr(self, meta, left, right):  # type: ignore
        self.__debug(meta, f"xor_expr({left}, {right})")
        return left ^ right

    def file_expr(self, meta, v) -> set[str]:  # type: ignore
        self.__debug(meta, f"file({v})")
        return read_role_from_file(v).permissions

    def role_expr(self, meta, v) -> set[str]:  # type: ignore
        self.__debug(meta, f"role({v})")
        return gcloud_describe_role(v).permissions


def parse(text: str) -> set[str]:
    """Parse text and eval it."""
    tree = new_parser().parse(text)
    r = Calculator().transform(tree)
    return cast(set[str], r)

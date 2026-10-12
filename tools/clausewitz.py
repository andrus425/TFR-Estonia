"""Small, lossless-order Clausewitz script reader for development checks.

This is a structural reader, not a replacement for HOI4's runtime validator.
Duplicate keys and bare list elements are deliberately preserved.
"""
from dataclasses import dataclass
import re


TOKEN = re.compile(r'\s+|\#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}]|[<>!=]=?|[^\s{}<>!=\"#]+')


@dataclass
class Entry:
    key: str
    op: str | None
    value: object
    line: int


@dataclass
class Block:
    entries: list[Entry]

    def get(self, key, default=None):
        return next((e.value for e in self.entries if e.key == key), default)

    def all(self, key):
        return [e.value for e in self.entries if e.key == key]

    def walk(self, parents=()):
        for entry in self.entries:
            yield parents, entry
            if isinstance(entry.value, Block):
                yield from entry.value.walk(parents + (entry.key,))


def atom(token):
    if token.startswith('"'):
        return token[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return token


def parse(text, source="<script>"):
    tokens = []
    offset = 0
    line = 1
    for match in TOKEN.finditer(text.lstrip("\ufeff")):
        if match.start() != offset:
            raise ValueError(f"{source}:{line}: unreadable input")
        token = match.group()
        if not token.isspace() and not token.startswith("#"):
            tokens.append((token, line))
        line += token.count("\n")
        offset = match.end()
    if offset != len(text.lstrip("\ufeff")):
        raise ValueError(f"{source}:{line}: unterminated string or unreadable input")
    index = 0

    def block(nested=False):
        nonlocal index
        entries = []
        while index < len(tokens):
            token, ln = tokens[index]
            if token == "}":
                if not nested:
                    raise ValueError(f"{source}:{ln}: unexpected closing brace")
                index += 1
                return Block(entries)
            if token in {"{", "=", ">", "<", "!=", ">=", "<="}:
                raise ValueError(f"{source}:{ln}: expected key, got {token}")
            index += 1
            op, value = None, atom(token)
            if index < len(tokens) and tokens[index][0] in {"=", ">", "<", "!=", ">=", "<="}:
                op = tokens[index][0]
                index += 1
                if index >= len(tokens):
                    raise ValueError(f"{source}:{ln}: missing value for {token}")
                val, _ = tokens[index]
                index += 1
                if val == "{":
                    value = block(True)
                elif val == "}":
                    raise ValueError(f"{source}:{ln}: missing value before closing brace")
                else:
                    value = atom(val)
            entries.append(Entry(atom(token), op, value, ln))
        if nested:
            raise ValueError(f"{source}:{line}: unclosed block")
        return Block(entries)

    return block()

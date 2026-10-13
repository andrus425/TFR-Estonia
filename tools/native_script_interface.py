"""Emit native HOI4 scripted-effect calls; HOI4 does not accept argument blocks.

Inputs live in country temporary variables. The authoring helper returns the
two native statements together so callers cannot forget to set their input.
"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
AMOUNT_INPUTS = {
    "TFR_EST_change_cohesion": "TFR_EST_cohesion_delta",
    "TFR_EST_change_readiness": "TFR_EST_readiness_delta",
    "TFR_EST_spend_budget": "TFR_EST_budget_cost",
    "TFR_EST_change_occupation_cooperation": "TFR_EST_occupation_cooperation_delta",
    "TFR_EST_change_occupation_resistance": "TFR_EST_occupation_resistance_delta",
}
CALL = re.compile(r"(?P<name>" + "|".join(AMOUNT_INPUTS) + r")\s*=\s*\{\s*AMOUNT\s*=\s*(?P<amount>[^\s{}]+)\s*\}")


def amount_call(name, amount):
    variable = AMOUNT_INPUTS[name]
    return f"set_temp_variable = {{ var = {variable} value = {amount} }}\n{name} = yes"


def native_amount_calls(text):
    def replace(match):
        start = text.rfind("\n", 0, match.start()) + 1
        indent = re.match(r"[ \t]*", text[start:]).group()
        return amount_call(match["name"], match["amount"]).replace("\n", "\n" + indent)
    return CALL.sub(replace, text)


def native_definitions(text):
    # Lex braces, respecting strings/comments, to restrict replacement to the
    # matching helper definition rather than a neighboring effect.
    token = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}]')
    edits = []
    for name, input_name in AMOUNT_INPUTS.items():
        header = re.search(r"(?m)^[ \t]*" + re.escape(name) + r"\s*=\s*\{", text)
        if not header: continue
        opening = header.end() - 1
        depth = 0
        for match in token.finditer(text, opening):
            if match.group() == "{": depth += 1
            elif match.group() == "}": depth -= 1
            if depth == 0:
                body = text[opening:match.end()]
                edits.append((opening, match.end(), body.replace("$AMOUNT$", input_name)))
                break
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    changed = []
    for directory in ("common", "events", "history"):
        for path in (ROOT / directory).rglob("TFR_EST_*.txt"):
            original = path.read_text(encoding="utf-8-sig")
            updated = native_amount_calls(native_definitions(original))
            if original != updated:
                changed.append(path.relative_to(ROOT).as_posix())
                if args.write: path.write_text(updated, encoding="utf-8", newline="\n")
    print(("Converted" if args.write else "Legacy interfaces remaining in") + f" {len(changed)} files.")
    for path in changed: print(path)
    return bool(changed) if args.check else False


if __name__ == "__main__":
    raise SystemExit(main())

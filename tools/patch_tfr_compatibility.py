"""Reproduce narrow, audited TFR Estonia compatibility overrides.

The installed parent is read-only. Run --check to verify generated files and
baseline hashes, or --write after reviewing a new upstream version. Dynamic
annex targets are guarded at the mutation itself; no annex-and-release repair.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PARENT = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356")
ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=<>]+|[^\s{}=<>#]+')


@dataclass
class Entry:
    key: str
    value: str | None
    start: int
    end: int
    children: list["Entry"]


def parse(text: str) -> list[Entry]:
    tokens = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text) if not m.group().startswith("#")]
    def block(i: int) -> tuple[list[Entry], int]:
        out = []
        while i < len(tokens) and tokens[i][0] != "}":
            key, start, end = tokens[i]
            i += 1
            if i >= len(tokens) or tokens[i][0] not in ("=", ">", "<", ">=", "<=", "!="):
                out.append(Entry(key, None, start, end, []))
                continue
            i += 1
            if tokens[i][0] == "{":
                children, i = block(i + 1)
                end = tokens[i][2]
                i += 1
                out.append(Entry(key, None, start, end, children))
            else:
                value, _, end = tokens[i]
                i += 1
                out.append(Entry(key, value, start, end, []))
        return out, i
    return block(0)[0]


def walk(entries: list[Entry], ancestors: tuple[Entry, ...] = ()):
    for e in entries:
        yield e, ancestors
        yield from walk(e.children, ancestors + (e,))


def indent_at(text: str, pos: int) -> str:
    start = text.rfind("\n", 0, pos) + 1
    prefix = text[start:pos]
    return prefix if prefix.strip() == "" else "\t"


def parent_patch(text: str, relative: str) -> tuple[str, list[dict]]:
    edits: list[tuple[int, int, str, str]] = []
    entries = parse(text)
    peace = relative == "common/on_actions/TFR_on_actions_ZZZ_peace.txt"
    for e, ancestors in walk(entries):
        raw = text[e.start:e.end]
        indent = indent_at(text, e.start)
        if e.key == "annex_country":
            target = next((c.value for c in e.children if c.key == "target"), None)
            if target == "EST" or (target and (target in ("ROOT", "PREV", "FROM", "THIS") or target.startswith(("event_target:", "var:"))) and (peace or "SOV" in relative or "GER" in relative or relative.endswith("00_TFR_scripted_effects_ZZZ_generic.txt"))):
                # Guard all scope/array-derived targets in these war scripts. Their
                # non-Estonia execution retains the original annex verbatim.
                transfer_troops = next((c.value for c in e.children if c.key == "transfer_troops"), "yes")
                if transfer_troops not in ("yes", "no"):
                    raise ValueError(f"Unsupported dynamic troop policy in {relative}: {transfer_troops}")
                transfer_troops_value = 0 if transfer_troops == "no" else 1
                guard = f"{target} = {{ original_tag = EST has_country_flag = TFR_EST_initialized }}"
                replacement = (f"if = {{\n{indent}\tlimit = {{ {guard} }}\n"
                               f"{indent}\t{target} = {{\n"
                               f"{indent}\t\tsave_event_target_as = TFR_EST_settlement_target\n"
                               f"{indent}\t\tset_temp_variable = {{ var = TFR_EST_settlement_transfer_troops value = {transfer_troops_value} }}\n"
                               f"{indent}\t}}\n"
                               f"{indent}\tTFR_EST_preserve_annexation = yes\n"
                               f"{indent}}}\n{indent}else = {{\n{indent}\t" + raw.replace("\n", "\n\t") + f"\n{indent}}}")
                edits.append((e.start, e.end, replacement, "pre-annex Estonia guard preserving troop policy"))
        elif e.key == "transfer_state" and e.value == "13":
            replacement = (f"if = {{\n{indent}\tlimit = {{ OR = {{ original_tag = EST NOT = {{ EST = {{ has_country_flag = TFR_EST_initialized }} }} }} }}\n"
                           f"{indent}\ttransfer_state = 13\n{indent}}}\n{indent}else = {{\n"
                           f"{indent}\tTFR_EST_protect_anchor = yes\n{indent}}}")
            edits.append((e.start, e.end, replacement, "protect Northern Estonia before transfer"))
        elif e.key in ("transfer_state_to", "set_state_owner_to") and e.value != "EST":
            # A state iterator can reach the anchor even if EST is nowhere in
            # the immediate block (all-country settlement arrays, for example).
            state_scope = any(a.key in ("every_state", "every_owned_state", "every_controlled_state", "13") for a in ancestors)
            if state_scope and (peace or "SOV" in relative or "GER" in relative):
                replacement = (f"if = {{\n{indent}\tlimit = {{ OR = {{ NOT = {{ state = 13 }} NOT = {{ EST = {{ has_country_flag = TFR_EST_initialized }} }} {e.value} = {{ original_tag = EST }} }} }}\n"
                               f"{indent}\t{raw}\n{indent}}}\n{indent}else = {{\n"
                               f"{indent}\t{e.value} = {{ TFR_EST_protect_anchor = yes }}\n{indent}}}")
                edits.append((e.start, e.end, replacement, "guard state iterator ownership transfer"))
        elif e.key == "set_state_controller_to" and e.value != "EST":
            state_scope = any(a.key in ("every_state", "every_owned_state", "every_controlled_state", "13") for a in ancestors)
            if state_scope and peace:
                replacement = (f"if = {{\n{indent}\tlimit = {{ OR = {{ NOT = {{ state = 13 }} NOT = {{ EST = {{ has_country_flag = TFR_EST_initialized }} }} {e.value} = {{ original_tag = EST }} }} }}\n"
                               f"{indent}\t{raw}\n{indent}}}")
                edits.append((e.start, e.end, replacement, "keep occupation anchor controller"))
        elif e.key == "country_exists" and e.value == "EST" and peace:
            edits.append((e.start, e.end, "TFR_EST_has_independent_estonia = yes", "defeated Estonia remains present"))
        elif e.key == "exists" and e.value == "no" and ancestors and ancestors[-1].key == "EST":
            edits.append((e.start, e.end, "TFR_EST_russian_occupation_or_absent = yes", "Russian occupation/pacification predicate"))
        elif e.key == "puppet" and e.value in ("EST", "ROOT"):
            # A harmless setter is followed by a queue, allowing the parent to
            # finish appointing leaders and transferring territory first.
            if e.value == "EST" or peace:
                guard = f"{e.value} = {{ original_tag = EST has_country_flag = TFR_EST_initialized }}"
                replacement = raw + (f"\n{indent}if = {{\n{indent}\tlimit = {{ {guard} }}\n"
                                     f"{indent}\t{e.value} = {{ TFR_EST_queue_occupation_reconciliation = yes }}\n{indent}}}")
                edits.append((e.start, e.end, replacement, "defer occupation setup after parent puppet"))
        elif e.key == "load_focus_tree" and e.value == "generic_focus":
            # Some parent follow-up events reload generic trees days later.
            replacement = (f"if = {{\n{indent}\tlimit = {{ original_tag = EST has_country_flag = TFR_EST_initialized is_subject = yes }}\n"
                           f"{indent}\tTFR_EST_queue_occupation_reconciliation = yes\n{indent}}}\n{indent}else = {{ {raw} }}")
            if peace or "SOV" in relative or "GER" in relative:
                edits.append((e.start, e.end, replacement, "prevent generic tree replacing occupation"))
    # Focus-tree content registration is deliberately a single tag addition.
    if relative.endswith("00_TFR_scripted_triggers_ZZZ_generic.txt"):
        marker = "has_content_tag = {"
        start = text.index(marker)
        pos = text.index("tag = SOV", start)
        edits.append((pos, pos, "tag = EST\n\t\t", "register Estonia as full content"))
    # Pacification applies only to Soviet-owned occupied territory. The retained
    # anchor and any remaining Estonian region are not resistance states.
    if relative == "common/decisions/TFR_decisions_SOV.txt":
        for e, _ in walk(entries):
            if e.key.startswith("SOV_") and "estonia" in e.key:
                for child, parents in walk(e.children):
                    if child.key in ("13", "191", "840", "1329") and child.children:
                        if any(p.key == "available" for p in parents):
                            new = (f"{child.key} = {{ OR = {{ NOT = {{ is_owned_by = SOV }} AND = {{ compliance > 80 resistance < 10 }} }} }}")
                            edits.append((child.start, child.end, new, "pacify only Soviet-owned Estonian states"))
                        elif any(p.key in ("remove_effect", "hidden_effect") for p in parents):
                            ins = child.start + text[child.start:child.end].index("{") + 1
                            edits.append((ins, ins, "\n\t\t\t\tif = { limit = { is_owned_by = SOV is_controlled_by = SOV }", "limit occupation decisions to Soviet-held territory"))
                            edits.append((child.end - 1, child.end - 1, "\n\t\t\t\t}", "close Soviet-held territory guard"))
                if e.key == "SOV_restore_order_estonia":
                    avail = next(c for c in e.children if c.key == "available")
                    insert = text.index("{", avail.start) + 1
                    edits.append((insert, insert, "\n\t\t\tany_owned_state = { is_core_of = EST }", "require occupied Estonian territory before pacification"))
    # Edits may not overlap: an enclosing replacement should be handled
    # explicitly rather than silently discarding a nested protection.
    edits.sort(key=lambda x: (x[0], x[1]))
    for a, b in zip(edits, edits[1:]):
        if a[1] > b[0]:
            raise ValueError(f"Overlapping protections in {relative}: {a[3]}, {b[3]}")
    audit = [{"line": text.count("\n", 0, a) + 1, "reason": reason} for a, _, _, reason in edits]
    for a, b, replacement, _ in reversed(edits):
        # New guard indentation can surround parent code indented with spaces.
        # Expand only replacement prefixes so no space-before-tab is introduced.
        replacement = re.sub(r"(?m)^[ \t]+", lambda m: m.group().expandtabs(4), replacement)
        tail = re.sub(r"^[ \t]+(?=\r?\n)", "", text[b:])
        text = text[:a] + replacement + tail
    return text, audit


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    candidates = ["common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt",
                  "common/on_actions/TFR_on_actions_ZZZ_peace.txt",
                  "common/scripted_effects/TFR_scripted_effects_SOV.txt",
                  "common/scripted_effects/TFR_scripted_effects_GER.txt",
                  "common/decisions/TFR_decisions_SOV.txt",
                  "common/decisions/TFR_decisions_GER.txt",
                  "events/TFR_events_SOV.txt",
                  "events/TFR_events_BLR.txt",
                  "common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt"]
    candidates += [str(p.relative_to(args.parent)).replace("\\", "/") for p in (args.parent / "common/national_focus").glob("TFR_national_focus_SOV*.txt")]
    candidates += [str(p.relative_to(args.parent)).replace("\\", "/") for p in (args.parent / "common/national_focus").glob("TFR_national_focus_GER*.txt")]
    baseline_descriptor = (args.parent / "descriptor.mod").read_text(encoding="utf-8-sig")
    version = re.search(r'^version="([^"]+)"', baseline_descriptor, re.M)[1]
    manifest = {"parent": "The Fire Rises", "version": version, "supported_game_version": "1.19.*", "protection": "EST survives supported scripted settlements with state 13; no post-annex recreation", "excluded_mutations": [{"path": "common/decisions/TFR_decisions_ZZZ_generic_debug.txt", "reason": "Developer-only map construction/console paths are outside supported campaign settlements"}], "overrides": []}
    failures = []
    for relative in sorted(set(candidates)):
        source = args.parent / relative
        source_bytes = source.read_bytes()
        text = source_bytes.decode("utf-8-sig")
        patched, audit = parent_patch(text, relative)
        if not audit:
            continue
        # Hash upstream bytes verbatim, retain its BOM, and emit canonical LF
        # so Git checkout normalization cannot invalidate generated hashes.
        bom = source_bytes.startswith(b"\xef\xbb\xbf")
        patched = patched.replace("\r\n", "\n").replace("\r", "\n")
        generated = ((b"\xef\xbb\xbf" if bom else b"") + patched.encode("utf-8"))
        destination = ROOT / relative
        manifest["overrides"].append({"path": relative, "upstream_sha256": hashlib.sha256(source_bytes).hexdigest(), "generated_sha256": hashlib.sha256(generated).hexdigest(), "changes": audit})
        if args.write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(generated)
        elif not destination.exists() or destination.read_bytes() != generated:
            failures.append(relative)
    manifest_path = ROOT / "docs/compatibility.json"
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if args.write:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(manifest_bytes)
    elif not manifest_path.exists() or manifest_path.read_bytes() != manifest_bytes:
        failures.append("docs/compatibility.json (upstream or generator differs)")
    if failures:
        raise SystemExit("Compatibility mismatch: " + ", ".join(failures))
    count = sum(len(o["changes"]) for o in manifest["overrides"])
    print(f"TFR {version}: {len(manifest['overrides'])} reproducible overrides, {count} audited protections; {'written' if args.write else 'verified'}.")


if __name__ == "__main__":
    main()

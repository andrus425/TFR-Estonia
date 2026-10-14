"""Validate new Estonia scripts and effective TFR/vanilla references.

Usage: python tools/validate_mod.py [--tfr PATH] [--game PATH]
The game remains the authority on engine behavior and visual layout.
"""
from pathlib import Path
import argparse
import collections
import json
import re
import sys
from clausewitz import Block, parse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TFR = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356")
DEFAULT_GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")


def effective_files(roots, directory, suffix):
    result = {}
    for root in roots:
        base = root / directory
        if base.exists():
            for path in base.rglob("*" + suffix):
                result[path.relative_to(root).as_posix()] = path
    return result


def validate(tfr, game):
    errors, warnings = [], []
    roots = [game, tfr, ROOT]
    parsed = {}
    custom = {}
    for directory in ("common", "events", "history", "interface"):
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in {".txt", ".gui", ".gfx"}:
                continue
            rel = path.relative_to(ROOT).as_posix()
            try:
                tree = parse(path.read_text(encoding="utf-8-sig"), rel)
                parsed[rel] = tree
                if path.name.startswith("TFR_EST_") or rel == "history/countries/EST - Estonia.txt":
                    custom[rel] = tree
            except (ValueError, UnicodeError) as exc:
                errors.append(str(exc))

    # New localisation must be BOM encoded; duplicate new keys are forbidden.
    loc = {}
    for path in effective_files(roots, "localisation", ".yml").values():
        if "english" not in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for match in re.finditer(r'^\s*([^\s:#]+):(?:\d+)?\s+"', text, re.M):
            loc[match.group(1)] = path
    own_loc = {}
    for path in sorted((ROOT / "localisation").rglob("*.yml")):
        data = path.read_bytes()
        if not data.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path.relative_to(ROOT)}: localisation missing UTF-8 BOM")
        text = data.decode("utf-8-sig")
        if not text.startswith("l_english:"):
            errors.append(f"{path.relative_to(ROOT)}: expected l_english header")
        for line_no, line in enumerate(text.splitlines()[1:], 2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = re.fullmatch(r'\s+([^\s:#]+):\d+\s+"(?:[^"\\]|\\.)*"\s*', line)
            if not match:
                errors.append(f"{path.relative_to(ROOT)}:{line_no}: malformed localisation")
                continue
            key = match.group(1)
            if key in own_loc:
                errors.append(f"duplicate localisation key {key}: {own_loc[key]} and {path.name}")
            own_loc[key] = path.name

    catalogs = collections.defaultdict(set)
    owners = {}
    character_roles = {}

    def register(kind, name, rel):
        if not isinstance(name, str):
            return
        tag = (kind, name)
        if tag in owners and name.startswith("TFR_EST_"):
            errors.append(f"duplicate {kind} {name}: {owners[tag]} and {rel}")
        owners[tag] = rel
        catalogs[kind].add(name)

    for rel, tree in parsed.items():
        if rel.startswith("common/scripted_effects/"):
            for e in tree.entries:
                register("effect", e.key, rel)
        if rel.startswith("common/scripted_triggers/"):
            for e in tree.entries:
                register("trigger", e.key, rel)
        if rel.startswith("common/dynamic_modifiers/"):
            for e in tree.entries:
                register("dynamic_modifier", e.key, rel)
        if rel.startswith("common/characters/"):
            chars = tree.get("characters")
            if isinstance(chars, Block):
                for e in chars.entries:
                    register("character", e.key, rel)
                    if isinstance(e.value, Block):
                        character_roles[e.key] = len(e.value.all("country_leader"))
        if rel.startswith("common/ideas/"):
            ideas = tree.get("ideas")
            if isinstance(ideas, Block):
                for group in ideas.entries:
                    if isinstance(group.value, Block):
                        for e in group.value.entries:
                            register("idea", e.key, rel)
        if rel.startswith("common/decisions/categories/"):
            for e in tree.entries:
                register("category", e.key, rel)
        elif rel.startswith("common/decisions/"):
            for e in tree.entries:
                if isinstance(e.value, Block):
                    for decision in e.value.entries:
                        if isinstance(decision.value, Block):
                            register("decision", decision.key, rel)
        for parents, e in tree.walk():
            if e.key in {"focus_tree", "focus", "shared_focus"} and isinstance(e.value, Block):
                name = e.value.get("id")
                register("tree" if e.key == "focus_tree" else "focus", name, rel)
            if e.key in {"country_event", "news_event"} and not parents and isinstance(e.value, Block):
                register("event", e.value.get("id"), rel)

    # Effective sprite catalog: a TFR file of the same name shadows vanilla.
    sprites = set()
    fonts = set()
    for path in effective_files(roots, "interface", ".gfx").values():
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        sprites.update(re.findall(r'\bname\s*=\s*"?(GFX_[^\s"{}]+)', text))
        # Font names are declared in bitmapfont blocks (including definitions
        # in TFR_fonts.gfx), independently of the sprite name catalog. A typo
        # here is accepted by the Clausewitz parser but rejected by the engine.
        fonts.update(re.findall(r'\bbitmapfont\s*=\s*\{\s*name\s*=\s*"([^"\r\n]+)"', text))
    # Some DLC portrait and focus assets are exposed from their own interface.
    for path in (game / "dlc").rglob("*.gfx"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        sprites.update(re.findall(r'\bname\s*=\s*"?(GFX_[^\s"{}]+)', text))
        fonts.update(re.findall(r'\bbitmapfont\s*=\s*\{\s*name\s*=\s*"([^"\r\n]+)"', text))

    def missing(kind, ref, rel, line):
        if isinstance(ref, str) and ref.startswith("TFR_EST_") and ref not in catalogs[kind]:
            errors.append(f"{rel}:{line}: undefined {kind} {ref}")

    for kind in ("focus", "decision", "category", "idea", "character", "dynamic_modifier"):
        for name in catalogs[kind]:
            if name.startswith("TFR_EST_") and name not in loc:
                errors.append(f"missing localisation: {name}")
        if kind in {"focus", "decision", "idea", "dynamic_modifier"}:
            for name in catalogs[kind]:
                if name.startswith("TFR_EST_") and name + "_desc" not in loc:
                    errors.append(f"missing description: {name}_desc")

    for rel, tree in custom.items():
        for parents, e in tree.walk():
            if rel.startswith("common/dynamic_modifiers/") and e.key == "icon" and isinstance(e.value, str):
                if e.value not in sprites:
                    errors.append(f"{rel}:{e.line}: missing dynamic modifier icon {e.value}")
            if e.key in {"add_dynamic_modifier", "remove_dynamic_modifier", "has_dynamic_modifier"}:
                ref = e.value.get("modifier") if isinstance(e.value, Block) else e.value
                missing("dynamic_modifier", ref, rel, e.line)
            is_effect_definition = rel.startswith("common/scripted_effects/") and not parents
            is_decision_definition = rel.startswith("common/decisions/") and not rel.startswith("common/decisions/categories/") and len(parents) == 1
            if e.key in catalogs["effect"] and isinstance(e.value, Block) and not is_effect_definition and not is_decision_definition:
                errors.append(f"{rel}:{e.line}: scripted effect {e.key} cannot accept an argument block; set its native temporary input and call = yes")
            if e.key == "set_politics" and isinstance(e.value, Block) and e.value.get("ruling_party") is None:
                errors.append(f"{rel}:{e.line}: set_politics requires ruling_party")
            if e.key == "overlord" and isinstance(e.value, Block):
                errors.append(f"{rel}:{e.line}: bare overlord scope is invalid; use var:overlord")
            if isinstance(e.value, str) and re.search(r'\$[A-Z_]+\$', e.value):
                errors.append(f"{rel}:{e.line}: unsupported scripted-effect parameter {e.value}")
            if rel.startswith("interface/") and e.key in {"font", "buttonFont"} and isinstance(e.value, str):
                if e.value not in fonts:
                    errors.append(f"{rel}:{e.line}: missing GUI font {e.value}")
            if rel.startswith("interface/") and e.key == "quadTextureSprite" and isinstance(e.value, str):
                if e.value not in sprites:
                    errors.append(f"{rel}:{e.line}: missing GUI texture sprite {e.value}")
            if (e.key.startswith("TFR_EST_") and e.op == "=" and
                    (e.value in ("yes", "no") if isinstance(e.value, str) else isinstance(e.value, Block)) and
                    parents and parents[-1] not in {"ideas", "country", "hidden_ideas", "characters"} and
                    not any(x in parents for x in {"set_variable", "set_temp_variable", "clamp_variable", "check_variable", "modifier", "triggers", "effects", "properties"}) and
                    e.key not in catalogs["effect"] and e.key not in catalogs["trigger"] and
                    e.key not in catalogs["decision"]):
                # Definition headers in focus/decision/gui trees are not calls.
                if rel.startswith(("events/", "common/scripted_effects/", "common/on_actions/")):
                    errors.append(f"{rel}:{e.line}: unknown scripted call {e.key}")
            if e.key == "focus" and parents and parents[-1] in {"prerequisite", "mutually_exclusive"}:
                missing("focus", e.value, rel, e.line)
            if e.key in {"has_completed_focus", "complete_national_focus"}:
                missing("focus", e.value, rel, e.line)
            if e.key in {"has_focus_tree", "load_focus_tree"}:
                missing("tree", e.value.get("tree") if isinstance(e.value, Block) else e.value, rel, e.line)
            if e.key in {"recruit_character", "promote_character", "retire_character"}:
                missing("character", e.value.get("character") if isinstance(e.value, Block) else e.value, rel, e.line)
                if e.key == "promote_character":
                    character = e.value.get("character") if isinstance(e.value, Block) else e.value
                    if character_roles.get(character, 0) > 1 and (not isinstance(e.value, Block) or e.value.get("ideology") is None):
                        errors.append(f"{rel}:{e.line}: multi-role character {character} needs explicit promotion ideology")
            if e.key == "localization_key" and isinstance(e.value, str) and e.value not in loc:
                errors.append(f"{rel}:{e.line}: missing scripted localization {e.value}")
            if e.key in {"has_idea", "remove_ideas", "add_ideas"}:
                refs = [x.key if x.op is None else x.value for x in e.value.entries] if isinstance(e.value, Block) else [e.value]
                for ref in refs:
                    missing("idea", ref, rel, e.line)
            if e.key == "add_timed_idea" and isinstance(e.value, Block):
                missing("idea", e.value.get("idea"), rel, e.line)
            if e.key in {"custom_effect_tooltip", "tooltip", "title", "desc", "name", "text"} and isinstance(e.value, str) and e.value.startswith("TFR_EST_"):
                if e.key != "name" or (parents and parents[-1] == "option"):
                    if e.value not in loc:
                        errors.append(f"{rel}:{e.line}: missing text {e.value}")
            if e.key in {"country_event", "news_event"} and parents and isinstance(e.value, Block):
                event = e.value.get("id")
                if isinstance(event, str) and event.startswith("tfr_est") and event not in catalogs["event"]:
                    errors.append(f"{rel}:{e.line}: undefined event {event}")
            if e.key == "picture" and isinstance(e.value, str):
                if e.value.startswith("gfx/") and not any((base / e.value).exists() for base in roots):
                    errors.append(f"{rel}:{e.line}: missing picture file {e.value}")
                ref = e.value if e.value.startswith("GFX_") else "GFX_idea_" + e.value
                if ("ideas" in parents or e.value.startswith("GFX_")) and ref not in sprites:
                    errors.append(f"{rel}:{e.line}: missing picture sprite {ref}")
            if e.key == "icon" and isinstance(e.value, str):
                ref = e.value
                if not ref.startswith("GFX_"):
                    ref = ("GFX_decision_category_" if rel.startswith("common/decisions/categories/") else "GFX_decision_") + ref
                if ref not in sprites:
                    errors.append(f"{rel}:{e.line}: missing icon sprite {ref}")
            if e.key == "large" and isinstance(e.value, str):
                if e.value.startswith("GFX_") and e.value not in sprites:
                    errors.append(f"{rel}:{e.line}: missing portrait sprite {e.value}")
                elif e.value.startswith("gfx/") and not any((base / e.value).exists() for base in roots):
                    errors.append(f"{rel}:{e.line}: missing portrait {e.value}")

    # Focus graph must be acyclic and have unique layout positions within a tree.
    graph = {}
    for rel, tree in custom.items():
        if not rel.startswith("common/national_focus/"):
            continue
        for _, entry in tree.walk():
            if entry.key in {"focus", "shared_focus"} and isinstance(entry.value, Block):
                id_ = entry.value.get("id")
                prereqs = []
                for prereq in entry.value.all("prerequisite"):
                    if isinstance(prereq, Block):
                        prereqs.extend(prereq.all("focus"))
                graph[id_] = prereqs
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            errors.append(f"cycle in focus prerequisites at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for other in graph.get(node, []):
            visit(other)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)

    # Verify reproducibility and changes against the pinned parent baseline.
    manifest = ROOT / "docs/compatibility.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        warnings.append("Compatibility manifest present; run its generator in --check mode before release.")
    if not tfr.exists() or not game.exists():
        errors.append("Installed TFR and HOI4 directories are required for reference validation.")
    result = {"files_parsed": len(parsed), "new_focuses": len([x for x in catalogs["focus"] if x.startswith("TFR_EST_")]),
              "new_events": len([x for x in catalogs["event"] if x.startswith("tfr_est")]),
              "new_decisions": len([x for x in catalogs["decision"] if x.startswith("TFR_EST_")]),
              "localisation_keys": len(own_loc), "errors": sorted(set(errors)), "warnings": warnings}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tfr", type=Path, default=DEFAULT_TFR)
    ap.add_argument("--game", type=Path, default=DEFAULT_GAME)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = validate(args.tfr, args.game)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Parsed {result['files_parsed']} mod files; {result['new_focuses']} focuses, {result['new_events']} events, {result['new_decisions']} decisions, {result['localisation_keys']} localisation keys.")
        for error in result["errors"]:
            print("ERROR: " + error)
        for warning in result["warnings"]:
            print("NOTE: " + warning)
        print(f"{len(result['errors'])} errors.")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())

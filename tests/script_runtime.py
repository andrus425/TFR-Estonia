"""Execute the arithmetic/control-flow subset used by the actual game scripts.

This deliberately does not emulate combat, UI, general country scope changes or the
engine's event scheduler. Tests can fail on missing numerical operations, rather
than silently falling back to a separately implemented election algorithm.
"""
from pathlib import Path
from fractions import Fraction
from datetime import date
from functools import lru_cache
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clausewitz import Block, parse
from native_script_interface import AMOUNT_INPUTS, amount_call


@lru_cache(maxsize=256)
def _parsed_script(path, modified_ns, byte_size):
    # Definitions are read-only during execution. Each Runtime keeps its own
    # catalogs and gameplay state; changed generated files invalidate this key.
    return parse(path.read_text(encoding="utf-8-sig"), str(path))


def parsed_script(path):
    metadata = path.stat()
    return _parsed_script(path, metadata.st_mtime_ns, metadata.st_size)


class Runtime:
    def __init__(self):
        self.variables = {}
        self.temp = {}
        self.flags = {"TFR_EST_initialized"}
        self.global_flags = set()
        self.ideas = set()
        self.dynamic = set()
        self.dynamic_additions = []
        self.dynamic_updates = 0
        self.focus_layout_refreshes = 0
        self.events = []
        self.messages = []
        self.characters = []
        self.leader = None
        self.templates = []
        self.calls = []
        self.politics = {}
        self.effects = {}
        self.triggers = {}
        self.props = {"is_ai": "no", "is_subject": "no", "tag": "EST", "original_tag": "EST", "has_war": "no", "has_capitulated": "no"}
        self.props.update({"date": date(2020, 1, 1), "game_rules": {}, "owner": "EST", "controller": "EST", "focus_tree": "TFR_EST_main_tree", "world_wars": set()})
        self.props['completed_focuses'] = set()
        for directory, catalog in (("scripted_effects", self.effects), ("scripted_triggers", self.triggers)):
            for path in (ROOT / "common" / directory).glob("TFR_EST_*.txt"):
                tree = parsed_script(path)
                catalog.update({e.key: e.value for e in tree.entries})
        # Execute TFR's real five-tier domestic COVID predicate from the
        # compatibility override, rather than inventing a test-only infection.
        generic_path = ROOT / "common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt"
        generic = parsed_script(generic_path)
        self.triggers["generic_has_corona"] = generic.get("generic_has_corona")
        self.state_id = None
        self.states = {n: {"owner": "EST", "controller": "EST", "slots": 25, "buildings": {}}
                       for n in (13, 191, 1329, 840)}
        self.operations = 0

    def num(self, value, args=None):
        value = str(value)
        if value == "global.year":
            return Fraction(self.props["date"].year)
        if value.startswith("$") and value.endswith("$"):
            value = str((args or {})[value.strip("$")])
        try:
            return Fraction(value)
        except ValueError:
            return self.temp.get(value, self.variables.get(value, Fraction(0)))

    def condition(self, block, args=None):
        if not isinstance(block, Block):
            raise AssertionError("Expected condition block")
        return all(self.test(e.key, e.op, e.value, args) for e in block.entries)

    def test(self, key, op, value, args=None):
        if key == "custom_trigger_tooltip":
            return all(self.test(e.key, e.op, e.value, args)
                       for e in value.entries if e.key != "tooltip")
        if key == "OR":
            return any(self.test(e.key, e.op, e.value, args) for e in value.entries)
        if key in ("AND", "limit"):
            return self.condition(value, args)
        if key == "NOT":
            # HOI4's NOT rejects each contained condition; use explicit single
            # conditions in tests where a multi-child interpretation matters.
            return all(not self.test(e.key, e.op, e.value, args) for e in value.entries)
        if key == "check_variable":
            if value.get("var") is not None:
                left = self.num(value.get("var"), args)
                right = self.num(value.get("value"), args)
                operation = value.get("compare", "equals")
            else:
                e = value.entries[0]
                left, right, operation = self.num(e.key, args), self.num(e.value, args), e.op
            return {"equals": left == right, "=": left == right,
                    "greater_than": left > right, ">": left > right,
                    "greater_than_or_equals": left >= right, ">=": left >= right,
                    "less_than": left < right, "<": left < right,
                    "less_than_or_equals": left <= right, "<=": left <= right,
                    "not_equals": left != right, "!=": left != right}[operation]
        if key == "has_country_flag":
            return value in self.flags
        if key == "has_global_flag":
            return value in self.global_flags
        if key == "has_idea":
            return value in self.ideas
        if key == "has_dynamic_modifier":
            return value.get("modifier") in self.dynamic
        if key == "always":
            return value == "yes"
        if key in self.triggers:
            answer = self.condition(self.triggers[key], args)
            return answer if value == "yes" else not answer
        if key == "date":
            target = date(*map(int, value.split(".")[:3]))
            actual = self.props["date"]
            return {">": actual > target, "<": actual < target, "=": actual == target}[op]
        if key == "has_game_rule":
            return self.props["game_rules"].get(value.get("rule"), "DEFAULT") == value.get("option")
        if key in {"is_owned_by", "is_controlled_by"}:
            field = "owner" if key == "is_owned_by" else "controller"
            return (self.states[self.state_id][field] if self.state_id is not None else self.props[field]) == value
        if key == "has_focus_tree":
            return self.props["focus_tree"] == value
        if key == "has_completed_focus":
            return value in self.props['completed_focuses']
        if key == "has_country_leader":
            return value.get("character") == self.leader
        if key == "has_government":
            return self.politics.get("ruling_party") == value
        if key == "has_autonomy_state":
            return self.props.get("autonomy_state") == value
        if key in {"SOV", "GER"} and isinstance(value, Block):
            before = self.props["tag"]
            self.props["tag"] = key
            answer = self.condition(value, args)
            self.props["tag"] = before
            return answer
        if key.isdigit() and isinstance(value, Block):
            previous = self.state_id
            self.state_id = int(key)
            try:
                return self.condition(value, args)
            finally:
                self.state_id = previous
        if key == "free_building_slots":
            if self.state_id is None:
                raise AssertionError("free_building_slots requires a state scope")
            state = self.states[self.state_id]
            free = state["slots"] - sum(state["buildings"].values())
            entry = next(e for e in value.entries if e.key == "size")
            target = self.num(entry.value, args)
            return {">": free > target, "=": free == target, "<": free < target}[entry.op]
        if key == "has_war_with":
            return frozenset((self.props["tag"], value)) in self.props["world_wars"]
        if key in self.props:
            return self.props[key] == value
        if key == "has_variable":
            return value in self.variables or value in self.temp
        # Date, country scopes and game rules are outside arithmetic tests.
        raise AssertionError(f"Unsupported test condition {key} {op} {value}")

    def call(self, name, arguments=None):
        if name not in self.effects:
            raise AssertionError(f"Undefined effect {name}")
        if arguments:
            if name not in AMOUNT_INPUTS or set(arguments) != {"AMOUNT"}:
                raise AssertionError("HOI4 scripted effects do not accept argument blocks")
            # Convenience for test fixtures: execute the actual native two-
            # statement authoring interface rather than emulating parameters.
            self.run(parse(amount_call(name, arguments["AMOUNT"])))
            return
        self.run(self.effects[name], arguments)

    def run(self, block, args=None):
        chain = None
        arithmetic = {"set_variable": "set", "set_temp_variable": "set",
                      "add_to_variable": "add", "add_to_temp_variable": "add",
                      "subtract_from_variable": "sub", "subtract_from_temp_variable": "sub",
                      "multiply_variable": "mul", "multiply_temp_variable": "mul",
                      "divide_variable": "div", "divide_temp_variable": "div",
                      "modulo_variable": "mod", "modulo_temp_variable": "mod"}
        for e in block.entries:
            self.operations += 1
            if self.operations > 200000:
                raise AssertionError("Script exceeded bounded-operation limit")
            key, value = e.key, e.value
            if key == "limit":
                continue
            if key in {"if", "else_if", "else"}:
                if key == "if":
                    chain = False
                allowed = not chain and (key == "else" or self.condition(value.get("limit", Block([])), args))
                if allowed:
                    self.run(value, args)
                    chain = True
                continue
            chain = None
            if key in arithmetic:
                store = self.temp if "temp" in key else self.variables
                if value.get("var") is not None:
                    var, number = value.get("var"), value.get("value")
                else:
                    var, number = value.entries[0].key, value.entries[0].value
                before, number = store.get(var, Fraction(0)), self.num(number, args)
                operation = arithmetic[key]
                if operation == "set": store[var] = number
                elif operation == "add": store[var] = before + number
                elif operation == "sub": store[var] = before - number
                elif operation == "mul": store[var] = before * number
                elif operation == "div": store[var] = before / number
                elif operation == "mod": store[var] = before % number
            elif key in {"clamp_variable", "clamp_temp_variable"}:
                store = self.temp if "temp" in key else self.variables
                var = value.get("var")
                number = store.get(var, Fraction(0))
                if value.get("min") is not None: number = max(number, self.num(value.get("min"), args))
                if value.get("max") is not None: number = min(number, self.num(value.get("max"), args))
                store[var] = number
            elif key == "set_country_flag":
                self.flags.add(value.get("flag") if isinstance(value, Block) else value)
            elif key == "clr_country_flag":
                self.flags.discard(value)
            elif key in {"add_ideas", "remove_ideas"}:
                refs = [x.key if x.op is None else x.value for x in value.entries] if isinstance(value, Block) else [value]
                for ref in refs:
                    if key == "add_ideas": self.ideas.add(ref)
                    else: self.ideas.discard(ref)
            elif key == "add_timed_idea":
                self.ideas.add(value.get("idea"))
            elif key == "remove_dynamic_modifier":
                self.dynamic.discard(value.get("modifier"))
            elif key == "add_dynamic_modifier":
                self.dynamic.add(value.get("modifier"))
                self.dynamic_additions.append(value.get("modifier"))
            elif key == "force_update_dynamic_modifier":
                self.dynamic_updates += 1
            elif key in {"hidden_effect", "effect"}:
                self.run(value, args)
            elif key == "effect_tooltip":
                # HOI4 renders this block without executing its effects.
                pass
            elif key == "while_loop_effect":
                count = 0
                while self.condition(value.get("limit"), args):
                    self.run(value, args)
                    count += 1
                    if count > 1000: raise AssertionError("Unbounded while loop")
            elif key in self.effects:
                if isinstance(value, Block):
                    raise AssertionError(f"HOI4 scripted effect {key} cannot accept an argument block")
                self.call(key)
            elif key in {"country_event", "news_event"}:
                self.events.append(value.get("id") if isinstance(value, Block) else value)
            elif key == "log": self.messages.append(value)
            elif key in {"promote_character", "recruit_character"}:
                self.characters.append(value)
                if key == "promote_character": self.leader = value.get("character") if isinstance(value, Block) else value
            elif key == "swap_ideas":
                self.ideas.discard(value.get("remove_idea"))
                self.ideas.add(value.get("add_idea"))
            elif key == "set_politics":
                self.politics.update({x.key: x.value for x in value.entries})
            elif key == "division_template": self.templates.append(value.get("name"))
            elif key == "load_focus_tree": self.props["focus_tree"] = value.get("tree") if isinstance(value, Block) else value
            elif key == "uncomplete_national_focus":
                # Model the documented completed-record operation only. The
                # native focus-progress engine and automatic cancellation are
                # deliberately outside this arithmetic/control-flow runtime.
                self.props['completed_focuses'].discard(value.get('focus'))
                self.calls.append((key, value.get('focus')))
            elif key in {"add_debt_with_inflation", "add_income_with_inflation"}:
                field = "debt_var_temp" if key == "add_debt_with_inflation" else "income_var_temp"
                self.calls.append((key, self.temp.get(field)))
            elif key in {"add_political_power", "army_experience", "add_stability"}:
                field = "political_power" if key == "add_political_power" else key
                self.props[field] = self.props.get(field, Fraction(0)) + self.num(value, args)
            elif key in {"ROOT", "EST"} or key.isdigit():
                previous = self.state_id
                self.state_id = None if key in {"ROOT", "EST"} else int(key)
                try:
                    self.run(value, args)
                finally:
                    self.state_id = previous
            elif key == "add_building_construction":
                if self.state_id is None:
                    raise AssertionError("Building construction requires a state scope")
                buildings = self.states[self.state_id]["buildings"]
                building = value.get("type")
                amount = int(self.num(value.get("level"), args))
                buildings[building] = buildings.get(building, 0) + amount
                self.calls.append(("add_building_construction", self.state_id, building, amount))
            elif key == "clear_variable": self.variables.pop(value, None)
            elif key == "mark_focus_tree_layout_dirty":
                self.focus_layout_refreshes += 1
            elif key in {"set_popularities", "clear_array", "custom_effect_tooltip", "set_party_name", "set_party_long_name"}:
                pass
            else:
                raise AssertionError(f"Unsupported numerical effect {key}")

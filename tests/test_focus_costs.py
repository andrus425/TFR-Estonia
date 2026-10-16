"""Visible parent-economy costs and concise but real focus requirements.

The debt tests execute TFR's actual inflation helper. GDP recalculation is a
deliberate empty fixture: this test checks the cost handed to the ledger and
tooltip, not TFR's independent national GDP model or HOI4's tooltip renderer.
"""
from datetime import date
from fractions import Fraction
import re
import unittest

from script_runtime import ROOT, Block, Runtime, parse
from patch_tfr_compatibility import DEFAULT_PARENT


PARENT_EFFECTS = "common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt"
COVID_IDEAS = (
    "lower_covid_cases", "low_covid_cases", "medium_covid_cases",
    "high_covid_cases", "higher_covid_cases",
)


def read_script(relative, base=ROOT):
    path = base / relative
    return parse(path.read_text(encoding="utf-8-sig"), str(path))


def shape(block):
    return tuple((entry.key, entry.op,
                  shape(entry.value) if isinstance(entry.value, Block) else entry.value)
                 for entry in block.entries)


def localization_values():
    values = {}
    for path in (ROOT / "localisation/english").glob("TFR_EST*.yml"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(r"^\s*(\S+):\d+\s+(.+)$", line)
            if match:
                values[match[1]] = match[2]
    return values


def contains(block, key):
    return any(entry.key == key for _, entry in block.walk())


def requirement_tooltips(block, triggers, seen=None):
    """Resolve authored scripted triggers without changing their scope."""
    seen = set() if seen is None else seen
    for _, entry in block.walk():
        if entry.key == "custom_trigger_tooltip":
            yield entry.value
        elif entry.key in triggers and entry.key not in seen:
            seen.add(entry.key)
            yield from requirement_tooltips(triggers[entry.key], triggers, seen)


def budget_call_paths(block, effects, hidden=False, stack=()):
    """Find cost calls through scripted effects, retaining tooltip visibility."""
    for parents, entry in block.walk():
        hidden_here = hidden or "hidden_effect" in parents
        if entry.key == "TFR_EST_spend_budget":
            yield stack, hidden_here
        elif entry.key in effects and entry.key not in stack:
            yield from budget_call_paths(effects[entry.key], effects,
                                         hidden_here, stack + (entry.key,))


class FocusCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent_debt = read_script(PARENT_EFFECTS).get("add_debt_with_inflation")
        cls.localization = localization_values()

    def runtime_with_parent_ledger(self):
        runtime = Runtime()
        runtime.effects["add_debt_with_inflation"] = self.parent_debt
        runtime.effects["check_gdp"] = Block([])
        return runtime

    def test_cost_uses_the_real_unmodified_parent_inflation_helper(self):
        upstream = read_script(PARENT_EFFECTS, DEFAULT_PARENT).get("add_debt_with_inflation")
        self.assertEqual(shape(self.parent_debt), shape(upstream))

    def test_public_budget_helper_keeps_tfr_debt_tooltip_visible(self):
        helper = Runtime().effects["TFR_EST_spend_budget"]
        calls = [(parents, entry) for parents, entry in helper.walk()
                 if entry.key == "add_debt_with_inflation"]
        self.assertEqual(len(calls), 1)
        self.assertNotIn("hidden_effect", calls[0][0])
        self.assertEqual(calls[0][1].value, "yes")
        self.assertFalse(contains(helper, "custom_effect_tooltip"),
                         "The parent must show its calculated numerical debt cost")

    def test_focus_reward_wrappers_do_not_hide_the_public_cost_helper(self):
        runtime = Runtime()
        charged_focuses = 0
        for path in (ROOT / "common/national_focus").glob("TFR_EST_*.txt"):
            tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
            for _, entry in tree.walk():
                if (entry.key not in ("focus", "shared_focus")
                        or not isinstance(entry.value, Block) or not entry.value.get("id")):
                    continue
                reward = entry.value.get("completion_reward", Block([]))
                calls = list(budget_call_paths(reward, runtime.effects))
                if calls:
                    charged_focuses += 1
                for stack, hidden in calls:
                    with self.subTest(focus=entry.value.get("id"), effect_path=stack):
                        self.assertFalse(hidden, "A focus wrapper must not hide TFR's calculated cost")
        self.assertGreater(charged_focuses, 100)

    def test_millions_are_converted_to_billions_before_real_parent_inflation(self):
        for millions in (Fraction(0), Fraction(25), Fraction(52), Fraction(1000), Fraction(25, 2)):
            for inflation in (Fraction(0), Fraction(1, 10), Fraction(1), Fraction(-1, 20)):
                runtime = self.runtime_with_parent_ledger()
                runtime.variables.update(debt_var=Fraction(2), inflation_var=inflation)
                runtime.temp["TFR_EST_budget_cost"] = millions
                runtime.call("TFR_EST_spend_budget")
                expected = millions / 1000 * (1 + inflation)
                with self.subTest(millions=millions, inflation=inflation):
                    self.assertEqual(runtime.temp["debt_var_temp"], expected)
                    self.assertEqual(runtime.variables["debt_var"], 2 + expected)

    def test_parent_tooltip_observes_the_adjusted_cost_before_debt_is_added(self):
        entries = self.parent_debt.entries
        index = next(index for index, entry in enumerate(entries)
                     if entry.key == "custom_effect_tooltip" and entry.value == "add_debt_tooltip")
        # Execute the real prefix, so moving the tooltip before the inflation
        # arithmetic fails this check even if the final ledger stays correct.
        runtime = Runtime()
        runtime.temp["debt_var_temp"] = Fraction(52, 1000)
        runtime.variables.update(inflation_var=Fraction(1, 10), debt_var=Fraction(2))
        runtime.run(Block(entries[:index]))
        self.assertEqual(runtime.temp["debt_var_temp"], Fraction(572, 10000))
        self.assertEqual(runtime.variables["debt_var"], 2)
        self.assertFalse(any("hidden_effect" in parents
                             for parents, entry in self.parent_debt.walk()
                             if entry.key == "custom_effect_tooltip" and entry.value == "add_debt_tooltip"))

    def test_cohesion_and_readiness_show_the_signed_numeric_input(self):
        runtime = Runtime()
        for meter in ("cohesion", "readiness"):
            helper = runtime.effects["TFR_EST_change_" + meter]
            tooltips = [(parents, entry.value) for parents, entry in helper.walk()
                        if entry.key == "custom_effect_tooltip"]
            self.assertEqual(len(tooltips), 1)
            parents, key = tooltips[0]
            self.assertNotIn("hidden_effect", parents)
            self.assertIn(key, self.localization)
            self.assertIn(f"[?TFR_EST_{meter}_delta|=+0]", self.localization[key])
            changes = [(parents, entry) for parents, entry in helper.walk()
                       if entry.key in ("add_to_variable", "clamp_variable")]
            self.assertTrue(changes)
            self.assertTrue(all("hidden_effect" in parents for parents, _ in changes),
                            "Internal meter arithmetic must not clutter the numerical tooltip")

    def test_hiding_meter_arithmetic_preserves_actual_deltas_and_clamping(self):
        for meter in ("cohesion", "readiness"):
            for before, delta, expected in ((55, 7, 62), (55, -100, 0), (25, 250, 100)):
                runtime = Runtime()
                runtime.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
                runtime.variables["TFR_EST_" + meter] = Fraction(before)
                runtime.temp["TFR_EST_" + meter + "_delta"] = Fraction(delta)
                runtime.call("TFR_EST_change_" + meter)
                with self.subTest(meter=meter, before=before, delta=delta):
                    self.assertEqual(runtime.variables["TFR_EST_" + meter], expected)


class FocusRequirementTooltipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.focuses = {}
        for route in ("opening", "ratas", "kallas"):
            tree = read_script(f"common/national_focus/TFR_EST_{route}.txt")
            cls.focuses.update({focus.get("id"): focus for focus in tree.all("shared_focus")})
        cls.localization = localization_values()
        cls.triggers = Runtime().triggers

    def runtime(self, route):
        runtime = Runtime()
        runtime.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        runtime.call("TFR_EST_initialize_parliament")
        if route == "ratas":
            runtime.flags.update({"TFR_EST_ratas_retained", "TFR_EST_opening_complete"})
            runtime.props["completed_focuses"].add("TFR_EST_opening_marriage_referendum")
        elif route == "kallas":
            runtime.flags.update({"TFR_EST_ratas_resigned", "TFR_EST_referendum_failed",
                                  "TFR_EST_opening_complete", "TFR_EST_scripted_cabinet_change"})
            runtime.call("TFR_EST_nominate_reform")
            runtime.variables["TFR_EST_coalition_centre"] = Fraction(1)
            runtime.call("TFR_EST_recount_confidence")
            runtime.call("TFR_EST_confirm_cabinet")
            runtime.flags.add("TFR_EST_reform_centre_formed")
        runtime.props["date"] = date(2021, 1, 28) if route != "opening" else date(2020, 3, 1)
        return runtime

    def available(self, runtime, route, suffix):
        return runtime.condition(self.focuses[f"TFR_EST_{route}_{suffix}"].get("available"))

    def test_representative_governing_requirements_have_localized_nonempty_wrappers(self):
        for route, suffix in (("opening", "pension_reform"),
                              ("ratas", "family_home_guarantees"),
                              ("kallas", "pension_twenty")):
            available = self.focuses[f"TFR_EST_{route}_{suffix}"].get("available")
            wrappers = list(requirement_tooltips(available, self.triggers))
            with self.subTest(route=route):
                self.assertTrue(wrappers)
                self.assertTrue(any(any(entry.key != "tooltip" and entry.key != "always"
                                        for entry in wrapper.entries)
                                    for wrapper in wrappers))
                for wrapper in wrappers:
                    self.assertIn(wrapper.get("tooltip"), self.localization)

    def test_concise_government_tooltips_still_enforce_51_real_coalition_seats(self):
        for route, suffix in (("opening", "pension_reform"),
                              ("ratas", "family_home_guarantees"),
                              ("kallas", "pension_twenty")):
            runtime = self.runtime(route)
            runtime.variables["TFR_EST_coalition_seats"] = Fraction(51)
            with self.subTest(route=route):
                self.assertTrue(self.available(runtime, route, suffix))
                runtime.variables["TFR_EST_coalition_seats"] = Fraction(50)
                runtime.variables["TFR_EST_confidence_seats"] = Fraction(101)
                self.assertFalse(self.available(runtime, route, suffix))

    def test_concise_government_tooltips_still_reject_caretaker_or_occupied_cabinets(self):
        for route, suffix in (("opening", "pension_reform"),
                              ("ratas", "family_home_guarantees"),
                              ("kallas", "pension_twenty")):
            for flag in ("TFR_EST_caretaker", "TFR_EST_occupied"):
                runtime = self.runtime(route)
                with self.subTest(route=route, restriction=flag):
                    self.assertTrue(self.available(runtime, route, suffix))
                    runtime.flags.add(flag)
                    self.assertFalse(self.available(runtime, route, suffix))

    def test_covid_tooltips_still_require_one_of_tfrs_actual_domestic_case_tiers(self):
        for route, suffix in (("opening", "covid_emergency"),
                              ("ratas", "hospital_covid"), ("kallas", "sick_pay")):
            runtime = self.runtime(route)
            with self.subTest(route=route, infection="absent"):
                self.assertFalse(self.available(runtime, route, suffix))
            for idea in COVID_IDEAS:
                runtime.ideas.add(idea)
                with self.subTest(route=route, infection=idea):
                    self.assertTrue(self.available(runtime, route, suffix))
                runtime.ideas.remove(idea)
            with self.subTest(route=route, infection="recovered"):
                self.assertFalse(self.available(runtime, route, suffix))


if __name__ == "__main__":
    unittest.main()

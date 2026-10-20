"""Keep native dynamic-modifier previews consistent with real focus effects.

HOI4 renders these display-only idea swaps. Structural checks and execution of
the actual rewards verify that the advertised deltas cannot silently diverge.
The test runtime does not emulate native tooltip rendering.
"""
from fractions import Fraction
import re
import unittest

from script_runtime import ROOT, Block, Runtime, parse
from build_focus_tooltips import CATEGORIES, focus_rewards, idea_definitions, outputs


def read_script(relative):
    path = ROOT / relative
    return parse(path.read_text(encoding="utf-8-sig"), str(path))


def reward_effect(focus_id):
    for route in ("opening", "ratas", "kallas", "reform_2023", "ekre_2023", "centre_2023", "isamaa_2023", "sde_2023", "e200_2023", "pp_2023"):
        prefix = f"TFR_EST_{route}_"
        if focus_id.startswith(prefix):
            return prefix + "reward_" + focus_id[len(prefix):]
    raise AssertionError(f"Unknown focus reward: {focus_id}")


class FocusEffectPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ideas = read_script("common/ideas/TFR_EST_focus_tooltips.txt").get("ideas")
        cls.country = cls.ideas.get("country")
        cls.catalog = {entry.key: entry.value for entry in cls.country.entries}
        cls.dynamic = read_script("common/dynamic_modifiers/TFR_EST_country.txt")
        cls.focuses = {}
        for route in ("opening", "ratas", "kallas", "reform_2023", "ekre_2023", "centre_2023", "isamaa_2023", "sde_2023", "e200_2023", "pp_2023"):
            tree = read_script(f"common/national_focus/TFR_EST_{route}.txt")
            cls.focuses.update({focus.get("id"): focus
                                for focus in tree.all("shared_focus")})

    def test_generated_files_match_reward_sources(self):
        for relative, text in outputs().items():
            with self.subTest(path=relative):
                encoding = "utf-8-sig" if relative.endswith(".yml") else "utf-8"
                self.assertEqual((ROOT / relative).read_bytes(), text.encode(encoding))

    def test_only_country_ideas_and_the_expected_preview_definitions_exist(self):
        self.assertEqual([entry.key for entry in self.ideas.entries], ["country"])
        self.assertEqual(set(self.catalog), set(idea_definitions()))
        self.assertEqual(len(focus_rewards()), 275)
        for ident, definition in self.catalog.items():
            with self.subTest(idea=ident):
                self.assertEqual(set(entry.key for entry in definition.entries),
                                 {"name", "picture", "allowed", "modifier"})
                self.assertEqual(definition.get("allowed").get("original_tag"), "EST")

    def test_empty_previews_have_no_modifiers(self):
        for category in CATEGORIES:
            definition = self.catalog[f"TFR_EST_tooltip_{category}_empty"]
            self.assertEqual(definition.get("modifier").entries, [])
            self.assertEqual(definition.get("name"), f"TFR_EST_{category}_dynamic")

    def test_delta_fields_belong_to_the_displayed_dynamic_modifier(self):
        for ident, (category, expected) in idea_definitions().items():
            with self.subTest(idea=ident):
                definition = self.catalog[ident]
                self.assertEqual(definition.get("name"), f"TFR_EST_{category}_dynamic")
                fields = {entry.key: Fraction(entry.value)
                          for entry in definition.get("modifier").entries}
                self.assertEqual(fields, {field: Fraction(str(amount))
                                          for field, amount in expected})
                dynamic = self.dynamic.get(f"TFR_EST_{category}_dynamic")
                for field in fields:
                    self.assertEqual(dynamic.get(field), f"TFR_EST_{category}_{field}_var")

    def test_all_275_real_reward_deltas_match_their_native_previews(self):
        # A nonzero saved baseline detects assignment/reset mistakes as well as
        # a wrong amount in either the preview or the persistent reward.
        bound_variables = {
            entry.value for definition in self.dynamic.entries
            for entry in definition.value.entries
            if isinstance(entry.value, str) and entry.value.startswith("TFR_EST_")
        }
        for focus_id, rewards in focus_rewards().items():
            with self.subTest(focus=focus_id):
                runtime = Runtime()
                runtime.variables.update(TFR_EST_cohesion=Fraction(55),
                                         TFR_EST_readiness=Fraction(25))
                runtime.call("TFR_EST_initialize_country_modifiers")
                for variable in bound_variables:
                    runtime.variables[variable] = Fraction(17, 100)
                before = {name: runtime.variables[name] for name in bound_variables}
                runtime.run(self.focuses[focus_id].get("completion_reward"))
                expected = {name: Fraction(0) for name in bound_variables}
                for category, changes in rewards.items():
                    for field, amount in changes:
                        expected[f"TFR_EST_{category}_{field}_var"] += Fraction(str(amount))
                actual = {name: runtime.variables[name] - before[name]
                          for name in bound_variables}
                self.assertEqual(actual, expected)
                self.assertFalse(set(self.catalog) & runtime.ideas)

    def test_every_actual_modifier_reward_uses_the_matching_tooltip_swap(self):
        runtime = Runtime()
        for focus_id, rewards in focus_rewards().items():
            # The referendum's completion is an inline lifecycle transition;
            # unlike the other focuses it has no named reward helper.
            effect = runtime.effects.get(reward_effect(focus_id),
                                         self.focuses[focus_id].get("completion_reward"))
            swaps = []
            for parents, entry in effect.walk():
                if entry.key == "swap_ideas" and "effect_tooltip" in parents:
                    swaps.append((entry.value.get("remove_idea"), entry.value.get("add_idea")))
            expected = [(f"TFR_EST_tooltip_{category}_empty", f"{focus_id}_{category}_delta")
                        for category, changes in rewards.items() if changes]
            with self.subTest(focus=focus_id):
                self.assertCountEqual(swaps, expected)

    def test_preview_ideas_are_never_granted_by_gameplay_scripts(self):
        referenced = set()
        for directory in ("common", "events", "history"):
            for path in (ROOT / directory).rglob("*.txt"):
                if not path.name.startswith("TFR_EST_"):
                    continue
                tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
                for parents, entry in tree.walk():
                    if isinstance(entry.value, str) and entry.value in self.catalog:
                        if entry.key in {"add_idea", "remove_idea"}:
                            self.assertIn("effect_tooltip", parents,
                                          f"{path}:{entry.line} executes a display-only idea")
                            referenced.add(entry.value)
                        if entry.key == "add_ideas":
                            self.fail(f"{path}:{entry.line} grants a display-only idea")
                    if entry.key == "add_ideas" and isinstance(entry.value, Block):
                        self.assertFalse({child.key for child in entry.value.entries} & set(self.catalog),
                                         f"{path}:{entry.line} grants display-only ideas")
        self.assertEqual(referenced, set(self.catalog))

    def test_preview_localisation_is_bom_encoded_and_aliases_existing_names(self):
        path = ROOT / "localisation/english/TFR_EST_focus_tooltips_l_english.yml"
        data = path.read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        aliases = dict(re.findall(r'^\s+(\S+):0 "([^"\r\n]+)"',
                                  data.decode("utf-8-sig"), re.M))
        expected = {}
        for ident, (category, _) in idea_definitions().items():
            for suffix in ("", "_desc"):
                expected[ident + suffix] = f"$TFR_EST_{category}_dynamic{suffix}$"
        self.assertEqual(aliases, expected)

    def test_effect_tooltip_does_not_apply_its_preview_effect(self):
        runtime = Runtime()
        runtime.run(parse("""
            effect_tooltip = {
                swap_ideas = {
                    remove_idea = TFR_EST_tooltip_economy_empty
                    add_idea = TFR_EST_opening_teacher_pay_economy_delta
                }
            }
        """))
        self.assertFalse(runtime.ideas)
        self.assertFalse(runtime.dynamic)


if __name__ == "__main__":
    unittest.main()

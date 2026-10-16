"""Execute Estonia's real reuse of TFR's five-tier Oil Crash spirit.

The arithmetic fixture does not emulate idea modifier calculation or focus UI.
The source-contract check reads the installed parent idea definitions instead.
"""
from fractions import Fraction
from itertools import product
import unittest

from script_runtime import ROOT, Runtime, parse
from build_energy_crisis import IDEAS, KALLAS_PROJECTS, RATAS_PROJECTS, SLOTS
from patch_tfr_compatibility import DEFAULT_PARENT, parse as parent_parse, walk


FACTORY = "TFR_EST_economy_industrial_capacity_factory_var"
GOODS = "TFR_EST_economy_consumer_goods_factor_var"
FACTORY_APPLIED = "TFR_EST_energy_factory_applied"
GOODS_APPLIED = "TFR_EST_energy_goods_applied"
STEPS = "TFR_EST_energy_response_steps"
MANAGED = "TFR_EST_energy_idea_managed"
SEEN = "TFR_EST_energy_crisis_seen"
NOTICE = "tfr_estonia_ratas.1"
ONSET = "SAU_saudi_civil_war_global"
ENDED = "SAU_saudi_civil_war_over_global"


class EnergyCrisisIdeaTests(unittest.TestCase):
    def runtime(self, active=True):
        r = Runtime()
        # Load the new generator output explicitly while other agents finish
        # removing the former definition from the continuation generator.
        path = ROOT / "common/scripted_effects/TFR_EST_energy.txt"
        r.effects.update({entry.key: entry.value for entry in
                          parse(path.read_text(encoding="utf-8"), str(path)).entries})
        r.call("TFR_EST_initialize_country_modifiers")
        r.variables[FACTORY] = Fraction(7, 100)
        r.variables[GOODS] = Fraction(-2, 100)
        if active:
            r.global_flags.add(ONSET)
        return r

    def reconcile(self, r):
        r.call("TFR_EST_reconcile_energy_crisis")

    def assert_tier(self, r, recovery):
        self.assertEqual(r.ideas.intersection(IDEAS),
                         {IDEAS[recovery]} if recovery < 5 else set())
        self.assertEqual(r.variables[FACTORY_APPLIED], 0)
        self.assertEqual(r.variables[GOODS_APPLIED], 0)
        self.assertEqual(r.variables[FACTORY], Fraction(7, 100))
        self.assertEqual(r.variables[GOODS], Fraction(-2, 100))

    def test_actual_parent_family_has_monotonic_real_penalties_and_script_grants(self):
        path = DEFAULT_PARENT / "common/ideas/TFR_ideas_GER.txt"
        # The parent file contains an unrelated empty `name =` value. Extract
        # just the audited idea definitions with its tolerant structural reader
        # and strictly parse each complete block for independent value checks.
        source = path.read_text(encoding="utf-8-sig")
        entries = {entry.key: entry for entry, _ in walk(parent_parse(source))
                   if entry.key in IDEAS}
        expected_energy = ("0.4", "0.3", "0.2", "0.15", "0.1")
        for index, idea in enumerate(IDEAS):
            entry = entries[idea]
            block = parse(source[entry.start:entry.end], str(path)).get(idea)
            with self.subTest(idea=idea):
                self.assertEqual(block.get("picture"), "GER_oil_crash")
                self.assertEqual(block.get("removal_cost"), "-1")
                self.assertEqual(block.get("allowed").get("always"), "no")
                modifiers = block.get("modifier")
                self.assertEqual(Fraction(modifiers.get("consumer_goods_factor")),
                                 Fraction(5 - index, 10))
                for key in ("production_factory_max_efficiency_factor",
                            "production_speed_buildings_factor", "stability_factor",
                            "business_value_factor"):
                    self.assertEqual(Fraction(modifiers.get(key)), Fraction(index - 5, 20))
                self.assertEqual(Fraction(modifiers.get("factory_energy_consumption")),
                                 Fraction(expected_energy[index]))
                self.assertEqual(Fraction(modifiers.get("poverty_development_monthly")),
                                 Fraction(index - 5, 100))
        self.assertFalse((ROOT / "common/ideas/TFR_EST_energy.txt").exists(),
                         "Reuse the parent's ideas instead of copying national spirits")

    def test_each_parent_onset_starts_the_real_spirit_and_one_notice(self):
        for flag in (ONSET, "saudi_civil_war_flag"):
            r = self.runtime(active=False)
            r.global_flags.add(flag)
            self.reconcile(r)
            with self.subTest(flag=flag):
                self.assert_tier(r, 0)
                self.assertIn(MANAGED, r.flags)
                self.assertIn(SEEN, r.flags)
                self.assertEqual(r.events, [NOTICE])

    def test_clean_world_has_no_spirit_or_notice(self):
        r = self.runtime(active=False)
        self.reconcile(r)
        self.assert_tier(r, 5)
        self.assertNotIn(MANAGED, r.flags)
        self.assertNotIn(SEEN, r.flags)
        self.assertFalse(r.events)

    def test_five_ratas_projects_each_reduce_one_stage_and_final_removes(self):
        r = self.runtime()
        self.reconcile(r)
        for recovery, project in enumerate(RATAS_PROJECTS, start=1):
            r.flags.add("TFR_EST_done_ratas_" + project)
            self.reconcile(r)
            with self.subTest(project=project):
                self.assert_tier(r, recovery)
                self.assertEqual(r.variables[STEPS], recovery)
        for _ in range(15):
            self.reconcile(r)
            self.assert_tier(r, 5)
        self.assertEqual(r.events, [NOTICE])

    def test_four_kallas_projects_remove_spirit_network_relief_counts_twice(self):
        r = self.runtime()
        self.reconcile(r)
        recovery = 0
        for project in KALLAS_PROJECTS:
            r.flags.add("TFR_EST_done_kallas_" + project)
            recovery += 2 if project == "energy_networks" else 1
            self.reconcile(r)
            with self.subTest(project=project):
                self.assert_tier(r, recovery)
                self.assertEqual(r.variables[STEPS], recovery)

    def test_all_512_mixed_route_combinations_cannot_count_equivalent_projects_twice(self):
        flags = ["TFR_EST_done_ratas_" + project for project in RATAS_PROJECTS]
        flags += ["TFR_EST_done_kallas_" + project for project in KALLAS_PROJECTS]
        for enabled in product((False, True), repeat=len(flags)):
            earned = {flag for flag, active in zip(flags, enabled) if active}
            expected = sum("TFR_EST_done_ratas_" + ratas in earned or
                           "TFR_EST_done_kallas_" + kallas in earned
                           for ratas, kallas in SLOTS)
            r = self.runtime()
            r.flags.update(earned)
            self.reconcile(r)
            with self.subTest(earned=sorted(earned)):
                self.assertEqual(r.variables[STEPS], expected)
                self.assert_tier(r, expected)

    def test_preparing_every_project_prevents_onset_spirit_and_never_regrants_it(self):
        for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS)):
            r = self.runtime(active=False)
            r.flags.update("TFR_EST_done_" + route + "_" + project for project in projects)
            self.reconcile(r)
            self.assert_tier(r, 5)
            r.global_flags.add(ONSET)
            for _ in range(3):
                self.reconcile(r)
            with self.subTest(route=route):
                self.assert_tier(r, 5)
                self.assertEqual(r.events, [NOTICE])

    def test_daily_reconciliation_preserves_membership_and_permanent_reforms(self):
        r = self.runtime()
        r.ideas.add("TFR_EST_total_defence")
        self.reconcile(r)
        before = (r.variables.copy(), r.flags.copy(), r.ideas.copy(), r.dynamic_updates)
        for _ in range(20):
            self.reconcile(r)
        self.assertEqual((r.variables, r.flags, r.ideas, r.dynamic_updates), before)
        self.assertEqual(r.events, [NOTICE])
        self.assertIn("TFR_EST_total_defence", r.ideas)

    def test_external_weaker_tier_is_adopted_without_worsening_or_double_spirits(self):
        for index, idea in enumerate(IDEAS):
            r = self.runtime()
            r.ideas.add(idea)
            self.reconcile(r)
            with self.subTest(idea=idea):
                self.assert_tier(r, index)
                self.assertEqual(r.variables["TFR_EST_energy_external_recovery"], index)
                r.flags.add("TFR_EST_done_ratas_lng_connection")
                self.reconcile(r)
                self.assert_tier(r, index + 1)

    def test_multiple_external_tiers_are_normalized_to_best_existing_recovery(self):
        r = self.runtime()
        r.ideas.update(IDEAS)
        self.reconcile(r)
        self.assert_tier(r, 4)
        r.flags.add("TFR_EST_done_ratas_building_renovation")
        self.reconcile(r)
        self.assert_tier(r, 5)

    def test_managed_missing_or_duplicate_tiers_repair_from_earned_progress(self):
        r = self.runtime()
        r.flags.add("TFR_EST_done_ratas_lng_connection")
        self.reconcile(r)
        r.ideas.difference_update(IDEAS)
        self.reconcile(r)
        self.assert_tier(r, 1)
        r.ideas.update(IDEAS)
        self.reconcile(r)
        self.assert_tier(r, 1)

    def test_parent_resolution_or_cleared_onset_removes_our_spirit(self):
        for use_resolution in (False, True):
            r = self.runtime()
            self.reconcile(r)
            if use_resolution:
                r.global_flags.add(ENDED)
            else:
                r.global_flags.clear()
            globals_before = r.global_flags.copy()
            self.reconcile(r)
            with self.subTest(use_resolution=use_resolution):
                self.assert_tier(r, 5)
                self.assertEqual(r.global_flags, globals_before)
                self.assertEqual(r.events, [NOTICE])

    def test_clean_world_does_not_remove_an_unmanaged_external_spirit(self):
        r = self.runtime(active=False)
        r.ideas.add(IDEAS[0])
        self.reconcile(r)
        self.assertEqual(r.ideas, {IDEAS[0]})
        self.assertNotIn(MANAGED, r.flags)

    def test_old_dynamic_penalties_are_reversed_once_preserving_other_reforms(self):
        r = self.runtime()
        r.variables[FACTORY_APPLIED] = Fraction(-3, 100)
        r.variables[GOODS_APPLIED] = Fraction(15, 1000)
        r.variables[FACTORY] += r.variables[FACTORY_APPLIED]
        r.variables[GOODS] += r.variables[GOODS_APPLIED]
        untouched = "TFR_EST_economy_research_speed_factor_var"
        r.variables[untouched] = Fraction(9, 100)
        self.reconcile(r)
        self.assert_tier(r, 0)
        self.assertEqual(r.variables[untouched], Fraction(9, 100))
        refreshes = r.dynamic_updates
        self.reconcile(r)
        self.assert_tier(r, 0)
        self.assertEqual(r.dynamic_updates, refreshes)

    def test_restored_state_preserves_progress_and_never_repeats_notice(self):
        r = self.runtime()
        r.flags.update({"TFR_EST_done_ratas_lng_connection",
                        "TFR_EST_done_kallas_energy_networks"})
        self.reconcile(r)
        loaded = self.runtime()
        loaded.variables = r.variables.copy()
        loaded.flags = r.flags.copy()
        loaded.ideas = r.ideas.copy()
        loaded.global_flags = r.global_flags.copy()
        self.reconcile(loaded)
        self.assertEqual((loaded.variables, loaded.flags, loaded.ideas),
                         (r.variables, r.flags, r.ideas))
        self.assertFalse(loaded.events)

    def test_initialized_estonia_guard_blocks_foreign_and_uninitialized_changes(self):
        for blocked in ("foreign", "uninitialized"):
            r = self.runtime()
            r.ideas.add(IDEAS[1])
            if blocked == "foreign":
                r.props["tag"] = "GER"
            else:
                r.flags.discard("TFR_EST_initialized")
            before = (r.variables.copy(), r.flags.copy(), r.global_flags.copy(), r.ideas.copy())
            self.reconcile(r)
            with self.subTest(blocked=blocked):
                self.assertEqual((r.variables, r.flags, r.global_flags, r.ideas), before)
                self.assertFalse(r.events)


if __name__ == "__main__":
    unittest.main()

"""Execute Estonia's parent Oil Crash spirit and retained-cabinet recovery.

The fixture uses the actual country effects and TFR's actual COVID predicate.
Event delivery, focus scheduling and the game's UI are outside this runtime.
"""
from fractions import Fraction
from itertools import product
import unittest

from script_runtime import ROOT, Runtime, parse
from build_ratas_continuation import POLICIES


FACTORY = "TFR_EST_economy_industrial_capacity_factory_var"
GOODS = "TFR_EST_economy_consumer_goods_factor_var"
FACTORY_APPLIED = "TFR_EST_energy_factory_applied"
GOODS_APPLIED = "TFR_EST_energy_goods_applied"
ACTIVE_FLAGS = ("SAU_saudi_civil_war_global", "saudi_civil_war_flag")
ENDED = "SAU_saudi_civil_war_over_global"
NOTICE = "tfr_estonia_ratas.1"
SEEN = "TFR_EST_energy_crisis_seen"
OWNED = "TFR_EST_covid_seed_owned"
RECORDED = "TFR_EST_covid_first_case_recorded"
TIERS = (
    "lower_covid_cases", "low_covid_cases", "medium_covid_cases",
    "high_covid_cases", "higher_covid_cases",
)
FACTORY_PROJECTS = ("lng_connection", "grid_synchronisation", "renewable_chp")
GOODS_PROJECTS = ("building_renovation", "network_charge_relief")
OIL_TIERS = tuple(f"GER_oil_crash{index}" for index in range(1, 6))
COVID_POLICIES = ("hospital_covid", "testing_tracing", "vaccinate_risk_groups")
COVID_DONE = {"TFR_EST_done_ratas_" + suffix for suffix in COVID_POLICIES}


class RatasCrisisTests(unittest.TestCase):
    def runtime(self, retained=False):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call("TFR_EST_initialize_country_modifiers")
        # Existing reforms must survive temporary shock reconciliation.
        r.variables[FACTORY] = Fraction(7, 100)
        r.variables[GOODS] = Fraction(-2, 100)
        r.variables["TFR_EST_economy_research_speed_factor_var"] = Fraction(3, 100)
        r.variables["TFR_EST_military_army_defence_factor_var"] = Fraction(4, 100)
        if retained:
            r.flags.update({"TFR_EST_ratas_retained", "TFR_EST_opening_complete", RECORDED,
                            "TFR_EST_done_ratas_renew_agreement"})
        return r

    def active(self, r):
        return r.condition(r.triggers["TFR_EST_energy_crisis_active"])

    def reconcile(self, r):
        r.call("TFR_EST_reconcile_energy_crisis")

    def assert_energy_tier(self, r, recovery):
        self.assertEqual(r.ideas.intersection(OIL_TIERS),
                         {OIL_TIERS[recovery]} if recovery < 5 else set())
        # The crisis now lives entirely in TFR's national spirit. These
        # migration ledgers remain zero and do not dilute permanent reforms.
        self.assertEqual(r.variables[FACTORY_APPLIED], 0)
        self.assertEqual(r.variables[GOODS_APPLIED], 0)
        self.assertEqual(r.variables[FACTORY], Fraction(7, 100))
        self.assertEqual(r.variables[GOODS], Fraction(-2, 100))

    def test_energy_trigger_uses_actual_onset_and_explicit_resolution(self):
        for primary, secondary, ended in product((False, True), repeat=3):
            with self.subTest(primary=primary, secondary=secondary, ended=ended):
                r = self.runtime()
                r.global_flags = {flag for flag, enabled in zip(
                    (*ACTIVE_FLAGS, ENDED), (primary, secondary, ended)) if enabled}
                self.assertEqual(self.active(r), (primary or secondary) and not ended)

    def test_clean_world_has_no_penalty_or_crisis_notice(self):
        r = self.runtime()
        before = r.variables.copy()
        self.reconcile(r)
        self.assert_energy_tier(r, 5)
        for key, value in before.items():
            self.assertEqual(r.variables[key], value)
        self.assertNotIn(SEEN, r.flags)
        self.assertFalse(r.events)

    def test_each_parent_onset_flag_applies_the_parent_oil_crash_spirit(self):
        for flag in ACTIVE_FLAGS:
            with self.subTest(flag=flag):
                r = self.runtime()
                r.global_flags.add(flag)
                self.reconcile(r)
                self.assert_energy_tier(r, 0)
                self.assertIn(SEEN, r.flags)
                self.assertEqual(r.events, [NOTICE])
                self.assertNotIn("TFR_EST_ratas_retained", r.flags,
                                 "The common crisis also affects other governments")

    def test_repeated_daily_reconciliation_does_not_stack_or_repeat_notice(self):
        r = self.runtime()
        r.global_flags.update(ACTIVE_FLAGS)
        self.reconcile(r)
        expected = r.variables.copy()
        for _ in range(20):
            r.call("TFR_EST_ratas_tick")
        self.assertEqual(r.variables, expected)
        self.assertEqual(r.events, [NOTICE])

    def test_resolution_removes_managed_spirit_even_with_stale_onset_flags(self):
        r = self.runtime()
        r.global_flags.update(ACTIVE_FLAGS)
        self.reconcile(r)
        r.global_flags.add(ENDED)
        self.reconcile(r)
        self.assert_energy_tier(r, 5)
        self.assertIn(SEEN, r.flags)
        self.assertEqual(r.events, [NOTICE])
        self.assertEqual(r.global_flags, {*ACTIVE_FLAGS, ENDED})

    def test_clearing_onset_flags_also_removes_managed_spirit(self):
        r = self.runtime()
        r.global_flags.update(ACTIVE_FLAGS)
        self.reconcile(r)
        r.global_flags.clear()
        self.reconcile(r)
        self.assert_energy_tier(r, 5)

    def test_repeated_onset_resolution_cycles_preserve_bonus_and_single_notice(self):
        r = self.runtime()
        for _ in range(4):
            r.global_flags = {ACTIVE_FLAGS[0]}
            self.reconcile(r)
            self.assert_energy_tier(r, 0)
            r.global_flags = {ENDED}
            self.reconcile(r)
            self.assert_energy_tier(r, 5)
        self.assertEqual(r.events, [NOTICE])

    def test_each_supply_project_advances_one_real_recovery_tier(self):
        for project in FACTORY_PROJECTS:
            with self.subTest(project=project):
                r = self.runtime()
                r.global_flags.add(ACTIVE_FLAGS[0])
                self.reconcile(r)
                r.flags.add("TFR_EST_done_ratas_" + project)
                self.reconcile(r)
                self.assert_energy_tier(r, 1)
                self.reconcile(r)
                self.assert_energy_tier(r, 1)

    def test_each_household_project_advances_one_real_recovery_tier(self):
        for project in GOODS_PROJECTS:
            with self.subTest(project=project):
                r = self.runtime()
                r.global_flags.add(ACTIVE_FLAGS[0])
                r.flags.add("TFR_EST_done_ratas_" + project)
                self.reconcile(r)
                self.assert_energy_tier(r, 1)

    def test_all_projects_remove_the_parent_spirit_before_world_resolution(self):
        r = self.runtime()
        r.global_flags.add(ACTIVE_FLAGS[0])
        for project in (*FACTORY_PROJECTS, *GOODS_PROJECTS):
            r.flags.add("TFR_EST_done_ratas_" + project)
        self.reconcile(r)
        self.assert_energy_tier(r, 5)
        r.global_flags.add(ENDED)
        self.reconcile(r)
        self.assert_energy_tier(r, 5)

    def test_projects_completed_before_onset_prevent_their_share_of_shock(self):
        r = self.runtime()
        r.flags.update({"TFR_EST_done_ratas_lng_connection",
                        "TFR_EST_done_ratas_network_charge_relief"})
        self.reconcile(r)
        self.assert_energy_tier(r, 5)
        r.global_flags.add(ACTIVE_FLAGS[0])
        self.reconcile(r)
        self.assert_energy_tier(r, 2)

    def test_permanent_reforms_added_during_crisis_survive_resolution(self):
        r = self.runtime()
        untouched = {key: value for key, value in r.variables.items()
                     if key not in {FACTORY, GOODS}}
        r.global_flags.add(ACTIVE_FLAGS[0])
        self.reconcile(r)
        r.variables[FACTORY] += Fraction(15, 1000)
        r.variables[GOODS] -= Fraction(1, 100)
        self.reconcile(r)
        r.global_flags = {ENDED}
        self.reconcile(r)
        self.assertEqual(r.variables[FACTORY], Fraction(85, 1000))
        self.assertEqual(r.variables[GOODS], Fraction(-3, 100))
        for key, value in untouched.items():
            self.assertEqual(r.variables[key], value)

    def test_saved_recovery_tier_repairs_without_reset_or_duplicate_reward(self):
        r = self.runtime()
        r.global_flags.add(ACTIVE_FLAGS[0])
        self.reconcile(r)
        loaded = Runtime()
        loaded.variables = r.variables.copy()
        loaded.flags = r.flags.copy()
        loaded.global_flags = r.global_flags.copy()
        self.reconcile(loaded)
        self.assertEqual(loaded.variables, r.variables)
        self.assertEqual(loaded.ideas, r.ideas)
        self.assertFalse(loaded.events)
        loaded.global_flags.add(ENDED)
        self.reconcile(loaded)
        self.assert_energy_tier(loaded, 5)

    def test_reconciler_requires_initialized_estonia_and_never_changes_parent_flags(self):
        for blocked in ("foreign", "uninitialized"):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                r.global_flags.update(ACTIVE_FLAGS)
                if blocked == "foreign":
                    r.props["tag"] = "GER"
                else:
                    r.flags.discard("TFR_EST_initialized")
                before = (r.variables.copy(), r.flags.copy(), r.global_flags.copy(),
                          r.ideas.copy(), r.dynamic_additions.copy())
                self.reconcile(r)
                self.assertEqual((r.variables, r.flags, r.global_flags, r.ideas,
                                  r.dynamic_additions), before)
                self.assertFalse(r.events)
        for helper in ("TFR_EST_reconcile_energy_crisis", "TFR_EST_ratas_tick"):
            self.assertFalse({entry.key for _, entry in Runtime().effects[helper].walk()}
                             & {"set_global_flag", "clr_global_flag"})

    def test_present_covid_is_reduced_exactly_one_tier_per_intervention(self):
        for current, target in zip(TIERS[1:], TIERS[:-1]):
            with self.subTest(current=current):
                r = self.runtime()
                r.ideas.update({current, "TFR_EST_total_defence"})
                r.flags.add(RECORDED)
                r.call("TFR_EST_ratas_reduce_covid")
                self.assertEqual(r.ideas, {target, "TFR_EST_total_defence"})
                self.assertIn(RECORDED, r.flags)
                self.assertNotIn(OWNED, r.flags,
                                 "A reduced external outbreak does not become our seed")

    def test_only_owned_lowest_case_tier_is_removed(self):
        for owned in (False, True):
            with self.subTest(owned=owned):
                r = self.runtime()
                r.ideas.add(TIERS[0])
                r.flags.add(RECORDED)
                if owned:
                    r.flags.add(OWNED)
                r.call("TFR_EST_ratas_reduce_covid")
                self.assertEqual(r.ideas, set() if owned else {TIERS[0]})
                self.assertNotIn(OWNED, r.flags)
                self.assertIn(RECORDED, r.flags)

    def test_clean_country_never_receives_infection_and_stale_ownership_is_cleared(self):
        for owned in (False, True):
            with self.subTest(owned=owned):
                r = self.runtime()
                r.flags.add(RECORDED)
                if owned:
                    r.flags.add(OWNED)
                r.call("TFR_EST_ratas_reduce_covid")
                self.assertFalse(r.ideas)
                self.assertNotIn(OWNED, r.flags)
                self.assertIn(RECORDED, r.flags)
                self.assertFalse(r.events)

    def test_covid_helper_does_not_change_a_foreign_country(self):
        for tier in (*TIERS, None):
            with self.subTest(tier=tier):
                r = self.runtime()
                r.props["tag"] = "LAT"
                r.flags.add(OWNED)
                if tier:
                    r.ideas.add(tier)
                before = (r.flags.copy(), r.ideas.copy(), r.variables.copy())
                r.call("TFR_EST_ratas_reduce_covid")
                self.assertEqual((r.flags, r.ideas, r.variables), before)

    def test_vaccination_focus_pays_and_improves_cases_once(self):
        r = self.runtime(retained=True)
        r.ideas.add("higher_covid_cases")
        path = ROOT / "common/national_focus/TFR_EST_ratas.txt"
        tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
        focus = next(entry.value for entry in tree.entries
                     if entry.value.get("id") == "TFR_EST_ratas_vaccinate_risk_groups")
        r.run(focus.get("completion_reward"))
        first = (r.variables.copy(), r.flags.copy(), r.ideas.copy(), r.calls.copy())
        r.run(focus.get("completion_reward"))
        self.assertEqual((r.variables, r.flags, r.ideas, r.calls), first)
        self.assertEqual(r.ideas.intersection(TIERS), {"high_covid_cases"})
        policy = next(policy for policy in POLICIES if policy.suffix == "vaccinate_risk_groups")
        self.assertEqual(r.calls, [("add_debt_with_inflation", Fraction(policy.budget, 1000))])
        self.assertEqual(r.variables["TFR_EST_cohesion"], 55 + policy.cohesion)

    def test_recovered_outbreak_bypasses_only_emergency_focuses_without_rewards(self):
        r = self.runtime(retained=True)
        before = r.variables.copy()
        r.call("TFR_EST_ratas_tick")
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertNotIn("TFR_EST_done_ratas_family_doctors", r.flags)
        self.assertEqual(r.calls, [])
        for key, value in before.items():
            self.assertEqual(r.variables[key], value)
        r.call("TFR_EST_ratas_tick")
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertEqual(r.calls, [])
        self.assertFalse(r.ideas)

    def test_bypassed_interventions_cannot_later_pay_their_skipped_rewards(self):
        r = self.runtime(retained=True)
        r.call("TFR_EST_ratas_tick")
        path = ROOT / "common/national_focus/TFR_EST_ratas.txt"
        tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
        before = r.variables.copy()
        for suffix in COVID_POLICIES:
            focus = next(entry.value for entry in tree.entries
                         if entry.value.get("id") == "TFR_EST_ratas_" + suffix)
            r.run(focus.get("completion_reward"))
        self.assertEqual(r.variables, before)
        self.assertFalse(r.calls)
        self.assertFalse(r.ideas)
        self.assertNotIn("TFR_EST_done_ratas_family_doctors", r.flags)

    def test_occupation_still_has_common_energy_shock_without_domestic_policy_rewards(self):
        r = self.runtime(retained=True)
        r.flags.add("TFR_EST_occupied")
        r.props["is_subject"] = "yes"
        r.global_flags.update(ACTIVE_FLAGS)
        before_cohesion = r.variables["TFR_EST_cohesion"]
        r.call("TFR_EST_ratas_tick")
        self.assert_energy_tier(r, 0)
        self.assertTrue(COVID_DONE.isdisjoint(r.flags))
        self.assertEqual(r.variables["TFR_EST_cohesion"], before_cohesion)
        self.assertFalse(r.calls)

    def test_recovery_bypass_requires_retained_independent_revealed_programme(self):
        for blocked in ("not_retained", "mandate_ended", "occupied", "subject",
                        "opening_unfinished", "renewal_unfinished", "no_recorded_outbreak",
                        "uninitialized", "foreign"):
            with self.subTest(blocked=blocked):
                r = self.runtime(retained=True)
                if blocked == "not_retained":
                    r.flags.discard("TFR_EST_ratas_retained")
                elif blocked == "mandate_ended":
                    r.flags.add("TFR_EST_ratas_mandate_ended")
                elif blocked == "occupied":
                    r.flags.add("TFR_EST_occupied")
                elif blocked == "subject":
                    r.props["is_subject"] = "yes"
                elif blocked == "opening_unfinished":
                    r.flags.discard("TFR_EST_opening_complete")
                elif blocked == "renewal_unfinished":
                    r.flags.discard("TFR_EST_done_ratas_renew_agreement")
                elif blocked == "no_recorded_outbreak":
                    r.flags.discard(RECORDED)
                elif blocked == "uninitialized":
                    r.flags.discard("TFR_EST_initialized")
                else:
                    r.props["tag"] = "GER"
                r.call("TFR_EST_ratas_tick")
                self.assertTrue(COVID_DONE.isdisjoint(r.flags))
                self.assertFalse(r.calls, "No occupation or blocked-cabinet intervention rewards")

    def test_native_completed_renewal_also_allows_recovery_bypass(self):
        r = self.runtime(retained=True)
        r.flags.discard("TFR_EST_done_ratas_renew_agreement")
        r.props["completed_focuses"].add("TFR_EST_ratas_renew_agreement")
        r.call("TFR_EST_ratas_tick")
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertNotIn("TFR_EST_done_ratas_family_doctors", r.flags)
        self.assertFalse(r.calls)

    def test_active_infection_does_not_receive_recovery_bypass(self):
        for tier in TIERS:
            with self.subTest(tier=tier):
                r = self.runtime(retained=True)
                r.ideas.add(tier)
                r.call("TFR_EST_ratas_tick")
                self.assertTrue(COVID_DONE.isdisjoint(r.flags))
                self.assertEqual(r.ideas, {tier})
                self.assertFalse(r.calls)

    def test_recovery_and_daily_bridge_never_reinfect_owned_case(self):
        r = self.runtime(retained=True)
        r.flags.add(OWNED)
        r.ideas.add(TIERS[0])
        r.call("TFR_EST_ratas_reduce_covid")
        r.call("TFR_EST_ratas_tick")
        r.call("TFR_EST_covid_tick")
        self.assertFalse(r.ideas)
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertIn(RECORDED, r.flags)
        self.assertNotIn(OWNED, r.flags)
        self.assertFalse(r.events)


if __name__ == "__main__":
    unittest.main()

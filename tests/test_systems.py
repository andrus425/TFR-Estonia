from datetime import date, timedelta
from fractions import Fraction
import unittest
from script_runtime import Runtime


class SystemsTests(unittest.TestCase):
    def setUp(self):
        self.r = Runtime()
        self.r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))

    def test_meter_clamping_and_exact_tiers(self):
        tiers = [(0, "fragile", "unprepared"), (24, "fragile", "unprepared"),
                 (25, "divided", "developing"), (49, "divided", "developing"),
                 (50, "functional", "prepared"), (74, "functional", "prepared"),
                 (75, "united", "resilient"), (100, "united", "resilient")]
        for level, coh, ready in tiers:
            self.r.variables["TFR_EST_cohesion"] = Fraction(level)
            self.r.variables["TFR_EST_readiness"] = Fraction(level)
            self.r.call("TFR_EST_refresh_meters")
            self.assertIn("TFR_EST_cohesion_" + coh, self.r.ideas)
            self.assertIn("TFR_EST_readiness_" + ready, self.r.ideas)
            self.assertEqual(len([x for x in self.r.ideas if x.startswith("TFR_EST_cohesion_")]), 1)
            self.assertEqual(len([x for x in self.r.ideas if x.startswith("TFR_EST_readiness_")]), 1)
        self.r.call("TFR_EST_change_cohesion", {"AMOUNT": -1000})
        self.r.call("TFR_EST_change_readiness", {"AMOUNT": 1000})
        self.assertEqual(self.r.variables["TFR_EST_cohesion"], 0)
        self.assertEqual(self.r.variables["TFR_EST_readiness"], 100)

    def test_modifier_repair_is_repeat_safe(self):
        self.r.call("TFR_EST_refresh_meters")
        expected = self.r.ideas.copy()
        self.r.ideas.clear()
        self.r.call("TFR_EST_refresh_meters")
        self.assertEqual(self.r.ideas, expected)
        self.r.call("TFR_EST_refresh_meters")
        self.assertEqual(self.r.ideas, expected)

    def test_budget_adapter_uses_millions_not_billions(self):
        self.r.call("TFR_EST_spend_budget", {"AMOUNT": 75})
        self.assertEqual(self.r.calls, [("add_debt_with_inflation", Fraction(75, 1000))])

    def test_reserve_authorization_is_once_and_uses_recruitment(self):
        self.r.variables["TFR_EST_readiness"] = Fraction(50)
        self.r.ideas.update({"NATO_anti_militarists_idea", "NATO_anti_militarists_idea1"})
        self.r.call("TFR_EST_mobilize_reserves")
        self.r.call("TFR_EST_mobilize_reserves")
        self.assertEqual(self.r.templates, ["Kaitseliidu reservbrigaad"])
        self.assertIn("TFR_EST_reserves_mobilized", self.r.flags)
        self.assertNotIn("NATO_anti_militarists_idea", self.r.ideas)
        self.assertNotIn("NATO_anti_militarists_idea1", self.r.ideas)

    def test_occupation_cannot_mobilize_national_reserves(self):
        self.r.variables["TFR_EST_readiness"] = Fraction(80)
        self.r.flags.add("TFR_EST_occupied")
        self.r.props["is_subject"] = "yes"
        self.r.call("TFR_EST_mobilize_reserves")
        self.assertFalse(self.r.templates)

    def test_only_current_government_programme_is_active(self):
        parties = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")
        self.r.flags.update("TFR_EST_" + p + "_programme" for p in parties)
        for index, party in enumerate(parties, 1):
            self.r.variables["TFR_EST_pm_party"] = Fraction(index)
            self.r.call("TFR_EST_refresh_programme")
            active = [x for x in self.r.ideas if x in {"TFR_EST_" + p + "_cabinet" for p in parties}]
            self.assertEqual(active, ["TFR_EST_" + party + "_cabinet"])
        self.r.flags.add("TFR_EST_caretaker")
        self.r.call("TFR_EST_refresh_programme")
        self.assertFalse([x for x in self.r.ideas if x in {"TFR_EST_" + p + "_cabinet" for p in parties}])

    def test_campaign_stages_and_main_tree_do_not_overwrite_occupation(self):
        self.r.global_flags.add("SOV_nato_war_begins_global")
        self.r.props["world_wars"] = {frozenset(("SOV", "GER"))}
        self.r.call("TFR_EST_reconcile_campaign")
        self.assertEqual(self.r.variables["TFR_EST_campaign_stage"], 1)
        self.r.global_flags.clear()
        self.r.props["world_wars"] = set()
        self.r.call("TFR_EST_reconcile_campaign")
        self.assertEqual(self.r.variables["TFR_EST_campaign_stage"], 2)
        self.r.global_flags.add("second_nato_war_flag")
        self.r.props["world_wars"] = {frozenset(("SOV", "GER"))}
        self.r.call("TFR_EST_reconcile_campaign")
        self.assertEqual(self.r.variables["TFR_EST_campaign_stage"], 3)
        self.r.flags.add("TFR_EST_occupied")
        self.r.props["is_subject"] = "yes"
        self.r.props["focus_tree"] = "TFR_EST_occupation_tree"
        self.r.props["world_wars"] = set()
        self.r.call("TFR_EST_reconcile_campaign")
        self.assertEqual(self.r.variables["TFR_EST_campaign_stage"], 4)
        self.assertEqual(self.r.props["focus_tree"], "TFR_EST_occupation_tree")

    def test_parempoolsed_formation_preserves_poll_total(self):
        self.r.call("TFR_EST_initialize_parliament")
        self.r.props["date"] = date(2022, 8, 5)
        self.r.call("TFR_EST_parliament_tick")
        self.assertEqual(self.r.variables["TFR_EST_active_pp"], 1)
        self.assertEqual(sum(self.r.variables["TFR_EST_support_" + p] for p in ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp", "other")), 10000)
        before = self.r.variables["TFR_EST_support_pp"]
        self.r.call("TFR_EST_parliament_tick")
        self.assertEqual(self.r.variables["TFR_EST_support_pp"], before)


if __name__ == "__main__":
    unittest.main()

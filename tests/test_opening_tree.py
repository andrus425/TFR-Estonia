"""Opening prerequisites, branch visibility, and real coalition-seat requirements.

These checks evaluate script structure and supported trigger behavior. They do
not emulate the focus GUI, focus-progress engine, or the event scheduler.
"""
from datetime import date, timedelta
from fractions import Fraction
import unittest

from script_runtime import ROOT, Block, Runtime, parse


OPENING_NAMES = (
    "pension_reform", "teacher_pay", "covid_emergency", "pension_increase",
    "wage_compensation", "excise_relief", "eastern_border", "kose_voobu",
    "three_seas", "research_budget", "marriage_referendum",
)
OPENING_IDS = tuple("TFR_EST_opening_" + name for name in OPENING_NAMES)
POLICY_IDS = OPENING_IDS[:-1]
PARTIES = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")


def read_script(relative):
    path = ROOT / relative
    return parse(path.read_text(encoding="utf-8-sig"), str(path))


def contains(block, key, value=None):
    return any(entry.key == key and (value is None or entry.value == value)
               for _, entry in block.walk())


class OpeningTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opening = read_script("common/national_focus/TFR_EST_opening.txt")
        cls.opening = opening
        cls.focuses = {focus.get("id"): focus
                       for focus in opening.all("shared_focus")}
        cls.main = read_script("common/national_focus/TFR_EST_normal.txt").get("focus_tree")
        cls.legacy = {focus.get("id"): focus for focus in cls.main.all("focus")}

    def runtime(self, ready_for_referendum=False):
        runtime = Runtime()
        runtime.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        runtime.call("TFR_EST_initialize_parliament")
        runtime.props["completed_focuses"] = set(POLICY_IDS) if ready_for_referendum else set()
        if ready_for_referendum:
            runtime.props["date"] = date(2020, 12, 24)
        return runtime

    def trigger(self, runtime, name):
        return runtime.test(name, "=", "yes")

    def legacy_visibility(self, runtime):
        return {focus_id for focus_id, focus in self.legacy.items()
                if runtime.condition(focus.get("allow_branch", Block([])))}

    def test_exactly_eleven_shared_opening_focuses_without_a_second_country_tree(self):
        self.assertEqual(tuple(self.focuses), OPENING_IDS)
        self.assertEqual(len(self.opening.all("shared_focus")), 11)
        self.assertFalse(self.opening.all("focus_tree"))
        self.assertFalse(self.opening.all("focus"))

    def test_every_opening_focus_costs_35_days(self):
        for focus_id, focus in self.focuses.items():
            with self.subTest(focus=focus_id):
                self.assertEqual(Fraction(focus.get("cost")) * 7, 35)

    def test_main_tree_imports_the_whole_opening_chain(self):
        self.assertCountEqual(self.main.all("shared_focus"), OPENING_IDS)
        self.assertEqual(self.main.get("initial_show_position").get("focus"), OPENING_IDS[0])

    def test_opening_is_one_ordered_chain_with_no_optional_or_mutually_exclusive_work(self):
        for index, focus_id in enumerate(OPENING_IDS):
            focus = self.focuses[focus_id]
            with self.subTest(focus=focus_id):
                parents = [p.get("focus") for p in focus.all("prerequisite")]
                self.assertEqual(parents, [] if index == 0 else [OPENING_IDS[index - 1]])
                self.assertFalse(focus.all("mutually_exclusive"))

    def test_each_policy_requires_the_actual_opening_coalition_majority(self):
        for focus_id in POLICY_IDS:
            with self.subTest(focus=focus_id):
                available = self.focuses[focus_id].get("available")
                self.assertEqual(available.get("TFR_EST_opening_coalition_majority"), "yes")
                self.assertEqual(self.focuses[focus_id].get("cancel_if_invalid"), "yes")
                self.assertEqual(self.focuses[focus_id].get("continue_if_invalid"), "no")

    def test_referendum_cannot_be_canceled_or_interrupted_by_confidence_loss(self):
        referendum = self.focuses[OPENING_IDS[-1]]
        self.assertEqual(referendum.get("cancelable"), "no")
        self.assertEqual(referendum.get("cancel_if_invalid"), "no")
        self.assertEqual(referendum.get("continue_if_invalid"), "yes")
        self.assertEqual(referendum.get("available").get("TFR_EST_can_start_referendum"), "yes")
        self.assertEqual(referendum.get("select_effect").get("TFR_EST_begin_referendum"), "yes")

    def test_referendum_completion_list_is_native_and_requires_all_ten_policies(self):
        runtime = self.runtime(True)
        trigger = runtime.triggers["TFR_EST_can_start_referendum"]
        completed = [entry.value for _, entry in trigger.walk()
                     if entry.key == "has_completed_focus"]
        self.assertCountEqual(completed, POLICY_IDS)
        self.assertTrue(self.trigger(runtime, "TFR_EST_can_start_referendum"))
        for missing in POLICY_IDS:
            with self.subTest(missing=missing):
                runtime.props["completed_focuses"] = set(POLICY_IDS) - {missing}
                self.assertFalse(self.trigger(runtime, "TFR_EST_can_start_referendum"))
        runtime.props["completed_focuses"] = set()
        self.assertFalse(self.trigger(runtime, "TFR_EST_can_start_referendum"))

    def test_persistent_policy_records_preserve_completion_across_tree_handoffs(self):
        runtime = self.runtime(True)
        runtime.props["completed_focuses"] = set()
        done_flags = {"TFR_EST_done_opening_" + name for name in OPENING_NAMES[:-1]}
        runtime.flags.update(done_flags)
        self.assertTrue(self.trigger(runtime, "TFR_EST_can_start_referendum"))
        for missing in done_flags:
            with self.subTest(missing_record=missing):
                runtime.flags.discard(missing)
                self.assertFalse(self.trigger(runtime, "TFR_EST_can_start_referendum"))
                runtime.flags.add(missing)

    def test_referendum_gate_is_strictly_after_23_december(self):
        runtime = self.runtime(True)
        trigger = runtime.triggers["TFR_EST_can_start_referendum"]
        dates = [(entry.op, entry.value) for _, entry in trigger.walk() if entry.key == "date"]
        self.assertIn((">", "2020.12.23"), dates)
        for actual, expected in ((date(2020, 12, 16), False),
                                 (date(2020, 12, 23), False),
                                 (date(2020, 12, 24), True),
                                 (date(2021, 2, 1), True)):
            with self.subTest(date=actual):
                runtime.props["date"] = actual
                self.assertEqual(self.trigger(runtime, "TFR_EST_can_start_referendum"), expected)

    def test_initial_57_seat_centre_ekre_isamaa_coalition_is_eligible(self):
        runtime = self.runtime()
        self.assertEqual(runtime.variables["TFR_EST_pm_party"], 2)
        self.assertEqual(runtime.variables["TFR_EST_coalition_seats"], 57)
        self.assertTrue(self.trigger(runtime, "TFR_EST_opening_coalition_majority"))

    def test_coalition_boundary_is_51_seats_and_supply_votes_cannot_replace_it(self):
        runtime = self.runtime()
        for centre_seats, expected in ((20, True), (19, False)):
            with self.subTest(centre_seats=centre_seats):
                runtime.variables["TFR_EST_seats_centre"] = Fraction(centre_seats)
                runtime.variables["TFR_EST_supply_reform"] = Fraction(1)
                runtime.call("TFR_EST_recount_confidence")
                self.assertGreaterEqual(runtime.variables["TFR_EST_confidence_seats"], 51)
                self.assertEqual(runtime.variables["TFR_EST_coalition_seats"], centre_seats + 31)
                self.assertEqual(self.trigger(runtime, "TFR_EST_opening_coalition_majority"), expected)

    def test_all_three_historical_partners_are_required_even_with_other_majority_support(self):
        for party in ("centre", "ekre", "isamaa"):
            with self.subTest(withdrawn_party=party):
                runtime = self.runtime()
                runtime.variables["TFR_EST_coalition_" + party] = Fraction(0)
                runtime.variables["TFR_EST_coalition_reform"] = Fraction(1)
                runtime.call("TFR_EST_recount_confidence")
                self.assertGreaterEqual(runtime.variables["TFR_EST_coalition_seats"], 51)
                self.assertFalse(self.trigger(runtime, "TFR_EST_opening_coalition_majority"))

    def test_caretaker_occupation_subject_or_other_pm_cannot_start_opening_legislation(self):
        for state in ("caretaker", "occupied", "subject", "other_pm"):
            with self.subTest(state=state):
                runtime = self.runtime(True)
                if state in {"caretaker", "occupied"}:
                    runtime.flags.add("TFR_EST_" + state)
                elif state == "subject":
                    runtime.props["is_subject"] = "yes"
                else:
                    runtime.variables["TFR_EST_pm_party"] = Fraction(1)
                self.assertFalse(self.trigger(runtime, "TFR_EST_opening_coalition_majority"))
                self.assertFalse(self.trigger(runtime, "TFR_EST_can_start_referendum"))

    def test_referendum_cannot_be_restarted_after_the_opening_concludes(self):
        runtime = self.runtime(True)
        runtime.flags.add("TFR_EST_opening_complete")
        self.assertFalse(self.trigger(runtime, "TFR_EST_can_start_referendum"))

    def test_all_existing_branches_require_the_opening_to_finish(self):
        self.assertTrue(self.legacy)
        for focus_id, focus in self.legacy.items():
            with self.subTest(focus=focus_id):
                allow = focus.get("allow_branch")
                self.assertIsInstance(allow, Block)
                self.assertTrue(contains(allow, "has_country_flag", "TFR_EST_opening_complete"))

    def test_initial_branch_conditions_expose_only_the_eleven_opening_definitions(self):
        runtime = self.runtime()
        # Even foreign/war lifecycle flags cannot expose legacy branches before
        # the authored opening finishes. This is a script graph, not a UI claim.
        runtime.flags.update({"TFR_EST_first_war_seen", "TFR_EST_second_war_seen",
                              "TFR_EST_first_war_ended", "TFR_EST_second_war_ended"})
        self.assertEqual(self.legacy_visibility(runtime), set())
        visible_opening = {focus_id for focus_id, focus in self.focuses.items()
                           if runtime.condition(focus.get("allow_branch", Block([])))}
        self.assertEqual(visible_opening, set(OPENING_IDS))

    def test_after_opening_party_branches_reveal_only_the_current_prime_ministers_party(self):
        for index, party in enumerate(PARTIES, 1):
            with self.subTest(party=party):
                runtime = self.runtime()
                runtime.flags.add("TFR_EST_opening_complete")
                runtime.flags.difference_update("TFR_EST_gov_" + p for p in PARTIES)
                runtime.flags.add("TFR_EST_gov_" + party)
                runtime.variables["TFR_EST_pm_party"] = Fraction(index)
                runtime.variables["TFR_EST_active_pp"] = Fraction(1)
                visible = self.legacy_visibility(runtime)
                for candidate in PARTIES:
                    branch = {focus_id for focus_id in self.legacy
                              if focus_id.startswith("TFR_EST_" + candidate + "_")}
                    self.assertTrue(branch)
                    self.assertEqual(branch & visible, branch if candidate == party else set())

    def test_unformed_parempoolsed_branch_stays_hidden(self):
        runtime = self.runtime()
        runtime.flags.add("TFR_EST_opening_complete")
        runtime.variables["TFR_EST_pm_party"] = Fraction(7)
        runtime.variables["TFR_EST_active_pp"] = Fraction(0)
        self.assertFalse({focus_id for focus_id in self.legacy_visibility(runtime)
                          if focus_id.startswith("TFR_EST_pp_")})

    def test_war_branches_stay_hidden_until_their_own_campaign_stage(self):
        runtime = self.runtime()
        runtime.flags.add("TFR_EST_opening_complete")
        first = {focus_id for focus_id in self.legacy if focus_id.startswith("TFR_EST_first_")}
        second = {focus_id for focus_id in self.legacy
                  if focus_id.startswith("TFR_EST_second_")
                  and focus_id != "TFR_EST_second_settlement"}
        self.assertTrue(first)
        self.assertTrue(second)
        visible = self.legacy_visibility(runtime)
        self.assertFalse(first & visible)
        self.assertFalse(second & visible)
        runtime.flags.add("TFR_EST_first_war_seen")
        visible = self.legacy_visibility(runtime)
        self.assertEqual(first & visible, first)
        self.assertFalse(second & visible)
        runtime.flags.add("TFR_EST_second_war_seen")
        self.assertEqual(second & self.legacy_visibility(runtime), second)
        self.assertNotIn("TFR_EST_second_settlement", self.legacy_visibility(runtime))
        runtime.variables["TFR_EST_campaign_stage"] = Fraction(4)
        self.assertIn("TFR_EST_second_settlement", self.legacy_visibility(runtime))
        runtime.props["has_war"] = "yes"
        self.assertNotIn("TFR_EST_second_settlement", self.legacy_visibility(runtime))

    def test_new_policy_rewards_use_helpers_and_add_no_separate_ideas(self):
        runtime = self.runtime()
        for focus_id, name in zip(POLICY_IDS, OPENING_NAMES[:-1]):
            with self.subTest(focus=focus_id):
                reward = self.focuses[focus_id].get("completion_reward")
                helper = "TFR_EST_opening_reward_" + name
                self.assertTrue(contains(reward, helper, "yes"))
                self.assertFalse(contains(reward, "add_ideas"))
                self.assertIn(helper, runtime.effects)
                self.assertFalse(contains(runtime.effects[helper], "add_ideas"))

    def test_nominal_and_maximum_banked_timelines_keep_the_scandal_inside_final_focus(self):
        start = date(2020, 1, 1)
        preliminary_days = sum(int(self.focuses[focus_id].get("cost")) * 7
                               for focus_id in POLICY_IDS)
        final_days = int(self.focuses[OPENING_IDS[-1]].get("cost")) * 7
        self.assertEqual(preliminary_days, 350)
        nominal_start = start + timedelta(days=preliminary_days)
        nominal_end = nominal_start + timedelta(days=final_days)
        self.assertEqual(nominal_start, date(2020, 12, 16))
        self.assertEqual(nominal_end, date(2021, 1, 20))
        gate = date(2020, 12, 24)
        shortest_end = gate + timedelta(days=final_days - 14)
        self.assertEqual(shortest_end, date(2021, 1, 14))
        for event_day in (date(2021, 1, 12), date(2021, 1, 13)):
            with self.subTest(event_day=event_day):
                self.assertTrue(nominal_start <= event_day < nominal_end)
                self.assertTrue(gate <= event_day < shortest_end)
        banked_wait = (gate - nominal_start).days
        self.assertEqual(banked_wait, 8)
        self.assertEqual(gate + timedelta(days=final_days - banked_wait), nominal_end)


if __name__ == "__main__":
    unittest.main()

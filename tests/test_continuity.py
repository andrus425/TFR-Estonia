from pathlib import Path
import unittest
from script_runtime import Runtime, ROOT, Block, parse


class ContinuityTests(unittest.TestCase):
    def test_every_focus_has_persistent_reward_guard(self):
        count = 0
        for path in (ROOT / "common/national_focus").glob("TFR_EST_*.txt"):
            tree = parse(path.read_text(encoding="utf-8-sig"))
            for _, e in tree.walk():
                if e.key != "focus" or not isinstance(e.value, Block): continue
                focus = e.value
                bypass = focus.get("bypass")
                reward = focus.get("completion_reward")
                self.assertIsInstance(bypass, Block, focus.get("id"))
                self.assertIsInstance(reward, Block, focus.get("id"))
                bypass_flags = {x.value for _, x in bypass.walk() if x.key == "has_country_flag"}
                reward_flags = {x.value for _, x in reward.walk() if x.key == "set_country_flag" and isinstance(x.value, str)}
                self.assertTrue(bypass_flags & reward_flags, "No persistent completion guard: " + focus.get("id"))
                count += 1
        self.assertGreaterEqual(count, 192)

    def test_occupation_does_not_restart_when_war_becomes_peace(self):
        r = Runtime()
        effect = r.effects["TFR_EST_enter_occupation"]
        outer = effect.get("if")
        generation = outer.get("if")
        # The ordinary interwar progression must not reset an existing same-
        # patron occupation, charge the transition twice, or restart its clock.
        r.flags.add("TFR_EST_occupied")
        r.variables.update(TFR_EST_occupation_patron_id=1,
                           TFR_EST_occupation_campaign_stage=1,
                           TFR_EST_campaign_stage=2,
                           TFR_EST_occupation_wave=1)
        r.props["autonomy_state"] = "TFR_EST_autonomy_occupation"
        r.call("TFR_EST_current_occupation_wave")
        # Examine the actual generation predicate. PATRON.id is substituted
        # with its fixed country ID for this arithmetic-only scope check.
        text = (ROOT / "common/scripted_effects/TFR_EST_occupation.txt").read_text(encoding="utf-8-sig")
        text = text.replace("event_target:TFR_EST_requested_patron.id", "1")
        replaced = parse(text).get("TFR_EST_enter_occupation").get("if").get("if")
        self.assertFalse(r.condition(replaced.get("limit")))
        r.global_flags.add("second_nato_war_flag")
        r.call("TFR_EST_current_occupation_wave")
        self.assertFalse(r.condition(replaced.get("limit")), "A new world war alone is not a new occupation settlement")
        r.flags.add("TFR_EST_force_new_occupation_generation")
        self.assertTrue(r.condition(replaced.get("limit")), "A protected new settlement can explicitly start the next mandate")
        r.flags.discard("TFR_EST_force_new_occupation_generation")
        r.variables["TFR_EST_occupation_patron_id"] = 2
        self.assertTrue(r.condition(replaced.get("limit")), "A genuinely different patron must create a new mandate")
        r.variables["TFR_EST_occupation_patron_id"] = 1
        r.flags.discard("TFR_EST_occupied")
        self.assertTrue(r.condition(replaced.get("limit")), "A fresh defeat of independent Estonia must create a mandate")

    def test_parliament_suspension_and_restoration_preserve_party_ledger(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call("TFR_EST_initialize_parliament")
        saved = {k: v for k, v in r.variables.items() if k.startswith(("TFR_EST_support_", "TFR_EST_seats_"))}
        r.flags.add("TFR_EST_parliament_open")
        r.flags.add("TFR_EST_occupied")
        r.call("TFR_EST_suspend_parliament")
        r.call("TFR_EST_suspend_parliament")
        self.assertNotIn("TFR_EST_parliament_open", r.flags)
        self.assertNotIn("TFR_EST_constitutional_presidency", r.ideas)
        r.call("TFR_EST_restore_parliament")
        self.assertEqual(saved, {k: v for k, v in r.variables.items() if k in saved})
        self.assertEqual(r.variables["TFR_EST_pm_party"], 2)
        self.assertIn("TFR_EST_restoration_election", r.flags)
        self.assertIn("TFR_EST_caretaker", r.flags)

    def test_root_initialization_is_idempotent(self):
        r = Runtime()
        r.flags.clear()
        r.call("TFR_EST_initialize_systems")
        before = r.variables.copy()
        events = r.events.copy()
        r.call("TFR_EST_initialize_systems")
        self.assertEqual(r.variables, before)
        self.assertEqual(r.events, events)
        self.assertEqual(r.variables["TFR_EST_coalition_seats"], 57)


if __name__ == "__main__":
    unittest.main()

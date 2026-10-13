"""Structural regression checks for survival guards and parent continuity.

These verify generated game scripts against the installed TFR baseline. They
cannot substitute for the in-game settlement/save/DLC matrix.
"""
import json
import unittest
from pathlib import Path

from patch_tfr_compatibility import DEFAULT_PARENT, ROOT, parse, walk


def shape(node):
    return node.key, node.value, tuple(shape(c) for c in node.children)


def nodes_with(entries, key):
    return [e for e, _ in walk(entries) if e.key == key]


def entry_child(e, key):
    return next((c for c in e.children if c.key == key), None)


def scalar(e, key):
    child = entry_child(e, key)
    return child.value if child else None


class SettlementProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "docs/compatibility.json").read_text(encoding="utf-8"))
        cls.pairs = {}
        for override in cls.manifest["overrides"]:
            path = override["path"]
            cls.pairs[path] = (
                parse((DEFAULT_PARENT / path).read_text(encoding="utf-8-sig")),
                parse((ROOT / path).read_text(encoding="utf-8-sig")),
            )

    def test_other_country_annex_semantics_are_retained(self):
        # Every old annex verb, including transfer_troops, remains available in
        # the non-Estonia branch. This catches accidental scope/field deletion.
        for path, (upstream, patched) in self.pairs.items():
            self.assertEqual([shape(e) for e in nodes_with(upstream, "annex_country")],
                             [shape(e) for e in nodes_with(patched, "annex_country")], path)

    def test_all_explicit_and_dynamic_estonia_annexes_are_prevented_before_annex(self):
        guards = 0
        for path, (_, patched) in self.pairs.items():
            for container, _ in walk([type("Root", (), {"key": "root", "value": None, "start": 0, "end": 0, "children": patched})()]):
                for i, e in enumerate(container.children):
                    if e.key != "else":
                        continue
                    annex = entry_child(e, "annex_country")
                    if not annex:
                        continue
                    target = scalar(annex, "target")
                    prior = container.children[i - 1] if i else None
                    helper = entry_child(prior, "TFR_EST_preserve_annexation") if prior and prior.key == "if" else None
                    if not helper:
                        continue
                    self.assertEqual(helper.value, "yes", path)
                    captured = entry_child(prior, target)
                    self.assertIsNotNone(captured, path)
                    self.assertEqual(scalar(captured, "save_event_target_as"), "TFR_EST_settlement_target", path)
                    policy = entry_child(captured, "set_temp_variable")
                    self.assertIsNotNone(policy, path)
                    self.assertEqual(scalar(policy, "var"), "TFR_EST_settlement_transfer_troops", path)
                    expected_policy = "0" if scalar(annex, "transfer_troops") == "no" else "1"
                    self.assertEqual(scalar(policy, "value"), expected_policy, path)
                    self.assertLess(prior.children.index(captured), prior.children.index(helper), path)
                    limit = entry_child(prior, "limit")
                    scope = entry_child(limit, target)
                    self.assertIsNotNone(scope, path)
                    self.assertEqual(scalar(scope, "original_tag"), "EST", path)
                    self.assertEqual(scalar(scope, "has_country_flag"), "TFR_EST_initialized", path)
                    guards += 1
            for annex, ancestors in walk(patched):
                if annex.key == "annex_country" and scalar(annex, "target") == "EST":
                    self.assertEqual(ancestors[-1].key, "else", path)
        self.assertGreater(guards, 100, "Dynamic European/faction annex paths must be included.")

    def test_parent_war_and_story_progression_is_retained(self):
        # The guard must not drop peace callbacks, follow-up wars or victory
        # flags for Russia, Germany and every unrelated campaign.
        for path, (upstream, patched) in self.pairs.items():
            for key in ("declare_war_on", "white_peace", "set_global_flag", "clr_global_flag", "country_event", "news_event", "complete_national_focus", "load_oob"):
                # A top-level event definition contains the changed settlement
                # itself. Compare event dispatches, not that whole definition.
                retained = lambda tree: [shape(e) for e in nodes_with(tree, key) if not entry_child(e, "option")]
                self.assertEqual(retained(upstream), retained(patched), f"{path}: {key}")

    def test_reserved_anchor_is_excluded_from_replacement_annex(self):
        effects = parse((ROOT / "common/scripted_effects/TFR_EST_occupation.txt").read_text(encoding="utf-8"))
        helper = next(e for e in effects if e.key == "TFR_EST_preserve_annexation")
        self.assertFalse(nodes_with(helper.children, "annex_country"))
        self.assertFalse(nodes_with(helper.children, "release"))
        target_scope = entry_child(helper, "event_target:TFR_EST_settlement_target")
        sweep = entry_child(target_scope, "every_owned_state")
        self.assertEqual(scalar(entry_child(entry_child(sweep, "limit"), "NOT"), "state"), "13")
        self.assertEqual(scalar(sweep, "transfer_state_to"), "event_target:TFR_EST_settlement_receiver")

    def test_converted_annexes_settle_original_forces_once_per_mandate(self):
        effects = parse((ROOT / "common/scripted_effects/TFR_EST_occupation.txt").read_text(encoding="utf-8"))
        helper = next(e for e in effects if e.key == "TFR_EST_settle_annexed_forces")
        guard = entry_child(helper, "if")
        check = entry_child(entry_child(entry_child(guard, "limit"), "NOT"), "check_variable")
        self.assertEqual(scalar(check, "var"), "TFR_EST_annexed_forces_generation")
        self.assertEqual(scalar(check, "value"), "TFR_EST_occupation_generation")
        completion = entry_child(guard, "set_variable")
        self.assertEqual(scalar(completion, "var"), "TFR_EST_annexed_forces_generation")
        self.assertEqual(scalar(completion, "value"), "TFR_EST_occupation_generation")
        destroy_branch = entry_child(guard, "if")
        deletion = entry_child(destroy_branch, "delete_unit")
        self.assertEqual(scalar(deletion, "disband"), "no", "No free equipment/manpower refund after destructive annexation.")
        transfer_branch = entry_child(guard, "else")
        self.assertIsNone(entry_child(transfer_branch, "delete_unit"))
        for branch, army in ((destroy_branch, "0"), (transfer_branch, "1")):
            transfer = entry_child(branch, "transfer_units_fraction")
            self.assertEqual(scalar(transfer, "target"), "event_target:TFR_EST_settlement_receiver")
            self.assertEqual(scalar(transfer, "army_ratio"), army)
            for field in ("stockpile_ratio", "navy_ratio", "air_ratio"):
                self.assertEqual(scalar(transfer, field), "1")
        callers = [e.key for e in effects if nodes_with(e.children, "TFR_EST_settle_annexed_forces")]
        self.assertEqual(callers, ["TFR_EST_preserve_annexation"], "Ordinary puppeting and daily reconciliation must retain their forces.")

    def test_medvedev_partition_and_tts_remainder_are_retained(self):
        for path, (upstream, patched) in self.pairs.items():
            for state in ("191", "840", "1329"):
                self.assertEqual(sum(e.value == state for e in nodes_with(upstream, "transfer_state")),
                                 sum(e.value == state for e in nodes_with(patched, "transfer_state")), f"{path}: state {state}")
        sov = self.pairs["common/scripted_effects/TFR_scripted_effects_SOV.txt"][1]
        self.assertTrue(any(e.value == "840" for e in nodes_with(sov, "transfer_state")))
        self.assertTrue(any(e.value == "1329" for e in nodes_with(sov, "transfer_state")))

    def test_autonomy_cannot_downgrade_or_integrate(self):
        state = parse((ROOT / "common/autonomous_states/TFR_EST_occupation.txt").read_text(encoding="utf-8"))[0]
        self.assertEqual(scalar(state, "is_puppet"), "yes")
        for gate in ("can_take_level", "can_lose_level"):
            self.assertEqual(scalar(entry_child(state, gate), "always"), "no")
        levels = entry_child(state, "allowed_levels_filter")
        self.assertEqual([e.key for e in levels.children], ["TFR_EST_autonomy_occupation"])

    def test_daily_repair_does_not_prevent_capture_or_repay_transition_rewards(self):
        effects = parse((ROOT / "common/scripted_effects/TFR_EST_occupation.txt").read_text(encoding="utf-8"))
        enter = next(e for e in effects if e.key == "TFR_EST_enter_occupation")
        for e, parents in walk(enter.children):
            if e.key == "set_state_controller_to":
                branch = next(p for p in reversed(parents) if p.key == "if")
                limit = entry_child(branch, "limit")
                check = entry_child(limit, "check_variable")
                self.assertEqual(scalar(check, "var"), "TFR_EST_new_settlement")
                self.assertEqual(scalar(check, "value"), "1")
            if e.key in ("TFR_EST_change_cohesion", "TFR_EST_change_readiness"):
                branch = next(p for p in reversed(parents) if p.key == "if")
                limit = entry_child(branch, "limit")
                self.assertIsNotNone(entry_child(limit, "OR"))
        reconcile = next(e for e in effects if e.key == "TFR_EST_reconcile_occupation")
        for e, parents in walk(reconcile.children):
            if e.key == "load_focus_tree":
                branch = next(p for p in reversed(parents) if p.key == "if")
                limit = entry_child(branch, "limit")
                alternatives = entry_child(limit, "OR")
                self.assertTrue(any(scalar(c, "has_focus_tree") == "TFR_EST_occupation_tree" for c in alternatives.children if c.key == "NOT"))

    def test_completed_projects_survive_tree_switch_without_repaying_rewards(self):
        focus_tree = parse((ROOT / "common/national_focus/TFR_EST_occupation.txt").read_text(encoding="utf-8"))[0]
        for focus in [e for e in focus_tree.children if e.key == "focus"]:
            done_flag = scalar(focus, "id") + "_done"
            self.assertEqual(scalar(entry_child(focus, "bypass"), "has_country_flag"), done_flag)
            reward = entry_child(entry_child(focus, "completion_reward"), "if")
            guard = entry_child(entry_child(reward, "limit"), "NOT")
            self.assertEqual(scalar(guard, "has_country_flag"), done_flag)
            self.assertEqual(scalar(reward, "set_country_flag"), done_flag)
        effects = parse((ROOT / "common/scripted_effects/TFR_EST_occupation.txt").read_text(encoding="utf-8"))
        enter = next(e for e in effects if e.key == "TFR_EST_enter_occupation")
        cleared = [e.value for e in nodes_with(enter.children, "clr_country_flag")]
        self.assertNotIn("TFR_EST_occupation_employment_done", cleared, "The factory project must remain one-time.")
        self.assertNotIn("TFR_EST_occupation_rebuild_done", cleared, "Material reconstruction must survive a second defeat.")
        self.assertIn("TFR_EST_occupation_accommodation_done", cleared, "A new patron permits a new political choice.")
        self.assertIn("TFR_EST_occupation_clandestine_done", cleared)

    def test_occupation_routes_all_have_live_gates_and_parent_art(self):
        focus_tree = parse((ROOT / "common/national_focus/TFR_EST_occupation.txt").read_text(encoding="utf-8"))[0]
        focuses = [e for e in focus_tree.children if e.key == "focus"]
        route_types = set()
        for e in focuses:
            gate = entry_child(e, "allow_branch")
            if gate:
                route_types.add(scalar(entry_child(gate, "check_variable"), "value"))
            self.assertEqual(scalar(entry_child(e, "available"), "has_country_flag"), "TFR_EST_occupied")
        self.assertEqual(route_types, {"1", "2", "3", "4", "5", "6", "7"})
        self.assertGreaterEqual(len(focuses), 35)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Check PM validity and real authored repair chains without a native scheduler.

The source runtime records actual idea membership changes, so removing and then
re-adding an incumbent cannot pass merely because the final idea set matches.
It evaluates each idea's authored availability; it does not invent the engine's
automatic cancellation rules or claim that a live game day was advanced.
"""
from datetime import date
import unittest

from script_runtime import ROOT, Runtime, parse


PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
INCUMBENTS = (
    ('TFR_EST_pm_reform', 'reform', ()),
    ('TFR_EST_pm_reform_michal', 'reform', ('TFR_EST_kallas_departed_for_europe',)),
    ('TFR_EST_pm_centre', 'centre', ()),
    ('TFR_EST_pm_centre_kiik', 'centre', ('TFR_EST_centre_leader_kiik',)),
    ('TFR_EST_pm_centre_kolvart', 'centre', ('TFR_EST_centre_leader_kolvart',)),
    ('TFR_EST_pm_ekre', 'ekre', ()),
    ('TFR_EST_pm_ekre_martin', 'ekre', ('TFR_EST_martin_leads_ekre',)),
    ('TFR_EST_pm_isamaa', 'isamaa', ()),
    ('TFR_EST_pm_sde', 'sde', ()),
    ('TFR_EST_pm_sde_laanemets', 'sde', ('TFR_EST_laanemets_leads_sde',)),
    ('TFR_EST_pm_e200', 'e200', ()),
    ('TFR_EST_pm_pp', 'pp', ()),
)


class PrimeMinisterRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.definitions = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text(
            encoding='utf-8-sig')).get('ideas').get('head_minister')
        cls.tokens = tuple(entry.key for entry in cls.definitions.entries)
        actions = parse((ROOT / 'common/on_actions/TFR_EST_systems.txt').read_text(
            encoding='utf-8-sig')).get('on_actions')
        cls.daily = actions.get('on_daily_EST').get('effect')
        cls.weekly = actions.get('on_weekly_EST').get('effect')

    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        return r

    def elect(self, r, party):
        for p in PARTIES:
            r.variables['TFR_EST_active_' + p] = 1
            r.variables['TFR_EST_support_' + p] = 10000 if p == party else 0
        r.variables['TFR_EST_support_other'] = 0
        r.call('TFR_EST_hold_election')
        r.call('TFR_EST_confirm_cabinet')

    def incumbent(self, token, party, flags):
        r = self.fresh()
        r.flags.update(flags)
        # Isolate stable cabinet repair from dated elections and succession.
        # These fixtures intentionally activate every party for confirmation.
        r.props['date'] = date(2020, 1, 2)
        self.elect(r, party)
        self.assertEqual(r.ideas.intersection(self.tokens), {token})
        self.reset_changes(r)
        return r

    def reset_changes(self, r):
        r.idea_additions.clear()
        r.idea_removals.clear()

    def pm_changes(self, r):
        return ([idea for idea in r.idea_additions if idea in self.tokens],
                [idea for idea in r.idea_removals if idea in self.tokens])

    def real_repair_chains(self, r):
        # Execute authored callbacks and their ordinary parliament controller.
        # This does not advance native time or emulate engine cancellation.
        for _ in range(3):
            r.run(self.daily)
            r.run(self.weekly)
            r.call('TFR_EST_reconcile_cabinet_leadership')
            r.call('TFR_EST_reconcile_presidency')

    def test_each_installed_pm_satisfies_its_authored_availability(self):
        self.assertEqual(len(self.tokens), 12)
        r = Runtime()
        for token in self.tokens:
            with self.subTest(incumbent=token):
                r.ideas = {token}
                self.assertTrue(r.condition(self.definitions.get(token).get('available')))

    def test_no_uninstalled_pm_becomes_available_for_player_appointment(self):
        r = Runtime()
        for installed in (None, *self.tokens):
            r.ideas = {installed} if installed else set()
            with self.subTest(installed=installed):
                available = {token for token in self.tokens
                             if r.condition(self.definitions.get(token).get('available'))}
                self.assertEqual(available, {installed} if installed else set())

    def test_all_twelve_incumbents_survive_real_repair_chains_without_churn(self):
        self.assertEqual(set(self.tokens), {token for token, _, _ in INCUMBENTS})
        for token, party, flags in INCUMBENTS:
            with self.subTest(incumbent=token):
                r = self.incumbent(token, party, flags)
                president = r.leader
                self.real_repair_chains(r)
                self.assertEqual(r.ideas.intersection(self.tokens), {token})
                self.assertEqual(self.pm_changes(r), ([], []))
                self.assertEqual(r.leader, president)
                self.assertTrue(r.condition(self.definitions.get(token).get('available')))

    def test_caretaker_incumbents_are_not_removed_and_reappointed_by_repairs(self):
        for token, party, flags in INCUMBENTS:
            with self.subTest(incumbent=token):
                r = self.incumbent(token, party, flags)
                r.call('TFR_EST_enter_caretaker')
                self.reset_changes(r)
                self.real_repair_chains(r)
                self.assertIn('TFR_EST_caretaker', r.flags)
                self.assertEqual(r.ideas.intersection(self.tokens), {token})
                self.assertEqual(self.pm_changes(r), ([], []))

    def test_actual_confirmed_party_transitions_replace_pm_exactly_once(self):
        r = self.fresh()
        incumbent = 'TFR_EST_pm_centre'
        for party in PARTIES:
            with self.subTest(incoming=party):
                expected = 'TFR_EST_pm_' + party
                self.reset_changes(r)
                self.elect(r, party)
                self.assertEqual(r.ideas.intersection(self.tokens), {expected})
                self.assertEqual(self.pm_changes(r), ([expected], [incumbent]))
                self.real_repair_chains(r)
                self.assertEqual(self.pm_changes(r), ([expected], [incumbent]))
                incumbent = expected

    def test_a_missing_incumbent_is_repaired_once_and_then_remains_quiet(self):
        for token, party, flags in INCUMBENTS:
            with self.subTest(incumbent=token):
                r = self.incumbent(token, party, flags)
                # Model a missing saved display entry, not a player dismissal.
                r.ideas.remove(token)
                r.call('TFR_EST_reconcile_executive_display')
                self.assertEqual(self.pm_changes(r), ([token], []))
                self.real_repair_chains(r)
                self.assertEqual(self.pm_changes(r), ([token], []))
                self.assertEqual(r.ideas.intersection(self.tokens), {token})

    def test_occupation_removes_once_and_restoration_reinstates_once(self):
        for token, party, flags in INCUMBENTS:
            with self.subTest(incumbent=token):
                r = self.incumbent(token, party, flags)
                r.flags.add('TFR_EST_occupied')
                r.props['is_subject'] = 'yes'
                r.leader = 'EST_yana_toom_char'
                r.call('TFR_EST_suspend_parliament')
                r.call('TFR_EST_suspend_parliament')
                r.call('TFR_EST_reconcile_executive_display')
                self.assertEqual(r.ideas.intersection(self.tokens), set())
                self.assertEqual(self.pm_changes(r), ([], [token]))
                self.assertEqual(r.leader, 'EST_yana_toom_char')
                self.reset_changes(r)
                r.props['is_subject'] = 'no'
                r.call('TFR_EST_restore_parliament')
                self.assertEqual(r.ideas.intersection(self.tokens), {token})
                self.assertEqual(self.pm_changes(r), ([token], []))
                self.real_repair_chains(r)
                self.assertEqual(self.pm_changes(r), ([token], []))

    def test_every_pm_still_blocks_manual_removal(self):
        r = Runtime()
        for token in self.tokens:
            with self.subTest(incumbent=token):
                r.ideas = {token}
                definition = self.definitions.get(token)
                self.assertFalse(r.condition(definition.get('allowed_to_remove')))
                self.assertEqual(definition.get('removal_cost'), '-1')


if __name__ == '__main__':
    unittest.main()

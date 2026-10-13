from datetime import date
import unittest

from script_runtime import Runtime, ROOT, Block, parse

PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
GROUPS = ('market_liberal', 'social_liberal', 'authoritarian_democrat', 'conservative', 'social_democrat', 'social_liberal', 'market_liberal')


class ExecutiveLifecycleTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        return r

    def ministers(self, r):
        return r.ideas & {'TFR_EST_pm_' + party for party in PARTIES}

    def test_all_seven_confirmed_cabinets_keep_separate_president(self):
        r = self.runtime()
        self.assertEqual(r.leader, 'TFR_EST_kersti_kaljulaid')
        self.assertEqual(self.ministers(r), {'TFR_EST_pm_centre'})
        for index, (party, group) in enumerate(zip(PARTIES, GROUPS), 1):
            r.call('TFR_EST_clear_coalition')
            for p in PARTIES:
                r.variables['TFR_EST_seats_' + p] = 101 if p == party else 0
            r.variables['TFR_EST_coalition_' + party] = 1
            r.variables['TFR_EST_nominee_party'] = index
            r.call('TFR_EST_recount_confidence')
            r.call('TFR_EST_confirm_cabinet')
            self.assertEqual(r.variables['TFR_EST_pm_party'], index)
            self.assertEqual(r.politics['ruling_party'], group)
            self.assertEqual(r.leader, 'TFR_EST_kersti_kaljulaid')
            self.assertEqual(self.ministers(r), {'TFR_EST_pm_' + party})

    def test_caretaker_and_presidential_succession_keep_ledger(self):
        r = self.runtime()
        r.call('TFR_EST_enter_caretaker')
        before = r.variables.copy()
        r.props['date'] = date(2021, 10, 11)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(r.leader, 'TFR_EST_alar_karis')
        self.assertEqual(self.ministers(r), {'TFR_EST_pm_centre'})
        self.assertIn('TFR_EST_caretaker', r.flags)
        for key in before:
            if key.startswith(('TFR_EST_support_', 'TFR_EST_seats_')) or key == 'TFR_EST_pm_party':
                self.assertEqual(r.variables[key], before[key])

    def test_occupation_hides_cabinet_without_overwriting_parent_leader(self):
        r = self.runtime()
        r.flags.add('TFR_EST_karis_president')
        r.call('TFR_EST_reconcile_presidency')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.leader = 'EST_yana_toom_char'
        r.call('TFR_EST_suspend_parliament')
        r.call('TFR_EST_reconcile_cabinet_leadership')
        r.call('TFR_EST_reconcile_presidency')
        self.assertNotIn('head_of_gov_ui_enabled', r.flags)
        self.assertFalse(self.ministers(r))
        self.assertEqual(r.leader, 'EST_yana_toom_char')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_restore_parliament')
        self.assertEqual(r.leader, 'TFR_EST_alar_karis')
        self.assertEqual(self.ministers(r), {'TFR_EST_pm_centre'})
        self.assertIn('head_of_gov_ui_enabled', r.flags)
        self.assertIn('TFR_EST_caretaker', r.flags)

    def test_display_repair_is_idempotent_and_ministers_are_locked(self):
        r = self.runtime()
        before = r.variables.copy()
        promotions = r.characters.copy()
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertEqual(r.variables, before)
        self.assertEqual(r.characters, promotions)
        ministers = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text()).get('ideas').get('head_minister')
        for entry in ministers.entries:
            idea = entry.value
            self.assertEqual(idea.get('available').get('always'), 'no')
            self.assertEqual(idea.get('allowed_to_remove').get('always'), 'no')
            self.assertEqual(idea.get('modifier').entries, [])

    def test_multirole_presidents_always_promote_an_explicit_ideology(self):
        r = self.runtime()
        helper = r.effects['TFR_EST_promote_constitutional_president']
        count = 0
        for _, e in helper.walk():
            if e.key == 'promote_character':
                self.assertIsInstance(e.value, Block)
                self.assertIsNotNone(e.value.get('ideology'))
                count += 1
        self.assertEqual(count, 10)


if __name__ == '__main__':
    unittest.main()

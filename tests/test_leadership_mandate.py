"""Election mandates own coalition leadership; normal negotiations cannot replace it."""
from fractions import Fraction
import hashlib
import unittest

from script_runtime import ROOT, Block, Runtime, parse


PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
EXECUTIVE_VARIABLES = ('TFR_EST_mandate_party', 'TFR_EST_nominee_party', 'TFR_EST_pm_party')
FOCUS_BASELINE = {
    'TFR_EST_occupation.txt': 'e0fd40ae1e48e8e355a2baba6b455625395c11be2c41141f6376c722aed5ffed',
}


class LeadershipMandateTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        return r

    def executive(self, r):
        return tuple(r.variables.get(key, Fraction(0)) for key in EXECUTIVE_VARIABLES)

    def votes(self, r, values):
        for party, value in zip(PARTIES, values):
            r.variables['TFR_EST_support_' + party] = Fraction(value)
            r.variables['TFR_EST_active_' + party] = Fraction(1)
        r.variables['TFR_EST_support_other'] = Fraction(10000 - sum(values))

    def majority(self, r, *parties):
        for party in parties:
            r.variables['TFR_EST_coalition_' + party] = Fraction(1)
            r.variables['TFR_EST_supply_' + party] = Fraction(0)
        r.call('TFR_EST_recount_confidence')

    def test_historical_centre_exception_survives_weekly_reconciliation(self):
        r = self.runtime()
        self.assertGreater(r.variables['TFR_EST_seats_reform'], r.variables['TFR_EST_seats_centre'])
        self.assertEqual(self.executive(r), (2, 2, 2))
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), (2, 2, 2))
        self.assertEqual(r.variables['TFR_EST_confidence_seats'], 57)
        self.assertNotIn('TFR_EST_caretaker', r.flags)

    def test_each_election_winner_is_automatically_the_mandated_leader(self):
        for index, party in enumerate(PARTIES, 1):
            with self.subTest(party=party):
                r = self.runtime()
                self.votes(r, tuple(10000 if p == party else 0 for p in PARTIES))
                r.call('TFR_EST_hold_election')
                self.assertEqual(self.executive(r), (index, index, 2))
                self.assertEqual(r.variables['TFR_EST_coalition_' + party], 1)
                self.assertEqual(r.variables['TFR_EST_supply_' + party], 0)
                self.assertEqual(r.variables['TFR_EST_confidence_seats'], 101)
                self.assertIn('TFR_EST_caretaker', r.flags)
                r.call('TFR_EST_confirm_cabinet')
                self.assertEqual(self.executive(r), (index, index, index))
                self.assertNotIn('TFR_EST_caretaker', r.flags)
                self.assertNotIn('TFR_EST_electoral_handover', r.flags)

    def test_equal_largest_seat_totals_use_fixed_party_order(self):
        for values, expected, tied in (
            ((3990, 3990, 2020, 0, 0, 0, 0), 1, ('reform', 'centre')),
            ((0, 3990, 3990, 2020, 0, 0, 0), 2, ('centre', 'ekre')),
            ((0, 0, 0, 0, 2020, 3990, 3990), 6, ('e200', 'pp')),
        ):
            with self.subTest(values=values):
                r = self.runtime()
                self.votes(r, values)
                r.call('TFR_EST_hold_election')
                first, second = (r.variables['TFR_EST_seats_' + party] for party in tied)
                self.assertEqual(first, second)
                self.assertEqual(first, max(r.variables['TFR_EST_seats_' + party] for party in PARTIES))
                self.assertEqual(r.variables['TFR_EST_mandate_party'], expected)
                self.assertEqual(r.variables['TFR_EST_nominee_party'], expected)

    def test_invalid_election_preserves_incumbent_and_mandate(self):
        for values in ((10001, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0)):
            with self.subTest(values=values):
                r = self.runtime()
                before = self.executive(r)
                seats = [r.variables['TFR_EST_seats_' + p] for p in PARTIES]
                coalition = [r.variables['TFR_EST_coalition_' + p] for p in PARTIES]
                self.votes(r, values)
                r.call('TFR_EST_hold_election')
                self.assertEqual(self.executive(r), before)
                self.assertEqual([r.variables['TFR_EST_seats_' + p] for p in PARTIES], seats)
                self.assertEqual([r.variables['TFR_EST_coalition_' + p] for p in PARTIES], coalition)
                self.assertNotIn('TFR_EST_electoral_handover', r.flags)
                self.assertNotIn('TFR_EST_caretaker', r.flags)
                self.assertTrue(r.messages)

    def test_invalid_election_cannot_consume_a_pending_electoral_handover(self):
        r = self.runtime()
        self.votes(r, (6000, 4000, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertEqual(self.executive(r), (1, 1, 2))
        self.assertIn('TFR_EST_electoral_handover', r.flags)
        self.votes(r, (10001, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertEqual(self.executive(r), (1, 1, 2))
        self.assertIn('TFR_EST_electoral_handover', r.flags)
        self.assertIn('TFR_EST_caretaker', r.flags)

    def test_incumbent_remains_caretaker_until_election_winner_has_51_votes(self):
        r = self.runtime()
        self.votes(r, (3600, 2800, 2000, 1600, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertEqual(self.executive(r), (1, 1, 2))
        self.assertLess(r.variables['TFR_EST_confidence_seats'], 51)
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(self.executive(r), (1, 1, 2))
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertIn('TFR_EST_electoral_handover', r.flags)
        self.majority(r, 'centre')
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(self.executive(r), (1, 1, 1))
        self.assertNotIn('TFR_EST_electoral_handover', r.flags)

    def test_obsolete_unapproved_nomination_effects_are_noops(self):
        for party in PARTIES:
            with self.subTest(party=party):
                r = self.runtime()
                before = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
                r.call('TFR_EST_nominate_' + party)
                self.assertEqual((r.variables, r.flags, r.ideas), before)

    def test_fabricated_nominee_cannot_bypass_the_mandate(self):
        for handover in (None, 'TFR_EST_electoral_handover', 'TFR_EST_scripted_handover'):
            with self.subTest(handover=handover):
                r = self.runtime()
                r.variables['TFR_EST_nominee_party'] = Fraction(1)
                self.majority(r, 'reform')
                r.call('TFR_EST_enter_caretaker')
                if handover:
                    r.flags.add(handover)
                r.call('TFR_EST_confirm_cabinet')
                self.assertEqual(r.variables['TFR_EST_mandate_party'], 2)
                self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
                self.assertIn('TFR_EST_caretaker', r.flags)

    def test_matching_fabricated_mandate_without_handover_cannot_replace_pm(self):
        r = self.runtime()
        r.variables['TFR_EST_mandate_party'] = Fraction(1)
        r.variables['TFR_EST_nominee_party'] = Fraction(1)
        self.majority(r, 'reform')
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_caretaker', r.flags)

    def test_confidence_recovery_reconfirms_the_same_incumbent(self):
        r = self.runtime()
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_enter_caretaker')
        self.majority(r, 'reform')
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(self.executive(r), (2, 2, 2))
        self.assertNotIn('TFR_EST_caretaker', r.flags)

    def test_ai_confidence_recovery_keeps_centre_despite_reform_route_rule(self):
        r = self.runtime()
        r.props['is_ai'] = 'yes'
        r.props['game_rules']['TFR_EST_AI_ROUTE'] = 'REFORM'
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), (2, 2, 2))
        self.assertEqual(r.variables['TFR_EST_coalition_centre'], 1)
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertNotIn('TFR_EST_caretaker', r.flags)

    def test_campaign_poll_changes_do_not_change_leadership_or_current_seats(self):
        r = self.runtime()
        before = self.executive(r)
        seats = [r.variables['TFR_EST_seats_' + p] for p in PARTIES]
        support = r.variables['TFR_EST_support_reform']
        for _ in range(4):
            r.call('TFR_EST_campaign_reform')
        r.call('TFR_EST_parliament_tick')
        self.assertGreater(r.variables['TFR_EST_support_reform'], support)
        self.assertEqual(self.executive(r), before)
        self.assertEqual([r.variables['TFR_EST_seats_' + p] for p in PARTIES], seats)

    def test_ai_election_handover_cannot_override_winner_with_preferred_party(self):
        r = self.runtime()
        r.props['is_ai'] = 'yes'
        r.props['game_rules']['TFR_EST_AI_ROUTE'] = 'CENTRE'
        self.votes(r, (3990, 3990, 2020, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertEqual(self.executive(r), (1, 1, 1))
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertNotIn('TFR_EST_caretaker', r.flags)

    def test_missing_mandate_repairs_from_saved_pm_not_largest_party(self):
        r = self.runtime()
        r.variables.pop('TFR_EST_mandate_party', None)
        r.variables['TFR_EST_nominee_party'] = Fraction(0)
        r.variables['TFR_EST_coalition_centre'] = Fraction(0)
        r.variables['TFR_EST_supply_centre'] = Fraction(1)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), (2, 2, 2))
        self.assertEqual(r.variables['TFR_EST_coalition_centre'], 1)
        self.assertEqual(r.variables['TFR_EST_supply_centre'], 0)
        self.assertNotIn('TFR_EST_electoral_handover', r.flags)

    def test_mandated_leader_cannot_be_removed_by_a_partner_withdrawal(self):
        r = self.runtime()
        path = ROOT / 'common/decisions/TFR_EST_parliament.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        withdrawal = next(item.value for category in tree.entries if isinstance(category.value, Block)
                          for item in category.value.entries if item.key == 'TFR_EST_withdraw_centre_decision')
        self.assertFalse(r.condition(withdrawal.get('visible')))
        r.variables['TFR_EST_coalition_centre'] = Fraction(0)
        r.variables['TFR_EST_supply_centre'] = Fraction(1)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), (2, 2, 2))
        self.assertEqual(r.variables['TFR_EST_coalition_centre'], 1)
        self.assertEqual(r.variables['TFR_EST_supply_centre'], 0)

    def test_occupation_and_restoration_preserve_mandate_until_new_election(self):
        r = self.runtime()
        before = self.executive(r)
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_suspend_parliament')
        self.votes(r, (0, 0, 10000, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertEqual(self.executive(r), before)
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_restore_parliament')
        self.assertEqual(self.executive(r), before)
        for _ in range(11):
            r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), before)
        self.assertIn('TFR_EST_restoration_election', r.flags)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.executive(r), (3, 3, 2))
        self.assertNotIn('TFR_EST_restoration_election', r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(self.executive(r), (3, 3, 3))

    def test_explicit_story_authorization_can_replace_leadership(self):
        r = self.runtime()
        r.flags.add('TFR_EST_scripted_cabinet_change')
        r.call('TFR_EST_nominate_ekre')
        r.flags.discard('TFR_EST_scripted_cabinet_change')
        self.assertEqual(self.executive(r), (3, 3, 2))
        self.assertIn('TFR_EST_scripted_handover', r.flags)
        self.majority(r, 'centre', 'isamaa')
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(self.executive(r), (3, 3, 3))
        self.assertNotIn('TFR_EST_scripted_handover', r.flags)

    def test_player_decisions_cannot_nominate_or_authorize_story_handover(self):
        path = ROOT / 'common/decisions/TFR_EST_parliament.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        decisions = [item for category in tree.entries if isinstance(category.value, Block)
                     for item in category.value.entries if isinstance(item.value, Block)]
        self.assertFalse(any(item.key.startswith('TFR_EST_nominate_') for item in decisions))
        self.assertTrue(any(item.key == 'TFR_EST_confirm_cabinet_decision' for item in decisions))
        for path in (ROOT / 'common/decisions').glob('TFR_EST_*.txt'):
            tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
            for _, entry in tree.walk():
                if entry.key == 'set_country_flag':
                    flag = entry.value.get('flag') if isinstance(entry.value, Block) else entry.value
                    self.assertNotIn(flag, {'TFR_EST_scripted_cabinet_change', 'TFR_EST_scripted_handover'})

    def test_occupation_tree_matches_the_current_layout_baseline(self):
        # Only horizontal positions changed in the October compact-tree revision.
        for name, expected in FOCUS_BASELINE.items():
            with self.subTest(tree=name):
                actual = hashlib.sha256((ROOT / 'common/national_focus' / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

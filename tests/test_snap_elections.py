"""Snap votes require one-use story authorization; the regular calendar survives."""
from datetime import date
from fractions import Fraction
import unittest

from script_runtime import Block, ROOT, Runtime, parse


PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
AUTHORIZATION = 'TFR_EST_scripted_snap_election'


class SnapElectionTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        return r

    def seats(self, r):
        return tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES)

    def reform_poll(self, r):
        for party in PARTIES:
            r.variables['TFR_EST_support_' + party] = Fraction(10000 if party == 'reform' else 0)
        r.variables['TFR_EST_support_other'] = Fraction(0)

    def test_no_snap_decision_or_player_authorization_exists(self):
        for path in (ROOT / 'common/decisions').glob('TFR_EST_*.txt'):
            tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
            for _, entry in tree.walk():
                self.assertNotEqual(entry.key, 'TFR_EST_snap_election_decision')
                self.assertNotIn(entry.key, {'TFR_EST_hold_election', 'TFR_EST_snap_election'})
                if entry.key == 'set_country_flag':
                    flag = entry.value.get('flag') if isinstance(entry.value, Block) else entry.value
                    self.assertNotEqual(flag, AUTHORIZATION)

    def test_no_authorization_is_an_exact_noop(self):
        r = self.runtime()
        self.reform_poll(r)
        before = (r.variables.copy(), r.flags.copy(), r.ideas.copy(), r.events.copy())
        r.call('TFR_EST_snap_election')
        self.assertEqual((r.variables, r.flags, r.ideas, r.events), before)

    def test_authorized_vote_changes_assembly_and_consumes_flag(self):
        r = self.runtime()
        self.reform_poll(r)
        r.flags.add(AUTHORIZATION)
        r.call('TFR_EST_snap_election')
        self.assertEqual(self.seats(r), (101, 0, 0, 0, 0, 0, 0))
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 1)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_electoral_handover', r.flags)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertNotIn(AUTHORIZATION, r.flags)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 52)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2023)
        before = (r.variables.copy(), r.flags.copy(), r.events.copy())
        r.call('TFR_EST_snap_election')
        self.assertEqual((r.variables, r.flags, r.events), before)

    def test_invalid_poll_consumes_authorization_without_cost_or_seat_change(self):
        r = self.runtime()
        self.reform_poll(r)
        r.variables['TFR_EST_support_reform'] = Fraction(10001)
        # Stale success markers cannot charge cohesion for a rejected vote.
        r.variables['TFR_EST_election_this_tick'] = Fraction(1)
        before = self.seats(r)
        r.flags.add(AUTHORIZATION)
        r.call('TFR_EST_snap_election')
        self.assertEqual(self.seats(r), before)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 2)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 55)
        self.assertNotIn(AUTHORIZATION, r.flags)
        self.assertIn('TFR_EST_election_invalid', r.flags)
        self.assertTrue(r.messages)

    def test_occupation_subject_and_restoration_block_and_consume_authorization(self):
        for blocked in ('occupation', 'subject', 'restoration'):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                self.reform_poll(r)
                if blocked == 'occupation':
                    r.flags.add('TFR_EST_occupied')
                elif blocked == 'subject':
                    r.props['is_subject'] = 'yes'
                else:
                    r.flags.add('TFR_EST_restoration_election')
                before = r.variables.copy()
                r.flags.add(AUTHORIZATION)
                r.call('TFR_EST_snap_election')
                self.assertEqual(r.variables, before)
                self.assertNotIn(AUTHORIZATION, r.flags)

    def test_prolonged_caretaker_does_not_automatically_hold_an_election(self):
        r = self.runtime()
        self.reform_poll(r)
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_enter_caretaker')
        before = self.seats(r)
        r.props['date'] = date(2022, 1, 1)
        for _ in range(26):
            r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.seats(r), before)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertNotIn('TFR_EST_election_held', r.flags)
        self.assertNotIn(AUTHORIZATION, r.flags)

    def test_regular_march_election_needs_no_snap_authorization(self):
        r = self.runtime()
        self.reform_poll(r)
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.seats(r), (101, 0, 0, 0, 0, 0, 0))
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 1)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 55)
        self.assertNotIn(AUTHORIZATION, r.flags)

    def test_restoration_election_still_occurs_after_84_days(self):
        r = self.runtime()
        self.reform_poll(r)
        r.call('TFR_EST_restore_parliament')
        for _ in range(11):
            r.call('TFR_EST_parliament_tick')
        self.assertIn('TFR_EST_restoration_election', r.flags)
        self.assertNotEqual(self.seats(r), (101, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_parliament_tick')
        self.assertNotIn('TFR_EST_restoration_election', r.flags)
        self.assertEqual(self.seats(r), (101, 0, 0, 0, 0, 0, 0))
        self.assertEqual(r.variables['TFR_EST_cohesion'], 55)

    def test_ai_renegotiation_does_not_authorize_snap_vote(self):
        r = self.runtime()
        self.reform_poll(r)
        r.props['is_ai'] = 'yes'
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.call('TFR_EST_enter_caretaker')
        before = self.seats(r)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.seats(r), before)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertNotIn(AUTHORIZATION, r.flags)
        self.assertNotIn('TFR_EST_election_held', r.flags)


if __name__ == '__main__':
    unittest.main()

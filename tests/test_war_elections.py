"""Execute the real first-war election controller and its parliament hooks."""
from copy import deepcopy
from datetime import date
from fractions import Fraction
from pathlib import Path
import unittest

from script_runtime import ROOT, Runtime, parse


PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
OVER = 'SOV_nato_war_over_global'
WINNERS = ('nato_nato_won_nato_war', 'SOV_first_nato_war_victory')
PENDING = 'TFR_EST_postwar_election_pending'
HELD = 'TFR_EST_postwar_election_held'
WAITING = 'TFR_EST_election_waiting_first_war'
RESTORATION = 'TFR_EST_restoration_election'


class WarElectionTests(unittest.TestCase):
    def runtime(self, after_2023=True):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        # Keep ordinary party formation out of election-controller fixtures.
        r.variables['TFR_EST_active_pp'] = Fraction(1)
        if after_2023:
            r.variables['TFR_EST_election_year'] = Fraction(2027)
            r.flags.add(WAITING)
            r.props['date'] = date(2027, 3, 5)
        return r

    def poll(self, r, party='reform', invalid=False):
        for name in PARTIES:
            r.variables['TFR_EST_support_' + name] = Fraction(10000 if name == party else 0)
            r.variables['TFR_EST_active_' + name] = Fraction(1)
        r.variables['TFR_EST_support_other'] = Fraction(1 if invalid else 0)

    def seats(self, r):
        return tuple(r.variables['TFR_EST_seats_' + name] for name in PARTIES)

    def election_count(self, r):
        return r.events.count('tfr_estonia_parliament.1')

    def conclude(self, r, winner=WINNERS[0]):
        r.global_flags.update((OVER, winner))
        r.global_flags.discard('SOV_nato_war_begins_global')
        r.props['world_wars'].clear()
        r.props.update(has_war='no', has_capitulated='no')

    def test_2023_remains_a_regular_march_election(self):
        r = self.runtime(after_2023=False)
        self.poll(r)
        r.props['date'] = date(2023, 3, 4)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 0)
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)
        self.assertIn(WAITING, r.flags)
        self.assertNotIn(HELD, r.flags)

    def test_invalid_2023_poll_keeps_calendar_and_assembly_for_retry(self):
        r = self.runtime(after_2023=False)
        self.poll(r, invalid=True)
        before = self.seats(r)
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(r.variables['TFR_EST_election_year'], 2023)
        self.assertEqual(self.seats(r), before)
        self.assertIn('TFR_EST_election_invalid', r.flags)
        self.poll(r)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)

    def test_fixed_2027_and_later_dates_cannot_bypass_the_first_war(self):
        for year in (2027, 2031, 2043):
            with self.subTest(year=year):
                r = self.runtime()
                self.poll(r)
                before = self.seats(r)
                r.props['date'] = date(year, 3, 6)
                for _ in range(3):
                    r.call('TFR_EST_parliament_tick')
                    r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 0)
                self.assertEqual(self.seats(r), before)
                self.assertEqual(r.variables['TFR_EST_election_year'], 2027)
                self.assertIn(WAITING, r.flags)

    def test_a_delayed_invalid_2023_ballot_cannot_create_a_2027_loophole(self):
        r = self.runtime(after_2023=False)
        self.poll(r)
        r.props['date'] = date(2027, 3, 5)
        r.call('TFR_EST_parliament_tick')
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 0)
        self.assertIn(WAITING, r.flags)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertIn(HELD, r.flags)

    def test_start_flag_and_quiet_declaration_frame_are_not_a_settlement(self):
        r = self.runtime()
        self.poll(r)
        r.global_flags.add('SOV_nato_war_begins_global')
        r.call('TFR_EST_reconcile_campaign')
        self.assertEqual(r.variables['TFR_EST_campaign_stage'], 2)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 0)
        self.assertNotIn(PENDING, r.flags)

    def test_temporary_peace_or_second_war_flag_is_not_a_first_settlement(self):
        for flags in ({'SOV_nato_war_begins_global'}, {'second_nato_war_flag'}):
            with self.subTest(flags=flags):
                r = self.runtime()
                self.poll(r)
                r.global_flags.update(flags)
                r.props['has_war'] = 'yes'
                r.call('TFR_EST_war_elections_tick')
                r.props['has_war'] = 'no'
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 0)

    def test_explicit_over_and_a_winner_are_both_required(self):
        for flags in ({OVER}, {WINNERS[0]}, {WINNERS[1]}):
            with self.subTest(flags=flags):
                r = self.runtime()
                self.poll(r)
                r.global_flags.update(flags)
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 0)
                self.assertNotIn(PENDING, r.flags)

    def test_either_parent_winner_triggers_an_independent_survivor_vote(self):
        for winner in WINNERS:
            with self.subTest(winner=winner):
                r = self.runtime()
                self.poll(r)
                self.conclude(r, winner)
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 1)
                self.assertIn(HELD, r.flags)
                self.assertNotIn(PENDING, r.flags)
                self.assertNotIn(WAITING, r.flags)
                self.assertEqual(r.variables['TFR_EST_postwar_term_days'], 0)
                self.assertEqual(r.variables['TFR_EST_election_year'], 2031)

    def test_early_settlement_votes_immediately_instead_of_waiting_until_2027(self):
        r = self.runtime()
        self.poll(r)
        r.props['date'] = date(2025, 9, 1)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2029)
        r.props['date'] = date(2027, 3, 5)
        r.variables['TFR_EST_postwar_term_days'] = Fraction(550)
        r.call('TFR_EST_parliament_tick')
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)

    def test_estonia_war_capitulation_or_active_european_front_defers_vote(self):
        for blocked in ('war', 'capitulation', 'german_front'):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                self.poll(r)
                self.conclude(r)
                if blocked == 'war':
                    r.props['has_war'] = 'yes'
                elif blocked == 'capitulation':
                    r.props['has_capitulated'] = 'yes'
                else:
                    r.props['world_wars'].add(frozenset(('SOV', 'GER')))
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 0)
                self.assertIn(PENDING, r.flags)
                self.conclude(r)
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 1)

    def test_occupied_or_subject_estonia_does_not_hold_an_independent_vote(self):
        for blocked in ('occupied', 'subject'):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                self.poll(r)
                self.conclude(r, WINNERS[1])
                if blocked == 'occupied':
                    r.flags.add('TFR_EST_occupied')
                else:
                    r.props['is_subject'] = 'yes'
                before = self.seats(r)
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(self.election_count(r), 0)
                self.assertEqual(self.seats(r), before)
                self.assertIn(PENDING, r.flags)

    def test_caretaker_status_does_not_block_the_postwar_vote(self):
        r = self.runtime()
        self.poll(r)
        r.call('TFR_EST_enter_caretaker')
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertIn('TFR_EST_caretaker', r.flags)

    def test_all_seven_parties_can_win_the_same_postwar_election(self):
        for index, party in enumerate(PARTIES, 1):
            with self.subTest(party=party):
                r = self.runtime()
                self.poll(r, party)
                self.conclude(r)
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual(r.variables['TFR_EST_mandate_party'], index)
                self.assertEqual(r.variables['TFR_EST_seats_' + party], 101)
                self.assertIn(HELD, r.flags)

    def test_invalid_postwar_input_keeps_old_assembly_and_pending_retry(self):
        r = self.runtime()
        self.poll(r, invalid=True)
        self.conclude(r)
        before = self.seats(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.seats(r), before)
        self.assertEqual(self.election_count(r), 0)
        self.assertIn(PENDING, r.flags)
        self.assertNotIn(HELD, r.flags)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)
        self.poll(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertIn(HELD, r.flags)

    def test_a_stale_success_marker_cannot_consume_an_invalid_postwar_vote(self):
        r = self.runtime()
        self.poll(r, invalid=True)
        self.conclude(r)
        r.variables['TFR_EST_election_this_tick'] = Fraction(1)
        r.call('TFR_EST_war_elections_tick')
        self.assertIn(PENDING, r.flags)
        self.assertNotIn(HELD, r.flags)
        self.assertEqual(self.election_count(r), 0)

    def test_postwar_vote_uses_the_existing_minister_formation_discount(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.ideas.discard('TFR_EST_cabinet_formation')
        r.call('TFR_EST_war_elections_tick')
        self.assertIn('TFR_EST_cabinet_formation', r.ideas)

    def test_pending_context_remains_set_during_the_mandate_callback(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.effects['test_original_assign_mandate'] = r.effects['TFR_EST_assign_election_mandate']
        r.effects['TFR_EST_assign_election_mandate'] = parse('''
            if = { limit = { has_country_flag = TFR_EST_postwar_election_pending }
                set_country_flag = test_postwar_context_seen }
            test_original_assign_mandate = yes
        ''')
        r.call('TFR_EST_war_elections_tick')
        self.assertIn('test_postwar_context_seen', r.flags)
        self.assertNotIn(PENDING, r.flags)

    def test_postwar_vote_never_repeats_on_daily_or_weekly_updates(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        for _ in range(3):
            r.call('TFR_EST_parliament_tick')
            r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)

    def test_new_four_year_term_counts_from_the_postwar_vote(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        r.props['date'] = date(2031, 3, 5)
        r.variables['TFR_EST_postwar_term_days'] = Fraction(1459)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 2)
        self.assertEqual(r.variables['TFR_EST_postwar_term_days'], 0)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2035)

    def test_invalid_future_regular_ballot_remains_due(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        r.variables['TFR_EST_postwar_term_days'] = Fraction(1460)
        self.poll(r, invalid=True)
        before = self.seats(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertEqual(self.seats(r), before)
        self.assertEqual(r.variables['TFR_EST_postwar_term_days'], 1461)
        self.poll(r, 'isamaa')
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 2)
        self.assertEqual(r.variables['TFR_EST_seats_isamaa'], 101)

    def test_restoration_retains_84_days_and_absorbs_the_postwar_vote(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r, WINNERS[1])
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_war_elections_tick')
        r.call('TFR_EST_restore_parliament')
        for _ in range(11):
            r.call('TFR_EST_war_elections_tick')
            r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 0)
        self.assertIn(RESTORATION, r.flags)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertNotIn(RESTORATION, r.flags)
        self.assertIn(HELD, r.flags)
        r.call('TFR_EST_war_elections_tick')
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)

    def test_invalid_restoration_poll_does_not_consume_either_schedule(self):
        r = self.runtime()
        self.poll(r, invalid=True)
        self.conclude(r)
        r.call('TFR_EST_restore_parliament')
        r.variables['TFR_EST_restore_days'] = Fraction(77)
        r.call('TFR_EST_parliament_tick')
        self.assertIn(RESTORATION, r.flags)
        self.assertIn(PENDING, r.flags)
        self.assertNotIn(HELD, r.flags)
        self.assertEqual(self.election_count(r), 0)
        self.poll(r)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertNotIn(RESTORATION, r.flags)
        self.assertIn(HELD, r.flags)

    def test_pending_restoration_waits_for_the_actual_european_peace(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.call('TFR_EST_restore_parliament')
        r.flags.add(PENDING)
        r.variables['TFR_EST_restore_days'] = Fraction(77)
        r.props['world_wars'].add(frozenset(('SOV', 'GER')))
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 0)
        self.assertIn(RESTORATION, r.flags)
        self.conclude(r)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertIn(HELD, r.flags)

    def test_a_later_restoration_vote_resets_term_without_a_duplicate_postwar_vote(self):
        r = self.runtime()
        self.poll(r)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        r.variables['TFR_EST_postwar_term_days'] = Fraction(800)
        r.props['date'] = date(2030, 1, 1)
        r.call('TFR_EST_restore_parliament')
        r.variables['TFR_EST_restore_days'] = Fraction(77)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(self.election_count(r), 2)
        self.assertEqual(r.variables['TFR_EST_postwar_term_days'], 0)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2034)
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 2)
        self.assertNotIn(PENDING, r.flags)

    def test_restoration_replaces_2023_calendar_missed_under_occupation(self):
        for settled in (False, True):
            with self.subTest(settled=settled):
                r = self.runtime(after_2023=False)
                self.poll(r)
                r.props['date'] = date(2025, 1, 1)
                if settled:
                    self.conclude(r)
                r.call('TFR_EST_restore_parliament')
                r.variables['TFR_EST_restore_days'] = Fraction(77)
                r.call('TFR_EST_parliament_tick')
                r.call('TFR_EST_war_elections_tick')
                r.call('TFR_EST_parliament_tick')
                self.assertEqual(self.election_count(r), 1)
                self.assertEqual(HELD in r.flags, settled)
                self.assertEqual(r.variables['TFR_EST_election_year'], 2029 if settled else 2027)

    def test_regular_backlog_after_an_early_settlement_is_only_one_vote(self):
        r = self.runtime(after_2023=False)
        self.poll(r)
        r.props['date'] = date(2025, 1, 1)
        self.conclude(r)
        r.call('TFR_EST_parliament_tick')
        r.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(r), 1)
        self.assertIn(HELD, r.flags)

    def test_save_reload_preserves_pending_and_held_transition_guards(self):
        r = self.runtime()
        self.poll(r, invalid=True)
        self.conclude(r)
        r.call('TFR_EST_war_elections_tick')
        loaded = deepcopy(r)
        self.poll(loaded)
        loaded.call('TFR_EST_war_elections_tick')
        loaded_again = deepcopy(loaded)
        loaded_again.call('TFR_EST_war_elections_tick')
        self.assertEqual(self.election_count(loaded_again), 1)
        self.assertIn(HELD, loaded_again.flags)
        self.assertNotIn(PENDING, loaded_again.flags)

    def test_script_authorized_snap_vote_remains_a_separate_exception(self):
        r = self.runtime()
        self.poll(r)
        r.flags.add('TFR_EST_scripted_snap_election')
        r.call('TFR_EST_snap_election')
        self.assertEqual(self.election_count(r), 1)
        self.assertNotIn(HELD, r.flags)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)

    def test_regular_calendar_availability_matches_postwar_and_restoration_state(self):
        r = self.runtime()
        self.assertFalse(r.test('TFR_EST_regular_calendar_available', '=', 'yes'))
        self.conclude(r)
        self.poll(r)
        r.call('TFR_EST_war_elections_tick')
        self.assertTrue(r.test('TFR_EST_regular_calendar_available', '=', 'yes'))
        r.flags.add(RESTORATION)
        self.assertFalse(r.test('TFR_EST_regular_calendar_available', '=', 'yes'))

    def test_controller_does_not_initialize_other_tags_or_new_countries(self):
        for blocked in ('tag', 'initialized'):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                self.conclude(r)
                if blocked == 'tag':
                    r.props['tag'] = 'LAT'
                else:
                    r.flags.discard('TFR_EST_initialized')
                before = (r.variables.copy(), r.flags.copy())
                r.call('TFR_EST_war_elections_tick')
                self.assertEqual((r.variables, r.flags), before)

    def test_installed_parent_settlements_define_the_flags_used_by_controller(self):
        parent = Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/3350890356/common/scripted_effects/TFR_scripted_effects_SOV.txt')
        if not parent.exists():
            self.skipTest('Installed TFR baseline unavailable')
        tree = parse(parent.read_text(encoding='utf-8-sig'), str(parent))
        for effect, winner in zip(('SOV_russian_defeat', 'SOV_russian_victory'), WINNERS):
            block = tree.get(effect)
            flags = {e.value for _, e in block.walk() if e.key == 'set_global_flag'}
            self.assertIn(OVER, flags)
            self.assertIn(winner, flags)


if __name__ == '__main__':
    unittest.main()

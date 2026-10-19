"""Exercise the authored 2023 programme, election handoff and paid factories.

The fixture executes real script conditions and rewards. It does not emulate
the native focus-progress UI, active-focus cancellation or save serialization.
"""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction
from random import Random
import sys
import unittest

from script_runtime import ROOT, Runtime, parse

sys.path.insert(0, str(ROOT / 'tools'))
from build_reform_2023 import POLICIES, outputs


PREFIX = 'TFR_EST_reform_2023_'
ROOT_FOCUS = PREFIX + 'new_mandate'
FINAL_FOCUS = PREFIX + 'account_to_parliament'
ACTIVE = PREFIX + 'mandate'
ENDED = PREFIX + 'mandate_ended'
WON = 'TFR_EST_reform_won_2023_election'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')


def read_script(relative):
    return parse((ROOT / relative).read_text(encoding='utf-8-sig'))


class Reform2023Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.focuses = {f.get('id'): f for f in read_script(
            'common/national_focus/TFR_EST_reform_2023.txt').all('shared_focus')}
        cls.main = read_script('common/national_focus/TFR_EST_normal.txt').get('focus_tree')

    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        r.call('TFR_EST_initialize_parliament')
        return r

    def votes(self, r, values=(3900, 1500, 1600, 700, 900, 1400, 0)):
        for party, value in zip(PARTIES, values):
            r.variables['TFR_EST_active_' + party] = 1
            r.variables['TFR_EST_support_' + party] = value
        r.variables['TFR_EST_support_other'] = 10000 - sum(values)

    def runtime(self, confirmed=True, retained=False):
        r = self.fresh()
        r.flags.add('TFR_EST_opening_complete')
        if retained:
            r.flags.add('TFR_EST_ratas_retained')
        else:
            r.flags.update({'TFR_EST_ratas_resigned', 'TFR_EST_referendum_failed',
                            'TFR_EST_reform_centre_formed'})
        r.props['date'] = date(2023, 3, 5)
        self.votes(r)
        r.call('TFR_EST_hold_election')
        if confirmed:
            r.variables['TFR_EST_coalition_e200'] = 1
            r.variables['TFR_EST_coalition_sde'] = 1
            r.call('TFR_EST_recount_confidence')
            r.call('TFR_EST_confirm_cabinet')
        r.props['date'] = date(2023, 4, 17)
        return r

    def visible(self, r):
        return {name for name, f in self.focuses.items()
                if r.condition(f.get('allow_branch'))}

    def selectable(self, r, name):
        f = self.focuses[name]
        completed = r.props['completed_focuses']
        return (name not in completed and r.condition(f.get('allow_branch'))
                and r.condition(f.get('available'))
                and all(any(parent in completed for parent in b.all('focus'))
                        for b in f.all('prerequisite')))

    def complete(self, r, suffix):
        name = suffix if suffix.startswith(PREFIX) else PREFIX + suffix
        self.assertTrue(self.selectable(r, name), name)
        r.props['completed_focuses'].add(name)
        r.run(self.focuses[name].get('completion_reward'))

    def factories(self, r):
        return sum(s['buildings'].get('arms_factory', 0) for s in r.states.values())

    def path(self, r, *suffixes):
        for suffix in suffixes:
            self.complete(r, suffix)

    def test_thirty_two_compact_shared_focuses_are_imported(self):
        self.assertEqual(len(self.focuses), 32)
        self.assertEqual(len(POLICIES), 32)
        self.assertCountEqual([name for name in self.main.all('shared_focus')
                               if name.startswith(PREFIX)], self.focuses)
        positions = {(int(f.get('x')), int(f.get('y'))) for f in self.focuses.values()}
        self.assertEqual(len(positions), 32)
        self.assertLessEqual(max(x for x, _ in positions), 8)
        self.assertLessEqual(max(y for _, y in positions), 8)
        self.assertEqual({f.get('cost') for f in self.focuses.values()}, {'5'})

    def test_opening_2020_has_no_2023_programme(self):
        r = self.fresh()
        self.assertFalse(self.visible(r))
        self.assertFalse(any(self.selectable(r, name) for name in self.focuses))

    def test_valid_2023_plurality_reveals_programme_before_confirmation(self):
        r = self.runtime(confirmed=False)
        self.assertIn(WON, r.flags)
        self.assertIn(ACTIVE, r.flags)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 1)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(self.visible(r), set(self.focuses))
        self.assertFalse(any(self.selectable(r, name) for name in self.focuses))

    def test_confirmed_majority_starts_only_root_then_five_player_choices(self):
        r = self.runtime()
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)}, {ROOT_FOCUS})
        self.complete(r, 'new_mandate')
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)},
                         {PREFIX + suffix for suffix in ('defence_three_percent', 'industrial_park',
                          'estonian_education', 'real_time_economy', 'vat_twenty_two')})

    def test_fifty_one_actual_coalition_seats_cannot_be_replaced_by_supply_votes(self):
        r = self.runtime()
        r.variables.update(TFR_EST_seats_reform=40, TFR_EST_seats_e200=11,
                           TFR_EST_seats_sde=0, TFR_EST_coalition_sde=0)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 51)
        self.assertTrue(self.selectable(r, ROOT_FOCUS))
        r.variables.update(TFR_EST_seats_e200=10, TFR_EST_supply_centre=1)
        r.call('TFR_EST_recount_confidence')
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 50)
        self.assertFalse(self.selectable(r, ROOT_FOCUS))

    def test_caretaker_occupation_other_pm_and_ended_mandate_cannot_start_focuses(self):
        for case in ('caretaker', 'occupation', 'subject', 'other_pm', 'other_mandate', 'ended'):
            with self.subTest(case=case):
                r = self.runtime()
                if case in ('caretaker', 'occupation', 'ended'):
                    r.flags.add({'caretaker': 'TFR_EST_caretaker', 'occupation': 'TFR_EST_occupied',
                                 'ended': ENDED}[case])
                elif case == 'subject':
                    r.props['is_subject'] = 'yes'
                else:
                    r.variables['TFR_EST_pm_party' if case == 'other_pm' else 'TFR_EST_mandate_party'] = 2
                self.assertFalse(any(r.condition(f.get('available')) for f in self.focuses.values()))

    def test_non_reform_2023_plurality_and_non2023_votes_do_not_activate_programme(self):
        for election_date, winner in ((date(2023, 3, 5), 'centre'),
                                      (date(2023, 3, 4), 'reform'),
                                      (date(2024, 1, 1), 'reform')):
            with self.subTest(election_date=election_date, winner=winner):
                r = self.fresh()
                r.props['date'] = election_date
                self.votes(r, tuple(10000 if p == winner else 0 for p in PARTIES))
                r.call('TFR_EST_hold_election')
                self.assertNotIn(ACTIVE, r.flags)
                self.assertNotIn(WON, r.flags)
                self.assertFalse(self.visible(r))

    def test_invalid_election_does_not_reveal_or_end_programme(self):
        for already_active in (False, True):
            with self.subTest(already_active=already_active):
                r = self.runtime() if already_active else self.fresh()
                r.props['date'] = date(2023, 6, 1)
                seats = tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES)
                self.votes(r, (10001, 0, 0, 0, 0, 0, 0))
                r.call('TFR_EST_hold_election')
                self.assertEqual(tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES), seats)
                self.assertNotIn(ENDED, r.flags)
                self.assertEqual(ACTIVE in r.flags, already_active)

    def test_next_valid_vote_ends_mandate_even_same_party_and_same_year(self):
        for next_date in (date(2023, 11, 1), date(2025, 3, 5)):
            r = self.runtime()
            self.complete(r, 'new_mandate')
            r.props['date'] = next_date
            self.votes(r, (10000, 0, 0, 0, 0, 0, 0))
            r.call('TFR_EST_hold_election')
            with self.subTest(next_date=next_date):
                self.assertIn(ENDED, r.flags)
                self.assertIn(WON, r.flags)
                self.assertFalse(self.visible(r))
                self.assertIn('TFR_EST_done_reform_2023_new_mandate', r.flags)
                r.call('TFR_EST_confirm_cabinet')
                self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
                self.assertFalse(self.visible(r))

    def test_postwar_ballot_cannot_be_mistaken_for_2023_mandate(self):
        for marker in ('TFR_EST_postwar_election_pending', 'TFR_EST_postwar_election_held'):
            r = self.fresh()
            r.props['date'] = date(2023, 7, 1)
            r.flags.add(marker)
            self.votes(r, (10000, 0, 0, 0, 0, 0, 0))
            r.call('TFR_EST_hold_election')
            with self.subTest(marker=marker):
                self.assertNotIn(WON, r.flags)
                self.assertNotIn(ACTIVE, r.flags)
                self.assertFalse(self.visible(r))

    def test_all_paths_are_acyclic_35_days_and_finish_before2027(self):
        r = self.runtime()
        rng = Random(2023)
        for count in range(32):
            choices = sorted(name for name in self.focuses if self.selectable(r, name))
            self.assertTrue(choices, f'Programme stalls after {count} focuses')
            name = rng.choice(choices)
            self.complete(r, name)
            r.props['date'] += timedelta(days=35)
        self.assertIn(FINAL_FOCUS, r.props['completed_focuses'])
        self.assertEqual(r.props['date'], date(2023, 4, 17) + timedelta(days=1120))
        self.assertLess(r.props['date'], date(2027, 1, 1))
        self.assertIn(PREFIX + 'programme_finished', r.flags)
        self.assertEqual(self.factories(r), 2)
        self.assertGreater(r.variables['TFR_EST_military_army_defence_factor_var'], 0)
        self.assertGreater(r.variables['TFR_EST_economy_research_speed_factor_var'], 0)
        self.assertIn(('add_income_with_inflation', Fraction(25, 1000)), r.calls)
        self.assertIn(('add_income_with_inflation', Fraction(15, 1000)), r.calls)
        self.assertEqual(r.props['add_stability'], Fraction(3, 100))

    def test_early_factory_and_military_paths_do_not_require_civilian_programme(self):
        def ancestors(name):
            found = {name}
            for block in self.focuses[name].all('prerequisite'):
                for parent in block.all('focus'):
                    found |= ancestors(parent)
            return found
        expected_days = {'ammunition_line': 105, 'drone_workshops': 140,
                         'defence_three_percent': 70, 'territorial_twenty_thousand': 105,
                         'layered_air_defence': 140, 'baltic_defence_line': 175}
        for suffix, days in expected_days.items():
            with self.subTest(suffix=suffix):
                path = ancestors(PREFIX + suffix)
                self.assertEqual(len(path) * 35, days)
                self.assertNotIn(FINAL_FOCUS, path)
                self.assertFalse(any(name.startswith(PREFIX + 'vat_') or
                                     name.startswith(PREFIX + 'estonian_education') for name in path))

    def test_final_report_requires_every_other_policy_record(self):
        r = self.runtime()
        for name in self.focuses:
            if name != FINAL_FOCUS:
                r.flags.add('TFR_EST_done_reform_2023_' + name.removeprefix(PREFIX))
                r.props['completed_focuses'].add(name)
        self.assertTrue(self.selectable(r, FINAL_FOCUS))
        r.flags.discard('TFR_EST_done_reform_2023_teacher_agreement')
        r.props['completed_focuses'].discard(PREFIX + 'teacher_agreement')
        self.assertFalse(self.selectable(r, FINAL_FOCUS))

    def test_handover_and_early_war_keep_programme_available(self):
        r = self.runtime()
        self.path(r, 'new_mandate', 'industrial_park')
        records = r.props['completed_focuses'].copy()
        r.props['date'] = date(2024, 7, 23)
        r.dynamic.add('EU_member_dynamic')
        r.call('TFR_EST_complete_reform_handover')
        r.props['has_war'] = 'yes'
        r.flags.add('TFR_EST_first_war_seen')
        self.assertIn('TFR_EST_pm_reform_michal', r.ideas)
        self.assertEqual(r.props['completed_focuses'], records)
        self.assertEqual(self.visible(r), set(self.focuses))
        self.assertTrue(self.selectable(r, PREFIX + 'ammunition_line'))

    def test_two_funded_factories_are_granted_once_and_costs_not_repeated(self):
        r = self.runtime()
        self.path(r, 'new_mandate', 'industrial_park', 'ammunition_line', 'drone_workshops')
        self.assertEqual(self.factories(r), 2)
        self.assertEqual(r.states[13]['buildings']['arms_factory'], 1)
        self.assertEqual(r.states[191]['buildings']['arms_factory'], 1)
        calls = r.calls.copy()
        values = r.variables.copy()
        for _ in range(3):
            r.call('TFR_EST_reform_2023_tick')
            for suffix in ('ammunition_line', 'drone_workshops'):
                r.run(self.focuses[PREFIX + suffix].get('completion_reward'))
        self.assertEqual(self.factories(r), 2)
        self.assertEqual(r.calls, calls)
        self.assertEqual(r.variables, values)
        self.assertIn(('add_debt_with_inflation', Fraction(140, 1000)), calls)
        self.assertIn(('add_debt_with_inflation', Fraction(120, 1000)), calls)

    def test_full_states_keep_paid_projects_pending_until_slots_open(self):
        r = self.runtime()
        for state in r.states.values():
            state['slots'] = 0
        self.path(r, 'new_mandate', 'industrial_park', 'ammunition_line', 'drone_workshops')
        self.assertEqual(self.factories(r), 0)
        for project in ('ammunition', 'drones'):
            self.assertIn(PREFIX + project + '_factory_pending', r.flags)
            self.assertNotIn(PREFIX + project + '_factory_granted', r.flags)
        costs = [c for c in r.calls if c[0] == 'add_debt_with_inflation']
        r.states[1329]['slots'] = 1
        r.call('TFR_EST_reform_2023_tick')
        self.assertEqual(self.factories(r), 1)
        self.assertIn(PREFIX + 'drones_factory_pending', r.flags)
        r.states[1329]['slots'] = 2
        r.call('TFR_EST_reform_2023_tick')
        self.assertEqual(self.factories(r), 2)
        self.assertFalse(any(PREFIX + p + '_factory_pending' in r.flags for p in ('ammunition', 'drones')))
        self.assertEqual([c for c in r.calls if c[0] == 'add_debt_with_inflation'], costs)

    def test_factory_must_be_both_owned_and_controlled_by_estonia(self):
        for case in ('owned_only', 'controlled_only', 'all_foreign'):
            with self.subTest(case=case):
                r = self.runtime()
                for state in r.states.values():
                    state['owner'] = 'EST' if case == 'owned_only' else 'SOV'
                    state['controller'] = 'EST' if case == 'controlled_only' else 'SOV'
                self.path(r, 'new_mandate', 'industrial_park', 'ammunition_line')
                self.assertEqual(self.factories(r), 0)
                self.assertIn(PREFIX + 'ammunition_factory_pending', r.flags)
                r.states[840].update(owner='EST', controller='EST')
                r.call('TFR_EST_reform_2023_tick')
                self.assertEqual(self.factories(r), 1)
                self.assertEqual(r.states[840]['buildings']['arms_factory'], 1)

    def test_occupation_cannot_fulfil_pending_factory_entitlements(self):
        r = self.runtime()
        r.flags.update({PREFIX + 'ammunition_factory_pending', 'TFR_EST_occupied'})
        r.call('TFR_EST_reform_2023_tick')
        self.assertEqual(self.factories(r), 0)
        self.assertIn(PREFIX + 'ammunition_factory_pending', r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.call('TFR_EST_reform_2023_tick')
        self.assertEqual(self.factories(r), 1)

    def test_visible_shared_and_war_focuses_have_no_coordinate_collisions(self):
        all_shared = {}
        for path in (ROOT / 'common/national_focus').glob('TFR_EST_*.txt'):
            all_shared.update({f.get('id'): f for f in read_script(
                str(path.relative_to(ROOT))).all('shared_focus')})
        native = {f.get('id'): f for f in self.main.all('focus')}
        candidates = native | {name: all_shared[name] for name in self.main.all('shared_focus')}
        for retained in (False, True):
            r = self.runtime(retained=retained)
            r.flags.add('TFR_EST_first_war_seen')
            r.props['has_war'] = 'yes'
            positions = {}
            for name, f in candidates.items():
                if f.get('allow_branch') is not None and not r.condition(f.get('allow_branch')):
                    continue
                position = (int(f.get('x')), int(f.get('y')))
                with self.subTest(retained=retained, focus=name, position=position):
                    self.assertNotIn(position, positions, f'{name} overlaps {positions.get(position)}')
                positions[position] = name

    def test_reproducible_source_and_bom_localisation(self):
        for relative, content in outputs().items():
            encoding = 'utf-8-sig' if relative.endswith('.yml') else 'utf-8'
            self.assertEqual((ROOT / relative).read_bytes(), content.encode(encoding))

    def late_porto_election(self, winner='reform', valid=True):
        r = self.fresh()
        opening = read_script('common/national_focus/TFR_EST_opening.txt').all('shared_focus')
        r.props['completed_focuses'].update(f.get('id') for f in opening)
        r.flags.update('TFR_EST_done_opening_' + f.get('id').removeprefix('TFR_EST_opening_')
                       for f in opening)
        r.flags.update({'TFR_EST_porto_investigation_seen', 'TFR_EST_porto_choice_presented',
                        'TFR_EST_referendum_active', 'TFR_EST_porto_choice_pending'})
        r.props['date'] = date(2023, 3, 5)
        values = (4500, 2500, 2000, 1000, 0, 0, 0) if winner == 'reform' else (2500, 4500, 2000, 1000, 0, 0, 0)
        self.votes(r, values if valid else (10001, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        if valid:
            r.variables['TFR_EST_coalition_centre' if winner == 'reform' else 'TFR_EST_coalition_reform'] = 1
            r.call('TFR_EST_recount_confidence')
            r.call('TFR_EST_confirm_cabinet')
            self.assertNotIn('TFR_EST_caretaker', r.flags)
            self.assertEqual(r.variables['TFR_EST_coalition_seats'], 71)
        return r

    def political_snapshot(self, r):
        return deepcopy((r.variables, r.flags, r.ideas, r.props, r.calls, r.events,
                         r.characters, r.politics))

    def test_delayed_porto_options_cannot_replace_2023_elected_government(self):
        for winner in ('reform', 'centre'):
            for choice in ('TFR_EST_keep_ratas', 'TFR_EST_ratas_steps_back'):
                with self.subTest(winner=winner, choice=choice):
                    r = self.late_porto_election(winner)
                    self.assertIn('TFR_EST_opening_assembly_ended', r.flags)
                    before = self.political_snapshot(r)
                    r.call(choice)
                    self.assertEqual(self.political_snapshot(r), before)
                    self.assertEqual(r.variables['TFR_EST_pm_party'], 1 if winner == 'reform' else 2)
                    self.assertEqual(bool(self.visible(r)), winner == 'reform')

    def test_queued_old_cabinet_and_story_tick_cannot_overwrite_new_coalition(self):
        for winner in ('reform', 'centre'):
            with self.subTest(winner=winner):
                r = self.late_porto_election(winner)
                # Even an already displayed old cabinet event must be harmless;
                # its effect rechecks assembly identity independently of queue cleanup.
                r.flags.add('TFR_EST_reform_handover_pending')
                r.variables['TFR_EST_reform_handover_days'] = 0
                before = self.political_snapshot(r)
                r.call('TFR_EST_form_reform_centre_cabinet')
                r.call('TFR_EST_opening_tick')
                self.assertEqual(self.political_snapshot(r), before)
                events = read_script('events/TFR_EST_opening.txt').all('country_event')
                for e in events:
                    if e.get('id') in ('tfr_estonia_opening.10', 'tfr_estonia_opening.11', 'tfr_estonia_opening.12'):
                        self.assertFalse(r.condition(e.get('trigger')), e.get('id'))

    def test_retirement_preserves_enacted_policies_without_inventing_ratas_choice(self):
        r = self.late_porto_election()
        self.assertIn('TFR_EST_opening_complete', r.flags)
        self.assertNotIn('TFR_EST_referendum_active', r.flags)
        for marker in ('TFR_EST_ratas_retained', 'TFR_EST_ratas_resigned',
                       'TFR_EST_porto_choice_resolved', 'TFR_EST_referendum_failed'):
            self.assertNotIn(marker, r.flags)
        for f in read_script('common/national_focus/TFR_EST_opening.txt').all('shared_focus'):
            name = f.get('id')
            self.assertIn(name, r.props['completed_focuses'])
            self.assertIn('TFR_EST_done_opening_' + name.removeprefix('TFR_EST_opening_'), r.flags)
            self.assertFalse(r.condition(f.get('allow_branch')))
            self.assertFalse(r.condition(f.get('available')))
        before = self.political_snapshot(r)
        r.call('TFR_EST_fail_referendum')
        r.call('TFR_EST_begin_referendum')
        self.assertEqual(self.political_snapshot(r), before)

    def test_invalid_ballot_does_not_retire_opening_assembly(self):
        r = self.late_porto_election(valid=False)
        self.assertNotIn('TFR_EST_opening_assembly_ended', r.flags)
        self.assertNotIn('TFR_EST_opening_complete', r.flags)
        self.assertIn('TFR_EST_referendum_active', r.flags)
        r.call('TFR_EST_ratas_steps_back')
        self.assertIn('TFR_EST_ratas_resigned', r.flags)
        self.assertIn('TFR_EST_referendum_failed', r.flags)
        self.assertIn('TFR_EST_reform_handover_pending', r.flags)

    def test_late_native_focus_completion_cannot_award_retired_opening_rewards(self):
        r = self.late_porto_election()
        opening = read_script('common/national_focus/TFR_EST_opening.txt').all('shared_focus')
        # A completion callback arriving after the election cannot record an
        # unfinished policy or apply its cost/reward to the elected government.
        for f in opening:
            name = f.get('id')
            r.flags.discard('TFR_EST_done_opening_' + name.removeprefix('TFR_EST_opening_'))
            r.props['completed_focuses'].discard(name)
        before = self.political_snapshot(r)
        for f in opening:
            r.run(f.get('completion_reward'))
        self.assertEqual(self.political_snapshot(r), before)


if __name__ == '__main__':
    unittest.main()

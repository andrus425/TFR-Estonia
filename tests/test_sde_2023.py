"""Execute SDE's elected programme, guarded investments and shared energy slots.

These checks exercise authored scripts and structural layout. They do not claim
native focus-menu inspection, natural campaign balance or save serialization.
"""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction
import hashlib
from itertools import product
import json
from random import Random
import sys
import unittest

from script_runtime import ROOT, Runtime, parse

sys.path.insert(0, str(ROOT / 'tools'))
from build_sde_2023 import AI_ORDER, ENERGY_STAGES, POLICIES, outputs
from build_energy_crisis import (SDE_2023_PROJECTS, SDE_2023_SLOTS, IDEAS,
                                CENTRE_2023_SLOTS, EKRE_2023_SLOTS, REFORM_2023_SLOTS, ISAMAA_2023_SLOTS, SLOTS)


PREFIX = 'TFR_EST_sde_2023_'
ROOT_FOCUS = PREFIX + 'new_mandate'
FINAL_FOCUS = PREFIX + 'account_to_parliament'
ACTIVE = PREFIX + 'mandate'
ENDED = PREFIX + 'mandate_ended'
WON = 'TFR_EST_sde_won_2023_election'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
PROJECTS = ('ammunition', 'maintenance')


def read_script(relative):
    return parse((ROOT / relative).read_text(encoding='utf-8-sig'))


class SDE2023Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.focuses = {f.get('id'): f for f in read_script(
            'common/national_focus/TFR_EST_sde_2023.txt').all('shared_focus')}
        cls.main = read_script('common/national_focus/TFR_EST_normal.txt').get('focus_tree')

    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        r.call('TFR_EST_initialize_parliament')
        return r

    def votes(self, r, values=(2200, 1800, 1100, 500, 3900, 500, 0)):
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
        r.call('TFR_EST_sde_handover_tick')
        self.votes(r)
        r.call('TFR_EST_hold_election')
        if confirmed:
            r.variables['TFR_EST_coalition_ekre'] = 1
            r.variables['TFR_EST_coalition_centre'] = 1
            r.call('TFR_EST_recount_confidence')
            r.call('TFR_EST_confirm_cabinet')
        r.props['date'] = date(2023, 4, 17)
        return r

    def visible(self, r):
        return {name for name, focus in self.focuses.items()
                if r.condition(focus.get('allow_branch'))}

    def selectable(self, r, name):
        focus = self.focuses[name]
        return (name not in r.props['completed_focuses']
                and r.condition(focus.get('allow_branch'))
                and r.condition(focus.get('available'))
                and all(any(parent in r.props['completed_focuses'] for parent in b.all('focus'))
                        for b in focus.all('prerequisite')))

    def complete(self, r, suffix):
        name = suffix if suffix.startswith(PREFIX) else PREFIX + suffix
        self.assertTrue(self.selectable(r, name), name)
        r.props['completed_focuses'].add(name)
        r.run(self.focuses[name].get('completion_reward'))

    def path(self, r, *suffixes):
        for suffix in suffixes:
            self.complete(r, suffix)

    def factories(self, r):
        return sum(state['buildings'].get('arms_factory', 0) for state in r.states.values())

    def test_thirty_two_compact_shared_focuses_and_275_total_shared_imports(self):
        self.assertEqual(len(POLICIES), 32)
        self.assertEqual(len(self.focuses), 32)
        self.assertEqual(len(self.main.all('shared_focus')), 275)
        self.assertCountEqual([name for name in self.main.all('shared_focus')
                               if name.startswith(PREFIX)], self.focuses)
        positions = {(int(f.get('x')), int(f.get('y'))) for f in self.focuses.values()}
        self.assertEqual(len(positions), 32)
        self.assertLessEqual(max(x for x, _ in positions), 8)
        self.assertLessEqual(max(y for _, y in positions), 8)
        self.assertEqual({f.get('cost') for f in self.focuses.values()}, {'5'})
        self.assertFalse(any(f.get('mutually_exclusive') for f in self.focuses.values()))

    def test_2020_opening_has_no_elected_sde_programme(self):
        r = self.fresh()
        self.assertFalse(self.visible(r))
        self.assertNotIn(WON, r.flags)
        self.assertNotIn(ACTIVE, r.flags)
        self.assertFalse(any(self.selectable(r, name) for name in self.focuses))

    def test_valid_2023_sde_plurality_reveals_before_confirmation(self):
        for retained in (False, True):
            r = self.runtime(confirmed=False, retained=retained)
            with self.subTest(retained=retained):
                self.assertIn(WON, r.flags)
                self.assertIn(ACTIVE, r.flags)
                self.assertEqual(r.variables['TFR_EST_mandate_party'], 5)
                self.assertEqual(self.visible(r), set(self.focuses))
                self.assertIn('TFR_EST_caretaker', r.flags)
                self.assertFalse(any(self.selectable(r, name) for name in self.focuses))

    def test_confirmed_root_opens_five_parallel_policy_choices(self):
        r = self.runtime()
        self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)}, {ROOT_FOCUS})
        self.complete(r, 'new_mandate')
        choices = {name for name in self.focuses if self.selectable(r, name)}
        self.assertEqual(len(choices), 5)
        self.assertIn(PREFIX + 'defence_commitment', choices)
        self.assertIn(PREFIX + 'industrial_guarantees', choices)

    def test_confirmed_sde_mandate_uses_laanemets_as_prime_minister(self):
        r = self.runtime()
        self.assertIn('TFR_EST_pm_sde_laanemets', r.ideas)
        self.assertIn('TFR_EST_laanemets_leads_sde', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
        for flag in ('TFR_EST_pm_person_urmas_reinsalu',
                     'TFR_EST_pm_person_martin_helme',
                     'TFR_EST_pm_person_tanel_kiik',
                     'TFR_EST_pm_person_mihhail_kolvart'):
            self.assertNotIn(flag, r.flags)
        self.complete(r, 'new_mandate')
        self.assertIn('TFR_EST_pm_sde_laanemets', r.ideas)

    def test_each_policy_branch_retains_prerequisites_without_calendar_gates(self):
        positions = {(int(f.get('x')), int(f.get('y'))): name
                     for name, f in self.focuses.items()}
        self.assertEqual(positions[(4, 0)], ROOT_FOCUS)
        for x in (0, 2, 4, 6, 8):
            for y in range(1, 7):
                name = positions[(x, y)]
                focus = self.focuses[name]
                expected_parent = ROOT_FOCUS if y == 1 else positions[(x, y - 1)]
                with self.subTest(focus=name):
                    self.assertEqual([block.all('focus') for block in focus.all('prerequisite')],
                                     [[expected_parent]])
                    self.assertFalse(any(entry.key == 'date'
                                         for _, entry in focus.get('available').walk()))

    def test_actual_51_seat_coalition_cannot_use_supply_as_cabinet_seats(self):
        r = self.runtime()
        r.variables.update(TFR_EST_seats_sde=40, TFR_EST_seats_centre=11,
                           TFR_EST_seats_ekre=0, TFR_EST_coalition_ekre=0)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 51)
        self.assertTrue(self.selectable(r, ROOT_FOCUS))
        r.variables.update(TFR_EST_seats_centre=10, TFR_EST_seats_ekre=20,
                           TFR_EST_supply_ekre=1)
        r.call('TFR_EST_recount_confidence')
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 50)
        self.assertFalse(self.selectable(r, ROOT_FOCUS))

    def test_a_single_party_majority_does_not_require_old_coalition_partners(self):
        r = self.fresh()
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_sde_handover_tick')
        self.votes(r, (0, 0, 0, 0, 10000, 0, 0))
        r.call('TFR_EST_hold_election')
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 101)
        self.assertEqual(r.variables['TFR_EST_coalition_ekre'], 0)
        self.assertEqual(r.variables['TFR_EST_coalition_centre'], 0)
        self.assertTrue(self.selectable(r, ROOT_FOCUS))

    def test_governing_requires_current_independent_noncaretaker_sde_mandate(self):
        for case in ('caretaker', 'occupation', 'subject', 'other_pm', 'other_mandate', 'ended'):
            with self.subTest(case=case):
                r = self.runtime()
                if case in ('caretaker', 'occupation', 'ended'):
                    r.flags.add({'caretaker': 'TFR_EST_caretaker', 'occupation': 'TFR_EST_occupied',
                                 'ended': ENDED}[case])
                elif case == 'subject':
                    r.props['is_subject'] = 'yes'
                else:
                    r.variables['TFR_EST_pm_party' if case == 'other_pm' else 'TFR_EST_mandate_party'] = 1
                self.assertFalse(any(r.condition(f.get('available')) for f in self.focuses.values()))

    def test_wrong_party_or_wrong_year_never_grants_the_programme(self):
        cases = [(date(2023, 3, 5), party) for party in PARTIES if party != 'sde']
        cases += [(date(2023, 3, 4), 'sde'), (date(2024, 1, 1), 'sde')]
        for election_date, winner in cases:
            r = self.fresh()
            r.props['date'] = election_date
            self.votes(r, tuple(10000 if party == winner else 0 for party in PARTIES))
            r.call('TFR_EST_hold_election')
            with self.subTest(election_date=election_date, winner=winner):
                self.assertNotIn(WON, r.flags)
                self.assertNotIn(ACTIVE, r.flags)
                self.assertFalse(self.visible(r))

    def test_invalid_ballot_neither_reveals_nor_ends_the_sde_mandate(self):
        for active in (False, True):
            r = self.runtime() if active else self.fresh()
            r.props['date'] = date(2023, 6, 1)
            before = tuple(r.variables['TFR_EST_seats_' + party] for party in PARTIES)
            self.votes(r, (10001, 0, 0, 0, 0, 0, 0))
            r.call('TFR_EST_hold_election')
            with self.subTest(active=active):
                self.assertEqual(tuple(r.variables['TFR_EST_seats_' + party] for party in PARTIES), before)
                self.assertNotIn(ENDED, r.flags)
                self.assertEqual(ACTIVE in r.flags, active)

    def test_the_next_valid_election_ends_the_programme_even_after_an_sde_win(self):
        for next_date in (date(2023, 11, 1), date(2026, 7, 1)):
            r = self.runtime()
            self.complete(r, 'new_mandate')
            r.props['date'] = next_date
            self.votes(r, (0, 0, 0, 0, 10000, 0, 0))
            r.call('TFR_EST_hold_election')
            with self.subTest(next_date=next_date):
                self.assertIn(ENDED, r.flags)
                self.assertIn(WON, r.flags)
                self.assertIn('TFR_EST_done_sde_2023_new_mandate', r.flags)
                self.assertFalse(self.visible(r))
                r.call('TFR_EST_confirm_cabinet')
                self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
                self.assertFalse(self.visible(r))

    def test_postwar_ballots_in_2023_cannot_grant_an_ordinary_2023_mandate(self):
        for marker in ('TFR_EST_postwar_election_pending', 'TFR_EST_postwar_election_held'):
            r = self.fresh()
            r.props['date'] = date(2023, 7, 1)
            r.flags.add(marker)
            self.votes(r, (0, 0, 0, 0, 10000, 0, 0))
            r.call('TFR_EST_hold_election')
            with self.subTest(marker=marker):
                self.assertNotIn(WON, r.flags)
                self.assertNotIn(ACTIVE, r.flags)

    def test_complete_programme_takes_1120_days_and_finishes_before_2027(self):
        r = self.runtime()
        rng = Random(202303)
        for count in range(32):
            choices = sorted(name for name in self.focuses if self.selectable(r, name))
            self.assertTrue(choices, f'Programme stalls after {count} focuses')
            self.complete(r, rng.choice(choices))
            r.props['date'] += timedelta(days=35)
        self.assertIn(FINAL_FOCUS, r.props['completed_focuses'])
        self.assertEqual(r.props['date'], date(2026, 5, 11))
        self.assertLess(r.props['date'], date(2027, 1, 1))
        self.assertIn(PREFIX + 'programme_finished', r.flags)
        self.assertEqual(self.factories(r), 2)
        self.assertGreater(r.variables['TFR_EST_military_army_defence_factor_var'], 0)
        self.assertGreater(r.variables['TFR_EST_economy_industrial_capacity_factory_var'], 0)
        self.assertCountEqual([call[1] for call in r.calls if call[0] == 'add_income_with_inflation'],
                              [Fraction(55, 1000)])

    def test_important_defence_and_factories_are_early_without_final_report(self):
        def ancestors(name):
            found = {name}
            for block in self.focuses[name].all('prerequisite'):
                for parent in block.all('focus'):
                    found |= ancestors(parent)
            return found
        expected = {'defence_commitment': 70, 'air_defence': 105,
                    'reserve_muster': 140, 'ammunition_workshop': 105, 'maintenance_workshop': 140}
        for suffix, days in expected.items():
            parents = ancestors(PREFIX + suffix)
            with self.subTest(suffix=suffix):
                self.assertEqual(len(parents) * 35, days)
                self.assertNotIn(FINAL_FOCUS, parents)
                self.assertLessEqual(days, 140)

    def test_final_report_requires_every_other_completed_policy(self):
        r = self.runtime()
        for name in self.focuses:
            if name != FINAL_FOCUS:
                r.flags.add('TFR_EST_done_sde_2023_' + name.removeprefix(PREFIX))
                r.props['completed_focuses'].add(name)
        self.assertTrue(self.selectable(r, FINAL_FOCUS))
        for name in self.focuses:
            if name == FINAL_FOCUS:
                continue
            record = 'TFR_EST_done_sde_2023_' + name.removeprefix(PREFIX)
            r.flags.discard(record)
            r.props['completed_focuses'].discard(name)
            with self.subTest(missing=name):
                self.assertFalse(self.selectable(r, FINAL_FOCUS))
            r.flags.add(record)
            r.props['completed_focuses'].add(name)

    def test_early_war_does_not_hide_or_end_the_elected_programme(self):
        r = self.runtime()
        self.path(r, 'new_mandate', 'industrial_guarantees')
        records = r.props['completed_focuses'].copy()
        r.props['has_war'] = 'yes'
        r.global_flags.add('SOV_nato_war_begins_global')
        r.call('TFR_EST_reconcile_campaign')
        self.assertEqual(self.visible(r), set(self.focuses))
        self.assertTrue(self.selectable(r, PREFIX + 'ammunition_workshop'))
        self.assertEqual(r.props['completed_focuses'], records)
        self.assertNotIn(ENDED, r.flags)

    def test_all_focus_rewards_are_once_only_and_cannot_recharge_the_budget(self):
        r = self.runtime()
        for policy in POLICIES:
            self.complete(r, policy.suffix)
        before = deepcopy((r.variables, r.flags, r.calls, r.ideas, r.states, r.props))
        for focus in self.focuses.values():
            r.run(focus.get('completion_reward'))
        self.assertEqual((r.variables, r.flags, r.calls, r.ideas, r.states, r.props), before)

    def test_budget_helpers_show_and_apply_exact_costs_in_parent_ledger_units(self):
        for policy in POLICIES:
            if not policy.budget:
                continue
            with self.subTest(policy=policy.suffix):
                r = self.fresh()
                helper = PREFIX + 'reward_' + policy.suffix
                effect = r.effects[helper]
                cost_calls = [parents for parents, entry in effect.walk()
                              if entry.key == 'TFR_EST_spend_budget']
                self.assertEqual(len(cost_calls), 1)
                self.assertNotIn('hidden_effect', cost_calls[0])
                self.assertNotIn('effect_tooltip', cost_calls[0])
                r.call(helper)
                self.assertEqual([call[1] for call in r.calls
                                  if call[0] == 'add_debt_with_inflation'],
                                 [Fraction(str(policy.budget)) / 1000])

    def test_two_funded_factories_are_delivered_once_with_visible_debt_costs(self):
        r = self.runtime()
        self.path(r, 'new_mandate', 'industrial_guarantees', 'ammunition_workshop', 'maintenance_workshop')
        self.assertEqual(self.factories(r), 2)
        calls = r.calls.copy()
        self.assertTrue(any(call[0] == 'add_debt_with_inflation' and call[1] > 0 for call in calls))
        for _ in range(3):
            r.call(PREFIX + 'tick')
            for suffix in ('ammunition_workshop', 'maintenance_workshop'):
                r.run(self.focuses[PREFIX + suffix].get('completion_reward'))
        self.assertEqual(self.factories(r), 2)
        self.assertEqual(r.calls, calls)
        for project in PROJECTS:
            self.assertIn(PREFIX + project + '_factory_granted', r.flags)
            self.assertNotIn(PREFIX + project + '_factory_pending', r.flags)

    def test_full_building_slots_keep_both_funded_projects_pending(self):
        r = self.runtime()
        for state in r.states.values():
            state['slots'] = 0
        self.path(r, 'new_mandate', 'industrial_guarantees', 'ammunition_workshop', 'maintenance_workshop')
        self.assertEqual(self.factories(r), 0)
        self.assertTrue(all(PREFIX + project + '_factory_pending' in r.flags for project in PROJECTS))
        costs = [call for call in r.calls if call[0] == 'add_debt_with_inflation']
        r.states[1329]['slots'] = 1
        r.call(PREFIX + 'tick')
        self.assertEqual(self.factories(r), 1)
        self.assertIn(PREFIX + 'maintenance_factory_pending', r.flags)
        r.states[1329]['slots'] = 2
        r.call(PREFIX + 'tick')
        self.assertEqual(self.factories(r), 2)
        self.assertEqual([call for call in r.calls if call[0] == 'add_debt_with_inflation'], costs)

    def test_factory_requires_both_ownership_and_control_with_state_fallback(self):
        for case in ('owned_only', 'controlled_only', 'all_foreign'):
            r = self.runtime()
            for state in r.states.values():
                state['owner'] = 'EST' if case == 'owned_only' else 'SOV'
                state['controller'] = 'EST' if case == 'controlled_only' else 'SOV'
            self.path(r, 'new_mandate', 'industrial_guarantees', 'ammunition_workshop')
            with self.subTest(case=case):
                self.assertEqual(self.factories(r), 0)
                self.assertIn(PREFIX + 'ammunition_factory_pending', r.flags)
                r.states[840].update(owner='EST', controller='EST')
                r.call(PREFIX + 'tick')
                self.assertEqual(self.factories(r), 1)
                self.assertEqual(r.states[840]['buildings']['arms_factory'], 1)

    def test_occupation_suspends_pending_factory_delivery_without_erasing_it(self):
        r = self.runtime()
        r.flags.update({PREFIX + 'ammunition_factory_pending', 'TFR_EST_occupied'})
        r.call(PREFIX + 'tick')
        self.assertEqual(self.factories(r), 0)
        self.assertIn(PREFIX + 'ammunition_factory_pending', r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.call(PREFIX + 'tick')
        self.assertEqual(self.factories(r), 1)

    def test_restoration_ballot_alone_releases_pending_caretaker_confirmation(self):
        # The March vote nominated SDE while the outgoing Centre cabinet
        # still served. Occupation interrupted confirmation; restoration must
        # finish its own valid ballot before a new cabinet can take office.
        r = self.fresh()
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_sde_handover_tick')
        self.votes(r, (0, 4000, 0, 0, 6000, 0, 0))
        r.call('TFR_EST_hold_election')
        r.props['date'] = date(2023, 4, 17)
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_suspend_parliament')
        r.call('TFR_EST_restore_parliament')
        self.assertIn('TFR_EST_restoration_election', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertIn(ACTIVE, r.flags)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 5)
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_caretaker', r.flags)
        # The authored weekly parliament controller owns the 84-day schedule.
        for _ in range(11):
            r.props['date'] += timedelta(days=7)
            r.call('TFR_EST_parliament_tick')
            self.assertIn('TFR_EST_restoration_election', r.flags)
            self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertEqual(r.variables['TFR_EST_restore_days'], 77)
        assembly = tuple(r.variables['TFR_EST_seats_' + party] for party in PARTIES)
        self.votes(r, (10001, 0, 0, 0, 0, 0, 0))
        r.props['date'] += timedelta(days=7)
        r.call('TFR_EST_parliament_tick')
        self.assertEqual(r.variables['TFR_EST_restore_days'], 84)
        self.assertIn('TFR_EST_restoration_election', r.flags)
        self.assertEqual(tuple(r.variables['TFR_EST_seats_' + party] for party in PARTIES), assembly)
        self.assertNotIn(ENDED, r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.votes(r, (0, 0, 0, 0, 10000, 0, 0))
        r.props['date'] += timedelta(days=7)
        r.call('TFR_EST_parliament_tick')
        self.assertNotIn('TFR_EST_restoration_election', r.flags)
        self.assertEqual(r.variables['TFR_EST_seats_sde'], 101)
        self.assertIn(ENDED, r.flags)
        self.assertFalse(self.visible(r))
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
        self.assertIn('TFR_EST_pm_sde_laanemets', r.ideas)
        self.assertNotIn('TFR_EST_caretaker', r.flags)
        self.assertFalse(self.visible(r))

    def test_pending_projects_and_reforms_survive_state_reload_without_repayment(self):
        r = self.runtime()
        for state in r.states.values():
            state['slots'] = 0
        self.path(r, 'new_mandate', 'industrial_guarantees', 'ammunition_workshop')
        loaded = deepcopy(r)
        loaded.states[191]['slots'] = 1
        costs = [call for call in loaded.calls if call[0] == 'add_debt_with_inflation']
        loaded.call(PREFIX + 'tick')
        loaded_again = deepcopy(loaded)
        loaded_again.call(PREFIX + 'tick')
        self.assertEqual(self.factories(loaded_again), 1)
        self.assertEqual([call for call in loaded_again.calls if call[0] == 'add_debt_with_inflation'], costs)
        self.assertIn('TFR_EST_done_sde_2023_ammunition_workshop', loaded_again.flags)

    def test_energy_policies_match_exactly_five_shared_recovery_slots(self):
        self.assertEqual(SDE_2023_SLOTS,
                         ('renewable_contracts', 'renewable_contracts', 'grid_connection', 'renovation', 'renovation'))
        self.assertEqual(ENERGY_STAGES, {'renewable_contracts': 2, 'grid_connection': 1, 'renovation': 2})
        r = self.runtime()
        r.global_flags.add('SAU_saudi_civil_war_global')
        for suffix, stages in (('renewable_contracts', 2), ('grid_connection', 3), ('renovation', 5)):
            r.flags.add('TFR_EST_done_sde_2023_' + suffix)
            r.call('TFR_EST_reconcile_energy_crisis')
            with self.subTest(policy=suffix):
                self.assertEqual(r.variables['TFR_EST_energy_response_steps'], stages)
                self.assertEqual(r.ideas.intersection(IDEAS), {IDEAS[stages]} if stages < 5 else set())

    def test_each_of_eight_sde_energy_combinations_shares_slots_with_all_prior_routes(self):
        old_flags = [f'TFR_EST_done_ratas_{ratas}' for ratas, _ in SLOTS]
        old_flags += [f'TFR_EST_done_kallas_{kallas}' for _, kallas in SLOTS]
        old_flags += [f'TFR_EST_done_reform_2023_{reform}' for reform in REFORM_2023_SLOTS]
        old_flags += [f'TFR_EST_done_ekre_2023_{ekre}' for ekre in EKRE_2023_SLOTS]
        old_flags += [f'TFR_EST_done_centre_2023_{centre}' for centre in CENTRE_2023_SLOTS]
        old_flags += [f'TFR_EST_done_isamaa_2023_{isamaa}' for isamaa in ISAMAA_2023_SLOTS]
        old_flags = list(dict.fromkeys(old_flags))
        rng = Random(2023)
        prior_cases = [set(), set(old_flags)]
        prior_cases += [{flag} for flag in old_flags]
        prior_cases += [{flag for flag in old_flags if rng.choice((False, True))} for _ in range(20)]
        for enabled in product((False, True), repeat=len(SDE_2023_PROJECTS)):
            new_flags = {f'TFR_EST_done_sde_2023_{project}'
                         for project, active in zip(SDE_2023_PROJECTS, enabled) if active}
            for old in prior_cases:
                r = self.runtime()
                r.global_flags.add('SAU_saudi_civil_war_global')
                r.flags.update(new_flags | old)
                earned = r.flags
                expected = sum(any(flag in earned for flag in (
                    'TFR_EST_done_ratas_' + ratas, 'TFR_EST_done_kallas_' + kallas,
                    'TFR_EST_done_reform_2023_' + reform, 'TFR_EST_done_ekre_2023_' + ekre,
                    'TFR_EST_done_centre_2023_' + centre,
                    'TFR_EST_done_isamaa_2023_' + isamaa,
                    'TFR_EST_done_sde_2023_' + sde))
                    for (ratas, kallas), reform, ekre, centre, isamaa, sde in zip(
                        SLOTS, REFORM_2023_SLOTS, EKRE_2023_SLOTS, CENTRE_2023_SLOTS, ISAMAA_2023_SLOTS, SDE_2023_SLOTS))
                r.call('TFR_EST_reconcile_energy_crisis')
                with self.subTest(new=sorted(new_flags), old=sorted(old)):
                    self.assertEqual(r.variables['TFR_EST_energy_response_steps'], expected)
                    self.assertEqual(r.ideas.intersection(IDEAS), {IDEAS[expected]} if expected < 5 else set())

    def test_completed_preparations_prevent_crisis_and_never_regrant_the_spirit(self):
        r = self.runtime()
        r.flags.update('TFR_EST_done_sde_2023_' + project for project in SDE_2023_PROJECTS)
        r.call('TFR_EST_reconcile_energy_crisis')
        r.global_flags.add('SAU_saudi_civil_war_global')
        for _ in range(3):
            r.call('TFR_EST_reconcile_energy_crisis')
        self.assertFalse(r.ideas.intersection(IDEAS))
        self.assertEqual(r.variables['TFR_EST_energy_response_steps'], 5)
        self.assertEqual(r.events.count('tfr_estonia_ratas.1'), 1)

    def test_sde_ai_order_covers_every_focus_and_prioritizes_early_preparation(self):
        self.assertCountEqual(AI_ORDER, [policy.suffix for policy in POLICIES])
        self.assertEqual(AI_ORDER[0], 'new_mandate')
        self.assertEqual(AI_ORDER[-1], 'account_to_parliament')
        for suffix in ('defence_commitment', 'ammunition_workshop', 'maintenance_workshop'):
            self.assertLess(AI_ORDER.index(suffix), 6)
        plans = read_script('common/ai_strategy_plans/TFR_EST_governments.txt')
        order = [entry.key for entry in plans.get('TFR_EST_sde_ai_plan').get('ai_national_focuses').entries]
        for suffix in ('defence_commitment', 'ammunition_workshop', 'maintenance_workshop'):
            self.assertIn(PREFIX + suffix, order)
            self.assertLess(order.index(PREFIX + suffix), order.index(PREFIX + 'account_to_parliament'))

    def test_sde_programme_replaces_legacy_domestic_content_without_hiding_war(self):
        r = self.runtime()
        r.global_flags.add('SOV_nato_war_begins_global')
        r.props['has_war'] = 'yes'
        r.call('TFR_EST_reconcile_campaign')
        self.assertFalse(r.test('TFR_EST_show_legacy_domestic_tree', '=', 'yes'))
        self.assertEqual(self.visible(r), set(self.focuses))
        all_shared = {}
        for path in (ROOT / 'common/national_focus').glob('TFR_EST_*.txt'):
            all_shared.update({f.get('id'): f for f in read_script(str(path.relative_to(ROOT))).all('shared_focus')})
        candidates = {f.get('id'): f for f in self.main.all('focus')}
        candidates |= {name: all_shared[name] for name in self.main.all('shared_focus')}
        positions = {}
        for name, focus in candidates.items():
            if focus.get('allow_branch') is not None and not r.condition(focus.get('allow_branch')):
                continue
            position = (int(focus.get('x')), int(focus.get('y')))
            self.assertNotIn(position, positions, f'{name} overlaps {positions.get(position)}')
            positions[position] = name
        self.assertTrue(any(not name.startswith(PREFIX) for name in positions.values()))

    def test_sde_outputs_and_untouched_other_programmes_are_reproducible_with_bom_localisation(self):
        from build_reform_2023 import outputs as reform_outputs
        from build_ekre_2023 import outputs as ekre_outputs
        from build_centre_2023 import outputs as centre_outputs
        from build_isamaa_2023 import outputs as isamaa_outputs
        for relative, content in (outputs() | reform_outputs() | ekre_outputs() | centre_outputs() | isamaa_outputs()).items():
            encoding = 'utf-8-sig' if relative.endswith('.yml') else 'utf-8'
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), content.encode(encoding))

    def test_all_363_preexisting_focus_descriptions_remain_byte_for_byte_unchanged(self):
        from test_focus_presentation import localization_values
        fixture = ROOT / 'tests/fixtures/pre_sde_2023_focus_descriptions.json'
        expected = json.loads(fixture.read_text(encoding='utf-8'))['descriptions']
        self.assertEqual(len(expected), 363)
        existing = {}
        for path in (ROOT / 'common/national_focus').glob('TFR_EST_*.txt'):
            if path.name in ('TFR_EST_sde_2023.txt', 'TFR_EST_e200_2023.txt', 'TFR_EST_pp_2023.txt'):
                continue
            for _, entry in read_script(str(path.relative_to(ROOT))).walk():
                if entry.key in ('focus', 'shared_focus') and hasattr(entry.value, 'get'):
                    ident = entry.value.get('id')
                    if ident:
                        existing[ident + '_desc'] = True
        self.assertEqual(set(expected), set(existing))
        values = localization_values()
        for key, digest in expected.items():
            with self.subTest(key=key):
                self.assertIn(key, values)
                self.assertEqual(hashlib.sha256(values[key].encode('utf-8')).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()

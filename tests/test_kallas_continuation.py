"""Evaluate the successor cabinet's actual graph, mandate and policy rewards.

The fixture executes authored triggers/effects, with no emulation of HOI4's
focus-progress engine, UI, event scheduler or campaign save serializer.
"""
from datetime import date, timedelta
from fractions import Fraction
from random import Random
import unittest

from script_runtime import ROOT, Block, Runtime, parse


PREFIX = 'TFR_EST_kallas_'
ROOT_FOCUS = PREFIX + 'govern_together'
FINAL_FOCUS = PREFIX + 'account_to_voters'
ENDED = 'TFR_EST_kallas_mandate_ended'
VISIBLE = PREFIX + 'branch_visible'
GOVERNING = PREFIX + 'governing'
FAILED = 'TFR_EST_referendum_failed'
FORMED = 'TFR_EST_reform_centre_formed'
RESIGNED = 'TFR_EST_ratas_resigned'
REFERENDUM = 'TFR_EST_opening_marriage_referendum'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')


def read_script(relative):
    path = ROOT / relative
    return parse(path.read_text(encoding='utf-8-sig'), str(path))


def contains(block, key, value=None):
    return any(entry.key == key and (value is None or entry.value == value)
               for _, entry in block.walk())


class KallasContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = read_script('common/national_focus/TFR_EST_kallas.txt')
        cls.focuses = {focus.get('id'): focus for focus in cls.shared.all('shared_focus')}
        cls.main = read_script('common/national_focus/TFR_EST_normal.txt').get('focus_tree')
        cls.legacy = {focus.get('id'): focus for focus in cls.main.all('focus')}

    def runtime(self, confirmed=True):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        r.call('TFR_EST_initialize_parliament')
        r.flags.update({RESIGNED, FAILED, 'TFR_EST_opening_complete'})
        r.props['completed_focuses'].update('TFR_EST_opening_' + suffix for suffix in (
            'pension_reform', 'teacher_pay', 'covid_emergency', 'pension_increase',
            'wage_compensation', 'excise_relief', 'eastern_border', 'kose_voobu',
            'three_seas', 'research_budget'))
        if confirmed:
            r.flags.add('TFR_EST_scripted_cabinet_change')
            r.call('TFR_EST_nominate_reform')
            r.variables['TFR_EST_coalition_centre'] = Fraction(1)
            r.call('TFR_EST_recount_confidence')
            r.call('TFR_EST_confirm_cabinet')
            r.flags.add(FORMED)
        else:
            r.flags.add('TFR_EST_reform_handover_pending')
            r.call('TFR_EST_enter_caretaker')
        r.props['date'] = date(2021, 1, 26)
        return r

    def trigger(self, r, name):
        return r.test(name, '=', 'yes')

    def visible(self, r):
        return {name for name, focus in self.focuses.items()
                if r.condition(focus.get('allow_branch'))}

    def selectable(self, r, name):
        completed = r.props['completed_focuses']
        return (name not in completed
                and all(any(parent in completed for parent in block.all('focus'))
                        for block in self.focuses[name].all('prerequisite'))
                and r.condition(self.focuses[name].get('available')))

    def complete(self, r, name):
        self.assertTrue(self.selectable(r, name), name)
        r.props['completed_focuses'].add(name)
        r.run(self.focuses[name].get('completion_reward'))

    def votes(self, r, values):
        for party, value in zip(PARTIES, values):
            r.variables['TFR_EST_active_' + party] = Fraction(1)
            r.variables['TFR_EST_support_' + party] = Fraction(value)
        r.variables['TFR_EST_support_other'] = Fraction(10000 - sum(values))

    def material_state(self, r):
        return (r.variables.copy(), r.flags.copy(), r.ideas.copy(), r.dynamic.copy(),
                r.calls.copy(), r.events.copy(), r.props.get('political_power', Fraction(0)))

    def test_twenty_shared_focuses_are_imported_without_resetting_the_country_tree(self):
        self.assertEqual(len(self.focuses), 20)
        self.assertFalse(self.shared.all('focus_tree'))
        self.assertFalse(self.shared.all('focus'))
        self.assertEqual(self.main.get('id'), 'TFR_EST_main_tree')
        self.assertCountEqual([name for name in self.main.all('shared_focus')
                               if name.startswith(PREFIX)], self.focuses)

    def test_initial_and_retained_ratas_governments_cannot_see_this_programme(self):
        for retained in (False, True):
            r = self.runtime()
            r.flags.difference_update({RESIGNED, FAILED, FORMED})
            if retained:
                r.flags.add('TFR_EST_ratas_retained')
            with self.subTest(retained=retained):
                self.assertFalse(self.visible(r))
                self.assertFalse(self.trigger(r, GOVERNING))

    def test_resignation_reveals_programme_but_caretaker_cannot_begin_it(self):
        r = self.runtime(confirmed=False)
        self.assertEqual(self.visible(r), set(self.focuses))
        self.assertFalse(self.trigger(r, GOVERNING))
        self.assertFalse(any(self.selectable(r, name) for name in self.focuses))
        self.assertNotIn(REFERENDUM, r.props['completed_focuses'])
        self.assertFalse(self.focuses[ROOT_FOCUS].all('prerequisite'),
                         'A failed referendum cannot be a successor prerequisite')
        self.assertFalse(self.trigger(r, 'TFR_EST_show_legacy_domestic_tree'))

    def test_confirmed_reform_centre_cabinet_can_start_with_failed_referendum(self):
        r = self.runtime()
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 60)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
        self.assertNotIn(REFERENDUM, r.props['completed_focuses'])
        self.assertTrue(self.trigger(r, GOVERNING))
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)},
                         {ROOT_FOCUS})

    def test_governing_requires_confirmed_independent_original_successor_cabinet(self):
        for change in ('resigned', 'failed', 'formed', 'opening', 'caretaker',
                       'pm', 'mandate', 'occupied', 'subject', 'ended', 'foreign'):
            r = self.runtime()
            if change in ('resigned', 'failed', 'formed', 'opening'):
                r.flags.discard({'resigned': RESIGNED, 'failed': FAILED,
                                 'formed': FORMED, 'opening': 'TFR_EST_opening_complete'}[change])
            elif change in ('caretaker', 'occupied', 'ended'):
                r.flags.add({'caretaker': 'TFR_EST_caretaker', 'occupied': 'TFR_EST_occupied',
                             'ended': ENDED}[change])
            elif change in ('pm', 'mandate'):
                r.variables['TFR_EST_' + ('pm_party' if change == 'pm' else 'mandate_party')] = Fraction(2)
            elif change == 'subject':
                r.props['is_subject'] = 'yes'
            else:
                r.props['tag'] = 'LAT'
            with self.subTest(change=change):
                self.assertFalse(self.trigger(r, GOVERNING))
                for name, focus in self.focuses.items():
                    self.assertFalse(r.condition(focus.get('available')), name)

    def test_fifty_one_actual_partner_seats_are_required_without_supply_substitution(self):
        r = self.runtime()
        r.variables['TFR_EST_seats_centre'] = Fraction(17)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 51)
        self.assertTrue(self.trigger(r, GOVERNING))
        r.variables['TFR_EST_seats_centre'] = Fraction(16)
        r.variables['TFR_EST_supply_ekre'] = Fraction(1)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 50)
        self.assertGreaterEqual(r.variables['TFR_EST_confidence_seats'], 51)
        self.assertFalse(self.trigger(r, GOVERNING))

    def test_neither_original_partner_can_be_replaced_by_a_different_majority(self):
        for missing in ('reform', 'centre'):
            r = self.runtime()
            r.variables['TFR_EST_coalition_' + missing] = Fraction(0)
            r.variables['TFR_EST_coalition_ekre'] = Fraction(1)
            r.variables['TFR_EST_coalition_isamaa'] = Fraction(1)
            r.call('TFR_EST_recount_confidence')
            with self.subTest(missing=missing):
                self.assertGreaterEqual(r.variables['TFR_EST_coalition_seats'], 51)
                self.assertFalse(self.trigger(r, GOVERNING))

    def test_generic_domestic_content_waits_for_new_mandate_but_war_content_does_not(self):
        r = self.runtime()
        domestic = {name: focus for name, focus in self.legacy.items()
                    if contains(focus.get('allow_branch'), 'TFR_EST_show_legacy_domestic_tree', 'yes')}
        self.assertGreaterEqual(len(domestic), 100)
        for name, focus in domestic.items():
            with self.subTest(domestic=name):
                self.assertFalse(r.condition(focus.get('allow_branch')))
                self.assertFalse(r.condition(focus.get('available')))
        for name, flag in (('TFR_EST_first_emergency', 'TFR_EST_first_war_seen'),
                           ('TFR_EST_second_emergency', 'TFR_EST_second_war_seen'),
                           ('TFR_EST_restored_authority', 'TFR_EST_restoration_pending')):
            r.flags.add(flag)
            with self.subTest(emergency=name):
                self.assertTrue(r.condition(self.legacy[name].get('allow_branch')))
                self.assertTrue(r.condition(self.legacy[name].get('available')))
                self.assertTrue(all(any(parent in r.props['completed_focuses']
                                        for parent in block.all('focus'))
                                    for block in self.legacy[name].all('prerequisite')),
                                'A failed referendum must not block emergency roots')

    def test_valid_election_ends_programme_even_when_reform_wins_again(self):
        for winner in ('reform', 'centre', 'ekre'):
            r = self.runtime()
            r.flags.add('TFR_EST_done_kallas_govern_together')
            self.votes(r, tuple(10000 if party == winner else 0 for party in PARTIES))
            r.call('TFR_EST_hold_election')
            with self.subTest(winner=winner):
                self.assertEqual(sum(r.variables['TFR_EST_seats_' + p] for p in PARTIES), 101)
                self.assertIn(ENDED, r.flags)
                self.assertIn(RESIGNED, r.flags)
                self.assertIn(FAILED, r.flags)
                self.assertIn(FORMED, r.flags)
                self.assertIn('TFR_EST_done_kallas_govern_together', r.flags)
                self.assertFalse(self.visible(r))
                self.assertTrue(self.trigger(r, 'TFR_EST_show_legacy_domestic_tree'))
                r.call('TFR_EST_confirm_cabinet')
                self.assertFalse(self.visible(r))
                self.assertNotIn('TFR_EST_caretaker', r.flags)
                new_cabinet = self.legacy['TFR_EST_' + winner + '_cabinet']
                self.assertTrue(r.condition(new_cabinet.get('allow_branch')))
                self.assertTrue(r.condition(new_cabinet.get('available')))
                self.assertTrue(all(any(parent in r.props['completed_focuses']
                                        for parent in block.all('focus'))
                                    for block in new_cabinet.all('prerequisite')),
                                'The new mandate must remain reachable without a successful referendum')

    def test_invalid_election_preserves_current_programme_and_assembly(self):
        for values in ((10001, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0)):
            r = self.runtime()
            seats = tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES)
            self.votes(r, values)
            r.call('TFR_EST_hold_election')
            with self.subTest(values=values):
                self.assertIn('TFR_EST_election_invalid', r.flags)
                self.assertNotIn(ENDED, r.flags)
                self.assertEqual(tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES), seats)
                self.assertTrue(self.trigger(r, GOVERNING))

    def test_regular_calendar_ends_successor_programme_on_five_march_2023(self):
        r = self.runtime()
        self.votes(r, (10000, 0, 0, 0, 0, 0, 0))
        r.props['date'] = date(2023, 3, 4)
        r.call('TFR_EST_parliament_tick')
        self.assertNotIn(ENDED, r.flags)
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_parliament_tick')
        self.assertIn(ENDED, r.flags)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)

    def test_election_during_caretaker_handover_cancels_stale_successor_callback(self):
        r = self.runtime(confirmed=False)
        self.votes(r, (0, 0, 10000, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertIn(ENDED, r.flags)
        self.assertNotIn('TFR_EST_reform_handover_pending', r.flags)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 3)
        before = (r.variables.copy(), r.flags.copy())
        r.call('TFR_EST_form_reform_centre_cabinet')
        self.assertEqual((r.variables, r.flags), before)

    def test_elections_without_resignation_history_do_not_create_a_kallas_mandate(self):
        r = self.runtime()
        r.flags.difference_update({RESIGNED, FAILED, FORMED})
        self.votes(r, (10000, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertNotIn(ENDED, r.flags)
        self.assertFalse(self.visible(r))

    def test_caretaker_and_occupation_pause_without_destroying_enacted_policies(self):
        r = self.runtime()
        self.complete(r, ROOT_FOCUS)
        r.call('TFR_EST_enter_caretaker')
        self.assertFalse(self.trigger(r, GOVERNING))
        self.assertNotIn(ENDED, r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertTrue(self.trigger(r, GOVERNING))
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_suspend_parliament')
        self.assertFalse(self.visible(r))
        self.assertIn('TFR_EST_done_kallas_govern_together', r.flags)
        self.assertNotIn(ENDED, r.flags)
        r.flags.discard('TFR_EST_occupied')
        self.assertTrue(self.trigger(r, GOVERNING))

    def test_restored_failed_referendum_route_uses_persistent_phase_when_native_history_is_lost(self):
        r = self.runtime()
        # A tree handoff can drop native completed IDs while our earned policy
        # markers survive. Hidden opening nodes cannot be relied on to bypass.
        r.flags.update('TFR_EST_done_opening_' + name.removeprefix('TFR_EST_opening_')
                       for name in r.props['completed_focuses'])
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_suspend_parliament')
        r.props['completed_focuses'].clear()
        r.flags.discard('TFR_EST_occupied')
        r.flags.update({'TFR_EST_first_war_seen', 'TFR_EST_restoration_pending'})

        def reachable(focus):
            return (r.condition(focus.get('allow_branch'))
                    and r.condition(focus.get('available'))
                    and all(any(parent in r.props['completed_focuses']
                                for parent in block.all('focus'))
                            for block in focus.all('prerequisite')))

        for name in ('TFR_EST_first_emergency', 'TFR_EST_restored_authority'):
            with self.subTest(restored_root=name):
                self.assertTrue(reachable(self.legacy[name]))
        self.votes(r, (10000, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(ENDED, r.flags)
        self.assertTrue(reachable(self.legacy['TFR_EST_reform_cabinet']))
        self.assertFalse(r.props['completed_focuses'])
        self.assertIn('TFR_EST_done_opening_kose_voobu', r.flags)
        self.assertIn(FAILED, r.flags)
        opening = read_script('common/national_focus/TFR_EST_opening.txt')
        self.assertTrue(all(not r.condition(focus.get('allow_branch'))
                            for focus in opening.all('shared_focus')))

    def test_graph_has_a_single_entry_parallel_choices_and_a_common_conclusion(self):
        roots = {name for name, focus in self.focuses.items() if not focus.all('prerequisite')}
        self.assertEqual(roots, {ROOT_FOCUS})
        r = self.runtime()
        r.ideas.add('higher_covid_cases')
        self.complete(r, ROOT_FOCUS)
        choices = {name for name in self.focuses if self.selectable(r, name)}
        self.assertGreaterEqual(len(choices), 4)
        self.assertNotIn(FINAL_FOCUS, choices)
        ancestors = set()

        def visit(name):
            for block in self.focuses[name].all('prerequisite'):
                self.assertEqual(len(block.all('focus')), 1,
                                 'These terminal prerequisites are all required')
                for parent in block.all('focus'):
                    self.assertIn(parent, self.focuses,
                                  'No successful referendum may be required')
                    if parent not in ancestors:
                        ancestors.add(parent)
                        visit(parent)

        visit(FINAL_FOCUS)
        self.assertEqual(ancestors, set(self.focuses).difference({FINAL_FOCUS}))

    def test_every_focus_takes_thirty_five_days_without_fixed_start_dates(self):
        for name, focus in self.focuses.items():
            with self.subTest(focus=name):
                self.assertEqual(Fraction(focus.get('cost')) * 7, 35)
                self.assertFalse(contains(focus, 'date'))
                self.assertFalse(focus.all('mutually_exclusive'))

    def test_conclusion_checks_all_nineteen_policy_records_in_every_representation(self):
        names = set(self.focuses).difference({FINAL_FOCUS})
        for representation in ('native', 'persistent', 'mixed'):
            r = self.runtime()
            r.ideas.add('higher_covid_cases')
            records = {}
            for index, name in enumerate(sorted(names)):
                done = 'TFR_EST_done_kallas_' + name.removeprefix(PREFIX)
                store, record = ((r.props['completed_focuses'], name)
                                 if representation == 'native' or (representation == 'mixed' and index % 2)
                                 else (r.flags, done))
                store.add(record)
                records[name] = (store, record)
            available = self.focuses[FINAL_FOCUS].get('available')
            self.assertTrue(r.condition(available))
            for name, (store, record) in records.items():
                with self.subTest(representation=representation, missing=name):
                    store.discard(record)
                    self.assertFalse(r.condition(available))
                    store.add(record)

    def test_different_branch_orders_finish_before_the_regular_election(self):
        orders = set()
        for seed in range(6):
            r = self.runtime()
            r.ideas.add('higher_covid_cases')
            order = []
            rng = Random(seed)
            while len(order) < len(self.focuses):
                choices = sorted(name for name in self.focuses if self.selectable(r, name))
                self.assertTrue(choices, 'The graph must not stall before the election')
                name = rng.choice(choices)
                self.complete(r, name)
                r.props['date'] += timedelta(days=int(Fraction(self.focuses[name].get('cost')) * 7))
                order.append(name)
            self.assertEqual(order[0], ROOT_FOCUS)
            self.assertEqual(order[-1], FINAL_FOCUS)
            self.assertEqual(r.props['date'], date(2022, 12, 27))
            self.assertEqual((date(2023, 3, 5) - r.props['date']).days, 68)
            self.assertIn('TFR_EST_kallas_programme_finished', r.flags)
            self.assertNotIn(ENDED, r.flags)
            orders.add(tuple(order))
        self.assertGreater(len(orders), 1)

    def test_completion_rewards_are_repeat_safe_after_restoring_persisted_state(self):
        for name, focus in self.focuses.items():
            r = self.runtime()
            r.ideas.add('higher_covid_cases')
            reward = focus.get('completion_reward')
            r.run(reward)
            expected = self.material_state(r)
            with self.subTest(focus=name):
                self.assertTrue(r.condition(focus.get('bypass')))
                r.run(reward)
                self.assertEqual(self.material_state(r), expected)
                loaded = self.runtime()
                loaded.variables = r.variables.copy()
                loaded.flags = r.flags.copy()
                loaded.ideas = r.ideas.copy()
                loaded.dynamic = r.dynamic.copy()
                loaded.props['political_power'] = r.props.get('political_power', Fraction(0))
                before = self.material_state(loaded)
                loaded.run(reward)
                self.assertEqual(self.material_state(loaded), before)

    def test_rewards_use_existing_country_modifiers_instead_of_new_national_spirits(self):
        r = self.runtime()
        for name, focus in self.focuses.items():
            helper = PREFIX + 'reward_' + name.removeprefix(PREFIX)
            with self.subTest(focus=name):
                self.assertTrue(contains(focus.get('completion_reward'), helper, 'yes'))
                self.assertFalse(contains(focus.get('completion_reward'), 'add_ideas'))
                self.assertTrue(contains(r.effects[helper], 'TFR_EST_initialize_country_modifiers', 'yes'))
                self.assertTrue(contains(r.effects[helper], 'TFR_EST_refresh_country_modifiers', 'yes'))
                self.assertFalse(contains(r.effects[helper], 'add_ideas'))


if __name__ == '__main__':
    unittest.main()

"""Evaluate the renewed coalition's graph, mandate and persistent rewards.

These checks execute the authored triggers and effects. They do not emulate
HOI4's focus UI, focus-progress scheduler or campaign save serialization.
"""
from datetime import date, timedelta
from fractions import Fraction
from random import Random
import unittest

from script_runtime import ROOT, Block, Runtime, parse


PREFIX = 'TFR_EST_ratas_'
RETAINED = 'TFR_EST_ratas_retained'
ENDED = 'TFR_EST_ratas_mandate_ended'
VISIBLE = 'TFR_EST_ratas_branch_visible'
GOVERNING = 'TFR_EST_ratas_governing'
LEGACY = 'TFR_EST_show_legacy_domestic_tree'
ROOT_FOCUS = PREFIX + 'renew_agreement'
FINAL_FOCUS = PREFIX + 'account_to_voters'
REFERENDUM = 'TFR_EST_opening_marriage_referendum'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
BRANCH_STARTS = frozenset(PREFIX + suffix for suffix in (
    'family_home_guarantees', 'state_jobs_counties', 'hospital_covid',
    'lng_connection', 'police_reserve',
))


def read_script(relative):
    path = ROOT / relative
    return parse(path.read_text(encoding='utf-8-sig'), str(path))


def contains(block, key, value=None):
    return any(entry.key == key and (value is None or entry.value == value)
               for _, entry in block.walk())


class RatasContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = read_script('common/national_focus/TFR_EST_ratas.txt')
        cls.focuses = {focus.get('id'): focus for focus in cls.shared.all('shared_focus')}
        cls.main = read_script('common/national_focus/TFR_EST_normal.txt').get('focus_tree')
        cls.legacy = {focus.get('id'): focus for focus in cls.main.all('focus')}

    def runtime(self, retained=True, opening_complete=True):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        r.call('TFR_EST_initialize_parliament')
        if retained:
            r.flags.add(RETAINED)
        if opening_complete:
            r.flags.add('TFR_EST_opening_complete')
            r.props['completed_focuses'].add(REFERENDUM)
        r.props['date'] = date(2021, 1, 28)
        return r

    def trigger(self, r, name):
        return r.test(name, '=', 'yes')

    def branch_visibility(self, r):
        return {name for name, focus in self.focuses.items()
                if r.condition(focus.get('allow_branch'))}

    def legacy_visibility(self, r):
        return {name for name, focus in self.legacy.items()
                if r.condition(focus.get('allow_branch'))}

    def prerequisites_complete(self, r, name):
        completed = r.props['completed_focuses']
        # Separate prerequisite blocks are ANDed; entries within one block
        # are alternatives. This matches HOI4's graph semantics.
        return all(any(parent in completed for parent in block.all('focus'))
                   for block in self.focuses[name].all('prerequisite'))

    def selectable(self, r, name):
        return (name not in r.props['completed_focuses']
                and self.prerequisites_complete(r, name)
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
                list(r.calls), list(r.events), r.props.get('political_power', Fraction(0)))

    def test_twenty_shared_focuses_are_imported_into_the_same_persistent_tree(self):
        self.assertEqual(len(self.focuses), 20)
        self.assertFalse(self.shared.all('focus_tree'))
        self.assertFalse(self.shared.all('focus'))
        self.assertEqual(self.main.get('id'), 'TFR_EST_main_tree')
        self.assertCountEqual([name for name in self.main.all('shared_focus')
                               if name.startswith(PREFIX)], self.focuses)

    def test_initial_and_resignation_paths_do_not_expose_the_continuation(self):
        for opening_complete in (False, True):
            r = self.runtime(retained=False, opening_complete=opening_complete)
            with self.subTest(opening_complete=opening_complete):
                self.assertEqual(self.branch_visibility(r), set())
                r.flags.add('TFR_EST_ratas_resigned')
                self.assertEqual(self.branch_visibility(r), set())

    def test_retaining_ratas_reveals_the_tree_before_referendum_completion(self):
        r = self.runtime(opening_complete=False)
        self.assertEqual(self.branch_visibility(r), set(self.focuses))
        self.assertFalse(self.selectable(r, ROOT_FOCUS))
        self.assertEqual(self.focuses[ROOT_FOCUS].get('prerequisite').all('focus'),
                         [REFERENDUM])
        r.flags.add('TFR_EST_opening_complete')
        r.props['completed_focuses'].add(REFERENDUM)
        self.assertTrue(self.selectable(r, ROOT_FOCUS))

    def test_occupation_and_foreign_scope_hide_the_continuation(self):
        for change in ('occupied', 'foreign'):
            r = self.runtime()
            if change == 'occupied':
                r.flags.add('TFR_EST_occupied')
            else:
                r.props['tag'] = 'LAT'
            with self.subTest(change=change):
                self.assertEqual(self.branch_visibility(r), set())
                self.assertFalse(self.trigger(r, GOVERNING))

    def test_governing_requires_the_original_leader_and_confirmed_cabinet(self):
        for change in ('caretaker', 'pm', 'mandate', 'subject', 'opening', 'retained', 'ended'):
            r = self.runtime()
            self.assertTrue(self.trigger(r, GOVERNING))
            if change == 'caretaker': r.flags.add('TFR_EST_caretaker')
            elif change == 'pm': r.variables['TFR_EST_pm_party'] = Fraction(1)
            elif change == 'mandate': r.variables['TFR_EST_mandate_party'] = Fraction(1)
            elif change == 'subject': r.props['is_subject'] = 'yes'
            elif change == 'opening': r.flags.discard('TFR_EST_opening_complete')
            elif change == 'retained': r.flags.discard(RETAINED)
            elif change == 'ended': r.flags.add(ENDED)
            with self.subTest(change=change):
                self.assertFalse(self.trigger(r, GOVERNING))
                for name, focus in self.focuses.items():
                    self.assertFalse(r.condition(focus.get('available')), name)

    def test_governing_uses_fifty_one_actual_coalition_seats(self):
        r = self.runtime()
        r.variables['TFR_EST_seats_isamaa'] = Fraction(6)
        r.variables['TFR_EST_seats_reform'] = Fraction(40)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 51)
        self.assertTrue(self.trigger(r, GOVERNING))
        r.variables['TFR_EST_seats_isamaa'] = Fraction(5)
        r.variables['TFR_EST_seats_reform'] = Fraction(41)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 50)
        self.assertFalse(self.trigger(r, GOVERNING))

    def test_supply_votes_do_not_replace_a_coalition_partner(self):
        r = self.runtime()
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.variables['TFR_EST_supply_ekre'] = Fraction(1)
        r.call('TFR_EST_recount_confidence')
        self.assertEqual(r.variables['TFR_EST_confidence_seats'], 57)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 38)
        self.assertFalse(self.trigger(r, GOVERNING))
        # A majority assembled from other partners also cannot impersonate
        # the specific Centre-Isamaa-EKRE programme.
        r.variables['TFR_EST_coalition_reform'] = Fraction(1)
        r.call('TFR_EST_recount_confidence')
        self.assertGreaterEqual(r.variables['TFR_EST_coalition_seats'], 51)
        self.assertFalse(self.trigger(r, GOVERNING))

    def test_every_original_partner_is_required_even_with_a_replacement_majority(self):
        for party in ('centre', 'ekre', 'isamaa'):
            r = self.runtime()
            r.variables['TFR_EST_coalition_' + party] = Fraction(0)
            r.variables['TFR_EST_coalition_reform'] = Fraction(1)
            r.call('TFR_EST_recount_confidence')
            with self.subTest(missing=party):
                self.assertGreaterEqual(r.variables['TFR_EST_coalition_seats'], 51)
                self.assertFalse(self.trigger(r, GOVERNING))

    def test_legacy_domestic_content_is_hidden_and_unavailable_during_this_mandate(self):
        r = self.runtime()
        self.assertFalse(self.trigger(r, LEGACY))
        domestic = {name: focus for name, focus in self.legacy.items()
                    if contains(focus.get('allow_branch'), LEGACY, 'yes')}
        self.assertGreaterEqual(len(domestic), 100)
        for name, focus in domestic.items():
            with self.subTest(focus=name):
                self.assertFalse(r.condition(focus.get('allow_branch')))
                self.assertFalse(r.condition(focus.get('available')))
        r.flags.add(ENDED)
        self.assertTrue(self.trigger(r, LEGACY))
        self.assertIn('TFR_EST_centre_cabinet', self.legacy_visibility(r))
        self.assertIn('TFR_EST_energy_audit', self.legacy_visibility(r))
        self.assertIn('TFR_EST_reserve_register', self.legacy_visibility(r))

    def test_war_and_restoration_content_remain_accessible_during_the_continuation(self):
        for name, flag in (
            ('TFR_EST_first_emergency', 'TFR_EST_first_war_seen'),
            ('TFR_EST_second_emergency', 'TFR_EST_second_war_seen'),
            ('TFR_EST_restored_authority', 'TFR_EST_restoration_pending'),
        ):
            r = self.runtime()
            r.flags.add(flag)
            focus = self.legacy[name]
            with self.subTest(focus=name):
                self.assertTrue(r.condition(focus.get('allow_branch')))
                self.assertTrue(r.condition(focus.get('available')))
        for name, stage in (('TFR_EST_reconstruction_audit', 2),
                            ('TFR_EST_second_settlement', 4)):
            r = self.runtime()
            r.variables['TFR_EST_campaign_stage'] = Fraction(stage)
            focus = self.legacy[name]
            with self.subTest(focus=name):
                self.assertTrue(r.condition(focus.get('allow_branch')))
                self.assertTrue(r.condition(focus.get('available')))

    def test_valid_election_ends_old_mandate_even_when_centre_wins_again(self):
        for winner in ('reform', 'centre', 'ekre'):
            r = self.runtime()
            r.flags.add('TFR_EST_done_ratas_child_tax_allowance')
            self.votes(r, tuple(10000 if party == winner else 0 for party in PARTIES))
            r.call('TFR_EST_hold_election')
            with self.subTest(winner=winner):
                self.assertEqual(sum(r.variables['TFR_EST_seats_' + p] for p in PARTIES), 101)
                self.assertIn(ENDED, r.flags)
                self.assertIn(RETAINED, r.flags)
                self.assertIn('TFR_EST_done_ratas_child_tax_allowance', r.flags)
                self.assertEqual(self.branch_visibility(r), set())
                self.assertFalse(self.trigger(r, GOVERNING))
                self.assertTrue(self.trigger(r, LEGACY))
                r.call('TFR_EST_confirm_cabinet')
                self.assertNotIn('TFR_EST_caretaker', r.flags)
                self.assertIn('TFR_EST_' + winner + '_cabinet', self.legacy_visibility(r))
                self.assertEqual(self.branch_visibility(r), set())

    def test_invalid_election_preserves_the_incumbent_continuation(self):
        for votes in ((10001, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0)):
            r = self.runtime()
            before = tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES)
            self.votes(r, votes)
            r.call('TFR_EST_hold_election')
            with self.subTest(votes=votes):
                self.assertIn('TFR_EST_election_invalid', r.flags)
                self.assertNotIn(ENDED, r.flags)
                self.assertEqual(tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES), before)
                self.assertTrue(self.trigger(r, GOVERNING))
                self.assertEqual(self.branch_visibility(r), set(self.focuses))

    def test_election_does_not_create_a_retained_ratas_history_on_the_resignation_path(self):
        r = self.runtime(retained=False)
        r.flags.add('TFR_EST_ratas_resigned')
        self.votes(r, (0, 10000, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertNotIn(ENDED, r.flags)
        self.assertNotIn(RETAINED, r.flags)
        self.assertTrue(self.trigger(r, LEGACY))
        self.assertEqual(self.branch_visibility(r), set())

    def test_regular_march_2023_calendar_ends_the_continuation_through_an_election(self):
        r = self.runtime()
        self.votes(r, (0, 10000, 0, 0, 0, 0, 0))
        r.props['date'] = date(2023, 3, 4)
        r.call('TFR_EST_parliament_tick')
        self.assertNotIn(ENDED, r.flags)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2023)
        r.props['date'] = date(2023, 3, 5)
        r.call('TFR_EST_parliament_tick')
        self.assertIn(ENDED, r.flags)
        self.assertEqual(r.variables['TFR_EST_election_year'], 2027)
        self.assertIn('TFR_EST_election_held', r.flags)

    def test_caretaker_and_occupation_pause_without_erasing_the_programme(self):
        r = self.runtime()
        self.complete(r, ROOT_FOCUS)
        done = 'TFR_EST_done_ratas_renew_agreement'
        r.call('TFR_EST_enter_caretaker')
        self.assertFalse(self.trigger(r, GOVERNING))
        self.assertNotIn(ENDED, r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertTrue(self.trigger(r, GOVERNING))
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_suspend_parliament')
        self.assertFalse(self.trigger(r, GOVERNING))
        self.assertNotIn(ENDED, r.flags)
        self.assertIn(RETAINED, r.flags)
        self.assertIn(done, r.flags)
        r.flags.discard('TFR_EST_occupied')
        self.assertTrue(self.trigger(r, GOVERNING))
        self.assertTrue(r.condition(self.focuses[ROOT_FOCUS].get('bypass')))

    def test_referendum_is_followed_by_one_root_then_five_parallel_policy_choices(self):
        r = self.runtime()
        r.ideas.add('higher_covid_cases')
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)}, {ROOT_FOCUS})
        self.complete(r, ROOT_FOCUS)
        self.assertEqual({name for name in self.focuses if self.selectable(r, name)}, BRANCH_STARTS)
        self.complete(r, PREFIX + 'police_reserve')
        choices = {name for name in self.focuses if self.selectable(r, name)}
        self.assertIn(PREFIX + 'territorial_training', choices)
        self.assertTrue(BRANCH_STARTS.difference({PREFIX + 'police_reserve'}) <= choices)
        self.assertNotIn(PREFIX + 'industrial_parks', choices)
        self.assertFalse(self.selectable(r, FINAL_FOCUS))

    def test_final_requires_every_policy_through_separate_and_prerequisites(self):
        final_parents = self.focuses[FINAL_FOCUS].all('prerequisite')
        self.assertEqual(len(final_parents), 5)
        self.assertTrue(all(len(block.all('focus')) == 1 for block in final_parents))
        ancestors = set()

        def visit(name):
            for block in self.focuses[name].all('prerequisite'):
                for parent in block.all('focus'):
                    if parent in self.focuses and parent not in ancestors:
                        ancestors.add(parent)
                        visit(parent)

        visit(FINAL_FOCUS)
        self.assertEqual(ancestors, set(self.focuses).difference({FINAL_FOCUS}))
        r = self.runtime()
        r.ideas.add('higher_covid_cases')
        r.props['completed_focuses'].update(self.focuses)
        r.props['completed_focuses'].discard(FINAL_FOCUS)
        self.assertTrue(self.selectable(r, FINAL_FOCUS))
        for parent in (block.get('focus') for block in final_parents):
            with self.subTest(missing=parent):
                r.props['completed_focuses'].discard(parent)
                self.assertFalse(self.selectable(r, FINAL_FOCUS))
                r.props['completed_focuses'].add(parent)

    def test_all_focuses_are_thirty_five_days_without_dates_or_mutual_exclusions(self):
        for name, focus in self.focuses.items():
            with self.subTest(focus=name):
                self.assertEqual(Fraction(focus.get('cost')) * 7, 35)
                self.assertFalse(contains(focus, 'date'))
                self.assertFalse(focus.all('mutually_exclusive'))

    def test_final_checks_every_earned_record_even_if_all_terminal_nodes_are_completed(self):
        policies = set(self.focuses).difference({FINAL_FOCUS})
        for representation in ('native', 'persistent', 'mixed'):
            r = self.runtime()
            r.ideas.add('higher_covid_cases')
            records = {}
            for index, name in enumerate(sorted(policies)):
                done = 'TFR_EST_done_ratas_' + name.removeprefix(PREFIX)
                if representation == 'native' or (representation == 'mixed' and index % 2):
                    r.props['completed_focuses'].add(name)
                    records[name] = (r.props['completed_focuses'], name)
                else:
                    r.flags.add(done)
                    records[name] = (r.flags, done)
            final_available = self.focuses[FINAL_FOCUS].get('available')
            self.assertTrue(r.condition(final_available))
            for name, (store, record) in records.items():
                with self.subTest(representation=representation, missing=name):
                    store.discard(record)
                    self.assertFalse(r.condition(final_available))
                    store.add(record)

    def test_different_policy_orders_complete_all_twenty_with_sixty_six_days_to_spare(self):
        orders = set()
        for seed in range(6):
            r = self.runtime()
            r.ideas.add('higher_covid_cases')
            order = []
            rng = Random(seed)
            while len(order) < len(self.focuses):
                choices = sorted(name for name in self.focuses if self.selectable(r, name))
                self.assertTrue(choices, 'The authored prerequisite graph stalled')
                name = rng.choice(choices)
                self.complete(r, name)
                r.props['date'] += timedelta(days=int(Fraction(self.focuses[name].get('cost')) * 7))
                order.append(name)
            self.assertEqual(order[0], ROOT_FOCUS)
            self.assertEqual(order[-1], FINAL_FOCUS)
            self.assertEqual(r.props['date'], date(2022, 12, 29))
            self.assertEqual((date(2023, 3, 5) - r.props['date']).days, 66)
            self.assertIn('TFR_EST_ratas_programme_finished', r.flags)
            self.assertNotIn(ENDED, r.flags)
            orders.add(tuple(order))
        self.assertGreater(len(orders), 1)

    def test_every_completion_reward_is_repeat_safe_including_after_saved_state_is_restored(self):
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
                # Recreate the arithmetic fixture with persisted gameplay data.
                # The actual game's save serializer is outside this test.
                restored = self.runtime()
                restored.variables = r.variables.copy()
                restored.flags = r.flags.copy()
                restored.ideas = r.ideas.copy()
                restored.dynamic = r.dynamic.copy()
                restored.props['political_power'] = r.props.get('political_power', Fraction(0))
                before = self.material_state(restored)
                restored.run(reward)
                self.assertEqual(self.material_state(restored), before)

    def test_new_rewards_use_the_shared_modifiers_without_new_national_spirits(self):
        r = self.runtime()
        for name, focus in self.focuses.items():
            reward = focus.get('completion_reward')
            helper = 'TFR_EST_ratas_reward_' + name.removeprefix(PREFIX)
            with self.subTest(focus=name):
                self.assertTrue(contains(reward, helper, 'yes'))
                self.assertFalse(contains(reward, 'add_ideas'))
                self.assertTrue(contains(r.effects[helper], 'TFR_EST_initialize_country_modifiers', 'yes'))
                self.assertTrue(contains(r.effects[helper], 'TFR_EST_refresh_country_modifiers', 'yes'))
                self.assertFalse(contains(r.effects[helper], 'add_ideas'))


if __name__ == '__main__':
    unittest.main()

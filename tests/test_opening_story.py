"""Run the authored opening effects; queue timings are inspected, not emulated."""
from datetime import date, timedelta
from fractions import Fraction
import unittest

from script_runtime import Block, ROOT, Runtime, parse


FINAL = 'TFR_EST_done_opening_marriage_referendum'
SEEN = 'TFR_EST_porto_investigation_seen'
RESOLVED = 'TFR_EST_porto_choice_resolved'
PENDING = 'TFR_EST_reform_handover_pending'
REWARDS = (
    'pension_reform', 'teacher_pay', 'covid_emergency', 'pension_increase',
    'wage_compensation', 'excise_relief', 'eastern_border', 'kose_voobu',
    'three_seas', 'research_budget',
)


class OpeningStoryTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.call('TFR_EST_initialize_country_modifiers')
        return r

    def events(self):
        path = ROOT / 'events/TFR_EST_opening.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        return {e.value.get('id'): e.value for e in tree.entries if e.key == 'country_event'}

    def option(self, r, event_id, index=0):
        option = self.events()[event_id].all('option')[index]
        effects = [e for e in option.entries if e.key in r.effects]
        self.assertEqual(len(effects), 1, 'A story option must call its authored helper')
        r.run(Block(effects))

    def ledger(self, r):
        return {k: v for k, v in r.variables.items()
                if k.startswith(('TFR_EST_seats_', 'TFR_EST_support_', 'TFR_EST_poll_', 'TFR_EST_active_'))
                or k == 'TFR_EST_election_year'}

    def modifiers(self, r):
        return {k: v for k, v in r.variables.items()
                if k.startswith(('TFR_EST_economy_', 'TFR_EST_military_'))}

    def investigation(self, r):
        r.props['date'] = date(2021, 1, 12)
        r.call('TFR_EST_begin_referendum')
        event = self.events()['tfr_estonia_opening.10']
        self.assertTrue(r.condition(event.get('trigger')))
        r.run(event.get('immediate'))
        self.option(r, 'tfr_estonia_opening.10')

    def test_january_11_does_not_queue_investigation_january_12_does(self):
        r = self.runtime()
        r.props['date'] = date(2021, 1, 11)
        r.call('TFR_EST_begin_referendum')
        self.assertIn('TFR_EST_referendum_active', r.flags)
        self.assertNotIn('tfr_estonia_opening.10', r.events)
        r.props['date'] = date(2021, 1, 12)
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.10'), 1)
        self.assertIn('TFR_EST_porto_notice_pending', r.flags)
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.10'), 1)

    def test_late_start_catches_up_and_choice_is_queued_one_day_later(self):
        r = self.runtime()
        r.props['date'] = date(2021, 2, 10)
        r.call('TFR_EST_begin_referendum')
        self.assertIn('tfr_estonia_opening.10', r.events)
        r.run(self.events()['tfr_estonia_opening.10'].get('immediate'))
        self.assertIn(SEEN, r.flags)
        self.assertNotIn('TFR_EST_porto_notice_pending', r.flags)
        self.option(r, 'tfr_estonia_opening.10')
        self.assertEqual(r.events.count('tfr_estonia_opening.11'), 1)
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.11'), 1)
        queues = [entry.value for _, entry in r.effects['TFR_EST_opening_tick'].walk()
                  if entry.key == 'country_event' and entry.value.get('id') == 'tfr_estonia_opening.11']
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0].get('days'), '1')

    def test_expired_queue_guard_allows_repair_without_double_resolution(self):
        r = self.runtime()
        r.props['date'] = date(2021, 1, 12)
        r.call('TFR_EST_begin_referendum')
        # The runtime does not expire timed flags; explicitly model expiration.
        r.flags.discard('TFR_EST_porto_notice_pending')
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.10'), 2)
        r.run(self.events()['tfr_estonia_opening.10'].get('immediate'))
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.11'), 1)
        r.flags.discard('TFR_EST_porto_choice_pending')
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.11'), 2)
        r.call('TFR_EST_keep_ratas')
        r.flags.discard('TFR_EST_porto_choice_pending')
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count('tfr_estonia_opening.11'), 2)

    def test_choices_require_seen_investigation_and_independent_parliament(self):
        for helper in ('TFR_EST_keep_ratas', 'TFR_EST_ratas_steps_back'):
            for blocked in ('unseen', 'occupied', 'subject'):
                with self.subTest(helper=helper, blocked=blocked):
                    r = self.runtime()
                    if blocked != 'unseen':
                        r.flags.add(SEEN)
                    if blocked == 'occupied':
                        r.flags.add('TFR_EST_occupied')
                    if blocked == 'subject':
                        r.props['is_subject'] = 'yes'
                    before = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
                    r.call(helper)
                    self.assertEqual((r.variables, r.flags, r.ideas), before)

    def test_keep_ratas_restores_57_seat_cabinet_without_new_election(self):
        r = self.runtime()
        self.investigation(r)
        ledger, modifiers, president = self.ledger(r), self.modifiers(r), r.leader
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.variables['TFR_EST_supply_reform'] = Fraction(1)
        r.call('TFR_EST_enter_caretaker')
        self.option(r, 'tfr_estonia_opening.11', 0)
        self.assertIn(RESOLVED, r.flags)
        self.assertIn('TFR_EST_ratas_retained', r.flags)
        self.assertNotIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 2)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 57)
        self.assertEqual(r.variables['TFR_EST_confidence_seats'], 57)
        self.assertEqual(r.variables['TFR_EST_supply_reform'], 0)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 49)
        self.assertEqual(self.ledger(r), ledger)
        self.assertEqual(self.modifiers(r), modifiers)
        self.assertEqual(r.leader, president)
        self.assertNotIn('TFR_EST_election_held', r.flags)
        self.assertNotIn('TFR_EST_scripted_cabinet_change', r.flags)

    def test_each_choice_is_once_only_and_excludes_the_other_choice(self):
        for first, second in (('TFR_EST_keep_ratas', 'TFR_EST_ratas_steps_back'),
                              ('TFR_EST_ratas_steps_back', 'TFR_EST_keep_ratas')):
            with self.subTest(first=first):
                r = self.runtime()
                self.investigation(r)
                r.call(first)
                before = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
                r.call(first)
                r.call(second)
                self.assertEqual((r.variables, r.flags, r.ideas), before)

    def test_resignation_leaves_ratas_caretaker_with_13_day_handover(self):
        r = self.runtime()
        self.investigation(r)
        ledger, modifiers, president = self.ledger(r), self.modifiers(r), r.leader
        self.option(r, 'tfr_estonia_opening.11', 1)
        self.assertIn(RESOLVED, r.flags)
        self.assertIn('TFR_EST_ratas_resigned', r.flags)
        self.assertIn(PENDING, r.flags)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertEqual(r.variables['TFR_EST_reform_handover_days'], 13)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 53)
        self.assertEqual(self.ledger(r), ledger)
        self.assertEqual(self.modifiers(r), modifiers)
        self.assertEqual(r.leader, president)
        self.assertNotIn('TFR_EST_election_held', r.flags)

    def test_pending_handover_blocks_player_and_ai_reconfirmation_of_ratas(self):
        for ai in ('no', 'yes'):
            with self.subTest(ai=ai):
                r = self.runtime()
                self.investigation(r)
                r.call('TFR_EST_ratas_steps_back')
                r.props['is_ai'] = ai
                self.assertFalse(r.condition(r.triggers['TFR_EST_can_confirm_mandated_cabinet']))
                r.call('TFR_EST_confirm_cabinet')
                if ai == 'yes':
                    r.call('TFR_EST_ai_cabinet')
                    r.call('TFR_EST_parliament_tick')
                self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
                self.assertIn('TFR_EST_caretaker', r.flags)
                self.assertIn(PENDING, r.flags)

    def test_thirteen_ticks_queue_successor_and_reform_centre_keeps_parliament(self):
        r = self.runtime()
        self.investigation(r)
        r.props['date'] = date(2021, 1, 13)
        r.call('TFR_EST_ratas_steps_back')
        ledger, modifiers, president = self.ledger(r), self.modifiers(r), r.leader
        for _ in range(12):
            r.props['date'] += timedelta(days=1)
            r.call('TFR_EST_opening_tick')
        self.assertNotIn('tfr_estonia_opening.12', r.events)
        r.props['date'] += timedelta(days=1)
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.props['date'], date(2021, 1, 26))
        self.assertEqual(r.events.count('tfr_estonia_opening.12'), 1)
        self.assertTrue(r.condition(self.events()['tfr_estonia_opening.12'].get('trigger')))
        self.option(r, 'tfr_estonia_opening.12')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 1)
        self.assertEqual(r.variables['TFR_EST_coalition_seats'], 60)
        self.assertEqual(r.variables['TFR_EST_confidence_seats'], 60)
        self.assertIn('TFR_EST_reform_centre_formed', r.flags)
        self.assertNotIn(PENDING, r.flags)
        self.assertNotIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(self.ledger(r), ledger)
        self.assertEqual(self.modifiers(r), modifiers)
        self.assertEqual(r.leader, president)
        self.assertNotIn('TFR_EST_election_held', r.flags)
        self.assertNotIn('TFR_EST_scripted_cabinet_change', r.flags)
        before = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
        r.call('TFR_EST_form_reform_centre_cabinet')
        self.assertEqual((r.variables, r.flags, r.ideas), before)

    def test_successor_requires_pending_handover_and_independence(self):
        for blocked in ('no_handover', 'occupied', 'subject'):
            with self.subTest(blocked=blocked):
                r = self.runtime()
                if blocked != 'no_handover':
                    r.flags.add(PENDING)
                if blocked == 'occupied':
                    r.flags.add('TFR_EST_occupied')
                if blocked == 'subject':
                    r.props['is_subject'] = 'yes'
                before = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
                r.call('TFR_EST_form_reform_centre_cabinet')
                self.assertEqual((r.variables, r.flags, r.ideas), before)

    def test_opening_reveal_requires_focus_completion_and_crisis_choice(self):
        for done, chosen in ((False, False), (True, False), (False, True), (True, True)):
            with self.subTest(done=done, chosen=chosen):
                r = self.runtime()
                r.flags.add('TFR_EST_referendum_active')
                r.flags.add(SEEN)
                if done:
                    r.flags.add(FINAL)
                if chosen:
                    r.flags.add(RESOLVED)
                tree, ledger, modifiers = r.props['focus_tree'], self.ledger(r), self.modifiers(r)
                r.call('TFR_EST_finish_opening')
                self.assertEqual('TFR_EST_opening_complete' in r.flags, done and chosen)
                self.assertEqual('TFR_EST_referendum_active' in r.flags, not (done and chosen))
                self.assertEqual(r.props['focus_tree'], tree)
                self.assertEqual(self.ledger(r), ledger)
                self.assertEqual(self.modifiers(r), modifiers)
                self.assertNotIn('TFR_EST_election_held', r.flags)

    def test_choice_after_finished_focus_reveals_without_waiting_for_another_focus(self):
        r = self.runtime()
        self.investigation(r)
        r.flags.add(FINAL)
        r.call('TFR_EST_finish_opening')
        self.assertNotIn('TFR_EST_opening_complete', r.flags)
        r.call('TFR_EST_keep_ratas')
        self.assertIn('TFR_EST_opening_complete', r.flags)
        self.assertNotIn('TFR_EST_referendum_active', r.flags)

    def test_story_never_loads_a_tree_annexes_or_calls_an_election(self):
        path = ROOT / 'common/scripted_effects/TFR_EST_opening.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        forbidden = {'load_focus_tree', 'annex_country', 'TFR_EST_hold_election', 'TFR_EST_snap_election'}
        for _, entry in tree.walk():
            self.assertNotIn(entry.key, forbidden)

    def test_opening_rewards_use_shared_budget_and_dynamic_modifiers(self):
        r = self.runtime()
        ledger = self.ledger(r)
        for reward in REWARDS:
            effect = 'TFR_EST_opening_reward_' + reward
            for _, entry in r.effects[effect].walk():
                self.assertNotIn(entry.key, {'add_ideas', 'add_timed_idea', 'create_unit', 'load_oob'})
            r.call(effect)
        self.assertEqual(self.ledger(r), ledger)
        self.assertEqual(r.variables['TFR_EST_cohesion'], 64)
        self.assertEqual(r.variables['TFR_EST_readiness'], 28)
        self.assertEqual(r.variables['TFR_EST_economy_industrial_capacity_factory_var'], Fraction(1, 100))
        self.assertEqual(r.variables['TFR_EST_economy_consumer_goods_factor_var'], Fraction(-1, 100))
        self.assertEqual(r.variables['TFR_EST_economy_production_speed_buildings_factor_var'], Fraction(1, 100))
        self.assertEqual(r.variables['TFR_EST_military_supply_consumption_factor_var'], Fraction(-1, 100))
        self.assertEqual(r.variables['TFR_EST_economy_production_factory_efficiency_gain_factor_var'], Fraction(1, 100))
        self.assertEqual(r.variables['TFR_EST_economy_research_speed_factor_var'], Fraction(1, 50))
        self.assertGreater(r.dynamic_updates, 0)
        self.assertEqual(len([call for call in r.calls if call[0] == 'add_debt_with_inflation']), 8)
        self.assertNotIn('TFR_EST_election_held', r.flags)


if __name__ == '__main__':
    unittest.main()

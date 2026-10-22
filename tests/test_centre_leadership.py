"""Distinguish Centre's opposition congress from the country's premiership."""
from copy import deepcopy
from datetime import date
import sys
import unittest

from script_runtime import ROOT, Runtime, parse

sys.path.insert(0, str(ROOT / 'tools'))
from build_centre_leadership import outputs

LOSS = 'TFR_EST_centre_lost_2023_election'
WIN = 'TFR_EST_centre_won_2023_election'
RESOLVED = 'TFR_EST_centre_leadership_resolved'
PENDING = 'TFR_EST_centre_leadership_pending'
PRESENTED = 'TFR_EST_centre_leadership_presented'
WAIT = 'TFR_EST_centre_leadership_waiting_confirmation'
EVENT = 'tfr_estonia_centre_leadership.1'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
PEOPLE = {'kiik': 'tanel_kiik', 'kolvart': 'mihhail_kolvart'}


class CentreLeadershipTests(unittest.TestCase):
    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.call('TFR_EST_initialize_ministers')
        return r

    def election(self, r, winner='reform', when=date(2023, 3, 5), mixed=False):
        r.props['date'] = when
        for p in PARTIES:
            r.variables['TFR_EST_active_' + p] = 1
            r.variables['TFR_EST_support_' + p] = (6000 if p == winner else 4000 if p == 'centre' else 0) if mixed else (10000 if p == winner else 0)
        r.variables['TFR_EST_support_other'] = 0
        r.call('TFR_EST_hold_election')

    def runtime(self, confirmed=True, junior=False):
        r = self.fresh()
        self.election(r, mixed=junior)
        if junior:
            r.variables['TFR_EST_coalition_centre'] = 1
            r.call('TFR_EST_recount_confidence')
        if confirmed:
            r.call('TFR_EST_confirm_cabinet')
        r.props['date'] = date(2023, 9, 10)
        return r

    def eligible(self, r):
        return r.test('TFR_EST_centre_leadership_eligible', '=', 'yes')

    def choose(self, r, leader):
        r.call('TFR_EST_choose_centre_leader_' + leader)

    def event(self):
        return parse((ROOT / 'events/TFR_EST_centre_leadership.txt').read_text()).get('country_event')

    def selected(self, r, relative, definition_name):
        tree = parse((ROOT / relative).read_text())
        definition = next(e.value for e in tree.entries if e.key == 'defined_text' and e.value.get('name') == definition_name)
        return next(e.value.get('localization_key') for e in definition.entries
                    if e.key == 'text' and r.condition(e.value.get('trigger')))

    def party_leader(self, r):
        return self.selected(r, 'common/scripted_localisation/TFR_EST_centre_leadership.txt', 'TFR_EST_centre_party_leader')

    def pm_name(self, r):
        return self.selected(r, 'common/scripted_localisation/TFR_EST_executive.txt', 'TFR_EST_pm_name')

    def cabinet_snapshot(self, r):
        return deepcopy((r.variables, r.politics, r.props, r.ideas, r.calls, r.characters))

    def test_opening_and_march_defeat_keep_ratas_as_party_chair(self):
        r = self.fresh()
        self.assertEqual(self.party_leader(r), 'TFR_EST_juri_ratas')
        self.election(r)
        self.assertIn(LOSS, r.flags)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertNotIn(EVENT, r.events)
        self.assertNotIn(RESOLVED, r.flags)
        self.assertEqual(self.party_leader(r), 'TFR_EST_juri_ratas')
        self.assertIn('TFR_EST_pm_centre', r.ideas)

    def test_congress_is_blocked_september9_and_queued_once_september10(self):
        r = self.runtime()
        r.props['date'] = date(2023, 9, 9)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertNotIn(EVENT, r.events)
        self.assertFalse(self.eligible(r))
        r.props['date'] = date(2023, 9, 10)
        self.assertTrue(self.eligible(r))
        r.call('TFR_EST_centre_leadership_tick')
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 1)
        self.assertIn(PENDING, r.flags)
        schedules = [e.value for _, e in r.effects['TFR_EST_centre_leadership_tick'].walk() if e.key == 'country_event']
        self.assertEqual(schedules[0].get('hours'), '1')

    def test_only_two_real_candidates_are_available_without_ratas_option(self):
        options = self.event().all('option')
        self.assertEqual(len(options), 2)
        self.assertEqual([o.get('name') for o in options],
                         ['TFR_EST_centre_congress_kiik', 'TFR_EST_centre_congress_kolvart'])
        helpers = [e.key for o in options for _, e in o.walk() if e.key.startswith('TFR_EST_choose_')]
        self.assertCountEqual(helpers, ['TFR_EST_choose_centre_leader_kiik', 'TFR_EST_choose_centre_leader_kolvart'])

    def test_centre2023_win_does_not_schedule_congress_or_replace_ratas(self):
        r = self.fresh()
        self.election(r, 'centre')
        r.call('TFR_EST_confirm_cabinet')
        r.props['date'] = date(2023, 9, 10)
        self.assertIn(WIN, r.flags)
        self.assertNotIn(LOSS, r.flags)
        self.assertFalse(self.eligible(r))
        r.call('TFR_EST_centre_leadership_tick')
        self.choose(r, 'kiik')
        self.choose(r, 'kolvart')
        self.assertNotIn(RESOLVED, r.flags)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertEqual(self.party_leader(r), 'TFR_EST_juri_ratas')

    def test_opposition_and_junior_coalition_choices_preserve_other_party_pm(self):
        for junior in (False, True):
            for leader, person in PEOPLE.items():
                with self.subTest(junior=junior, leader=leader):
                    r = self.runtime(junior=junior)
                    before = self.cabinet_snapshot(r)
                    self.choose(r, leader)
                    self.assertEqual(self.cabinet_snapshot(r), before)
                    self.assertIn(RESOLVED, r.flags)
                    self.assertIn('TFR_EST_centre_leader_' + leader, r.flags)
                    self.assertEqual(self.party_leader(r), 'TFR_EST_' + person)
                    self.assertEqual(self.pm_name(r), 'TFR_EST_kaja_kallas')
                    self.assertNotIn('TFR_EST_pm_person_' + person, r.flags)

    def test_ratas_caretaker_waits_for_actual_cabinet_confirmation(self):
        for leader in PEOPLE:
            with self.subTest(leader=leader):
                r = self.runtime(confirmed=False)
                self.assertIn('TFR_EST_caretaker', r.flags)
                self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
                self.choose(r, leader)
                self.assertIn(WAIT, r.flags)
                self.assertEqual(self.pm_name(r), 'TFR_EST_juri_ratas')
                self.assertIn('TFR_EST_pm_centre', r.ideas)
                r.call('TFR_EST_reconcile_executive_display')
                self.assertIn('TFR_EST_pm_centre', r.ideas)
                r.call('TFR_EST_confirm_cabinet')
                self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
                self.assertEqual(self.pm_name(r), 'TFR_EST_kaja_kallas')
                self.assertNotIn(WAIT, r.flags)

    def test_confirmed_centre_pm_after_authorized_story_adopts_selected_leader(self):
        for leader, person in PEOPLE.items():
            with self.subTest(leader=leader):
                r = self.runtime(junior=True)
                r.flags.add('TFR_EST_scripted_cabinet_change')
                r.call('TFR_EST_nominate_centre')
                r.variables['TFR_EST_coalition_reform'] = 1
                r.call('TFR_EST_recount_confidence')
                r.call('TFR_EST_confirm_cabinet')
                before_variables = r.variables.copy()
                before_portfolios = {i for i in r.ideas if i.startswith('TFR_EST_minister_')}
                self.choose(r, leader)
                self.assertEqual(r.variables, before_variables)
                self.assertEqual({i for i in r.ideas if i.startswith('TFR_EST_minister_')}, before_portfolios)
                self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
                self.assertEqual(self.pm_name(r), 'TFR_EST_' + person)
                self.assertIn('TFR_EST_pm_centre_' + leader, r.ideas)
                self.assertNotIn('TFR_EST_pm_centre', r.ideas)

    def test_selected_leader_is_used_for_future_centre_government(self):
        for leader, person in PEOPLE.items():
            r = self.runtime()
            self.choose(r, leader)
            self.election(r, 'centre', date(2028, 3, 5))
            r.call('TFR_EST_confirm_cabinet')
            with self.subTest(leader=leader):
                self.assertIn('TFR_EST_pm_centre_' + leader, r.ideas)
                self.assertIn('TFR_EST_pm_person_' + person, r.flags)
                self.assertEqual(self.pm_name(r), 'TFR_EST_' + person)
                r.call('TFR_EST_enter_caretaker')
                r.call('TFR_EST_reconcile_executive_display')
                self.assertEqual(self.pm_name(r), 'TFR_EST_' + person)

    def test_late2023_centre_win_preserves_already_chosen_leader(self):
        for leader in PEOPLE:
            r = self.runtime()
            self.choose(r, leader)
            self.election(r, 'centre', date(2023, 10, 1))
            r.call('TFR_EST_confirm_cabinet')
            with self.subTest(leader=leader):
                self.assertIn(WIN, r.flags)
                self.assertNotIn(LOSS, r.flags)
                self.assertIn(RESOLVED, r.flags)
                self.assertIn('TFR_EST_centre_leader_' + leader, r.flags)
                self.assertIn('TFR_EST_pm_centre_' + leader, r.ideas)

    def test_centre_win_while_notice_queued_makes_delivery_and_both_options_obsolete(self):
        r = self.runtime()
        r.call('TFR_EST_centre_leadership_tick')
        self.assertIn(PENDING, r.flags)
        self.election(r, 'centre', date(2023, 9, 11))
        r.call('TFR_EST_confirm_cabinet')
        self.assertFalse(r.condition(self.event().get('trigger')))
        before = self.cabinet_snapshot(r)
        for leader in PEOPLE:
            self.choose(r, leader)
        self.assertEqual(self.cabinet_snapshot(r), before)
        self.assertNotIn(RESOLVED, r.flags)
        self.assertIn('TFR_EST_pm_centre', r.ideas)

    def test_already_displayed_notice_is_also_guarded_after_centre_win(self):
        r = self.runtime()
        r.call('TFR_EST_centre_leadership_tick')
        r.run(self.event().get('immediate'))
        self.election(r, 'centre', date(2023, 9, 11))
        r.call('TFR_EST_confirm_cabinet')
        before = self.cabinet_snapshot(r)
        for option in self.event().all('option'):
            r.run(option.get('hidden_effect'))
        self.assertEqual(self.cabinet_snapshot(r), before)
        self.assertNotIn(RESOLVED, r.flags)

    def test_occupation_invalidates_notice_then_independence_requeues_once(self):
        r = self.runtime()
        r.call('TFR_EST_centre_leadership_tick')
        r.run(self.event().get('immediate'))
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        self.assertFalse(r.condition(self.event().get('trigger')))
        for leader in PEOPLE:
            self.choose(r, leader)
        self.assertNotIn(RESOLVED, r.flags)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertNotIn(PENDING, r.flags)
        self.assertNotIn(PRESENTED, r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 2)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 2)

    def test_notice_immediate_and_resolved_choice_prevent_duplicate_events_or_rewards(self):
        r = self.runtime()
        r.call('TFR_EST_centre_leadership_tick')
        self.assertTrue(r.condition(self.event().get('trigger')))
        r.run(self.event().get('immediate'))
        self.assertIn(PRESENTED, r.flags)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 1)
        self.choose(r, 'kiik')
        before = deepcopy((r.variables, r.flags, r.ideas, r.calls, r.props))
        self.choose(r, 'kiik')
        self.choose(r, 'kolvart')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertEqual((r.variables, r.flags, r.ideas, r.calls, r.props), before)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 1)

    def test_selected_centre_leader_survives_occupation_and_restoration(self):
        for leader, person in PEOPLE.items():
            r = self.runtime()
            self.choose(r, leader)
            self.election(r, 'centre', date(2028, 3, 5))
            r.call('TFR_EST_confirm_cabinet')
            r.flags.add('TFR_EST_occupied')
            r.props['is_subject'] = 'yes'
            r.leader = 'EST_yana_toom_char'
            r.call('TFR_EST_reconcile_executive_display')
            with self.subTest(leader=leader):
                self.assertIn('TFR_EST_centre_leader_' + leader, r.flags)
                self.assertNotIn('TFR_EST_pm_person_' + person, r.flags)
                self.assertNotIn('TFR_EST_pm_centre_' + leader, r.ideas)
                self.assertEqual(r.leader, 'EST_yana_toom_char')
                r.flags.discard('TFR_EST_occupied')
                r.props['is_subject'] = 'no'
                r.call('TFR_EST_reconcile_executive_display')
                self.assertIn('TFR_EST_pm_centre_' + leader, r.ideas)

    def test_unconfirmed_ratas_caretaker_survives_occupation_before_handover(self):
        r = self.runtime(confirmed=False)
        self.choose(r, 'kiik')
        self.assertIn(WAIT, r.flags)
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_centre_pm_identity')
        self.assertIn(WAIT, r.flags)
        self.assertIn('TFR_EST_centre_leader_kiik', r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertIn(WAIT, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_juri_ratas')
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertNotIn('TFR_EST_pm_person_tanel_kiik', r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertNotIn(WAIT, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_kaja_kallas')

    def test_already_selected_centre_caretaker_restores_its_actual_leader(self):
        r = self.runtime()
        self.choose(r, 'kiik')
        self.election(r, 'centre', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        r.call('TFR_EST_enter_caretaker')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_reconcile_executive_display')
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertNotIn(WAIT, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_tanel_kiik')
        self.assertIn('TFR_EST_pm_centre_kiik', r.ideas)

    def test_invalid_vote_does_not_create_a_leadership_crisis(self):
        r = self.fresh()
        r.props['date'] = date(2023, 3, 5)
        for p in PARTIES:
            r.variables['TFR_EST_support_' + p] = 10001 if p == 'reform' else 0
        r.variables['TFR_EST_support_other'] = 0
        r.call('TFR_EST_hold_election')
        r.props['date'] = date(2023, 9, 10)
        self.assertNotIn(LOSS, r.flags)
        self.assertFalse(self.eligible(r))
        self.choose(r, 'kiik')
        self.assertEqual(self.party_leader(r), 'TFR_EST_juri_ratas')

    def test_dropped_unpresented_notice_can_retry_after_queue_expiry(self):
        r = self.runtime()
        r.call('TFR_EST_centre_leadership_tick')
        # Expiry itself belongs to the engine; the callback can be retried
        # after its native two-day queue guard expires without presentation.
        r.flags.discard(PENDING)
        r.call('TFR_EST_centre_leadership_tick')
        self.assertEqual(r.events.count(EVENT), 2)
        self.assertIn(PENDING, r.flags)

    def test_leader_marker_is_cleared_for_other_pm_without_losing_party_choice(self):
        r = self.runtime()
        self.choose(r, 'kolvart')
        self.election(r, 'centre', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.election(r, 'reform', date(2032, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn('TFR_EST_centre_leader_kolvart', r.flags)
        self.assertNotIn('TFR_EST_pm_person_mihhail_kolvart', r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_kaja_kallas')
        self.assertEqual(self.party_leader(r), 'TFR_EST_mihhail_kolvart')

    def test_minister_occupation_cleanup_clears_current_pm_markers_only(self):
        r = self.runtime()
        self.choose(r, 'kolvart')
        self.election(r, 'centre', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn('TFR_EST_pm_person_mihhail_kolvart', r.flags)
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_reconcile_ministers')
        self.assertNotIn('TFR_EST_pm_person_mihhail_kolvart', r.flags)
        self.assertIn('TFR_EST_centre_leader_kolvart', r.flags)
        self.assertIn(RESOLVED, r.flags)

    def test_both_native_pm_ideas_remain_locked_and_use_individual_portraits(self):
        ideas = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text()).get('ideas').get('head_minister')
        sprites = parse((ROOT / 'interface/TFR_EST_executive.gfx').read_text()).get('spriteTypes')
        for leader in PEOPLE:
            idea = ideas.get('TFR_EST_pm_centre_' + leader)
            self.assertEqual(idea.get('available').get('has_idea'), 'TFR_EST_pm_centre_' + leader)
            self.assertEqual(idea.get('allowed_to_remove').get('always'), 'no')
            self.assertEqual(idea.get('modifier').entries, [])
            sprite = next(e.value for e in sprites.entries if e.value.get('name') == 'GFX_idea_TFR_EST_pm_centre_' + leader)
            self.assertTrue(sprite.get('texturefile').startswith('gfx/leaders/EST/ministers/'))
            icon = next(e.value for e in sprites.entries if e.value.get('name') == 'GFX_idea_TFR_EST_pm_centre_' + leader + '_icon')
            self.assertTrue(icon.get('texturefile').startswith('gfx/interface/ideas/EST/ministers/'))
            self.assertEqual(idea.get('picture'), 'TFR_EST_pm_centre_' + leader + '_icon')

    def test_reproducible_outputs_and_bom_localisation(self):
        for relative, content in outputs().items():
            encoding = 'utf-8-sig' if relative.endswith('.yml') else 'utf-8'
            self.assertEqual((ROOT / relative).read_bytes(), content.encode(encoding))


if __name__ == '__main__':
    unittest.main()

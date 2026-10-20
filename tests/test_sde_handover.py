"""Run the real date-driven SDE succession and its independent PM identity repair."""
from copy import deepcopy
from datetime import date
import sys
import unittest

from script_runtime import ROOT, Runtime, parse

sys.path.insert(0, str(ROOT / 'tools'))
from build_sde_handover import outputs

CAREER = 'TFR_EST_laanemets_leads_sde'
PERSON = 'TFR_EST_pm_person_lauri_laanemets'
WAIT = 'TFR_EST_sde_handover_waiting_confirmation'
PENDING = 'TFR_EST_sde_handover_pending'
PRESENTED = 'TFR_EST_sde_handover_presented'
SAAR = 'TFR_EST_pm_sde'
LAANEMETS = 'TFR_EST_pm_sde_laanemets'
EVENT = 'tfr_estonia_sde_handover.1'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')


class SDEHandoverTests(unittest.TestCase):
    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.call('TFR_EST_initialize_ministers')
        return r

    def election(self, r, winner='sde', when=date(2021, 12, 1), junior=False):
        r.props['date'] = when
        for p in PARTIES:
            r.variables['TFR_EST_active_' + p] = 1
            r.variables['TFR_EST_support_' + p] = (6000 if p == winner else 4000 if p == 'sde' else 0) if junior else (10000 if p == winner else 0)
        r.variables['TFR_EST_support_other'] = 0
        r.call('TFR_EST_hold_election')

    def government(self, winner='sde', junior=False):
        r = self.fresh()
        self.election(r, winner, junior=junior)
        if junior:
            r.variables['TFR_EST_coalition_sde'] = 1
            r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_confirm_cabinet')
        r.props['date'] = date(2022, 2, 5)
        r.events.clear()
        return r

    def selected(self, r, relative, name):
        tree = parse((ROOT / relative).read_text(encoding='utf-8-sig'))
        definition = next(e.value for e in tree.entries if e.key == 'defined_text' and e.value.get('name') == name)
        return next(e.value.get('localization_key') for e in definition.entries
                    if e.key == 'text' and r.condition(e.value.get('trigger')))

    def party_leader(self, r):
        return self.selected(r, 'common/scripted_localisation/TFR_EST_sde_handover.txt', 'TFR_EST_sde_party_leader')

    def pm_name(self, r):
        return self.selected(r, 'common/scripted_localisation/TFR_EST_executive.txt', 'TFR_EST_pm_name')

    def hog(self, r):
        return self.selected(r, 'common/scripted_localisation/00_TFR_scripted_loc_ZZZ_hog_tt.txt', 'head_of_gov_dynamic_loc')

    def event(self):
        return parse((ROOT / 'events/TFR_EST_sde_handover.txt').read_text(encoding='utf-8')).get('country_event')

    def cabinet_snapshot(self, r):
        return deepcopy((r.variables, r.politics, r.props, r.ideas, r.calls, r.characters, r.leader))

    def test_opening_and_february4_keep_saar_as_party_chair(self):
        r = self.fresh()
        self.assertEqual(self.party_leader(r), 'TFR_EST_indrek_saar')
        r.props['date'] = date(2022, 2, 4)
        r.call('TFR_EST_sde_handover_tick')
        r.call('TFR_EST_complete_sde_handover')
        self.assertNotIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertFalse(r.events)

    def test_first_february5_daily_changes_party_before_notice_acknowledgement(self):
        r = self.fresh()
        r.props['date'] = date(2022, 2, 5)
        r.call('TFR_EST_sde_handover_tick')
        self.assertIn(CAREER, r.flags)
        self.assertEqual(self.party_leader(r), 'TFR_EST_lauri_laanemets')
        self.assertEqual(r.events, [EVENT])
        self.assertIn(PENDING, r.flags)
        self.assertNotIn(PRESENTED, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_juri_ratas')
        schedules = [e.value for _, e in r.effects['TFR_EST_sde_handover_tick'].walk() if e.key == 'country_event']
        self.assertEqual(schedules[0].get('hours'), '1')

    def test_complete_helper_enforces_date_internally(self):
        for when, expected in ((date(2022, 2, 4), False), (date(2022, 2, 5), True)):
            with self.subTest(when=when):
                r = self.fresh()
                r.props['date'] = when
                r.call('TFR_EST_complete_sde_handover')
                self.assertEqual(CAREER in r.flags, expected)

    def test_opposition_and_junior_coalition_preserve_every_cabinet_record(self):
        for junior in (False, True):
            with self.subTest(junior=junior):
                r = self.government('reform', junior=junior)
                before = self.cabinet_snapshot(r)
                r.call('TFR_EST_sde_handover_tick')
                self.assertEqual(self.cabinet_snapshot(r), before)
                self.assertIn(CAREER, r.flags)
                self.assertNotIn(PERSON, r.flags)
                self.assertEqual(self.pm_name(r), 'TFR_EST_kaja_kallas')
                self.assertEqual(self.hog(r), 'TFR_EST_hog_reform')

    def test_confirmed_sde_government_changes_only_pm_identity(self):
        r = self.government()
        variables, politics, props, ideas, calls, characters, president = self.cabinet_snapshot(r)
        self.assertIn(SAAR, ideas)
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.variables, variables)
        self.assertEqual(r.politics, politics)
        self.assertEqual(r.props, props)
        self.assertEqual(r.calls, calls)
        self.assertEqual(r.characters, characters)
        self.assertEqual(r.leader, president)
        self.assertEqual(r.ideas, ideas - {SAAR} | {LAANEMETS})
        self.assertIn(PERSON, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_lauri_laanemets')
        self.assertEqual(self.hog(r), 'TFR_EST_hog_sde_laanemets')

    def test_saar_caretaker_waits_for_reconfirmed_sde_cabinet(self):
        r = self.government()
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_sde_handover_tick')
        self.assertIn(WAIT, r.flags)
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertEqual(self.pm_name(r), 'TFR_EST_indrek_saar')
        self.assertEqual(self.hog(r), 'TFR_EST_hog_sde')
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_ministers')
        self.assertIn(SAAR, r.ideas)
        self.assertNotIn(LAANEMETS, r.ideas)
        r.call('TFR_EST_confirm_cabinet')
        self.assertNotIn(WAIT, r.flags)
        self.assertIn(LAANEMETS, r.ideas)

    def test_outgoing_saar_caretaker_does_not_replace_winning_other_party(self):
        r = self.government()
        self.election(r, 'reform', date(2022, 2, 1))
        r.props['date'] = date(2022, 2, 5)
        r.call('TFR_EST_sde_handover_tick')
        self.assertIn(WAIT, r.flags)
        self.assertIn(SAAR, r.ideas)
        r.call('TFR_EST_confirm_cabinet')
        self.assertNotIn(WAIT, r.flags)
        self.assertIn('TFR_EST_pm_reform', r.ideas)
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)

    def test_actual_2023_sde_election_and_confirmation_uses_laanemets(self):
        r = self.fresh()
        r.props['date'] = date(2022, 2, 5)
        r.call('TFR_EST_sde_handover_tick')
        self.election(r, 'sde', date(2023, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 5)
        self.assertIn(LAANEMETS, r.ideas)
        self.assertNotIn(SAAR, r.ideas)
        self.assertEqual(self.party_leader(r), 'TFR_EST_lauri_laanemets')

    def test_late_first_daily_catches_up_when_campaign_remains_independent(self):
        r = self.fresh()
        r.props['date'] = date(2023, 4, 17)
        r.call('TFR_EST_sde_handover_tick')
        self.assertIn(CAREER, r.flags)
        self.assertEqual(self.party_leader(r), 'TFR_EST_lauri_laanemets')

    def test_occupied_congress_is_deferred_until_first_independent_daily(self):
        for subject, occupation in (('yes', False), ('no', True), ('yes', True)):
            with self.subTest(subject=subject, occupation=occupation):
                r = self.fresh()
                r.props.update(date=date(2022, 2, 5), is_subject=subject)
                if occupation:
                    r.flags.add('TFR_EST_occupied')
                r.leader = 'EST_yana_toom_char'
                r.call('TFR_EST_sde_handover_tick')
                r.call('TFR_EST_complete_sde_handover')
                self.assertNotIn(CAREER, r.flags)
                self.assertEqual(r.leader, 'EST_yana_toom_char')
                self.assertFalse(r.events)
                r.flags.discard('TFR_EST_occupied')
                r.props['is_subject'] = 'no'
                r.call('TFR_EST_reconcile_executive_display')
                r.call('TFR_EST_sde_handover_tick')
                self.assertIn(CAREER, r.flags)
                self.assertEqual(r.events, [EVENT])

    def test_foreign_or_uninitialized_scopes_cannot_perform_handover(self):
        for mutate in (lambda r: r.props.update(tag='LAT', original_tag='LAT'),
                       lambda r: r.flags.discard('TFR_EST_initialized')):
            r = self.fresh()
            r.props['date'] = date(2022, 2, 5)
            mutate(r)
            before = self.cabinet_snapshot(r)
            r.call('TFR_EST_sde_handover_tick')
            r.call('TFR_EST_complete_sde_handover')
            self.assertEqual(self.cabinet_snapshot(r), before)
            self.assertNotIn(CAREER, r.flags)
            self.assertFalse(r.events)

    def test_notification_has_one_acknowledgement_and_no_change_effect(self):
        options = self.event().all('option')
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0].get('name'), 'TFR_EST_sde_handover_option')
        self.assertIsNone(options[0].get('hidden_effect'))
        self.assertNotIn('TFR_EST_complete_sde_handover', {e.key for _, e in options[0].walk()})

    def test_notification_immediate_prevents_repeat_queues(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.events, [EVENT])
        self.assertTrue(r.condition(self.event().get('trigger')))
        r.run(self.event().get('immediate'))
        self.assertIn(PRESENTED, r.flags)
        self.assertNotIn(PENDING, r.flags)
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.events, [EVENT])
        self.assertFalse(r.condition(self.event().get('trigger')))

    def test_pending_expiry_can_retry_undelivered_notice_without_reward(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        before = self.cabinet_snapshot(r)
        r.flags.discard(PENDING)  # Native engine owns timed flag expiration.
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.events, [EVENT, EVENT])
        self.assertEqual(self.cabinet_snapshot(r), before)

    def test_occupation_invalidates_pending_delivery_and_restoration_retries(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        self.assertFalse(r.condition(self.event().get('trigger')))
        r.call('TFR_EST_sde_handover_tick')
        self.assertNotIn(PENDING, r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.events, [EVENT, EVENT])
        self.assertTrue(r.condition(self.event().get('trigger')))

    def test_delivered_notice_is_not_replayed_after_occupation(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        r.run(self.event().get('immediate'))
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_sde_handover_tick')
        r.flags.discard('TFR_EST_occupied')
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.events, [EVENT])
        self.assertIn(PRESENTED, r.flags)

    def test_current_laanemets_survives_occupation_and_restoration(self):
        r = self.government()
        r.flags.add('TFR_EST_karis_president')
        r.call('TFR_EST_sde_handover_tick')
        self.assertEqual(r.leader, 'TFR_EST_alar_karis')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.leader = 'EST_yana_toom_char'
        r.call('TFR_EST_reconcile_ministers')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertEqual(r.leader, 'EST_yana_toom_char')
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertNotIn(LAANEMETS, r.ideas)
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertEqual(r.leader, 'TFR_EST_alar_karis')
        self.assertIn(LAANEMETS, r.ideas)

    def test_saar_waiting_caretaker_keeps_person_through_occupation(self):
        r = self.government()
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_sde_handover_tick')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_reconcile_ministers')
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_sde_pm_identity')
        self.assertIn(CAREER, r.flags)
        self.assertIn(WAIT, r.flags)
        self.assertNotIn(PERSON, r.flags)
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(SAAR, r.ideas)
        self.assertEqual(self.pm_name(r), 'TFR_EST_indrek_saar')
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(LAANEMETS, r.ideas)

    def test_already_laanemets_caretaker_restores_its_actual_person(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        r.call('TFR_EST_enter_caretaker')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.call('TFR_EST_reconcile_executive_display')
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertNotIn(WAIT, r.flags)
        self.assertIn(LAANEMETS, r.ideas)

    def test_future_sde_cabinet_restores_career_after_other_party(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        self.election(r, 'reform', date(2023, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertNotIn(LAANEMETS, r.ideas)
        self.election(r, 'sde', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(CAREER, r.flags)
        self.assertIn(PERSON, r.flags)
        self.assertIn(LAANEMETS, r.ideas)

    def test_handover_repair_and_deferred_notice_are_repeat_safe(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        before = deepcopy((r.variables, r.flags, r.ideas, r.calls, r.props, r.characters))
        for _ in range(3):
            r.call('TFR_EST_sde_handover_tick')
            r.call('TFR_EST_complete_sde_handover')
            r.call('TFR_EST_reconcile_executive_display')
            r.call('TFR_EST_reconcile_ministers')
        self.assertEqual((r.variables, r.flags, r.ideas, r.calls, r.props, r.characters), before)
        self.assertEqual(r.events, [EVENT])

    def test_persisted_records_reconstruct_display_without_replaying_congress(self):
        r = self.government()
        r.call('TFR_EST_sde_handover_tick')
        r.run(self.event().get('immediate'))
        restored = self.fresh()
        for name in ('variables', 'flags', 'ideas', 'politics', 'props', 'leader'):
            setattr(restored, name, deepcopy(getattr(r, name)))
        restored.ideas.discard(LAANEMETS)
        restored.flags.discard(PERSON)
        restored.call('TFR_EST_reconcile_executive_display')
        restored.call('TFR_EST_sde_handover_tick')
        self.assertIn(LAANEMETS, restored.ideas)
        self.assertIn(PERSON, restored.flags)
        self.assertEqual(self.pm_name(restored), 'TFR_EST_lauri_laanemets')
        self.assertFalse(restored.events)

    def test_laanemets_head_minister_is_locked_and_shows_actual_incumbent_only(self):
        ideas = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text(encoding='utf-8')).get('ideas').get('head_minister')
        definition = ideas.get(LAANEMETS)
        self.assertEqual(definition.get('available').get('always'), 'no')
        self.assertEqual(definition.get('allowed_to_remove').get('always'), 'no')
        self.assertEqual(definition.get('modifier').entries, [])
        self.assertEqual(definition.get('removal_cost'), '-1')
        r = self.government()
        self.assertFalse(r.condition(definition.get('visible')))
        r.call('TFR_EST_sde_handover_tick')
        self.assertTrue(r.condition(definition.get('visible')))
        self.assertFalse(r.condition(ideas.get(SAAR).get('visible')))
        sprites = parse((ROOT / 'interface/TFR_EST_executive.gfx').read_text(encoding='utf-8')).get('spriteTypes')
        sprite = next(e.value for e in sprites.entries if e.value.get('name') == 'GFX_idea_' + LAANEMETS)
        self.assertTrue(sprite.get('texturefile').startswith('gfx/leaders/Europe/'))

    def test_party_tooltip_and_decision_description_show_chair_in_opposition(self):
        gui = (ROOT / 'interface/TFR_EST_parliament.gui').read_text(encoding='utf-8')
        self.assertIn('text = "TFR_EST_party_sde" pdx_tooltip = "TFR_EST_sde_party_leader_tt"', gui)
        loc = (ROOT / 'localisation/english/TFR_EST_parliament_l_english.yml').read_text(encoding='utf-8-sig')
        self.assertIn('SDE party leader: [TFR_EST_sde_party_leader]', loc)

    def test_daily_hook_calls_automatic_controller(self):
        daily = parse((ROOT / 'common/on_actions/TFR_EST_systems.txt').read_text(encoding='utf-8')).get('on_actions').get('on_daily_EST')
        self.assertIn('TFR_EST_sde_handover_tick', {e.key for _, e in daily.walk()})

    def test_generated_outputs_are_reproducible_with_bom_localisation(self):
        for relative, content in outputs().items():
            encoding = 'utf-8-sig' if relative.endswith('.yml') else 'utf-8'
            self.assertEqual((ROOT / relative).read_bytes(), content.encode(encoding))


if __name__ == '__main__':
    unittest.main()

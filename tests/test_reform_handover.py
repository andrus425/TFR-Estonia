"""Exercise the real succession controller and the existing native PM display."""
from datetime import date
from pathlib import Path
import sys
import unittest

from script_runtime import Runtime, ROOT, parse

sys.path.insert(0, str(ROOT / 'tools'))
from build_reform_handover import outputs

CAREER = 'TFR_EST_kallas_departed_for_europe'
PERSON = 'TFR_EST_pm_person_kristen_michal'
PENDING = 'TFR_EST_reform_2024_handover_pending'
EVENT = 'tfr_estonia_reform_handover.1'
KALLAS = 'TFR_EST_pm_reform'
MICHAL = 'TFR_EST_pm_reform_michal'


class ReformHandoverTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.props['date'] = date(2024, 7, 23)
        r.flags.add('TFR_EST_reform_2023_mandate')
        r.flags.discard('TFR_EST_caretaker')
        r.variables.update(TFR_EST_pm_party=1, TFR_EST_mandate_party=1,
                           TFR_EST_coalition_reform=1, TFR_EST_coalition_seats=60,
                           TFR_EST_confidence_seats=60)
        r.politics['ruling_party'] = 'market_liberal'
        r.dynamic.add('EU_member_dynamic')
        r.call('TFR_EST_reconcile_executive_display')
        r.events.clear()
        return r

    def eligible(self, r):
        return r.condition(r.triggers['TFR_EST_reform_handover_eligible'])

    def event(self):
        return parse((ROOT / 'events/TFR_EST_reform_handover.txt').read_text(
            encoding='utf-8-sig')).get('country_event')

    def test_historical_date_and_one_delayed_notice(self):
        r = self.runtime()
        r.props['date'] = date(2024, 7, 22)
        r.call('TFR_EST_reform_handover_tick')
        self.assertFalse(r.events)
        r.props['date'] = date(2024, 7, 23)
        r.call('TFR_EST_reform_handover_tick')
        r.call('TFR_EST_reform_handover_tick')
        self.assertEqual(r.events, [EVENT])
        self.assertIn(PENDING, r.flags)
        self.assertNotIn(CAREER, r.flags)
        scheduled = [e.value for _, e in r.effects['TFR_EST_reform_handover_tick'].walk()
                     if e.key == 'country_event']
        self.assertEqual(scheduled[0].get('days'), '1')

    def test_requires_confirmed_reform_2023_coalition_and_eu(self):
        cases = {
            'subject': lambda r: r.props.update(is_subject='yes'),
            'occupation': lambda r: r.flags.add('TFR_EST_occupied'),
            'caretaker': lambda r: r.flags.add('TFR_EST_caretaker'),
            'no_confidence': lambda r: r.variables.update(TFR_EST_confidence_seats=50),
            'minority_coalition': lambda r: r.variables.update(TFR_EST_coalition_seats=50),
            'other_pm': lambda r: r.variables.update(TFR_EST_pm_party=2),
            'other_mandate': lambda r: r.variables.update(TFR_EST_mandate_party=2),
            'no_reform_partner': lambda r: r.variables.update(TFR_EST_coalition_reform=0),
            'wrong_assembly': lambda r: r.flags.discard('TFR_EST_reform_2023_mandate'),
            'ended_mandate': lambda r: r.flags.add('TFR_EST_reform_2023_mandate_ended'),
            'not_eu': lambda r: r.dynamic.discard('EU_member_dynamic'),
            'already_departed': lambda r: r.flags.add(CAREER),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                r = self.runtime()
                mutate(r)
                self.assertFalse(self.eligible(r))
                r.call('TFR_EST_reform_handover_tick')
                self.assertFalse(r.events)

    def test_invalidated_notice_is_cleared_and_retried(self):
        r = self.runtime()
        r.call('TFR_EST_reform_handover_tick')
        r.flags.add('TFR_EST_caretaker')
        self.assertFalse(r.condition(self.event().get('trigger')))
        r.call('TFR_EST_reform_handover_tick')
        self.assertNotIn(PENDING, r.flags)
        r.flags.discard('TFR_EST_caretaker')
        r.call('TFR_EST_reform_handover_tick')
        self.assertEqual(r.events, [EVENT, EVENT])

    def test_delivered_event_rechecks_before_switching(self):
        r = self.runtime()
        r.call('TFR_EST_reform_handover_tick')
        r.variables['TFR_EST_pm_party'] = 2
        self.assertFalse(r.condition(self.event().get('trigger')))
        r.call('TFR_EST_complete_reform_handover')
        self.assertNotIn(CAREER, r.flags)
        self.assertNotIn(MICHAL, r.ideas)
        r.variables['TFR_EST_pm_party'] = 1
        r.dynamic.discard('EU_member_dynamic')
        r.call('TFR_EST_complete_reform_handover')
        self.assertNotIn(CAREER, r.flags)

    def test_event_changes_only_person_and_keeps_assembly_and_rewards(self):
        r = self.runtime()
        r.call('TFR_EST_reform_handover_tick')
        variables = r.variables.copy()
        ideas = r.ideas.copy()
        president = r.leader
        politics = r.politics.copy()
        self.assertTrue(r.condition(self.event().get('trigger')))
        r.run(self.event().get('option').get('hidden_effect'))
        self.assertIn(CAREER, r.flags)
        self.assertIn(PERSON, r.flags)
        self.assertNotIn(PENDING, r.flags)
        self.assertEqual(r.variables, variables)
        self.assertEqual(r.politics, politics)
        self.assertEqual(r.leader, president)
        self.assertEqual(r.ideas, ideas - {KALLAS} | {MICHAL})
        self.assertNotIn('TFR_EST_caretaker', r.flags)

    def test_handover_and_display_repair_are_repeat_safe(self):
        r = self.runtime()
        r.call('TFR_EST_complete_reform_handover')
        expected = (r.variables.copy(), r.flags.copy(), r.ideas.copy())
        for _ in range(3):
            r.call('TFR_EST_complete_reform_handover')
            r.call('TFR_EST_reform_handover_tick')
            r.call('TFR_EST_reconcile_executive_display')
        self.assertEqual((r.variables, r.flags, r.ideas), expected)
        self.assertFalse(r.events)

    def test_next_reform_mandate_and_confidence_recovery_keep_michal(self):
        r = self.runtime()
        r.call('TFR_EST_complete_reform_handover')
        r.flags.discard('TFR_EST_reform_2023_mandate')
        r.flags.add('TFR_EST_caretaker')
        r.call('TFR_EST_clear_pm_person_markers')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MICHAL, r.ideas)
        r.flags.discard('TFR_EST_caretaker')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MICHAL, r.ideas)
        self.assertNotIn(KALLAS, r.ideas)

    def test_other_party_then_reform_returns_to_michal(self):
        r = self.runtime()
        r.call('TFR_EST_complete_reform_handover')
        r.variables['TFR_EST_pm_party'] = 2
        r.call('TFR_EST_reconcile_executive_display')
        self.assertNotIn(MICHAL, r.ideas)
        self.assertNotIn(PERSON, r.flags)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertIn(CAREER, r.flags)
        r.variables['TFR_EST_pm_party'] = 1
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MICHAL, r.ideas)
        self.assertIn(PERSON, r.flags)

    def test_occupation_preserves_career_without_overwriting_parent_leader(self):
        r = self.runtime()
        r.call('TFR_EST_complete_reform_handover')
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.leader = 'EST_yana_toom_char'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertNotIn(MICHAL, r.ideas)
        self.assertNotIn(PERSON, r.flags)
        self.assertIn(CAREER, r.flags)
        self.assertEqual(r.leader, 'EST_yana_toom_char')
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MICHAL, r.ideas)

    def test_pm_name_prefers_michal_only_after_departure(self):
        definitions = parse((ROOT / 'common/scripted_localisation/TFR_EST_executive.txt').read_text())
        name = definitions.get('defined_text')
        def selected(r):
            return next(e.value.get('localization_key') for e in name.entries
                        if e.key == 'text' and r.condition(e.value.get('trigger')))
        r = self.runtime()
        self.assertEqual(selected(r), 'TFR_EST_kaja_kallas')
        r.call('TFR_EST_complete_reform_handover')
        self.assertEqual(selected(r), 'TFR_EST_kristen_michal')
        r.variables['TFR_EST_pm_party'] = 2
        self.assertEqual(selected(r), 'TFR_EST_juri_ratas')

    def test_michal_is_a_locked_native_head_minister(self):
        definition = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text()).get('ideas').get('head_minister').get(MICHAL)
        self.assertEqual(definition.get('available').get('always'), 'no')
        self.assertEqual(definition.get('allowed_to_remove').get('always'), 'no')
        self.assertEqual(definition.get('removal_cost'), '-1')
        self.assertEqual(definition.get('modifier').entries, [])
        r = self.runtime()
        self.assertFalse(r.condition(definition.get('visible')))
        r.call('TFR_EST_complete_reform_handover')
        self.assertTrue(r.condition(definition.get('visible')))

    def test_generated_files_are_reproducible_and_localisation_has_bom(self):
        for relative, content in outputs().items():
            encoding = 'utf-8-sig' if relative.endswith('.yml') else 'utf-8'
            self.assertEqual((ROOT / relative).read_bytes(), content.encode(encoding))


if __name__ == '__main__':
    unittest.main()

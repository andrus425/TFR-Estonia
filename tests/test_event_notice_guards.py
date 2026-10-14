"""Check event delivery guards; native scheduling and popup rendering are separate."""
from datetime import date
from fractions import Fraction
import unittest

from script_runtime import ROOT, Runtime, parse


CHOICE = 'tfr_estonia_opening.11'
CABINET = 'tfr_estonia_opening.12'
NOTICES = (
    (CHOICE, 'TFR_EST_porto_choice_pending', 'TFR_EST_porto_choice_presented'),
    (CABINET, 'TFR_EST_new_cabinet_notice_pending', 'TFR_EST_new_cabinet_notice_presented'),
)


class EventNoticeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'events/TFR_EST_opening.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        cls.events = {event.get('id'): event for event in tree.all('country_event')}

    def runtime(self, notice):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.props['date'] = date(2021, 1, 13)
        r.flags.add('TFR_EST_porto_investigation_seen')
        r.flags.add('TFR_EST_referendum_active')
        if notice == CABINET:
            r.call('TFR_EST_ratas_steps_back')
            r.variables['TFR_EST_reform_handover_days'] = Fraction(0)
        r.call('TFR_EST_opening_tick')
        self.assertEqual(r.events.count(notice), 1)
        return r

    def test_unanswered_presented_notice_does_not_requeue_after_timed_guard_expires(self):
        for event_id, queue_flag, presented_flag in NOTICES:
            with self.subTest(notice=event_id):
                r = self.runtime(event_id)
                event = self.events[event_id]
                self.assertTrue(r.condition(event.get('trigger')))
                r.run(event.get('immediate'))
                self.assertIn(presented_flag, r.flags)
                # This runtime deliberately does not expire timed flags.
                # Removing the queue guard models time continuing while the
                # player leaves the already delivered popup unanswered.
                for _ in range(8):
                    r.flags.discard(queue_flag)
                    r.call('TFR_EST_opening_tick')
                self.assertEqual(r.events.count(event_id), 1)
                if event_id == CHOICE:
                    self.assertNotIn('TFR_EST_porto_choice_resolved', r.flags)
                else:
                    self.assertIn('TFR_EST_reform_handover_pending', r.flags)
                    self.assertNotIn('TFR_EST_reform_centre_formed', r.flags)

    def test_presented_flag_blocks_an_already_queued_duplicate_at_delivery(self):
        for event_id, _, presented_flag in NOTICES:
            with self.subTest(notice=event_id):
                r = self.runtime(event_id)
                event = self.events[event_id]
                self.assertTrue(r.condition(event.get('trigger')))
                r.run(event.get('immediate'))
                self.assertIn(presented_flag, r.flags)
                self.assertFalse(r.condition(event.get('trigger')))

    def test_lost_unpresented_occupation_queue_retries_after_independence(self):
        for event_id, queue_flag, presented_flag in NOTICES:
            with self.subTest(notice=event_id):
                r = self.runtime(event_id)
                event = self.events[event_id]
                self.assertNotIn(presented_flag, r.flags)
                r.flags.add('TFR_EST_occupied')
                r.props['is_subject'] = 'yes'
                self.assertFalse(r.condition(event.get('trigger')))
                # The original queued event is dropped without executing
                # immediate. Its short-lived queue flag subsequently expires.
                r.flags.discard(queue_flag)
                for _ in range(3):
                    r.call('TFR_EST_opening_tick')
                self.assertEqual(r.events.count(event_id), 1)
                r.flags.discard('TFR_EST_occupied')
                r.props['is_subject'] = 'no'
                r.call('TFR_EST_opening_tick')
                self.assertEqual(r.events.count(event_id), 2)
                self.assertIn(queue_flag, r.flags)
                self.assertNotIn(presented_flag, r.flags)
                self.assertTrue(r.condition(event.get('trigger')))
                r.run(event.get('immediate'))
                r.flags.discard(queue_flag)
                r.call('TFR_EST_opening_tick')
                self.assertEqual(r.events.count(event_id), 2)

    def test_ordinary_confirmation_of_authorized_reform_handover_reconciles_pending_story(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.props['date'] = date(2021, 1, 13)
        r.flags.add('TFR_EST_porto_investigation_seen')
        r.call('TFR_EST_ratas_steps_back')
        r.flags.add('TFR_EST_scripted_cabinet_change')
        r.call('TFR_EST_nominate_reform')
        r.variables['TFR_EST_coalition_centre'] = Fraction(1)
        r.call('TFR_EST_recount_confidence')
        self.assertTrue(r.condition(r.triggers['TFR_EST_can_confirm_mandated_cabinet']))
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
        self.assertNotIn('TFR_EST_caretaker', r.flags)
        self.assertIn('TFR_EST_reform_handover_pending', r.flags)
        before = r.variables['TFR_EST_cohesion']
        r.call('TFR_EST_opening_tick')
        self.assertIn('TFR_EST_reform_centre_formed', r.flags)
        self.assertNotIn('TFR_EST_reform_handover_pending', r.flags)
        self.assertEqual(r.variables['TFR_EST_cohesion'], before)
        self.assertNotIn(CABINET, r.events)
        r.call('TFR_EST_opening_tick')
        self.assertNotIn(CABINET, r.events)


if __name__ == '__main__':
    unittest.main()

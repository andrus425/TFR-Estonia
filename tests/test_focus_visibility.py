"""Exercise authored layout invalidation without emulating the focus interface."""
from fractions import Fraction
from itertools import product
import unittest

from script_runtime import Block, ROOT, Runtime, parse


EFFECT = 'TFR_EST_refresh_focus_visibility'
SIGNATURE = 'TFR_EST_focus_visibility_signature'


def script(relative):
    path = ROOT / relative
    return parse(path.read_text(encoding='utf-8-sig'), str(path))


def has_entry(block, key, value):
    return any(entry.key == key and entry.value == value for _, entry in block.walk())


class FocusVisibilityTests(unittest.TestCase):
    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_campaign_stage=Fraction(0), TFR_EST_pm_party=Fraction(2),
                           TFR_EST_active_pp=Fraction(0))
        return r

    def test_first_refresh_records_signature_and_unchanged_calls_do_nothing(self):
        r = self.runtime()
        self.assertNotIn(SIGNATURE, r.variables)
        self.assertEqual(r.focus_layout_refreshes, 0)
        r.call(EFFECT)
        self.assertIn(SIGNATURE, r.variables)
        self.assertEqual(r.focus_layout_refreshes, 1)
        before = r.variables[SIGNATURE]
        for _ in range(5):
            r.call(EFFECT)
        self.assertEqual(r.variables[SIGNATURE], before)
        self.assertEqual(r.focus_layout_refreshes, 1)

    def test_every_visibility_input_refreshes_once_on_change_and_again_on_reversion(self):
        cases = (
            ('variable', 'TFR_EST_campaign_stage', Fraction(3)),
            ('variable', 'TFR_EST_pm_party', Fraction(1)),
            ('variable', 'TFR_EST_active_pp', Fraction(1)),
            ('property', 'has_war', 'yes'),
            *(('flag', flag, True) for flag in (
                'TFR_EST_opening_complete', 'TFR_EST_occupied', 'TFR_EST_caretaker',
                'TFR_EST_first_war_seen', 'TFR_EST_second_war_seen',
                'TFR_EST_restoration_pending',
                'TFR_EST_ratas_retained', 'TFR_EST_ratas_mandate_ended',
                'TFR_EST_referendum_failed', 'TFR_EST_reform_centre_formed',
                'TFR_EST_kallas_mandate_ended',
                'TFR_EST_reform_2023_mandate', 'TFR_EST_reform_2023_mandate_ended',
                'TFR_EST_opening_assembly_ended',
                'TFR_EST_ekre_2023_mandate', 'TFR_EST_ekre_2023_mandate_ended',
                'TFR_EST_centre_2023_mandate', 'TFR_EST_centre_2023_mandate_ended',
                'TFR_EST_isamaa_2023_mandate', 'TFR_EST_isamaa_2023_mandate_ended',
                'TFR_EST_sde_2023_mandate', 'TFR_EST_sde_2023_mandate_ended',
                'TFR_EST_e200_2023_mandate', 'TFR_EST_e200_2023_mandate_ended',
                'TFR_EST_pp_2023_mandate', 'TFR_EST_pp_2023_mandate_ended',
            )),
        )
        for kind, field, changed in cases:
            with self.subTest(input=field):
                r = self.runtime()
                r.call(EFFECT)
                original = (r.variables[SIGNATURE], r.variables["TFR_EST_focus_visibility_late_signature"])
                if kind == 'flag':
                    r.flags.add(field)
                else:
                    store = r.variables if kind == 'variable' else r.props
                    previous = store[field]
                    store[field] = changed
                r.call(EFFECT)
                self.assertNotEqual((r.variables[SIGNATURE], r.variables["TFR_EST_focus_visibility_late_signature"]), original)
                self.assertEqual(r.focus_layout_refreshes, 2)
                r.call(EFFECT)
                self.assertEqual(r.focus_layout_refreshes, 2)
                if kind == 'flag':
                    r.flags.discard(field)
                else:
                    store[field] = previous
                r.call(EFFECT)
                self.assertEqual((r.variables[SIGNATURE], r.variables["TFR_EST_focus_visibility_late_signature"]), original)
                self.assertEqual(r.focus_layout_refreshes, 3)

    def test_unrelated_poll_and_meter_changes_do_not_invalidate_layout(self):
        r = self.runtime()
        r.call(EFFECT)
        r.variables.update(TFR_EST_support_reform=Fraction(4000),
                           TFR_EST_cohesion=Fraction(75), TFR_EST_readiness=Fraction(60))
        r.call(EFFECT)
        self.assertEqual(r.focus_layout_refreshes, 1)

    def test_handover_visibility_bits_do_not_collide_with_caretaker_or_war_bits(self):
        # Different lifecycle states must invalidate allow_branch even when
        # a handover, an occupation callback and a war change arrive together.
        fields = ('TFR_EST_first_war_seen', 'TFR_EST_second_war_seen',
                  'TFR_EST_restoration_pending', 'TFR_EST_referendum_failed',
                  'TFR_EST_reform_centre_formed', 'TFR_EST_kallas_mandate_ended',
                  'TFR_EST_caretaker')
        signatures = set()
        r = self.runtime()
        for values in product((False, True), repeat=len(fields) + 1):
            r.flags.difference_update(fields)
            r.flags.update(field for field, enabled in zip(fields, values) if enabled)
            r.props['has_war'] = 'yes' if values[-1] else 'no'
            r.call(EFFECT)
            self.assertNotIn(r.variables[SIGNATURE], signatures, values)
            signatures.add(r.variables[SIGNATURE])

    def test_foreign_country_cannot_record_or_refresh_estonian_layout(self):
        r = self.runtime()
        r.props['tag'] = 'GER'
        before = (r.variables.copy(), r.temp.copy(), r.flags.copy())
        r.call(EFFECT)
        self.assertEqual((r.variables, r.temp, r.flags), before)
        self.assertEqual(r.focus_layout_refreshes, 0)

    def test_entering_caretaker_calls_visibility_controller_without_repeated_refresh(self):
        r = self.runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.call(EFFECT)
        before = r.focus_layout_refreshes
        r.call('TFR_EST_enter_caretaker')
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(r.focus_layout_refreshes, before + 1)
        r.call('TFR_EST_enter_caretaker')
        self.assertEqual(r.focus_layout_refreshes, before + 1)

    def test_daily_refresh_is_after_opening_story_reconciliation(self):
        actions = script('common/on_actions/TFR_EST_systems.txt').get('on_actions')
        daily = actions.get('on_daily_EST').get('effect')
        guarded = daily.get('if')
        effects = [entry.key for entry in guarded.entries]
        self.assertIn('TFR_EST_opening_tick', effects)
        self.assertIn(EFFECT, effects)
        self.assertGreater(effects.index(EFFECT), effects.index('TFR_EST_opening_tick'))

    def test_visibility_gates_do_not_become_unrelated_focus_availability_requirements(self):
        tree = script('common/national_focus/TFR_EST_normal.txt').get('focus_tree')
        focuses = {focus.get('id'): focus for focus in tree.all('focus')}
        self.assertTrue(focuses)
        for focus_id, focus in focuses.items():
            with self.subTest(focus=focus_id):
                branch = focus.get('allow_branch')
                available = focus.get('available')
                self.assertIsInstance(branch, Block)
                self.assertIsInstance(available, Block)
                self.assertTrue(has_entry(branch, 'has_country_flag', 'TFR_EST_opening_complete'))
                self.assertFalse(has_entry(available, 'has_country_flag', 'TFR_EST_opening_complete'))
        # War and restoration predicates are gameplay gates and must remain
        # in availability as well as their matching hidden-branch condition.
        for focus_id, flag in (
            ('TFR_EST_first_emergency', 'TFR_EST_first_war_seen'),
            ('TFR_EST_second_emergency', 'TFR_EST_second_war_seen'),
            ('TFR_EST_restored_authority', 'TFR_EST_restoration_pending'),
        ):
            with self.subTest(crisis_focus=focus_id):
                focus = focuses[focus_id]
                self.assertTrue(has_entry(focus.get('allow_branch'), 'has_country_flag', flag))
                self.assertTrue(has_entry(focus.get('available'), 'has_country_flag', flag))
        for focus_id in ('TFR_EST_reconstruction_audit', 'TFR_EST_second_settlement'):
            with self.subTest(settlement_focus=focus_id):
                focus = focuses[focus_id]
                self.assertTrue(has_entry(focus.get('allow_branch'), 'has_war', 'no'))
                self.assertTrue(has_entry(focus.get('available'), 'has_war', 'no'))


if __name__ == '__main__':
    unittest.main()

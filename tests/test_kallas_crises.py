"""Successor-cabinet COVID gates and shared, non-stacking energy mitigation.

These checks execute the real country effects and five-tier parent predicate.
They do not simulate event delivery, focus scheduling, UI or saved-game files.
"""
from fractions import Fraction
from itertools import product
import unittest

from script_runtime import ROOT, Runtime, parse


FACTORY = 'TFR_EST_economy_industrial_capacity_factory_var'
GOODS = 'TFR_EST_economy_consumer_goods_factor_var'
FACTORY_APPLIED = 'TFR_EST_energy_factory_applied'
GOODS_APPLIED = 'TFR_EST_energy_goods_applied'
ONSET = 'SAU_saudi_civil_war_global'
RESOLUTION = 'SAU_saudi_civil_war_over_global'
TIERS = ('lower_covid_cases', 'low_covid_cases', 'medium_covid_cases',
         'high_covid_cases', 'higher_covid_cases')
RECORDED = 'TFR_EST_covid_first_case_recorded'
OWNED = 'TFR_EST_covid_seed_owned'
COVID_POLICIES = ('sick_pay', 'hospital_support', 'frontline_vaccination')
COVID_DONE = {'TFR_EST_done_kallas_' + suffix for suffix in COVID_POLICIES}
PROJECTS = ('energy_households', 'energy_networks', 'gas_reserve', 'lng_connection')
SUPPLY_SLOTS = (
    ('ratas_lng_connection', 'kallas_lng_connection'),
    ('ratas_grid_synchronisation', 'kallas_gas_reserve'),
    ('ratas_renewable_chp', 'kallas_energy_networks'),
)
GOODS_SLOTS = (
    ('ratas_building_renovation', 'kallas_energy_households'),
    ('ratas_network_charge_relief', 'kallas_energy_networks'),
)


class KallasCrisisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'common/national_focus/TFR_EST_kallas.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        cls.focuses = {focus.get('id'): focus for focus in tree.all('shared_focus')}

    def runtime(self, root_completed=True):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=Fraction(55), TFR_EST_readiness=Fraction(25))
        r.call('TFR_EST_initialize_parliament')
        r.flags.update({'TFR_EST_ratas_resigned', 'TFR_EST_referendum_failed',
                        'TFR_EST_opening_complete', 'TFR_EST_reform_centre_formed', RECORDED})
        r.flags.add('TFR_EST_scripted_cabinet_change')
        r.call('TFR_EST_nominate_reform')
        r.variables['TFR_EST_coalition_centre'] = Fraction(1)
        r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_confirm_cabinet')
        if root_completed:
            r.flags.add('TFR_EST_done_kallas_govern_together')
        r.call('TFR_EST_initialize_country_modifiers')
        r.variables[FACTORY] = Fraction(7, 100)
        r.variables[GOODS] = Fraction(-2, 100)
        r.call('TFR_EST_reconcile_energy_crisis')
        return r

    def reconcile(self, r):
        r.call('TFR_EST_reconcile_energy_crisis')

    def assert_contribution(self, r, factory, goods):
        factory, goods = Fraction(factory), Fraction(goods)
        self.assertEqual(r.variables[FACTORY_APPLIED], factory)
        self.assertEqual(r.variables[GOODS_APPLIED], goods)
        self.assertEqual(r.variables[FACTORY], Fraction(7, 100) + factory)
        self.assertEqual(r.variables[GOODS], Fraction(-2, 100) + goods)

    def test_case_interventions_require_actual_domestic_cases_instead_of_world_news(self):
        for idea in (*TIERS, None):
            r = self.runtime()
            if idea:
                r.ideas.add(idea)
            r.global_flags.add('COVID19_pandemic')
            r.flags.add('TFR_EST_opening_covid_announced')
            with self.subTest(tier=idea):
                for suffix in COVID_POLICIES:
                    self.assertEqual(r.condition(self.focuses['TFR_EST_kallas_' + suffix].get('available')),
                                     idea is not None, suffix)
                self.assertTrue(r.condition(self.focuses['TFR_EST_kallas_covid_certificates'].get('available')),
                                'The institutional certificate policy remains after recovery')

    def test_recovered_outbreak_skips_only_emergency_policies_without_rewards(self):
        r = self.runtime()
        before = (r.variables.copy(), r.calls.copy(), r.ideas.copy())
        r.call('TFR_EST_kallas_tick')
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertNotIn('TFR_EST_done_kallas_covid_certificates', r.flags)
        self.assertNotIn('TFR_EST_done_kallas_mental_health', r.flags)
        self.assertEqual((r.variables, r.calls, r.ideas), before)
        r.call('TFR_EST_kallas_tick')
        self.assertEqual((r.variables, r.calls, r.ideas), before)

    def test_skipped_emergency_rewards_cannot_be_claimed_by_direct_completion_later(self):
        r = self.runtime()
        r.call('TFR_EST_kallas_tick')
        before = (r.variables.copy(), r.calls.copy(), r.ideas.copy())
        for suffix in COVID_POLICIES:
            r.run(self.focuses['TFR_EST_kallas_' + suffix].get('completion_reward'))
        self.assertEqual((r.variables, r.calls, r.ideas), before)

    def test_recovery_bypass_requires_a_revealed_independent_started_programme(self):
        for blocked in ('resigned', 'failed', 'ended', 'occupied', 'subject',
                        'opening', 'root', 'recorded', 'uninitialized', 'foreign'):
            r = self.runtime()
            if blocked in ('resigned', 'failed', 'opening', 'root', 'recorded', 'uninitialized'):
                r.flags.discard({'resigned': 'TFR_EST_ratas_resigned',
                                 'failed': 'TFR_EST_referendum_failed',
                                 'opening': 'TFR_EST_opening_complete',
                                 'root': 'TFR_EST_done_kallas_govern_together',
                                 'recorded': RECORDED, 'uninitialized': 'TFR_EST_initialized'}[blocked])
            elif blocked in ('ended', 'occupied'):
                r.flags.add('TFR_EST_kallas_mandate_ended' if blocked == 'ended' else 'TFR_EST_occupied')
            elif blocked == 'subject':
                r.props['is_subject'] = 'yes'
            else:
                r.props['tag'] = 'LAT'
            with self.subTest(blocked=blocked):
                r.call('TFR_EST_kallas_tick')
                self.assertTrue(COVID_DONE.isdisjoint(r.flags))
                self.assertFalse(r.calls)

    def test_native_completed_entry_focus_also_allows_recovered_case_bypass(self):
        r = self.runtime(root_completed=False)
        r.props['completed_focuses'].add('TFR_EST_kallas_govern_together')
        r.call('TFR_EST_kallas_tick')
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertFalse(r.calls)

    def test_each_active_case_tier_prevents_the_recovery_bypass(self):
        for tier in TIERS:
            r = self.runtime()
            r.ideas.add(tier)
            with self.subTest(tier=tier):
                r.call('TFR_EST_kallas_tick')
                self.assertTrue(COVID_DONE.isdisjoint(r.flags))
                self.assertEqual(r.ideas.intersection(TIERS), {tier})
                self.assertFalse(r.calls)

    def test_frontline_vaccination_improves_existing_severity_only_once(self):
        r = self.runtime()
        r.ideas.update({'higher_covid_cases', 'TFR_EST_total_defence'})
        reward = self.focuses['TFR_EST_kallas_frontline_vaccination'].get('completion_reward')
        r.run(reward)
        self.assertEqual(r.ideas.intersection(TIERS), {'high_covid_cases'})
        self.assertIn('TFR_EST_total_defence', r.ideas)
        self.assertEqual(len(r.calls), 1)
        self.assertEqual(r.calls[0][0], 'add_debt_with_inflation')
        self.assertGreater(r.calls[0][1], 0)
        before = (r.variables.copy(), r.flags.copy(), r.ideas.copy(), r.calls.copy())
        r.run(reward)
        self.assertEqual((r.variables, r.flags, r.ideas, r.calls), before)

    def test_vaccinating_owned_lowest_tier_recovers_without_bridge_reinfection(self):
        r = self.runtime()
        r.ideas.add(TIERS[0])
        r.flags.add(OWNED)
        r.run(self.focuses['TFR_EST_kallas_frontline_vaccination'].get('completion_reward'))
        r.call('TFR_EST_kallas_tick')
        r.call('TFR_EST_covid_tick')
        self.assertFalse(r.ideas.intersection(TIERS))
        self.assertNotIn(OWNED, r.flags)
        self.assertIn(RECORDED, r.flags)
        self.assertTrue(COVID_DONE.issubset(r.flags))
        self.assertFalse(r.events)

    def test_external_lowest_tier_is_not_removed_as_an_owned_estonian_seed(self):
        r = self.runtime()
        r.ideas.add(TIERS[0])
        r.run(self.focuses['TFR_EST_kallas_frontline_vaccination'].get('completion_reward'))
        self.assertEqual(r.ideas.intersection(TIERS), {TIERS[0]})
        self.assertNotIn(OWNED, r.flags)

    def test_successor_government_receives_shared_energy_shock_without_ratas_choice(self):
        r = self.runtime()
        self.assertNotIn('TFR_EST_ratas_retained', r.flags)
        r.global_flags.add(ONSET)
        # The daily bridge calls this existing common reconciler before the
        # successor's recovery tick; its name does not restrict the government.
        r.call('TFR_EST_ratas_tick')
        r.call('TFR_EST_kallas_tick')
        self.assert_contribution(r, '-0.04', '0.03')
        self.assertEqual(r.events, ['tfr_estonia_ratas.1'])
        for _ in range(5):
            r.call('TFR_EST_ratas_tick')
            r.call('TFR_EST_kallas_tick')
        self.assert_contribution(r, '-0.04', '0.03')
        self.assertEqual(r.events, ['tfr_estonia_ratas.1'])

    def test_each_kallas_energy_policy_mitigates_its_promised_portion_of_shock(self):
        cases = {'energy_households': ('-0.04', '0.015'),
                 'energy_networks': ('-0.03', '0.015'),
                 'gas_reserve': ('-0.03', '0.03'),
                 'lng_connection': ('-0.03', '0.03')}
        for suffix, (factory, goods) in cases.items():
            r = self.runtime()
            r.global_flags.add(ONSET)
            r.flags.add('TFR_EST_done_kallas_' + suffix)
            with self.subTest(policy=suffix):
                self.reconcile(r)
                self.assert_contribution(r, factory, goods)

    def test_equivalent_project_flags_from_both_routes_do_not_double_count_a_slot(self):
        for group, slots in (('factory', SUPPLY_SLOTS), ('goods', GOODS_SLOTS)):
            for pair in slots:
                for enabled in ((True, False), (False, True), (True, True)):
                    r = self.runtime()
                    r.global_flags.add(ONSET)
                    r.flags.update('TFR_EST_done_' + flag for flag, active in zip(pair, enabled) if active)
                    self.reconcile(r)
                    with self.subTest(group=group, pair=pair, enabled=enabled):
                        if group == 'factory':
                            self.assertEqual(r.variables[FACTORY_APPLIED], Fraction(-3, 100))
                        else:
                            self.assertEqual(r.variables[GOODS_APPLIED], Fraction(15, 1000))

    def test_all_mixed_route_flags_keep_mitigation_at_the_same_limit(self):
        slots = (*SUPPLY_SLOTS, *GOODS_SLOTS)
        # Select either government's implementation for every shared slot.
        # energy_networks legitimately serves one supply and one consumer slot.
        for choices in product((0, 1), repeat=len(slots)):
            r = self.runtime()
            r.global_flags.add(ONSET)
            r.flags.update('TFR_EST_done_' + slot[choice] for slot, choice in zip(slots, choices))
            with self.subTest(choices=choices):
                self.reconcile(r)
                self.assert_contribution(r, '-0.01', 0)
                for slot in slots:
                    r.flags.update('TFR_EST_done_' + flag for flag in slot)
                self.reconcile(r)
                self.assert_contribution(r, '-0.01', 0)

    def test_preparation_before_parent_crisis_becomes_effective_at_onset(self):
        r = self.runtime()
        r.flags.update('TFR_EST_done_kallas_' + suffix for suffix in PROJECTS)
        self.reconcile(r)
        self.assert_contribution(r, 0, 0)
        self.assertFalse(r.events)
        r.global_flags.add(ONSET)
        self.reconcile(r)
        self.assert_contribution(r, '-0.01', 0)

    def test_crisis_resolution_preserves_permanent_reforms_and_prepared_projects(self):
        r = self.runtime()
        r.global_flags.add(ONSET)
        self.reconcile(r)
        r.flags.add('TFR_EST_done_kallas_energy_households')
        r.variables[FACTORY] += Fraction(15, 1000)
        r.variables[GOODS] -= Fraction(1, 100)
        self.reconcile(r)
        r.global_flags.add(RESOLUTION)
        self.reconcile(r)
        self.assertEqual(r.variables[FACTORY], Fraction(85, 1000))
        self.assertEqual(r.variables[GOODS], Fraction(-3, 100))
        self.assertEqual(r.variables[FACTORY_APPLIED], 0)
        self.assertEqual(r.variables[GOODS_APPLIED], 0)
        self.assertIn('TFR_EST_done_kallas_energy_households', r.flags)
        self.assertEqual(r.global_flags, {ONSET, RESOLUTION})

    def test_persisted_energy_contribution_repairs_without_stacking_after_reload(self):
        r = self.runtime()
        r.global_flags.add(ONSET)
        r.flags.update('TFR_EST_done_kallas_' + suffix for suffix in PROJECTS)
        self.reconcile(r)
        loaded = Runtime()
        loaded.variables = r.variables.copy()
        loaded.flags = r.flags.copy()
        loaded.global_flags = r.global_flags.copy()
        self.reconcile(loaded)
        self.assertEqual(loaded.variables, r.variables)
        self.assertFalse(loaded.events)
        loaded.global_flags.add(RESOLUTION)
        self.reconcile(loaded)
        self.assert_contribution(loaded, 0, 0)


if __name__ == '__main__':
    unittest.main()

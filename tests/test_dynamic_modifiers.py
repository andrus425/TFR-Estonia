"""Country modifier foundation, without migrating existing focus rewards."""
from fractions import Fraction
import hashlib
import unittest

from script_runtime import ROOT, Runtime
from clausewitz import Block, parse


MODIFIER_FIELDS = {
    'economy': (
        'production_speed_buildings_factor',
        'industrial_capacity_factory',
        'industrial_capacity_dockyard',
        'production_factory_efficiency_gain_factor',
        'production_factory_max_efficiency_factor',
        'research_speed_factor',
        'local_resources_factor',
        'consumer_goods_factor',
    ),
    'military': (
        'army_attack_factor',
        'army_defence_factor',
        'army_org_factor',
        'mobilization_speed',
        'training_time_army_factor',
        'dig_in_speed_factor',
        'attrition',
        'supply_consumption_factor',
    ),
}
MODIFIERS = {'TFR_EST_economy_dynamic', 'TFR_EST_military_dynamic'}
VARIABLES = {
    f'TFR_EST_{category}_{field}_var'
    for category, fields in MODIFIER_FIELDS.items()
    for field in fields
}
FOCUS_BASELINE = {
    'TFR_EST_occupation.txt': 'e0fd40ae1e48e8e355a2baba6b455625395c11be2c41141f6376c722aed5ffed',
    'TFR_national_focus_SOV_communist_new.txt': 'd266e91326f5e4ec4d67369c1901b4b58531f3c084a56e59918a9f88a1f512aa',
}


class DynamicModifierTests(unittest.TestCase):
    def test_new_estonia_starts_with_two_neutral_modifiers(self):
        runtime = Runtime()
        runtime.call('TFR_EST_initialize_country_modifiers')
        self.assertEqual(runtime.dynamic, MODIFIERS)
        self.assertTrue(VARIABLES.issubset(runtime.variables))
        for variable in VARIABLES:
            with self.subTest(variable=variable):
                self.assertEqual(runtime.variables[variable], 0)

    def test_missing_variable_repair_preserves_each_authored_value(self):
        runtime = Runtime()
        # A mixture of economic bonuses and military penalties catches a reset
        # that would otherwise be invisible with an entirely zero baseline.
        expected = {}
        for index, variable in enumerate(sorted(VARIABLES)):
            if index % 2:
                expected[variable] = Fraction(index + 1, -100 if index % 3 else 100)
                runtime.variables[variable] = expected[variable]
            else:
                expected[variable] = Fraction(0)
        runtime.call('TFR_EST_initialize_country_modifiers')
        self.assertEqual({v: runtime.variables[v] for v in VARIABLES}, expected)

    def test_repeat_initialization_does_not_reapply_or_stack_modifiers(self):
        runtime = Runtime()
        runtime.call('TFR_EST_initialize_country_modifiers')
        first_additions = list(runtime.dynamic_additions)
        for _ in range(5):
            runtime.call('TFR_EST_initialize_country_modifiers')
        self.assertCountEqual(first_additions, MODIFIERS)
        self.assertEqual(runtime.dynamic_additions, first_additions)
        self.assertEqual(runtime.dynamic, MODIFIERS)

    def test_refresh_repairs_only_missing_modifier_without_resetting_values(self):
        runtime = Runtime()
        runtime.call('TFR_EST_initialize_country_modifiers')
        runtime.variables['TFR_EST_economy_research_speed_factor_var'] = Fraction(7, 100)
        runtime.variables['TFR_EST_military_supply_consumption_factor_var'] = Fraction(-9, 100)
        expected = runtime.variables.copy()
        first_additions = list(runtime.dynamic_additions)
        runtime.dynamic.remove('TFR_EST_military_dynamic')
        runtime.call('TFR_EST_refresh_country_modifiers')
        self.assertEqual(runtime.variables, expected)
        self.assertEqual(runtime.dynamic, MODIFIERS)
        self.assertEqual(runtime.dynamic_additions, first_additions + ['TFR_EST_military_dynamic'])

    def test_non_estonia_scope_cannot_initialize_or_refresh(self):
        for tag in ('GER', 'SOV', 'LAT'):
            for effect in ('TFR_EST_initialize_country_modifiers', 'TFR_EST_refresh_country_modifiers'):
                with self.subTest(tag=tag, effect=effect):
                    runtime = Runtime()
                    runtime.props['tag'] = tag
                    runtime.call(effect)
                    self.assertFalse(runtime.dynamic)
                    self.assertFalse(runtime.variables)
                    self.assertFalse(runtime.dynamic_additions)

    def test_definition_fields_bind_to_separate_persistent_variables(self):
        path = ROOT / 'common/dynamic_modifiers/TFR_EST_country.txt'
        tree = parse(path.read_text(encoding='utf-8-sig'), str(path))
        self.assertEqual({entry.key for entry in tree.entries}, MODIFIERS)
        for category, fields in MODIFIER_FIELDS.items():
            with self.subTest(category=category):
                definition = tree.get(f'TFR_EST_{category}_dynamic')
                self.assertIsInstance(definition, Block)
                bound_fields = {entry.key: entry.value for entry in definition.entries
                                if entry.key not in {'icon', 'enable', 'remove_trigger'} }
                self.assertEqual(bound_fields, {
                    field: f'TFR_EST_{category}_{field}_var' for field in fields
                })
                self.assertEqual(definition.get('enable').get('tag'), 'EST')

    def test_foundation_preserves_existing_focus_and_cabinet_reward_ideas(self):
        runtime = Runtime()
        existing = {
            'TFR_EST_maintenance_network', 'TFR_EST_total_defence',
            'TFR_EST_reform_cabinet', 'TFR_EST_readiness_developing',
        }
        runtime.ideas.update(existing)
        runtime.call('TFR_EST_initialize_country_modifiers')
        runtime.call('TFR_EST_refresh_country_modifiers')
        self.assertEqual(runtime.ideas, existing)

    def test_estonia_modifier_initialization_does_not_touch_parent_dynamic_modifiers(self):
        runtime = Runtime()
        runtime.dynamic.update({'economy_dynamic_modifier', 'GER_army_dynamic_modifier'})
        runtime.call('TFR_EST_initialize_country_modifiers')
        self.assertEqual(runtime.dynamic, MODIFIERS | {'economy_dynamic_modifier', 'GER_army_dynamic_modifier'})

    def test_occupation_and_parent_trees_match_the_current_baseline(self):
        for name, expected in FOCUS_BASELINE.items():
            with self.subTest(tree=name):
                actual = hashlib.sha256((ROOT / 'common/national_focus' / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

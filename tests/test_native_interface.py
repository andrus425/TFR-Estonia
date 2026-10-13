import unittest

from script_runtime import Runtime, parse
from native_script_interface import amount_call, native_amount_calls, native_definitions


class NativeInterfaceTests(unittest.TestCase):
    def test_argument_block_is_rejected_by_script_execution(self):
        r = Runtime()
        with self.assertRaisesRegex(AssertionError, "cannot accept an argument block"):
            r.run(parse("TFR_EST_change_cohesion = { AMOUNT = 4 }"))

    def test_migration_preserves_input_order_and_native_behavior(self):
        old = "hidden_effect = {\n    TFR_EST_change_cohesion = { AMOUNT = -10 }\n    TFR_EST_change_readiness = { AMOUNT = 7 }\n}"
        converted = native_amount_calls(old)
        self.assertNotIn("AMOUNT", converted)
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.run(parse(converted))
        self.assertEqual(r.variables["TFR_EST_cohesion"], 45)
        self.assertEqual(r.variables["TFR_EST_readiness"], 32)

    def test_indented_definitions_can_be_migrated_in_any_order(self):
        source = '''    TFR_EST_change_readiness = { add_to_variable = { var = TFR_EST_readiness value = $AMOUNT$ } }
    TFR_EST_change_cohesion = { add_to_variable = { var = TFR_EST_cohesion value = $AMOUNT$ } }
    unrelated = { log = "$AMOUNT$ stays here" }
'''
        converted = native_definitions(source)
        self.assertIn("value = TFR_EST_readiness_delta", converted)
        self.assertIn("value = TFR_EST_cohesion_delta", converted)
        self.assertIn('log = "$AMOUNT$ stays here"', converted)
        self.assertEqual(native_definitions(converted), converted)


if __name__ == "__main__":
    unittest.main()

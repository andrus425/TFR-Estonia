"""Create an ignored, temporary country-history arithmetic QA overlay.

The engine executes country history while building its 2020 frontend snapshot,
so these cases exercise native scripted effects without UI automation. This is
not a natural campaign, combat simulation, save test or occupation settlement.
Diplomatic transitions and unit transfers require a running campaign, and must
not be invoked during country-history construction.
"""
from pathlib import Path
import json
import re
from native_script_interface import amount_call

ROOT = Path(__file__).resolve().parents[1]
PARTIES = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")


def check(name, conditions):
    return f'''if = {{
    limit = {{ {conditions} }}
    log = "TFR_EST_ENGINE_QA_PASS {name}"
}}
else = {{ log = "TFR_EST_ENGINE_QA_FAIL {name}" }}
'''


def polls(values, other=0):
    out = []
    for p, value in zip(PARTIES, values):
        out.extend((f"set_variable = {{ TFR_EST_active_{p} = 1 }}", f"set_variable = {{ TFR_EST_support_{p} = {value} }}"))
    out.append(f"set_variable = {{ TFR_EST_support_other = {other} }}")
    return "\n".join(out) + "\n"


def eq(variable, value):
    return f"check_variable = {{ var = {variable} value = {value} compare = equals }}"


def main():
    submod_descriptor = (ROOT / "descriptor.mod").read_text(encoding="utf-8-sig")
    submod_name = re.search(r'^\s*name\s*=\s*"([^"\n]+)"', submod_descriptor, re.M).group(1)
    base = ROOT / ".cache/engine_qa"
    (base / "history/countries").mkdir(parents=True, exist_ok=True)
    descriptor = f'''name="TFR Estonia Engine QA"
version="1.0.0"
supported_version="1.19.*"
dependencies={{"The Fire Rises" "{submod_name}"}}
path="{base.as_posix()}"
'''
    (base / "descriptor.mod").write_text(descriptor, encoding="utf-8")
    body = ["\n# Isolated native engine arithmetic assertions.\n",
            "log = \"TFR_EST_ENGINE_QA_BEGIN\"\n",
            "set_country_flag = TFR_EST_initialized\n",
            "set_variable = { TFR_EST_cohesion = 55 }\nset_variable = { TFR_EST_readiness = 25 }\n",
            "TFR_EST_initialize_parliament = yes\n",
            check("historical_101_and_57", eq("TFR_EST_coalition_seats", 57) + " " + eq("TFR_EST_seats_reform", 34) + " " + eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2)),
            polls((5000, 5000, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
            check("tie_51_50", eq("TFR_EST_seats_reform", 51) + " " + eq("TFR_EST_seats_centre", 50) + " " + eq("TFR_EST_mandate_party", 1) + " " + eq("TFR_EST_nominee_party", 1)),
            polls((500, 499, 3500, 2000, 1500, 1000, 0), other=1001), "TFR_EST_hold_election = yes\n",
            check("threshold_exact_five", eq("TFR_EST_seats_centre", 0) + " " + "check_variable = { var = TFR_EST_seats_reform value = 0 compare = greater_than } " + eq("TFR_EST_allocated", 101)),
            "set_variable = { TFR_EST_saved_seats_reform = TFR_EST_seats_reform }\n",
            "set_variable = { TFR_EST_support_reform = 10001 }\nTFR_EST_hold_election = yes\n",
            check("invalid_preserves_assembly", eq("TFR_EST_seats_reform", "TFR_EST_saved_seats_reform")),
            polls((1400, 1400, 1400, 1400, 1400, 1400, 1400), other=200), "TFR_EST_hold_election = yes\n",
            check("seven_party_remainders", eq("TFR_EST_allocated", 101) + " " + eq("TFR_EST_seats_reform", 15) + " " + eq("TFR_EST_seats_centre", 15) + " " + eq("TFR_EST_seats_ekre", 15) + " " + eq("TFR_EST_seats_pp", 14) + " " + eq("TFR_EST_mandate_party", 1)),
            "set_country_flag = TFR_EST_occupied\n", polls((10000, 0, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
            check("occupied_election_noop", eq("TFR_EST_seats_reform", 15)),
            "clr_country_flag = TFR_EST_occupied\n",
            amount_call("TFR_EST_change_cohesion", -1000) + "\n",
            amount_call("TFR_EST_change_readiness", 1000) + "\n",
            "log = \"TFR_EST_ENGINE_QA_METERS cohesion=[?TFR_EST_cohesion] readiness=[?TFR_EST_readiness]\"\n",
            check("meter_clamps", eq("TFR_EST_cohesion", 0) + " " + eq("TFR_EST_readiness", 100)),
            "set_variable = { TFR_EST_cohesion = 55 }\nset_variable = { TFR_EST_readiness = 25 }\nTFR_EST_refresh_meters = yes\nTFR_EST_initialize_parliament = yes\n",
            ]
    assertions = ["historical_101_and_57", "tie_51_50", "threshold_exact_five", "invalid_preserves_assembly", "seven_party_remainders", "occupied_election_noop", "meter_clamps"]
    body.extend([
        "TFR_EST_nominate_reform = yes\n",
        check("unapproved_nomination_noop", eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2) + " " + eq("TFR_EST_nominee_party", 2)),
        "set_variable = { TFR_EST_nominee_party = 1 }\nset_variable = { TFR_EST_coalition_reform = 1 }\nTFR_EST_recount_confidence = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("fabricated_nominee_rejected", eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2)),
        "TFR_EST_initialize_parliament = yes\nset_variable = { TFR_EST_coalition_ekre = 0 }\nTFR_EST_recount_confidence = yes\nTFR_EST_enter_caretaker = yes\nTFR_EST_ai_cabinet = yes\n",
        check("ai_confidence_recovery_keeps_centre", eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2) + " NOT = { has_country_flag = TFR_EST_caretaker }"),
        polls((3990, 3990, 2020, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        check("equal_seat_mandate_order", eq("TFR_EST_seats_reform", 40) + " " + eq("TFR_EST_seats_centre", 40) + " " + eq("TFR_EST_mandate_party", 1)),
        # Frontend country snapshots may run the AI's automatic coalition
        # formation. Build the equivalent player pending-cabinet state explicitly
        # before checking the confidence gate, while retaining the elected seats.
        "log = \"TFR_EST_ENGINE_QA_AUTOMATIC_CABINET pm=[?TFR_EST_pm_party] confidence=[?TFR_EST_confidence_seats] centre=[?TFR_EST_coalition_centre]\"\n",
        "TFR_EST_clear_coalition = yes\nset_variable = { TFR_EST_pm_party = 2 }\nset_variable = { TFR_EST_coalition_reform = 1 }\nTFR_EST_recount_confidence = yes\nset_country_flag = TFR_EST_electoral_handover\nTFR_EST_enter_caretaker = yes\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        "TFR_EST_confirm_cabinet = yes\n",
        check("minority_winner_waits_for_confidence", eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_nominee_party", 1) + " has_country_flag = TFR_EST_caretaker"),
        "set_variable = { TFR_EST_coalition_centre = 1 }\nTFR_EST_recount_confidence = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("elected_successor_confirmed", eq("TFR_EST_pm_party", 1) + " " + eq("TFR_EST_mandate_party", 1) + " NOT = { has_country_flag = TFR_EST_electoral_handover } NOT = { has_country_flag = TFR_EST_caretaker }"),
        "set_variable = { TFR_EST_support_reform = 10001 }\nTFR_EST_hold_election = yes\n",
        check("invalid_election_keeps_confirmed_mandate", eq("TFR_EST_pm_party", 1) + " " + eq("TFR_EST_mandate_party", 1) + " NOT = { has_country_flag = TFR_EST_electoral_handover }"),
        "TFR_EST_initialize_parliament = yes\n",
    ])
    assertions.extend(["unapproved_nomination_noop", "fabricated_nominee_rejected", "ai_confidence_recovery_keeps_centre", "equal_seat_mandate_order", "minority_winner_waits_for_confidence", "elected_successor_confirmed", "invalid_election_keeps_confirmed_mandate"])
    # Presentation effects are valid at history time: unlike diplomacy or unit
    # transfers, these only select already-recruited characters and minister ideas.
    body.append(check("president_and_opening_pm", "has_country_leader = { character = TFR_EST_kersti_kaljulaid ruling_only = yes } has_idea = TFR_EST_pm_centre has_country_flag = head_of_gov_ui_enabled " + eq("TFR_EST_pm_party", 2)))
    assertions.append("president_and_opening_pm")
    groups = ("market_liberal", "social_liberal", "authoritarian_democrat", "conservative", "social_democrat", "social_liberal", "market_liberal")
    for index, (party, group) in enumerate(zip(PARTIES, groups), 1):
        body.append(f"set_variable = {{ TFR_EST_pm_party = {index} }}\nTFR_EST_reconcile_cabinet_leadership = yes\n")
        name = "president_with_pm_" + party
        body.append(check(name, f"has_country_leader = {{ character = TFR_EST_kersti_kaljulaid ruling_only = yes }} has_idea = TFR_EST_pm_{party} has_government = {group}"))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_karis_president\nTFR_EST_reconcile_presidency = yes\n",
        check("presidential_handover_keeps_pm", "has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } has_idea = TFR_EST_pm_pp " + eq("TFR_EST_pm_party", 7)),
        "TFR_EST_enter_caretaker = yes\nTFR_EST_reconcile_executive_display = yes\n",
        check("caretaker_keeps_executive", "has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } has_idea = TFR_EST_pm_pp has_country_flag = TFR_EST_caretaker"),
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\nTFR_EST_reconcile_presidency = yes\n",
        check("occupation_hides_hog", "NOT = { has_country_flag = head_of_gov_ui_enabled } " + " ".join(f"NOT = {{ has_idea = TFR_EST_pm_{party} }}" for party in PARTIES) + " " + eq("TFR_EST_pm_party", 7)),
        "TFR_EST_restore_parliament = yes\n",
        check("restoration_restores_saved_executive", "has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } has_idea = TFR_EST_pm_pp has_country_flag = head_of_gov_ui_enabled has_country_flag = TFR_EST_caretaker"),
        "clr_country_flag = TFR_EST_karis_president\nclr_country_flag = TFR_EST_restoration_election\nclr_country_flag = TFR_EST_caretaker\nTFR_EST_initialize_parliament = yes\nTFR_EST_reconcile_presidency = yes\n",
    ])
    assertions.extend(["presidential_handover_keeps_pm", "caretaker_keeps_executive", "occupation_hides_hog", "restoration_restores_saved_executive"])
    # Native modifier values must follow persistent variables immediately, and
    # missing-membership repair must not reset previously authored adjustments.
    dynamic_ids = ("TFR_EST_economy_dynamic", "TFR_EST_military_dynamic")
    dynamic_present = " ".join(f"has_dynamic_modifier = {{ modifier = {name} }}" for name in dynamic_ids)
    body.extend([
        "TFR_EST_initialize_country_modifiers = yes\n",
        check("country_modifiers_neutral", dynamic_present + " " + eq("TFR_EST_economy_industrial_capacity_factory_var", 0) + " " + eq("TFR_EST_military_supply_consumption_factor_var", 0)),
        "set_variable = { TFR_EST_qa_factory_before = modifier@industrial_capacity_factory }\nset_variable = { TFR_EST_qa_supply_before = modifier@supply_consumption_factor }\n",
        "set_variable = { TFR_EST_economy_industrial_capacity_factory_var = 0.03 }\nset_variable = { TFR_EST_military_supply_consumption_factor_var = -0.05 }\nTFR_EST_refresh_country_modifiers = yes\n",
        "set_variable = { TFR_EST_qa_factory_delta = modifier@industrial_capacity_factory }\nsubtract_from_variable = { var = TFR_EST_qa_factory_delta value = TFR_EST_qa_factory_before }\nset_variable = { TFR_EST_qa_supply_delta = modifier@supply_consumption_factor }\nsubtract_from_variable = { var = TFR_EST_qa_supply_delta value = TFR_EST_qa_supply_before }\n",
        "log = \"TFR_EST_ENGINE_QA_DYNAMIC factory_delta=[?TFR_EST_qa_factory_delta] supply_delta=[?TFR_EST_qa_supply_delta]\"\n",
        check("country_modifier_values_apply", eq("TFR_EST_qa_factory_delta", 0.03) + " " + eq("TFR_EST_qa_supply_delta", -0.05)),
        "TFR_EST_initialize_country_modifiers = yes\nTFR_EST_initialize_country_modifiers = yes\n",
        check("country_modifier_reinit_preserves_values", dynamic_present + " " + eq("TFR_EST_economy_industrial_capacity_factory_var", 0.03) + " " + eq("TFR_EST_military_supply_consumption_factor_var", -0.05)),
        "remove_dynamic_modifier = { modifier = TFR_EST_economy_dynamic }\nTFR_EST_initialize_country_modifiers = yes\n",
        check("country_modifier_membership_repair", dynamic_present + " " + eq("TFR_EST_economy_industrial_capacity_factory_var", 0.03) + " " + eq("TFR_EST_military_supply_consumption_factor_var", -0.05)),
        "set_variable = { TFR_EST_economy_industrial_capacity_factory_var = 0 }\nset_variable = { TFR_EST_military_supply_consumption_factor_var = 0 }\nTFR_EST_refresh_country_modifiers = yes\n",
    ])
    assertions.extend(["country_modifiers_neutral", "country_modifier_values_apply", "country_modifier_reinit_preserves_values", "country_modifier_membership_repair"])
    body.extend([
        "TFR_EST_initialize_parliament = yes\n",
        check("opening_initial_coalition", "TFR_EST_opening_coalition_majority = yes NOT = { TFR_EST_can_start_referendum = yes } " + eq("TFR_EST_coalition_seats", 57)),
        "set_variable = { TFR_EST_coalition_ekre = 0 }\nset_variable = { TFR_EST_supply_reform = 1 }\nTFR_EST_recount_confidence = yes\n",
        check("opening_supply_cannot_replace_coalition", "NOT = { TFR_EST_coalition_majority = yes } " + eq("TFR_EST_coalition_seats", 38) + " " + eq("TFR_EST_confidence_seats", 72)),
        "TFR_EST_initialize_parliament = yes\nTFR_EST_snap_election = yes\n",
        check("snap_election_unapproved_noop", eq("TFR_EST_seats_reform", 34) + " " + eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_election_year", 2023)),
        "set_country_flag = TFR_EST_porto_investigation_seen\nTFR_EST_ratas_steps_back = yes\n",
        check("porto_ratas_caretaker", "has_country_flag = TFR_EST_caretaker has_country_flag = TFR_EST_reform_handover_pending NOT = { TFR_EST_can_confirm_mandated_cabinet = yes } " + eq("TFR_EST_pm_party", 2)),
        "TFR_EST_ai_cabinet = yes\nTFR_EST_confirm_cabinet = yes\nTFR_EST_form_reform_centre_cabinet = yes\n",
        check("porto_reform_centre_successor", "NOT = { has_country_flag = TFR_EST_caretaker } NOT = { has_country_flag = TFR_EST_reform_handover_pending } has_country_leader = { character = TFR_EST_kersti_kaljulaid ruling_only = yes } " + eq("TFR_EST_pm_party", 1) + " " + eq("TFR_EST_mandate_party", 1) + " " + eq("TFR_EST_coalition_seats", 60) + " " + eq("TFR_EST_seats_reform", 34) + " " + eq("TFR_EST_election_year", 2023)),
        "TFR_EST_initialize_parliament = yes\nclr_country_flag = TFR_EST_porto_choice_resolved\nclr_country_flag = TFR_EST_ratas_resigned\nclr_country_flag = TFR_EST_reform_centre_formed\nTFR_EST_keep_ratas = yes\n",
        check("porto_original_coalition_retained", "has_country_flag = TFR_EST_ratas_retained NOT = { has_country_flag = TFR_EST_caretaker } " + eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2) + " " + eq("TFR_EST_coalition_seats", 57)),
        "clr_country_flag = TFR_EST_porto_choice_resolved\nclr_country_flag = TFR_EST_ratas_retained\nclr_country_flag = TFR_EST_porto_investigation_seen\nTFR_EST_initialize_parliament = yes\n",
    ])
    assertions.extend(["opening_initial_coalition", "opening_supply_cannot_replace_coalition", "snap_election_unapproved_noop", "porto_ratas_caretaker", "porto_reform_centre_successor", "porto_original_coalition_retained"])
    body.append("log = \"TFR_EST_ENGINE_QA_END\"\n")
    source = (ROOT / "history/countries/EST - Estonia.txt").read_text(encoding="utf-8-sig")
    # Country history executes top-level commands independently. Keep native
    # temporary inputs and their consumers in one effect context, matching a
    # focus reward or decision complete_effect in an actual campaign.
    (base / "history/countries/EST - Estonia.txt").write_text(source + "\nhidden_effect = {\n" + "".join(body) + "\n}\n", encoding="utf-8")
    (base / "assertions.json").write_text(json.dumps(assertions), encoding="utf-8")
    print(json.dumps({"descriptor": str(base / "descriptor.mod"), "assertions": len(assertions), "campaign": False}))


if __name__ == "__main__": main()

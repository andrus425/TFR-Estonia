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
    # These generated idea-category cost modifiers are dynamic engine tokens.
    # Only the QA overlay reads them as modifier@ values; synchronize those
    # test-only lookup tokens rather than changing the parent's token file.
    token_directory = base / "common/synchronized_dynamic_tokens"
    token_directory.mkdir(parents=True, exist_ok=True)
    (token_directory / "TFR_EST_qa_minister_tokens.txt").write_text(
        "\n".join(slot + "_minister_cost_factor" for slot in
                  ("foreign", "economic", "interior", "intelligence", "theorist")) + "\n",
        encoding="utf-8")
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
        "clr_country_flag = TFR_EST_opening_assembly_ended\nclr_country_flag = TFR_EST_opening_complete\n",
        check("opening_initial_coalition", "TFR_EST_opening_coalition_majority = yes NOT = { TFR_EST_can_start_referendum = yes } " + eq("TFR_EST_coalition_seats", 57)),
        "set_variable = { TFR_EST_coalition_ekre = 0 }\nset_variable = { TFR_EST_supply_reform = 1 }\nTFR_EST_recount_confidence = yes\n",
        check("opening_supply_cannot_replace_coalition", "NOT = { TFR_EST_coalition_majority = yes } " + eq("TFR_EST_coalition_seats", 38) + " " + eq("TFR_EST_confidence_seats", 72)),
        "TFR_EST_initialize_parliament = yes\nTFR_EST_snap_election = yes\n",
        check("snap_election_unapproved_noop", eq("TFR_EST_seats_reform", 34) + " " + eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_election_year", 2023)),
        "set_country_flag = TFR_EST_porto_investigation_seen\nTFR_EST_ratas_steps_back = yes\n",
        check("porto_ratas_caretaker", "has_country_flag = TFR_EST_caretaker has_country_flag = TFR_EST_reform_handover_pending NOT = { TFR_EST_can_confirm_mandated_cabinet = yes } " + eq("TFR_EST_pm_party", 2)),
        "TFR_EST_ai_cabinet = yes\nTFR_EST_confirm_cabinet = yes\nTFR_EST_form_reform_centre_cabinet = yes\n",
        check("porto_reform_centre_successor", "NOT = { has_country_flag = TFR_EST_caretaker } NOT = { has_country_flag = TFR_EST_reform_handover_pending } has_country_leader = { character = TFR_EST_kersti_kaljulaid ruling_only = yes } " + eq("TFR_EST_pm_party", 1) + " " + eq("TFR_EST_mandate_party", 1) + " " + eq("TFR_EST_coalition_seats", 60) + " " + eq("TFR_EST_seats_reform", 34) + " " + eq("TFR_EST_election_year", 2023)),
        "TFR_EST_initialize_parliament = yes\nclr_country_flag = TFR_EST_porto_choice_resolved\nclr_country_flag = TFR_EST_ratas_resigned\nclr_country_flag = TFR_EST_reform_centre_formed\nclr_country_flag = TFR_EST_referendum_failed\nclr_country_flag = TFR_EST_opening_complete\nTFR_EST_keep_ratas = yes\n",
        check("porto_original_coalition_retained", "has_country_flag = TFR_EST_ratas_retained NOT = { has_country_flag = TFR_EST_caretaker } " + eq("TFR_EST_pm_party", 2) + " " + eq("TFR_EST_mandate_party", 2) + " " + eq("TFR_EST_coalition_seats", 57)),
        "clr_country_flag = TFR_EST_porto_choice_resolved\nclr_country_flag = TFR_EST_ratas_retained\nclr_country_flag = TFR_EST_porto_investigation_seen\nTFR_EST_initialize_parliament = yes\n",
    ])
    assertions.extend(["opening_initial_coalition", "opening_supply_cannot_replace_coalition", "snap_election_unapproved_noop", "porto_ratas_caretaker", "porto_reform_centre_successor", "porto_original_coalition_retained"])
    # The frontend date is 1 January 2020, so do not spoof dates or trigger the
    # guarded first-case seeding event. Exercise the actual parent infection
    # trigger and response helper with isolated idea fixtures instead.
    covid_tiers = ("lower_covid_cases", "low_covid_cases", "medium_covid_cases", "high_covid_cases", "higher_covid_cases")
    for tier in covid_tiers:
        body.append(f"if = {{ limit = {{ has_idea = {tier} }} set_country_flag = TFR_EST_qa_saved_{tier} }}\nremove_ideas = {tier}\n")
    body.extend([
        "if = { limit = { has_country_flag = TFR_EST_opening_covid_announced } set_country_flag = TFR_EST_qa_saved_covid_announced }\nclr_country_flag = TFR_EST_opening_covid_announced\n",
        "TFR_EST_begin_covid_response = yes\n",
        check("covid_absent_blocks_response", "NOT = { generic_has_corona = yes } NOT = { has_country_flag = TFR_EST_opening_covid_announced }"),
        "set_variable = { TFR_EST_qa_covid_tiers_detected = 0 }\n",
    ])
    for tier in covid_tiers:
        body.append(f"add_ideas = {tier}\nif = {{ limit = {{ generic_has_corona = yes has_idea = {tier} }} add_to_variable = {{ TFR_EST_qa_covid_tiers_detected = 1 }} }}\nremove_ideas = {tier}\n")
    body.extend([
        check("covid_all_five_parent_tiers_detected", eq("TFR_EST_qa_covid_tiers_detected", 5) + " NOT = { generic_has_corona = yes }"),
        "add_ideas = lower_covid_cases\nTFR_EST_begin_covid_response = yes\nTFR_EST_begin_covid_response = yes\n",
        check("covid_active_response_recorded", "generic_has_corona = yes has_country_flag = TFR_EST_opening_covid_announced"),
        "remove_ideas = lower_covid_cases\nclr_country_flag = TFR_EST_opening_covid_announced\nclear_variable = TFR_EST_qa_covid_tiers_detected\n",
    ])
    for tier in covid_tiers:
        body.append(f"if = {{ limit = {{ has_country_flag = TFR_EST_qa_saved_{tier} }} add_ideas = {tier} clr_country_flag = TFR_EST_qa_saved_{tier} }}\n")
    body.append("if = { limit = { has_country_flag = TFR_EST_qa_saved_covid_announced } set_country_flag = TFR_EST_opening_covid_announced clr_country_flag = TFR_EST_qa_saved_covid_announced }\n")
    assertions.extend(["covid_absent_blocks_response", "covid_all_five_parent_tiers_detected", "covid_active_response_recorded"])
    # Retained-coalition visibility, actual energy contributions and election
    # handoff are safe in the frontend's isolated hidden-effect context.
    body.extend([
        "TFR_EST_initialize_parliament = yes\nset_country_flag = TFR_EST_ratas_retained\nclr_country_flag = TFR_EST_ratas_mandate_ended\nclr_country_flag = TFR_EST_opening_complete\n",
        check("ratas_choice_reveals_before_referendum_finishes", "TFR_EST_ratas_branch_visible = yes NOT = { TFR_EST_ratas_governing = yes }"),
        "set_country_flag = TFR_EST_opening_complete\n",
        check("ratas_majority_governs_without_legacy_domestic", "TFR_EST_ratas_governing = yes NOT = { TFR_EST_show_legacy_domestic_tree = yes } " + eq("TFR_EST_coalition_seats", 57)),
        "set_variable = { var = TFR_EST_qa_energy_factory_before value = TFR_EST_economy_industrial_capacity_factory_var }\nset_variable = { var = TFR_EST_qa_energy_goods_before value = TFR_EST_economy_consumer_goods_factor_var }\n",
    ])
    energy_flags = ("SAU_saudi_civil_war_global", "saudi_civil_war_flag", "SAU_saudi_civil_war_over_global")
    energy_policies = ("lng_connection", "grid_synchronisation", "renewable_chp", "building_renovation", "network_charge_relief")
    for index, global_flag in enumerate(energy_flags):
        body.append(f"if = {{ limit = {{ has_global_flag = {global_flag} }} set_country_flag = TFR_EST_qa_saved_energy_{index} }}\nclr_global_flag = {global_flag}\n")
    body.extend([
        "set_global_flag = SAU_saudi_civil_war_global\nTFR_EST_reconcile_energy_crisis = yes\nTFR_EST_reconcile_energy_crisis = yes\n",
        "set_variable = { var = TFR_EST_qa_energy_factory_delta value = TFR_EST_economy_industrial_capacity_factory_var }\nsubtract_from_variable = { var = TFR_EST_qa_energy_factory_delta value = TFR_EST_qa_energy_factory_before }\nset_variable = { var = TFR_EST_qa_energy_goods_delta value = TFR_EST_economy_consumer_goods_factor_var }\nsubtract_from_variable = { var = TFR_EST_qa_energy_goods_delta value = TFR_EST_qa_energy_goods_before }\n",
        check("ratas_energy_shock_applies_once", "has_idea = GER_oil_crash1 " + eq("TFR_EST_qa_energy_factory_delta", 0) + " " + eq("TFR_EST_qa_energy_goods_delta", 0)),
    ])
    for suffix in energy_policies:
        body.append(f"set_country_flag = TFR_EST_done_ratas_{suffix}\n")
    body.extend([
        "TFR_EST_reconcile_energy_crisis = yes\n",
        check("ratas_energy_preparations_mitigate", " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) + " " + eq("TFR_EST_energy_response_steps", 5) + " " + eq("TFR_EST_energy_factory_applied", 0) + " " + eq("TFR_EST_energy_goods_applied", 0)),
        "set_global_flag = SAU_saudi_civil_war_over_global\nTFR_EST_reconcile_energy_crisis = yes\n",
        check("ratas_energy_resolution_preserves_reforms", eq("TFR_EST_economy_industrial_capacity_factory_var", "TFR_EST_qa_energy_factory_before") + " " + eq("TFR_EST_economy_consumer_goods_factor_var", "TFR_EST_qa_energy_goods_before") + " " + eq("TFR_EST_energy_factory_applied", 0)),
    ])
    for index, global_flag in enumerate(energy_flags):
        body.append(f"clr_global_flag = {global_flag}\nif = {{ limit = {{ has_country_flag = TFR_EST_qa_saved_energy_{index} }} set_global_flag = {global_flag} clr_country_flag = TFR_EST_qa_saved_energy_{index} }}\n")
    body.extend([
        "add_ideas = lower_covid_cases\nset_country_flag = TFR_EST_covid_seed_owned\nset_country_flag = TFR_EST_covid_first_case_recorded\nset_country_flag = TFR_EST_done_ratas_renew_agreement\nTFR_EST_ratas_reduce_covid = yes\nTFR_EST_ratas_tick = yes\n",
        check("ratas_covid_recovery_bypasses_only_emergency_policies", "NOT = { generic_has_corona = yes } NOT = { has_country_flag = TFR_EST_covid_seed_owned } has_country_flag = TFR_EST_covid_first_case_recorded has_country_flag = TFR_EST_done_ratas_hospital_covid has_country_flag = TFR_EST_done_ratas_testing_tracing has_country_flag = TFR_EST_done_ratas_vaccinate_risk_groups NOT = { has_country_flag = TFR_EST_done_ratas_family_doctors }"),
        "set_country_flag = TFR_EST_done_ratas_family_home_guarantees\n",
        polls((0, 10000, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        check("ratas_valid_centre_election_ends_old_mandate", "has_country_flag = TFR_EST_ratas_mandate_ended has_country_flag = TFR_EST_ratas_retained has_country_flag = TFR_EST_done_ratas_family_home_guarantees NOT = { TFR_EST_ratas_branch_visible = yes } TFR_EST_show_legacy_domestic_tree = yes " + eq("TFR_EST_mandate_party", 2)),
    ])
    assertions.extend([
        "ratas_choice_reveals_before_referendum_finishes", "ratas_majority_governs_without_legacy_domestic",
        "ratas_energy_shock_applies_once", "ratas_energy_preparations_mitigate",
        "ratas_energy_resolution_preserves_reforms", "ratas_covid_recovery_bypasses_only_emergency_policies",
        "ratas_valid_centre_election_ends_old_mandate",
    ])
    # Build the opposite story outcome independently. A deliberately completed
    # referendum exercises the documented late-choice uncompletion path; an
    # active focus's native validity update still requires a running campaign.
    from build_opening_content import POLICIES as OPENING_POLICIES
    body.append("TFR_EST_initialize_parliament = yes\n")
    for flag_name in ("opening_assembly_ended", "ratas_retained", "ratas_resigned", "ratas_mandate_ended", "kallas_mandate_ended", "reform_centre_formed", "porto_choice_resolved", "referendum_failed", "opening_complete", "done_opening_marriage_referendum"):
        body.append(f"clr_country_flag = TFR_EST_{flag_name}\n")
    for policy in OPENING_POLICIES[:-1]:
        body.append(f"set_country_flag = TFR_EST_done_opening_{policy.suffix}\ncomplete_national_focus = TFR_EST_opening_{policy.suffix}\n")
    body.extend([
        "set_country_flag = TFR_EST_referendum_active\ncomplete_national_focus = TFR_EST_opening_marriage_referendum\nset_country_flag = TFR_EST_porto_investigation_seen\nTFR_EST_ratas_steps_back = yes\n",
        check("kallas_late_resignation_fails_only_referendum", "has_country_flag = TFR_EST_referendum_failed has_country_flag = TFR_EST_opening_complete has_country_flag = TFR_EST_caretaker TFR_EST_kallas_branch_visible = yes NOT = { TFR_EST_kallas_governing = yes } NOT = { has_completed_focus = TFR_EST_opening_marriage_referendum } NOT = { has_country_flag = TFR_EST_done_opening_marriage_referendum } " + " ".join(f"has_completed_focus = TFR_EST_opening_{p.suffix}" for p in OPENING_POLICIES[:-1])),
        "TFR_EST_form_reform_centre_cabinet = yes\n",
        check("kallas_confirmed_cabinet_route", "TFR_EST_kallas_governing = yes NOT = { TFR_EST_show_legacy_domestic_tree = yes } NOT = { TFR_EST_ratas_branch_visible = yes } " + eq("TFR_EST_coalition_seats", 60) + " " + eq("TFR_EST_pm_party", 1)),
        "set_country_flag = TFR_EST_done_kallas_govern_together\nadd_ideas = lower_covid_cases\nset_country_flag = TFR_EST_covid_seed_owned\nTFR_EST_kallas_reduce_covid = yes\nTFR_EST_kallas_tick = yes\n",
        check("kallas_covid_recovery_leaves_certificate_reform", "NOT = { generic_has_corona = yes } has_country_flag = TFR_EST_done_kallas_sick_pay has_country_flag = TFR_EST_done_kallas_hospital_support has_country_flag = TFR_EST_done_kallas_frontline_vaccination NOT = { has_country_flag = TFR_EST_done_kallas_covid_certificates }"),
    ])
    for suffix in energy_policies:
        body.append(f"clr_country_flag = TFR_EST_done_ratas_{suffix}\n")
    for index, global_flag in enumerate(energy_flags):
        body.append(f"if = {{ limit = {{ has_global_flag = {global_flag} }} set_country_flag = TFR_EST_qa_saved_kallas_energy_{index} }}\nclr_global_flag = {global_flag}\n")
    for suffix in ("energy_households", "energy_networks", "gas_reserve", "lng_connection"):
        body.append(f"set_country_flag = TFR_EST_done_kallas_{suffix}\n")
    body.extend([
        "set_global_flag = SAU_saudi_civil_war_global\nTFR_EST_reconcile_energy_crisis = yes\n",
        check("kallas_energy_mitigation", " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) + " " + eq("TFR_EST_energy_response_steps", 5) + " " + eq("TFR_EST_energy_factory_applied", 0) + " " + eq("TFR_EST_energy_goods_applied", 0)),
    ])
    for suffix in energy_policies:
        body.append(f"set_country_flag = TFR_EST_done_ratas_{suffix}\n")
    body.extend([
        "TFR_EST_reconcile_energy_crisis = yes\n",
        check("kallas_mixed_energy_does_not_stack", " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) + " " + eq("TFR_EST_energy_response_steps", 5) + " " + eq("TFR_EST_energy_factory_applied", 0) + " " + eq("TFR_EST_energy_goods_applied", 0)),
    ])
    for index, global_flag in enumerate(energy_flags):
        body.append(f"clr_global_flag = {global_flag}\nif = {{ limit = {{ has_country_flag = TFR_EST_qa_saved_kallas_energy_{index} }} set_global_flag = {global_flag} clr_country_flag = TFR_EST_qa_saved_kallas_energy_{index} }}\n")
    body.extend([
        "TFR_EST_reconcile_energy_crisis = yes\n",
        polls((10000, 0, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        check("kallas_reform_election_ends_old_mandate", "has_country_flag = TFR_EST_kallas_mandate_ended has_country_flag = TFR_EST_reform_centre_formed NOT = { TFR_EST_kallas_branch_visible = yes } TFR_EST_show_legacy_domestic_tree = yes NOT = { has_country_flag = TFR_EST_reform_handover_pending } " + eq("TFR_EST_mandate_party", 1)),
    ])
    assertions.extend([
        "kallas_late_resignation_fails_only_referendum", "kallas_confirmed_cabinet_route",
        "kallas_covid_recovery_leaves_certificate_reform", "kallas_energy_mitigation",
        "kallas_mixed_energy_does_not_stack", "kallas_reform_election_ends_old_mandate",
    ])
    # Run real reward helpers natively; preview blocks must remain display-only.
    from build_focus_tooltips import idea_definitions
    body.extend([
        "set_variable = { TFR_EST_qa_construction_before = TFR_EST_economy_production_speed_buildings_factor_var }\nset_variable = { TFR_EST_qa_supply_before = TFR_EST_military_supply_consumption_factor_var }\n",
        "TFR_EST_opening_reward_kose_voobu = yes\n",
        "set_variable = { TFR_EST_qa_construction_delta = TFR_EST_economy_production_speed_buildings_factor_var }\nsubtract_from_variable = { var = TFR_EST_qa_construction_delta value = TFR_EST_qa_construction_before }\nset_variable = { TFR_EST_qa_supply_delta = TFR_EST_military_supply_consumption_factor_var }\nsubtract_from_variable = { var = TFR_EST_qa_supply_delta value = TFR_EST_qa_supply_before }\n",
        check("compact_focus_reward_deltas", eq("TFR_EST_qa_construction_delta", .05) + " " + eq("TFR_EST_qa_supply_delta", -.04)),
        check("preview_ideas_are_display_only", " ".join(f"NOT = {{ has_idea = {ident} }}" for ident in idea_definitions())),
    ])
    assertions.extend(["compact_focus_reward_deltas", "preview_ideas_are_display_only"])
    # Native minister slots apply traits themselves; test these without invoking
    # diplomatic transitions or simulating a political-screen button purchase.
    from build_ministers import CANDIDATES, OPENING, candidate_id, eligibility
    opening_ministers = " ".join(f"has_idea = TFR_EST_minister_{suffix}" for suffix in OPENING)
    body.extend([
        "TFR_EST_suspend_ministers = yes\nclr_country_flag = TFR_EST_ministers_initialized\nTFR_EST_initialize_parliament = yes\nTFR_EST_initialize_ministers = yes\n",
        check("ministers_historical_cabinet", opening_ministers + " has_idea = TFR_EST_pm_centre " + eq("TFR_EST_pm_party", 2)),
        check("ministers_coalition_required", "TFR_EST_can_appoint_urmas_reinsalu_foreign = yes NOT = { TFR_EST_can_appoint_urmas_paet_foreign = yes } NOT = { TFR_EST_can_appoint_tiit_riisalo_economic = yes }"),
        check("ministers_second_office_blocked", "has_idea = TFR_EST_minister_mart_helme_interior NOT = { TFR_EST_can_appoint_mart_helme_foreign = yes }"),
        "remove_ideas = TFR_EST_minister_taavi_aas_economic\nTFR_EST_initialize_ministers = yes\nTFR_EST_reconcile_ministers = yes\n",
        check("ministers_player_vacancy_preserved", "NOT = { has_idea = TFR_EST_minister_taavi_aas_economic } has_idea = TFR_EST_minister_juri_luik_defence"),
        "set_variable = { TFR_EST_pm_party = 3 }\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("ministers_pm_cannot_hold_portfolio", "has_idea = TFR_EST_pm_ekre NOT = { has_idea = TFR_EST_minister_mart_helme_interior } NOT = { TFR_EST_can_appoint_mart_helme_foreign = yes } NOT = { TFR_EST_can_appoint_mart_helme_interior = yes } TFR_EST_can_appoint_jaak_madison_foreign = yes TFR_EST_can_appoint_alar_laneman_interior = yes"),
        "set_variable = { TFR_EST_pm_party = 2 }\nTFR_EST_reconcile_cabinet_leadership = yes\nset_variable = { TFR_EST_coalition_sde = 1 }\nTFR_EST_recount_confidence = yes\n",
        "force_update_dynamic_modifier = yes\nset_variable = { TFR_EST_qa_minister_stability_before = modifier@stability_factor }\nadd_ideas = TFR_EST_minister_katri_raik_interior\nforce_update_dynamic_modifier = yes\nset_variable = { TFR_EST_qa_minister_stability_delta = modifier@stability_factor }\nsubtract_from_variable = { var = TFR_EST_qa_minister_stability_delta value = TFR_EST_qa_minister_stability_before }\nlog = \"TFR_EST_ENGINE_QA_MINISTER stability_before=[?TFR_EST_qa_minister_stability_before] stability_delta=[?TFR_EST_qa_minister_stability_delta]\"\n",
        check("ministers_trait_applies_country_buff", "has_idea = TFR_EST_minister_katri_raik_interior " + eq("TFR_EST_qa_minister_stability_delta", .04)),
        "set_variable = { TFR_EST_coalition_sde = 0 }\nTFR_EST_recount_confidence = yes\n",
        check("ministers_withdrawn_party_vacates", "NOT = { has_idea = TFR_EST_minister_katri_raik_interior } has_idea = TFR_EST_minister_juri_luik_defence has_idea = TFR_EST_pm_centre"),
        "TFR_EST_enter_caretaker = yes\n",
        check("ministers_caretaker_retains_no_appointments", "has_idea = TFR_EST_minister_juri_luik_defence NOT = { TFR_EST_can_appoint_urmas_reinsalu_foreign = yes }"),
        "clr_country_flag = TFR_EST_caretaker\nremove_ideas = TFR_EST_cabinet_formation\nforce_update_dynamic_modifier = yes\n",
    ])
    minister_assertions = ["ministers_historical_cabinet", "ministers_coalition_required", "ministers_second_office_blocked", "ministers_player_vacancy_preserved", "ministers_pm_cannot_hold_portfolio", "ministers_trait_applies_country_buff", "ministers_withdrawn_party_vacates", "ministers_caretaker_retains_no_appointments"]
    # All five prices must receive the real native cost-factor discount. Capture
    # their existing baselines so unrelated parent modifiers remain valid.
    factors = ("foreign", "economic", "interior", "intelligence", "theorist")
    for slot in factors:
        body.append(f"set_variable = {{ TFR_EST_qa_{slot}_cost_before = modifier@{slot}_minister_cost_factor }}\n")
    body.extend([
        polls((10001, 0, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        check("ministers_invalid_election_no_discount", "NOT = { has_idea = TFR_EST_cabinet_formation }"),
        polls((10000, 0, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        "force_update_dynamic_modifier = yes\n",
    ])
    for slot in factors:
        body.append(f"set_variable = {{ TFR_EST_qa_{slot}_cost_delta = modifier@{slot}_minister_cost_factor }}\nsubtract_from_variable = {{ var = TFR_EST_qa_{slot}_cost_delta value = TFR_EST_qa_{slot}_cost_before }}\n")
        body.append(f'log = "TFR_EST_ENGINE_QA_MINISTER {slot}_cost_before=[?TFR_EST_qa_{slot}_cost_before] delta=[?TFR_EST_qa_{slot}_cost_delta]"\n')
    body.append(check("ministers_valid_election_discount", "has_idea = TFR_EST_cabinet_formation " + " ".join(eq(f"TFR_EST_qa_{slot}_cost_delta", -.8) for slot in factors)))
    minister_assertions.extend(["ministers_invalid_election_no_discount", "ministers_valid_election_discount"])
    # Directly activate the seven parties for isolated coverage. This asserts
    # candidacies rather than inventing a legal zero-seat coalition in play.
    body.append("clr_country_flag = TFR_EST_caretaker\n")
    for party in PARTIES:
        body.append(f"set_variable = {{ TFR_EST_active_{party} = 1 }}\nset_variable = {{ TFR_EST_coalition_{party} = 1 }}\n")
    for index, party in enumerate(PARTIES, 1):
        body.append(f"set_variable = {{ TFR_EST_pm_party = {index} }}\nTFR_EST_reconcile_cabinet_leadership = yes\n")
        # A PM's same person is deliberately excluded; EKRE has alternatives.
        nominees = [c for c in CANDIDATES if c['party'] == party and c['person'] != 'mart_helme']
        name = "ministers_full_cabinet_" + party
        body.append(check(name, " ".join(eligibility(candidate) + " = yes" for candidate in nominees)))
        minister_assertions.append(name)
    body.extend([
        "set_variable = { TFR_EST_pm_party = 4 }\nset_country_flag = TFR_EST_pm_person_urmas_reinsalu\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("ministers_reinsalu_pm_alternative", "TFR_EST_person_is_pm_urmas_reinsalu = yes NOT = { has_idea = TFR_EST_minister_urmas_reinsalu_foreign } NOT = { TFR_EST_can_appoint_urmas_reinsalu_foreign = yes } TFR_EST_can_appoint_trivimi_velliste_foreign = yes"),
        "set_variable = { TFR_EST_pm_party = 3 }\nset_country_flag = TFR_EST_pm_person_martin_helme\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("ministers_martin_pm_alternative", "TFR_EST_person_is_pm_martin_helme = yes NOT = { TFR_EST_person_is_pm_mart_helme = yes } NOT = { TFR_EST_can_appoint_martin_helme_economic = yes } TFR_EST_can_appoint_rene_kokk_economic = yes TFR_EST_can_appoint_mart_helme_interior = yes"),
    ])
    minister_assertions.extend(["ministers_reinsalu_pm_alternative", "ministers_martin_pm_alternative"])
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("ministers_occupation_clears_all_five", "NOT = { has_idea = TFR_EST_cabinet_formation } " + " ".join(f"NOT = {{ has_idea = {candidate_id(candidate)} }}" for candidate in CANDIDATES)),
    ])
    minister_assertions.append("ministers_occupation_clears_all_five")
    assertions.extend(minister_assertions)
    # 2023 programme and postwar calendar: run native effects in this 2020
    # snapshot, explicitly seeding historical mandate flags. Date progression,
    # event delivery and natural focus selection remain campaign tests.
    body.extend([
        "clr_country_flag = TFR_EST_occupied\nclr_country_flag = TFR_EST_parliament_suspended\nclr_country_flag = TFR_EST_restoration_election\nTFR_EST_initialize_parliament = yes\n",
        check("reform2023_hidden_at_start", "NOT = { TFR_EST_reform_2023_branch_visible = yes }"),
        "set_country_flag = TFR_EST_reform_won_2023_election\nset_country_flag = TFR_EST_reform_2023_mandate\nclr_country_flag = TFR_EST_reform_2023_mandate_ended\nTFR_EST_clear_coalition = yes\nset_variable = { TFR_EST_pm_party = 1 }\nset_variable = { TFR_EST_mandate_party = 1 }\nset_variable = { TFR_EST_nominee_party = 1 }\nset_variable = { TFR_EST_seats_reform = 60 }\nset_variable = { TFR_EST_coalition_reform = 1 }\nclr_country_flag = TFR_EST_caretaker\nTFR_EST_recount_confidence = yes\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("reform2023_confirmed_programme", "TFR_EST_reform_2023_branch_visible = yes TFR_EST_reform_2023_governing = yes NOT = { TFR_EST_show_legacy_domestic_tree = yes }"),
        "set_variable = { TFR_EST_coalition_seats = 50 }\n",
        "set_country_flag = TFR_EST_opening_assembly_ended\nset_country_flag = TFR_EST_porto_investigation_seen\nclr_country_flag = TFR_EST_porto_choice_resolved\nTFR_EST_recount_confidence = yes\nTFR_EST_keep_ratas = yes\nTFR_EST_ratas_steps_back = yes\nTFR_EST_form_reform_centre_cabinet = yes\nTFR_EST_opening_tick = yes\n",
        check("reform2023_stale_porto_choices_blocked", eq("TFR_EST_pm_party", 1) + " " + eq("TFR_EST_mandate_party", 1) + " NOT = { has_country_flag = TFR_EST_caretaker } NOT = { has_country_flag = TFR_EST_porto_choice_resolved } NOT = { has_country_flag = TFR_EST_reform_handover_pending } TFR_EST_reform_2023_branch_visible = yes"),
        "set_variable = { TFR_EST_coalition_seats = 50 }\n",
        check("reform2023_actual_coalition_gate", "NOT = { TFR_EST_reform_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\nset_variable = { TFR_EST_qa_org_before = TFR_EST_military_army_org_factor_var }\nset_variable = { TFR_EST_qa_supply_before = TFR_EST_military_supply_consumption_factor_var }\nTFR_EST_reform_2023_reward_defence_three_percent = yes\nset_variable = { TFR_EST_qa_org_delta = TFR_EST_military_army_org_factor_var }\nsubtract_from_variable = { var = TFR_EST_qa_org_delta value = TFR_EST_qa_org_before }\nset_variable = { TFR_EST_qa_supply_delta = TFR_EST_military_supply_consumption_factor_var }\nsubtract_from_variable = { var = TFR_EST_qa_supply_delta value = TFR_EST_qa_supply_before }\n",
        check("reform2023_native_military_deltas", eq("TFR_EST_qa_org_delta", .04) + " " + eq("TFR_EST_qa_supply_delta", -.03)),
        "13 = { add_extra_state_shared_building_slots = 2 set_variable = { TFR_EST_qa_factory_before = arms_factory_level } }\n191 = { add_extra_state_shared_building_slots = 2 set_variable = { TFR_EST_qa_factory_before = arms_factory_level } }\nset_country_flag = TFR_EST_reform_2023_ammunition_factory_pending\nset_country_flag = TFR_EST_reform_2023_drones_factory_pending\nTFR_EST_reform_2023_grant_industry = yes\n13 = { set_variable = { TFR_EST_qa_factory_delta = arms_factory_level } subtract_from_variable = { var = TFR_EST_qa_factory_delta value = TFR_EST_qa_factory_before } }\n191 = { set_variable = { TFR_EST_qa_factory_delta = arms_factory_level } subtract_from_variable = { var = TFR_EST_qa_factory_delta value = TFR_EST_qa_factory_before } }\n",
        check("reform2023_two_native_factories", "has_country_flag = TFR_EST_reform_2023_ammunition_factory_granted has_country_flag = TFR_EST_reform_2023_drones_factory_granted 13 = { " + eq("TFR_EST_qa_factory_delta", 1) + " } 191 = { " + eq("TFR_EST_qa_factory_delta", 1) + " }"),
        "TFR_EST_reform_2023_grant_industry = yes\n13 = { set_variable = { TFR_EST_qa_factory_delta = arms_factory_level } subtract_from_variable = { var = TFR_EST_qa_factory_delta value = TFR_EST_qa_factory_before } }\n191 = { set_variable = { TFR_EST_qa_factory_delta = arms_factory_level } subtract_from_variable = { var = TFR_EST_qa_factory_delta value = TFR_EST_qa_factory_before } }\n",
        check("reform2023_factories_do_not_repeat", "13 = { " + eq("TFR_EST_qa_factory_delta", 1) + " } 191 = { " + eq("TFR_EST_qa_factory_delta", 1) + " }"),
        "add_ideas = GER_oil_crash1\nset_country_flag = TFR_EST_done_reform_2023_grid_connection\nset_country_flag = TFR_EST_done_reform_2023_wind_permits\nset_country_flag = TFR_EST_done_reform_2023_renovation\nTFR_EST_reconcile_energy_crisis = yes\n",
        check("reform2023_parent_energy_removed", " ".join(f"NOT = {{ has_idea = GER_oil_crash{n} }}" for n in range(1, 6))),
        "set_variable = { TFR_EST_election_year = 2027 }\nclr_country_flag = TFR_EST_postwar_election_held\nclr_country_flag = TFR_EST_postwar_election_pending\nTFR_EST_war_elections_tick = yes\n",
        check("reform2023_no_prewar_2027_vote", "has_country_flag = TFR_EST_election_waiting_first_war NOT = { has_country_flag = TFR_EST_postwar_election_held } " + eq("TFR_EST_seats_reform", 60)),
        polls((6000, 4000, 0, 0, 0, 0, 0)),
        "set_global_flag = SOV_nato_war_over_global\nset_global_flag = nato_nato_won_nato_war\nTFR_EST_war_elections_tick = yes\nlog = \"TFR_EST_ENGINE_QA_CALENDAR year=[?TFR_EST_election_year] term=[?TFR_EST_postwar_term_days]\"\n",
        check("reform2023_postwar_native_year", "has_country_flag = TFR_EST_postwar_election_held NOT = { has_country_flag = TFR_EST_postwar_election_pending } " + eq("TFR_EST_election_year", 2024) + " " + eq("TFR_EST_postwar_term_days", 0)),
        check("reform2023_postwar_ends_programme", "has_country_flag = TFR_EST_reform_2023_mandate_ended NOT = { TFR_EST_reform_2023_branch_visible = yes }"),
        "TFR_EST_war_elections_tick = yes\n",
        check("reform2023_postwar_vote_once", eq("TFR_EST_postwar_term_days", 1)),
        "clr_global_flag = SOV_nato_war_over_global\nclr_global_flag = nato_nato_won_nato_war\nset_variable = { TFR_EST_pm_party = 1 }\nset_variable = { TFR_EST_mandate_party = 1 }\nclr_country_flag = TFR_EST_caretaker\nclr_country_flag = TFR_EST_reform_2023_mandate_ended\nset_country_flag = TFR_EST_karis_president\nTFR_EST_reconcile_presidency = yes\n",
        check("michal_calendar_guard_2020", "NOT = { TFR_EST_reform_handover_eligible = yes }"),
        "set_country_flag = TFR_EST_kallas_departed_for_europe\nTFR_EST_reconcile_executive_display = yes\n",
        check("michal_native_pm_and_president", "has_idea = TFR_EST_pm_reform_michal NOT = { has_idea = TFR_EST_pm_reform } has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 1)),
        "set_variable = { TFR_EST_pm_party = 2 }\nTFR_EST_reconcile_executive_display = yes\n",
        check("michal_other_party_keeps_career", "has_idea = TFR_EST_pm_centre NOT = { has_idea = TFR_EST_pm_reform_michal } has_country_flag = TFR_EST_kallas_departed_for_europe"),
        "set_variable = { TFR_EST_pm_party = 1 }\nTFR_EST_reconcile_executive_display = yes\n",
        check("michal_returns_with_reform", "has_idea = TFR_EST_pm_reform_michal has_country_flag = TFR_EST_pm_person_kristen_michal"),
    ])
    assertions.extend([
        "reform2023_hidden_at_start", "reform2023_confirmed_programme", "reform2023_actual_coalition_gate", "reform2023_stale_porto_choices_blocked",
        "reform2023_native_military_deltas", "reform2023_two_native_factories", "reform2023_factories_do_not_repeat",
        "reform2023_parent_energy_removed", "reform2023_no_prewar_2027_vote", "reform2023_postwar_native_year",
        "reform2023_postwar_ends_programme", "reform2023_postwar_vote_once", "michal_calendar_guard_2020",
        "michal_native_pm_and_president", "michal_other_party_keeps_career", "michal_returns_with_reform",
    ])
    # EKRE's elected 2023 programme. As above, the snapshot stays in 2020:
    # real date/winner activation is source-tested, while native effects use
    # explicit, isolated mandate fixtures.
    from build_ekre_2023 import POLICIES as EKRE_POLICIES, PREFIX as EKRE_PREFIX, INDUSTRY_PROJECTS as EKRE_INDUSTRY, ENERGY_STAGES as EKRE_ENERGY
    body.extend([
        "TFR_EST_initialize_parliament = yes\n",
        check("ekre2023_hidden_at_start", "NOT = { TFR_EST_ekre_2023_branch_visible = yes }"),
        "set_country_flag = TFR_EST_ekre_won_2023_election\nset_country_flag = TFR_EST_ekre_2023_mandate\nclr_country_flag = TFR_EST_ekre_2023_mandate_ended\nTFR_EST_clear_coalition = yes\nset_variable = { TFR_EST_seats_ekre = 60 }\nset_variable = { TFR_EST_seats_centre = 40 }\nset_variable = { TFR_EST_seats_reform = 1 }\nset_variable = { TFR_EST_coalition_ekre = 1 }\nset_variable = { TFR_EST_mandate_party = 3 }\nset_variable = { TFR_EST_nominee_party = 3 }\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_recount_confidence = yes\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("ekre2023_waits_for_confirmation", "TFR_EST_ekre_2023_branch_visible = yes NOT = { TFR_EST_ekre_2023_governing = yes } NOT = { has_country_flag = TFR_EST_martin_leads_ekre } has_idea = TFR_EST_pm_centre " + eq("TFR_EST_pm_party", 2)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("ekre2023_confirmed_martin_and_president", "TFR_EST_ekre_2023_governing = yes has_idea = TFR_EST_pm_ekre_martin NOT = { has_idea = TFR_EST_pm_ekre } has_country_flag = TFR_EST_pm_person_martin_helme has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } NOT = { TFR_EST_show_legacy_domestic_tree = yes } NOT = { has_idea = TFR_EST_minister_martin_helme_economic } TFR_EST_can_appoint_rene_kokk_economic = yes TFR_EST_can_appoint_mart_helme_interior = yes " + eq("TFR_EST_pm_party", 3)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("ekre2023_actual_coalition_gate", "NOT = { TFR_EST_ekre_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["ekre2023_hidden_at_start", "ekre2023_waits_for_confirmation", "ekre2023_confirmed_martin_and_president", "ekre2023_actual_coalition_gate"])
    defence = next(p for p in EKRE_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_ekre_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(EKRE_PREFIX + "reward_" + defence.suffix + " = yes\n")
    for field, amount in defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_ekre_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_ekre_delta_{field} value = TFR_EST_qa_ekre_before_{field} }}\n")
    body.append(check("ekre2023_native_military_deltas", " ".join(eq("TFR_EST_qa_ekre_delta_" + field, amount) for field, amount in defence.military)))
    assertions.append("ekre2023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_ekre_factory_before = arms_factory_level }} }}\n")
    for project in EKRE_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_ekre_2023_{project}_factory_pending\n")
    body.append("TFR_EST_ekre_2023_grant_industry = yes\n")
    factory_checks = " ".join(f"has_country_flag = TFR_EST_ekre_2023_{project}_factory_granted" for project in EKRE_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_ekre_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_ekre_factory_delta value = TFR_EST_qa_ekre_factory_before }} }}\n")
        factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_ekre_factory_delta", 1) + " }"
    body.append(check("ekre2023_two_native_factories", factory_checks))
    body.append("TFR_EST_ekre_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_ekre_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_ekre_factory_delta value = TFR_EST_qa_ekre_factory_before }} }}\n")
    body.append(check("ekre2023_factories_do_not_repeat", factory_checks))
    assertions.extend(["ekre2023_two_native_factories", "ekre2023_factories_do_not_repeat"])
    from build_energy_crisis import RATAS_PROJECTS, KALLAS_PROJECTS, REFORM_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("ekre2023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("ekre2023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in EKRE_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_ekre_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "ekre2023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("ekre2023_occupation_hides_martin", "NOT = { has_idea = TFR_EST_pm_ekre_martin } NOT = { has_country_flag = TFR_EST_pm_person_martin_helme } has_country_flag = TFR_EST_martin_leads_ekre NOT = { TFR_EST_ekre_2023_branch_visible = yes }"),
        "TFR_EST_restore_parliament = yes\n",
        check("ekre2023_restoration_preserves_martin", "has_idea = TFR_EST_pm_ekre_martin has_country_flag = TFR_EST_caretaker TFR_EST_ekre_2023_branch_visible = yes NOT = { TFR_EST_ekre_2023_governing = yes }"),
        "clr_country_flag = TFR_EST_restoration_election\n",
        polls((0, 0, 10000, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("ekre2023_next_vote_ends_programme", "has_country_flag = TFR_EST_ekre_2023_mandate_ended NOT = { TFR_EST_ekre_2023_branch_visible = yes } has_idea = TFR_EST_pm_ekre_martin has_country_flag = TFR_EST_pm_person_martin_helme " + eq("TFR_EST_pm_party", 3)),
    ])
    assertions.extend(["ekre2023_occupation_hides_martin", "ekre2023_restoration_preserves_martin", "ekre2023_next_vote_ends_programme"])
    # Centre programme and executive identities. The frontend stays in 2020;
    # the September date guard is tested as a native rejection, while source
    # tests exercise actual September event eligibility and both options.
    from build_centre_2023 import POLICIES as CENTRE_POLICIES, PREFIX as CENTRE_PREFIX, INDUSTRY_PROJECTS as CENTRE_INDUSTRY, ENERGY_STAGES as CENTRE_ENERGY
    body.extend([
        "TFR_EST_initialize_parliament = yes\n",
        check("centre2023_hidden_at_start", "NOT = { TFR_EST_centre_2023_branch_visible = yes }"),
        polls((0, 6000, 4000, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        "set_country_flag = TFR_EST_centre_won_2023_election\nset_country_flag = TFR_EST_centre_2023_mandate\nclr_country_flag = TFR_EST_centre_2023_mandate_ended\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("centre2023_waits_for_confirmation", "TFR_EST_centre_2023_branch_visible = yes NOT = { TFR_EST_centre_2023_governing = yes } has_idea = TFR_EST_pm_centre " + eq("TFR_EST_pm_party", 2)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("centre2023_confirmed_ratas_and_president", "TFR_EST_centre_2023_governing = yes has_idea = TFR_EST_pm_centre NOT = { TFR_EST_show_legacy_domestic_tree = yes } has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } NOT = { has_country_flag = TFR_EST_centre_leadership_resolved } " + eq("TFR_EST_pm_party", 2)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("centre2023_actual_coalition_gate", "NOT = { TFR_EST_centre_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["centre2023_hidden_at_start", "centre2023_waits_for_confirmation", "centre2023_confirmed_ratas_and_president", "centre2023_actual_coalition_gate"])
    centre_defence = next(p for p in CENTRE_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in centre_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_centre_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(CENTRE_PREFIX + "reward_" + centre_defence.suffix + " = yes\n")
    for field, amount in centre_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_centre_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_centre_delta_{field} value = TFR_EST_qa_centre_before_{field} }}\n")
    body.append(check("centre2023_native_military_deltas", " ".join(eq("TFR_EST_qa_centre_delta_" + field, amount) for field, amount in centre_defence.military)))
    assertions.append("centre2023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_centre_factory_before = arms_factory_level }} }}\n")
    for project in CENTRE_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_centre_2023_{project}_factory_pending\n")
    body.append("TFR_EST_centre_2023_grant_industry = yes\n")
    centre_factory_checks = " ".join(f"has_country_flag = TFR_EST_centre_2023_{project}_factory_granted" for project in CENTRE_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_centre_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_centre_factory_delta value = TFR_EST_qa_centre_factory_before }} }}\n")
        centre_factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_centre_factory_delta", 1) + " }"
    body.append(check("centre2023_two_native_factories", centre_factory_checks))
    body.append("TFR_EST_centre_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_centre_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_centre_factory_delta value = TFR_EST_qa_centre_factory_before }} }}\n")
    body.append(check("centre2023_factories_do_not_repeat", centre_factory_checks))
    assertions.extend(["centre2023_two_native_factories", "centre2023_factories_do_not_repeat"])
    from build_energy_crisis import EKRE_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS), ("ekre_2023", EKRE_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("centre2023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("centre2023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in CENTRE_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_centre_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "centre2023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        polls((0, 10000, 0, 0, 0, 0, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("centre2023_next_vote_ends_programme", "has_country_flag = TFR_EST_centre_2023_mandate_ended NOT = { TFR_EST_centre_2023_branch_visible = yes } has_idea = TFR_EST_pm_centre " + eq("TFR_EST_pm_party", 2)),
        "clr_country_flag = TFR_EST_centre_won_2023_election\nset_country_flag = TFR_EST_centre_lost_2023_election\nTFR_EST_centre_leadership_tick = yes\nTFR_EST_choose_centre_leader_kiik = yes\nTFR_EST_choose_centre_leader_kolvart = yes\n",
        check("centre_congress_date_guard_2020", "NOT = { has_country_flag = TFR_EST_centre_leadership_resolved } NOT = { has_country_flag = TFR_EST_centre_leader_kiik } NOT = { has_country_flag = TFR_EST_centre_leader_kolvart } has_idea = TFR_EST_pm_centre"),
        "set_country_flag = TFR_EST_centre_leadership_resolved\nset_country_flag = TFR_EST_centre_leader_kiik\nclr_country_flag = TFR_EST_centre_leader_kolvart\nTFR_EST_reconcile_executive_display = yes\n",
        check("centre_congress_kiik_native_identity", "has_idea = TFR_EST_pm_centre_kiik NOT = { has_idea = TFR_EST_pm_centre } has_country_flag = TFR_EST_pm_person_tanel_kiik has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 2)),
        "set_variable = { TFR_EST_pm_party = 3 }\nTFR_EST_reconcile_executive_display = yes\n",
        check("centre_congress_other_pm_preserved", "has_idea = TFR_EST_pm_ekre_martin NOT = { has_idea = TFR_EST_pm_centre_kiik } has_country_flag = TFR_EST_centre_leader_kiik " + eq("TFR_EST_pm_party", 3)),
        "set_variable = { TFR_EST_pm_party = 2 }\nclr_country_flag = TFR_EST_centre_leader_kiik\nset_country_flag = TFR_EST_centre_leader_kolvart\nTFR_EST_reconcile_executive_display = yes\n",
        check("centre_congress_kolvart_native_identity", "has_idea = TFR_EST_pm_centre_kolvart NOT = { has_idea = TFR_EST_pm_centre_kiik } NOT = { has_idea = TFR_EST_pm_centre } has_country_flag = TFR_EST_pm_person_mihhail_kolvart " + eq("TFR_EST_pm_party", 2)),
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("centre_congress_occupation_preserves_choice", "has_country_flag = TFR_EST_centre_leader_kolvart NOT = { has_idea = TFR_EST_pm_centre_kolvart } NOT = { has_country_flag = TFR_EST_pm_person_mihhail_kolvart }"),
        "TFR_EST_restore_parliament = yes\n",
        check("centre_congress_restoration_preserves_choice", "has_idea = TFR_EST_pm_centre_kolvart has_country_flag = TFR_EST_centre_leader_kolvart has_country_flag = TFR_EST_caretaker"),
    ])
    assertions.extend(["centre2023_next_vote_ends_programme", "centre_congress_date_guard_2020", "centre_congress_kiik_native_identity", "centre_congress_other_pm_preserved", "centre_congress_kolvart_native_identity", "centre_congress_occupation_preserves_choice", "centre_congress_restoration_preserves_choice"])
    # As with the other elected programmes, the frontend remains in 2020.
    # Source tests validate legitimate 2023 election entry; this native block
    # seeds the mandate to verify its effects, delivery and executive gates.
    from build_isamaa_2023 import POLICIES as ISAMAA_POLICIES, PREFIX as ISAMAA_PREFIX, INDUSTRY_PROJECTS as ISAMAA_INDUSTRY, ENERGY_STAGES as ISAMAA_ENERGY
    body.extend([
        # The preceding independent Centre restoration case deliberately leaves
        # a restoration ballot pending. This separate ordinary-election fixture
        # must close that test state; actual gameplay keeps its confirmation lock.
        "clr_country_flag = TFR_EST_restoration_election\nTFR_EST_initialize_parliament = yes\n",
        check("isamaa2023_hidden_at_start", "NOT = { TFR_EST_isamaa_2023_branch_visible = yes }"),
        polls((0, 4000, 0, 6000, 0, 0, 0)), "TFR_EST_hold_election = yes\n",
        # Frontend countries are AI-controlled and immediately confirm a
        # majority after the vote. Seed a caretaker frame explicitly, as for
        # the older programme QA blocks; source tests cover the player handoff.
        "set_country_flag = TFR_EST_isamaa_won_2023_election\nset_country_flag = TFR_EST_isamaa_2023_mandate\nclr_country_flag = TFR_EST_isamaa_2023_mandate_ended\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("isamaa2023_waits_for_confirmation", "TFR_EST_isamaa_2023_branch_visible = yes NOT = { TFR_EST_isamaa_2023_governing = yes } has_country_flag = TFR_EST_caretaker " + eq("TFR_EST_pm_party", 4)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("isamaa2023_confirmed_seeder_and_president", "TFR_EST_isamaa_2023_governing = yes has_idea = TFR_EST_pm_isamaa NOT = { TFR_EST_show_legacy_domestic_tree = yes } has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 4)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("isamaa2023_actual_coalition_gate", "NOT = { TFR_EST_isamaa_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["isamaa2023_hidden_at_start", "isamaa2023_waits_for_confirmation", "isamaa2023_confirmed_seeder_and_president", "isamaa2023_actual_coalition_gate"])
    isamaa_defence = next(p for p in ISAMAA_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in isamaa_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_isamaa_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(ISAMAA_PREFIX + "reward_" + isamaa_defence.suffix + " = yes\n")
    for field, amount in isamaa_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_isamaa_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_isamaa_delta_{field} value = TFR_EST_qa_isamaa_before_{field} }}\n")
    body.append(check("isamaa2023_native_military_deltas", " ".join(eq("TFR_EST_qa_isamaa_delta_" + field, amount) for field, amount in isamaa_defence.military)))
    assertions.append("isamaa2023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_isamaa_factory_before = arms_factory_level }} }}\n")
    for project in ISAMAA_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_isamaa_2023_{project}_factory_pending\n")
    body.append("TFR_EST_isamaa_2023_grant_industry = yes\n")
    isamaa_factory_checks = " ".join(f"has_country_flag = TFR_EST_isamaa_2023_{project}_factory_granted" for project in ISAMAA_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_isamaa_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_isamaa_factory_delta value = TFR_EST_qa_isamaa_factory_before }} }}\n")
        isamaa_factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_isamaa_factory_delta", 1) + " }"
    body.append(check("isamaa2023_two_native_factories", isamaa_factory_checks))
    body.append("TFR_EST_isamaa_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_isamaa_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_isamaa_factory_delta value = TFR_EST_qa_isamaa_factory_before }} }}\n")
    body.append(check("isamaa2023_factories_do_not_repeat", isamaa_factory_checks))
    assertions.extend(["isamaa2023_two_native_factories", "isamaa2023_factories_do_not_repeat"])
    from build_energy_crisis import CENTRE_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS), ("ekre_2023", EKRE_2023_PROJECTS), ("centre_2023", CENTRE_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("isamaa2023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("isamaa2023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in ISAMAA_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_isamaa_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "isamaa2023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("isamaa2023_occupation_hides_programme", "NOT = { TFR_EST_isamaa_2023_branch_visible = yes } NOT = { has_idea = TFR_EST_pm_isamaa }"),
        "TFR_EST_restore_parliament = yes\n",
        check("isamaa2023_restoration_keeps_programme", "TFR_EST_isamaa_2023_branch_visible = yes NOT = { TFR_EST_isamaa_2023_governing = yes } has_country_flag = TFR_EST_caretaker has_idea = TFR_EST_pm_isamaa"),
        "clr_country_flag = TFR_EST_restoration_election\n",
        polls((0, 0, 0, 10000, 0, 0, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("isamaa2023_next_vote_ends_programme", "has_country_flag = TFR_EST_isamaa_2023_mandate_ended NOT = { TFR_EST_isamaa_2023_branch_visible = yes } has_idea = TFR_EST_pm_isamaa " + eq("TFR_EST_pm_party", 4)),
    ])
    assertions.extend(["isamaa2023_occupation_hides_programme", "isamaa2023_restoration_keeps_programme", "isamaa2023_next_vote_ends_programme"])
    # The 2020 frontend cannot deliver a historical 2022 congress naturally.
    # Verify its native date rejection, then seed career history explicitly for
    # display tests. Source tests exercise the real February 4/5 transition.
    from build_sde_2023 import POLICIES as SDE_POLICIES, PREFIX as SDE_PREFIX, INDUSTRY_PROJECTS as SDE_INDUSTRY, ENERGY_STAGES as SDE_ENERGY
    body.extend([
        "clr_country_flag = TFR_EST_restoration_election\nTFR_EST_initialize_parliament = yes\n",
        check("sde2023_hidden_at_start", "NOT = { TFR_EST_sde_2023_branch_visible = yes }"),
        polls((0, 0, 0, 0, 10000, 0, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\nTFR_EST_sde_handover_tick = yes\nTFR_EST_complete_sde_handover = yes\n",
        check("sde_handover_date_guard_2020", "NOT = { has_country_flag = TFR_EST_laanemets_leads_sde } NOT = { has_country_flag = TFR_EST_pm_person_lauri_laanemets } has_idea = TFR_EST_pm_sde " + eq("TFR_EST_pm_party", 5)),
        "set_country_flag = TFR_EST_laanemets_leads_sde\nTFR_EST_reconcile_executive_display = yes\n",
        check("sde_handover_laanemets_native_identity", "has_idea = TFR_EST_pm_sde_laanemets NOT = { has_idea = TFR_EST_pm_sde } has_country_flag = TFR_EST_pm_person_lauri_laanemets has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 5)),
        "set_variable = { TFR_EST_pm_party = 4 }\nTFR_EST_reconcile_executive_display = yes\n",
        check("sde_handover_other_pm_preserved", "has_idea = TFR_EST_pm_isamaa NOT = { has_idea = TFR_EST_pm_sde_laanemets } NOT = { has_country_flag = TFR_EST_pm_person_lauri_laanemets } has_country_flag = TFR_EST_laanemets_leads_sde " + eq("TFR_EST_pm_party", 4)),
        "TFR_EST_initialize_parliament = yes\n",
        polls((0, 4000, 0, 0, 6000, 0, 0)), "TFR_EST_hold_election = yes\n",
        # Native history countries are AI-controlled and auto-confirm a
        # majority. Seed a caretaker frame to test the player-facing gate.
        "set_country_flag = TFR_EST_sde_won_2023_election\nset_country_flag = TFR_EST_sde_2023_mandate\nclr_country_flag = TFR_EST_sde_2023_mandate_ended\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("sde2023_waits_for_confirmation", "TFR_EST_sde_2023_branch_visible = yes NOT = { TFR_EST_sde_2023_governing = yes } has_country_flag = TFR_EST_caretaker " + eq("TFR_EST_pm_party", 5)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("sde2023_confirmed_laanemets_and_president", "TFR_EST_sde_2023_governing = yes has_idea = TFR_EST_pm_sde_laanemets NOT = { has_idea = TFR_EST_pm_sde } NOT = { TFR_EST_show_legacy_domestic_tree = yes } has_country_flag = TFR_EST_pm_person_lauri_laanemets has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 5)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("sde2023_actual_coalition_gate", "NOT = { TFR_EST_sde_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["sde2023_hidden_at_start", "sde_handover_date_guard_2020", "sde_handover_laanemets_native_identity", "sde_handover_other_pm_preserved", "sde2023_waits_for_confirmation", "sde2023_confirmed_laanemets_and_president", "sde2023_actual_coalition_gate"])
    sde_defence = next(p for p in SDE_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in sde_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_sde_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(SDE_PREFIX + "reward_" + sde_defence.suffix + " = yes\n")
    for field, amount in sde_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_sde_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_sde_delta_{field} value = TFR_EST_qa_sde_before_{field} }}\n")
    body.append(check("sde2023_native_military_deltas", " ".join(eq("TFR_EST_qa_sde_delta_" + field, amount) for field, amount in sde_defence.military)))
    assertions.append("sde2023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_sde_factory_before = arms_factory_level }} }}\n")
    for project in SDE_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_sde_2023_{project}_factory_pending\n")
    body.append("TFR_EST_sde_2023_grant_industry = yes\n")
    sde_factory_checks = " ".join(f"has_country_flag = TFR_EST_sde_2023_{project}_factory_granted" for project in SDE_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_sde_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_sde_factory_delta value = TFR_EST_qa_sde_factory_before }} }}\n")
        sde_factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_sde_factory_delta", 1) + " }"
    body.append(check("sde2023_two_native_factories", sde_factory_checks))
    body.append("TFR_EST_sde_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_sde_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_sde_factory_delta value = TFR_EST_qa_sde_factory_before }} }}\n")
    body.append(check("sde2023_factories_do_not_repeat", sde_factory_checks))
    assertions.extend(["sde2023_two_native_factories", "sde2023_factories_do_not_repeat"])
    from build_energy_crisis import ISAMAA_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS), ("ekre_2023", EKRE_2023_PROJECTS), ("centre_2023", CENTRE_2023_PROJECTS), ("isamaa_2023", ISAMAA_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("sde2023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("sde2023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in SDE_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_sde_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "sde2023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("sde2023_occupation_hides_programme", "NOT = { TFR_EST_sde_2023_branch_visible = yes } NOT = { has_idea = TFR_EST_pm_sde_laanemets } NOT = { has_country_flag = TFR_EST_pm_person_lauri_laanemets } has_country_flag = TFR_EST_laanemets_leads_sde"),
        "TFR_EST_restore_parliament = yes\n",
        check("sde2023_restoration_keeps_programme", "TFR_EST_sde_2023_branch_visible = yes NOT = { TFR_EST_sde_2023_governing = yes } has_country_flag = TFR_EST_caretaker has_idea = TFR_EST_pm_sde_laanemets has_country_flag = TFR_EST_laanemets_leads_sde"),
        "clr_country_flag = TFR_EST_restoration_election\n",
        polls((0, 0, 0, 0, 10000, 0, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("sde2023_next_vote_ends_programme", "has_country_flag = TFR_EST_sde_2023_mandate_ended NOT = { TFR_EST_sde_2023_branch_visible = yes } has_idea = TFR_EST_pm_sde_laanemets has_country_flag = TFR_EST_laanemets_leads_sde " + eq("TFR_EST_pm_party", 5)),
    ])
    assertions.extend(["sde2023_occupation_hides_programme", "sde2023_restoration_keeps_programme", "sde2023_next_vote_ends_programme"])
    # The frontend remains in 2020. Source tests exercise legitimate 2023
    # electoral entry; these native cases seed the mandate and caretaker frame.
    from build_e200_2023 import POLICIES as E200_POLICIES, PREFIX as E200_PREFIX, INDUSTRY_PROJECTS as E200_INDUSTRY, ENERGY_STAGES as E200_ENERGY
    body.extend([
        "clr_country_flag = TFR_EST_restoration_election\nTFR_EST_initialize_parliament = yes\n",
        check("e2002023_hidden_at_start", "NOT = { TFR_EST_e200_2023_branch_visible = yes }"),
        polls((0, 4000, 0, 0, 0, 6000, 0)), "TFR_EST_hold_election = yes\n",
        # Native history countries are AI-controlled and auto-confirm a
        # majority. Explicitly seed a caretaker to exercise availability.
        "set_country_flag = TFR_EST_e200_won_2023_election\nset_country_flag = TFR_EST_e200_2023_mandate\nclr_country_flag = TFR_EST_e200_2023_mandate_ended\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("e2002023_waits_for_confirmation", "TFR_EST_e200_2023_branch_visible = yes NOT = { TFR_EST_e200_2023_governing = yes } has_country_flag = TFR_EST_caretaker " + eq("TFR_EST_pm_party", 6)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("e2002023_confirmed_cabinet_and_president", "TFR_EST_e200_2023_governing = yes has_idea = TFR_EST_pm_e200 NOT = { TFR_EST_show_legacy_domestic_tree = yes } has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 6)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("e2002023_actual_coalition_gate", "NOT = { TFR_EST_e200_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["e2002023_hidden_at_start", "e2002023_waits_for_confirmation", "e2002023_confirmed_cabinet_and_president", "e2002023_actual_coalition_gate"])
    e200_defence = next(p for p in E200_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in e200_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_e200_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(E200_PREFIX + "reward_" + e200_defence.suffix + " = yes\n")
    for field, amount in e200_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_e200_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_e200_delta_{field} value = TFR_EST_qa_e200_before_{field} }}\n")
    body.append(check("e2002023_native_military_deltas", " ".join(eq("TFR_EST_qa_e200_delta_" + field, amount) for field, amount in e200_defence.military)))
    assertions.append("e2002023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_e200_factory_before = arms_factory_level }} }}\n")
    for project in E200_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_e200_2023_{project}_factory_pending\n")
    body.append("TFR_EST_e200_2023_grant_industry = yes\n")
    e200_factory_checks = " ".join(f"has_country_flag = TFR_EST_e200_2023_{project}_factory_granted" for project in E200_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_e200_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_e200_factory_delta value = TFR_EST_qa_e200_factory_before }} }}\n")
        e200_factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_e200_factory_delta", 1) + " }"
    body.append(check("e2002023_two_native_factories", e200_factory_checks))
    body.append("TFR_EST_e200_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_e200_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_e200_factory_delta value = TFR_EST_qa_e200_factory_before }} }}\n")
    body.append(check("e2002023_factories_do_not_repeat", e200_factory_checks))
    assertions.extend(["e2002023_two_native_factories", "e2002023_factories_do_not_repeat"])
    from build_energy_crisis import SDE_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS), ("ekre_2023", EKRE_2023_PROJECTS), ("centre_2023", CENTRE_2023_PROJECTS), ("isamaa_2023", ISAMAA_2023_PROJECTS), ("sde_2023", SDE_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("e2002023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("e2002023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in E200_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_e200_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "e2002023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("e2002023_occupation_hides_programme", "NOT = { TFR_EST_e200_2023_branch_visible = yes } NOT = { has_idea = TFR_EST_pm_e200 }"),
        "TFR_EST_restore_parliament = yes\n",
        check("e2002023_restoration_keeps_programme", "TFR_EST_e200_2023_branch_visible = yes NOT = { TFR_EST_e200_2023_governing = yes } has_country_flag = TFR_EST_caretaker has_idea = TFR_EST_pm_e200"),
        "clr_country_flag = TFR_EST_restoration_election\n",
        polls((0, 0, 0, 0, 0, 10000, 0)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("e2002023_next_vote_ends_programme", "has_country_flag = TFR_EST_e200_2023_mandate_ended NOT = { TFR_EST_e200_2023_branch_visible = yes } has_idea = TFR_EST_pm_e200 " + eq("TFR_EST_pm_party", 6)),
    ])
    assertions.extend(["e2002023_occupation_hides_programme", "e2002023_restoration_keeps_programme", "e2002023_next_vote_ends_programme"])
    # The frontend remains in 2020. Source tests exercise legitimate 2023
    # electoral entry; these native cases seed the mandate and caretaker frame.
    from build_pp_2023 import POLICIES as PP_POLICIES, PREFIX as PP_PREFIX, INDUSTRY_PROJECTS as PP_INDUSTRY, ENERGY_STAGES as PP_ENERGY
    body.extend([
        "clr_country_flag = TFR_EST_restoration_election\nTFR_EST_initialize_parliament = yes\n",
        check("pp2023_hidden_at_start", "NOT = { TFR_EST_pp_2023_branch_visible = yes }"),
        polls((4000, 0, 0, 0, 0, 0, 6000)), "TFR_EST_hold_election = yes\n",
        # Native history countries are AI-controlled and auto-confirm a
        # majority. Explicitly seed a caretaker to exercise availability.
        "set_country_flag = TFR_EST_pp_won_2023_election\nset_country_flag = TFR_EST_pp_2023_mandate\nclr_country_flag = TFR_EST_pp_2023_mandate_ended\nset_country_flag = TFR_EST_electoral_handover\nset_country_flag = TFR_EST_caretaker\nTFR_EST_reconcile_cabinet_leadership = yes\n",
        check("pp2023_waits_for_confirmation", "TFR_EST_pp_2023_branch_visible = yes NOT = { TFR_EST_pp_2023_governing = yes } has_country_flag = TFR_EST_caretaker " + eq("TFR_EST_pm_party", 7)),
        "TFR_EST_confirm_cabinet = yes\n",
        check("pp2023_confirmed_cabinet_and_president", "TFR_EST_pp_2023_governing = yes has_idea = TFR_EST_pm_pp NOT = { TFR_EST_show_legacy_domestic_tree = yes } has_country_leader = { character = TFR_EST_alar_karis ruling_only = yes } " + eq("TFR_EST_pm_party", 7)),
        "set_variable = { TFR_EST_coalition_seats = 50 }\nset_variable = { TFR_EST_confidence_seats = 90 }\n",
        check("pp2023_actual_coalition_gate", "NOT = { TFR_EST_pp_2023_governing = yes }"),
        "TFR_EST_recount_confidence = yes\n",
    ])
    assertions.extend(["pp2023_hidden_at_start", "pp2023_waits_for_confirmation", "pp2023_confirmed_cabinet_and_president", "pp2023_actual_coalition_gate"])
    pp_defence = next(p for p in PP_POLICIES if p.x == 0 and p.y == 1)
    for field, amount in pp_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_pp_before_{field} = TFR_EST_military_{field}_var }}\n")
    body.append(PP_PREFIX + "reward_" + pp_defence.suffix + " = yes\n")
    for field, amount in pp_defence.military:
        body.append(f"set_variable = {{ TFR_EST_qa_pp_delta_{field} = TFR_EST_military_{field}_var }}\nsubtract_from_variable = {{ var = TFR_EST_qa_pp_delta_{field} value = TFR_EST_qa_pp_before_{field} }}\n")
    body.append(check("pp2023_native_military_deltas", " ".join(eq("TFR_EST_qa_pp_delta_" + field, amount) for field, amount in pp_defence.military)))
    assertions.append("pp2023_native_military_deltas")
    for state in (13, 191):
        body.append(f"{state} = {{ add_extra_state_shared_building_slots = 2 set_variable = {{ TFR_EST_qa_pp_factory_before = arms_factory_level }} }}\n")
    for project in PP_INDUSTRY:
        body.append(f"set_country_flag = TFR_EST_pp_2023_{project}_factory_pending\n")
    body.append("TFR_EST_pp_2023_grant_industry = yes\n")
    pp_factory_checks = " ".join(f"has_country_flag = TFR_EST_pp_2023_{project}_factory_granted" for project in PP_INDUSTRY)
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_pp_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_pp_factory_delta value = TFR_EST_qa_pp_factory_before }} }}\n")
        pp_factory_checks += f" {state} = {{ " + eq("TFR_EST_qa_pp_factory_delta", 1) + " }"
    body.append(check("pp2023_two_native_factories", pp_factory_checks))
    body.append("TFR_EST_pp_2023_grant_industry = yes\n")
    for state in (13, 191):
        body.append(f"{state} = {{ set_variable = {{ TFR_EST_qa_pp_factory_delta = arms_factory_level }} subtract_from_variable = {{ var = TFR_EST_qa_pp_factory_delta value = TFR_EST_qa_pp_factory_before }} }}\n")
    body.append(check("pp2023_factories_do_not_repeat", pp_factory_checks))
    assertions.extend(["pp2023_two_native_factories", "pp2023_factories_do_not_repeat"])
    from build_energy_crisis import SDE_2023_PROJECTS, E200_2023_PROJECTS
    for route, projects in (("ratas", RATAS_PROJECTS), ("kallas", KALLAS_PROJECTS), ("reform_2023", REFORM_2023_PROJECTS), ("ekre_2023", EKRE_2023_PROJECTS), ("centre_2023", CENTRE_2023_PROJECTS), ("isamaa_2023", ISAMAA_2023_PROJECTS), ("sde_2023", SDE_2023_PROJECTS), ("e200_2023", E200_2023_PROJECTS)):
        for project in projects:
            body.append(f"clr_country_flag = TFR_EST_done_{route}_{project}\n")
    body.append("set_global_flag = SAU_saudi_civil_war_global\nclr_global_flag = SAU_saudi_civil_war_over_global\nset_country_flag = TFR_EST_energy_idea_managed\nset_variable = { TFR_EST_energy_external_recovery = 0 }\nTFR_EST_reconcile_energy_crisis = yes\n")
    body.append(check("pp2023_energy_starts_at_parent_tier", "has_idea = GER_oil_crash1"))
    assertions.append("pp2023_energy_starts_at_parent_tier")
    completed_stages = 0
    for project, stages in PP_ENERGY.items():
        body.append(f"set_country_flag = TFR_EST_done_pp_2023_{project}\nTFR_EST_reconcile_energy_crisis = yes\n")
        completed_stages += stages
        name = "pp2023_native_energy_" + project
        conditions = " ".join(f"NOT = {{ has_idea = GER_oil_crash{i} }}" for i in range(1, 6)) if completed_stages >= 5 else f"has_idea = GER_oil_crash{completed_stages + 1}"
        body.append(check(name, conditions))
        assertions.append(name)
    body.extend([
        "set_country_flag = TFR_EST_occupied\nTFR_EST_suspend_parliament = yes\n",
        check("pp2023_occupation_hides_programme", "NOT = { TFR_EST_pp_2023_branch_visible = yes } NOT = { has_idea = TFR_EST_pm_pp }"),
        "TFR_EST_restore_parliament = yes\n",
        check("pp2023_restoration_keeps_programme", "TFR_EST_pp_2023_branch_visible = yes NOT = { TFR_EST_pp_2023_governing = yes } has_country_flag = TFR_EST_caretaker has_idea = TFR_EST_pm_pp"),
        "clr_country_flag = TFR_EST_restoration_election\n",
        polls((0, 0, 0, 0, 0, 0, 10000)), "TFR_EST_hold_election = yes\nTFR_EST_confirm_cabinet = yes\n",
        check("pp2023_next_vote_ends_programme", "has_country_flag = TFR_EST_pp_2023_mandate_ended NOT = { TFR_EST_pp_2023_branch_visible = yes } has_idea = TFR_EST_pm_pp " + eq("TFR_EST_pm_party", 7)),
    ])
    assertions.extend(["pp2023_occupation_hides_programme", "pp2023_restoration_keeps_programme", "pp2023_next_vote_ends_programme"])
    body.append("log = \"TFR_EST_ENGINE_QA_END\"\n")
    source = (ROOT / "history/countries/EST - Estonia.txt").read_text(encoding="utf-8-sig")
    # Country history executes top-level commands independently. Keep native
    # temporary inputs and their consumers in one effect context, matching a
    # focus reward or decision complete_effect in an actual campaign.
    (base / "history/countries/EST - Estonia.txt").write_text(source + "\nhidden_effect = {\n" + "".join(body) + "\n}\n", encoding="utf-8")
    (base / "assertions.json").write_text(json.dumps(assertions), encoding="utf-8")
    print(json.dumps({"descriptor": str(base / "descriptor.mod"), "assertions": len(assertions), "campaign": False}))


if __name__ == "__main__": main()

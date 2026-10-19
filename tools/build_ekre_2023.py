"""Build EKRE's conditional 2023 mandate: 32 compact, 35-day focuses.

The hypothetical programme adapts EKRE's own 2023 election, defence and
population platforms. Sources and gameplay abstractions are recorded in
docs/EKRE_2023_SOURCES.md. It does not reproduce an enacted historical cabinet.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ratas_continuation import Policy
from focus_reward_model import concise_trigger, modifier_reward
from native_script_interface import amount_call


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_ekre_2023_"
INDUSTRY_PROJECTS = ("ammunition", "repairs")
ENERGY_STAGES = {"narva_blocks": 2, "kiisa_reserve": 1, "regulated_power": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_ekre_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "An EKRE-Led Parliamentary Mandate",
           "EKRE has won the largest delegation. Negotiate a funded programme with our actual coalition partners; a plurality still needs a parliamentary majority.",
           "national_unity", (), 4, 0, cohesion=2,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Fund the Three-Percent Defence Commitment",
           "Approve procurement instalments and command preparations before a European war reaches Estonia. A spending commitment must be matched by contracts and dependable stores.",
           "defence", ("new_mandate",), 0, 1, budget=110, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("reserve_training", "Prepare the Expanded Reserve Establishment",
           "Schedule instructors, call-up records and equipment accounting for a larger reserve. Expansion remains a training and procurement task rather than an instant addition to the army.",
           "army_doctrines", ("defence_commitment",), 0, 2, budget=65, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("air_defence", "Finance Air Defence for Key Regions",
           "Fund site planning, crews and procurement for medium- and short-range protection. Integrate the systems we can maintain instead of promising an immediate nationwide shield.",
           "air_fighter", ("reserve_training",), 0, 3, budget=95, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("coastal_defence", "Prepare Coastal Positions and Mine Stores",
           "Prepare shore positions, observation posts and controlled stores for coastal defence. Naval and ground commanders must agree responsibilities before hostilities begin.",
           "construct_military", ("air_defence",), 0, 4, budget=65, readiness=4,
           military=(("army_defence_factor", .03), ("dig_in_speed_factor", .10))),
    Policy("military_border_guard", "Organise a Military Border-Guard Reserve",
           "Define the proposed border service's crisis command and reserve duties. Train personnel and finance communications without treating an administrative change as a new field army.",
           "defence", ("coastal_defence",), 0, 5, budget=55, readiness=5,
           military=(("army_org_factor", .03), ("mobilization_speed", .10))),
    Policy("shelters", "Fund Shelters and Civil-Protection Training",
           "Survey shelters, fund essential repairs and require protection in major new buildings. Municipal exercises should test evacuation, first aid and continuity of services.",
           "construct_infrastructure", ("military_border_guard",), 0, 6, budget=55, cohesion=3, readiness=5,
           military=(("dig_in_speed_factor", .10), ("attrition", -.025))),

    # Domestic contracts and two initial workshops are a bounded TFR adaptation
    # of the platform's funded equipment and reserve-expansion commitments.
    Policy("defence_contracts", "Place Maintainable Domestic Defence Contracts",
           "Translate equipment plans into contracts that Estonian suppliers can service. Start with ammunition handling and repairs while preserving ordinary production and procurement limits.",
           "small_arms", ("new_mandate",), 2, 1, budget=40,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Finance an Ammunition Workshop",
           "Pay for one inspected ammunition-production workshop. This initial facility supplies Estonia's production base; it does not deliver an automatic stockpile or complete the entire rearmament programme.",
           "construct_mil_factory", ("defence_contracts",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_ekre_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_ekre_2023_factory_tt\nhidden_effect = { TFR_EST_ekre_2023_grant_industry = yes }"),
    Policy("repair_workshop", "Finance an Equipment Repair Workshop",
           "Fund a second workshop for servicing, component manufacture and overhaul. Reliable maintenance keeps procured equipment useful; Estonia must still manufacture or purchase the equipment itself.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_ekre_2023_repairs_factory_pending\ncustom_effect_tooltip = TFR_EST_ekre_2023_factory_tt\nhidden_effect = { TFR_EST_ekre_2023_grant_industry = yes }"),
    Policy("existing_railways", "Redirect Investment to Existing Railways",
           "Review Rail Baltic commitments and redirect this programme's investment toward existing railway links. Publish the contractual costs and prioritize usable domestic connections.",
           "construct_infrastructure", ("repair_workshop",), 2, 4, budget=70, cohesion=-1,
           economic=(("production_speed_buildings_factor", .04),),
           military=(("supply_consumption_factor", -.03),)),
    Policy("trunk_roads", "Fund the Tallinn Trunk-Road Sections",
           "Select and fund practical four-lane sections toward Tartu, Pärnu and Narva. Phased construction improves movement without declaring three complete highways finished at once.",
           "construct_infrastructure", ("existing_railways",), 2, 5, budget=90,
           economic=(("production_speed_buildings_factor", .04),),
           military=(("supply_consumption_factor", -.03),)),
    Policy("food_reserves", "Contract Domestic Emergency Food Reserves",
           "Contract inspected staple-food reserves and rotate them through domestic suppliers. Farmers and transport operators need payment and clear emergency delivery arrangements.",
           "consumer_goods", ("trunk_roads",), 2, 6, budget=45, cohesion=3, readiness=3,
           economic=(("local_resources_factor", .04), ("consumer_goods_factor", -.01))),

    Policy("narva_blocks", "Overhaul the Idle Narva Power Blocks",
           "Commission technical surveys and overhaul contracts for idle generating units. Fund dependable capacity and fuel arrangements while accounting for operating and environmental costs.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=85, cohesion=-1,
           economic=(("industrial_capacity_factory", .05), ("local_resources_factor", .05))),
    Policy("kiisa_reserve", "Bring Kiisa Capacity into the Supply Plan",
           "Review the gas station's company structure and commercial availability. Secure fuel and dispatch arrangements while keeping emergency reserve requirements explicit.",
           "oil_refinery", ("narva_blocks",), 4, 2, budget=55,
           economic=(("industrial_capacity_factory", .03), ("production_factory_max_efficiency_factor", .025))),
    Policy("regulated_power", "Fund the Three-Cent Electricity Proposal",
           "Prepare the proposed state-backed supply contracts and their subsidy reserve. Resolve carbon-cost and legal disputes; a promised tariff does not make electricity generation free.",
           "production", ("kiisa_reserve",), 4, 3, budget=80, cohesion=-1,
           economic=(("industrial_capacity_factory", .04), ("consumer_goods_factor", -.015)),
           extra="add_political_power = -30"),
    Policy("fuel_excise", "Lower Fuel Excise to the EU Minimum",
           "Reduce the proposed fuel duties and update tax administration. Lower operating costs help firms and households, while the treasury loses recurring receipts.",
           "consumer_goods", ("regulated_power",), 4, 4, cohesion=2,
           economic=(("consumer_goods_factor", -.015), ("production_speed_buildings_factor", .025)),
           extra="set_temp_variable = { var = income_var_temp value = -0.015 }\nadd_income_with_inflation = yes"),
    Policy("food_vat", "Introduce Five-Percent VAT on Food",
           "Legislate the reduced food rate and monitor how the change reaches customers. Record the revenue loss alongside the relief delivered to household budgets.",
           "consumer_goods", ("fuel_excise",), 4, 5, cohesion=3,
           economic=(("consumer_goods_factor", -.025),),
           extra="set_temp_variable = { var = income_var_temp value = -0.04 }\nadd_income_with_inflation = yes"),
    Policy("medicine_vat", "Reduce Medicine VAT to Five Percent",
           "Apply the proposed lower rate to medicines and update pharmacy billing. Improved affordability requires a funded revenue adjustment and continued access to supplies.",
           "consumer_goods", ("food_vat",), 4, 6, cohesion=3,
           economic=(("consumer_goods_factor", -.01), ("production_factory_max_efficiency_factor", .025)),
           extra="set_temp_variable = { var = income_var_temp value = -0.008 }\nadd_income_with_inflation = yes"),

    Policy("child_tax_relief", "Link Parents' Tax Relief to Children",
           "Draft the child-linked income-tax allowance with clear eligibility and legal limits. Publish its distribution and recurring cost before claiming the policy pays for itself.",
           "consumer_goods", ("new_mandate",), 6, 1, budget=20, cohesion=2,
           economic=(("consumer_goods_factor", -.015),),
           extra="set_temp_variable = { var = income_var_temp value = -0.02 }\nadd_income_with_inflation = yes"),
    Policy("family_home_loans", "Pilot Child-Linked Family Home Loans",
           "Fund a limited loan programme with child-linked repayment relief. Begin with assessed borrowers and a defined public guarantee rather than underwriting every mortgage.",
           "construct_civ_factory", ("child_tax_relief",), 6, 2, budget=65, cohesion=3,
           economic=(("production_speed_buildings_factor", .035),)),
    Policy("student_loan_relief", "Fund Parents' Student-Loan Relief",
           "Create an application process for the proposed child-linked student-loan cancellation. Budget the first claims and explain the eligibility rules to lenders and families.",
           "scientific_exchange", ("family_home_loans",), 6, 3, budget=30, cohesion=3,
           economic=(("research_speed_factor", .025),)),
    Policy("family_doctors", "Finance Duty Hours for Family Doctors",
           "Contract additional primary-care duty hours and local pharmacy cover. Patients need reliable appointments and referrals rather than another promise of shorter queues.",
           "consumer_goods", ("student_loan_relief",), 6, 4, budget=45, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .025),)),
    Policy("rural_maternity", "Restore Round-the-Clock Midwife Cover",
           "Fund midwife duty arrangements in smaller hospitals and family practices. Assess staffing and safe referral routes before extending the service.",
           "consumer_goods", ("family_doctors",), 6, 5, budget=35, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .025),)),
    Policy("thirteenth_pension", "Budget the Thirteenth-Pension Supplement",
           "Fund the proposed additional annual payment for pensioners below the average pension. Explain who receives it and provide for the cost alongside defence spending.",
           "consumer_goods", ("rural_maternity",), 6, 6, budget=65, cohesion=4,
           economic=(("consumer_goods_factor", -.015),)),

    Policy("parliamentary_scrutiny", "Strengthen Parliamentary Security Scrutiny",
           "Fund committee expertise and lawful access to oversight information. Review institutional accountability while maintaining operational secrecy and independent proceedings.",
           "political_pressure", ("new_mandate",), 8, 1, budget=15, cohesion=2,
           extra="add_political_power = 30"),
    Policy("e_vote_audit", "Commission an Independent E-Voting Audit",
           "Commission independent technical scrutiny and publish the findings. The audit does not presume fraud, change allocated seats or call another election.",
           "scientific_exchange", ("parliamentary_scrutiny",), 8, 2, budget=20, cohesion=2,
           economic=(("research_speed_factor", .02),)),
    Policy("citizens_initiative", "Draft the Citizens' Initiative Procedure",
           "Prepare the proposed procedure for citizen-initiated bills and referendums. Establish signature verification and constitutional safeguards before seeking the necessary parliamentary approval.",
           "national_unity", ("e_vote_audit",), 8, 3, budget=15, cohesion=3,
           extra="add_political_power = -20"),
    Policy("presidential_election_bill", "Draft Direct Presidential Elections",
           "Prepare the constitutional amendment and its required procedure. Introducing a bill does not replace the incumbent president or bypass the existing constitution.",
           "political_pressure", ("citizens_initiative",), 8, 4, budget=15, cohesion=2,
           extra="add_political_power = -30"),
    Policy("constitutional_review", "Review European Measures in the Riigikogu",
           "Resource constitutional scrutiny of proposed European measures and the government's negotiating mandate. Publish disputed obligations without automatically withdrawing Estonia from its alliances.",
           "political_pressure", ("presidential_election_bill",), 8, 5, budget=15, cohesion=-2,
           extra="add_political_power = 45"),
    Policy("estonian_education", "Fund Estonian-Language Teaching Capacity",
           "Prepare teachers and teaching materials for Estonian-language instruction. Budget practical support for pupils and institutions instead of treating a legislative requirement as sufficient staffing.",
           "scientific_exchange", ("constitutional_review",), 8, 6, budget=50, cohesion=2,
           economic=(("research_speed_factor", .035), ("production_factory_efficiency_gain_factor", .025))),

    Policy("account_to_parliament", "Account for the National Conservative Programme",
           "Report the programme's costs and results to the Riigikogu. Review incomplete legislation and long projects without calling an election or changing the European war's course.",
           "national_unity", ("shelters", "food_reserves", "medicine_vat", "thirteenth_pension", "estonian_education"), 4, 8,
           cohesion=3, extra="set_country_flag = TFR_EST_ekre_2023_programme_finished\nadd_political_power = 75"),
)


_EARLY_AI = ("new_mandate", "defence_commitment", "defence_contracts",
             "ammunition_workshop", "repair_workshop", "reserve_training",
             "air_defence", "coastal_defence", "military_border_guard", "shelters",
             "narva_blocks", "kiisa_reserve", "regulated_power")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_ekre_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_ekre_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = GFX_goal_generic_{p.icon}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_ekre_2023_branch_visible = yes }}
    available = {{
        TFR_EST_ekre_2023_governing = yes{extra}
    }}
    bypass = {{ has_country_flag = {done(p.suffix)} }}
    cancel_if_invalid = yes
    continue_if_invalid = no
    ai_will_do = {{ factor = {priority} }}
    completion_reward = {{
        if = {{
            limit = {{ NOT = {{ has_country_flag = {done(p.suffix)} }} }}
            set_country_flag = {done(p.suffix)}
            {PREFIX}reward_{p.suffix} = yes
        }}
    }}
}}
""")
    return "".join(out)


def build_triggers() -> str:
    text = """# An EKRE plurality in the validated 2023 ballot grants this mandate.
TFR_EST_ekre_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_ekre_2023_mandate
    has_country_flag = TFR_EST_ekre_won_2023_election
    NOT = { has_country_flag = TFR_EST_ekre_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 3 compare = equals }
}
TFR_EST_ekre_2023_governing = {
    TFR_EST_ekre_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 3 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 3 compare = equals }
    check_variable = { var = TFR_EST_coalition_ekre value = 1 compare = equals }
}
TFR_EST_ekre_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_ekre_2023_governing", "TFR_EST_ekre_2023_all_policies_done"):
        text = concise_trigger(name, text)
    return text


def build_effects() -> str:
    out = ["# Each focus applies its reward inside a persistent once-only guard.\n"]
    for p in POLICIES:
        effects = ["hidden_effect = { TFR_EST_initialize_country_modifiers = yes }"]
        for value, helper in ((p.budget, "TFR_EST_spend_budget"), (p.cohesion, "TFR_EST_change_cohesion"), (p.readiness, "TFR_EST_change_readiness")):
            if value:
                effects.append(amount_call(helper, value))
        for group, fields in (("economy", p.economic), ("military", p.military)):
            if fields:
                effects.append(modifier_reward(PREFIX + p.suffix, group, fields))
        if p.extra:
            effects.append(p.extra)
        if p.suffix in ENERGY_STAGES:
            effects.append("custom_effect_tooltip = " + PREFIX + p.suffix + "_energy_tt")
        effects.append("hidden_effect = { TFR_EST_reconcile_energy_crisis = yes TFR_EST_refresh_country_modifiers = yes }")
        out.append(f"{PREFIX}reward_{p.suffix} = {{\n    " + "\n    ".join(effects) + "\n}\n\n")
    out.append("""# Keep funded entitlements pending if every eligible slot is occupied.
# Mark each project delivered only inside the selected state after construction.
TFR_EST_ekre_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_ekre_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_ekre_2023_{project}_factory_granted }}
            }}
            {state} = {{
                if = {{
                    limit = {{
                        is_owned_by = EST
                        is_controlled_by = EST
                        free_building_slots = {{ building = arms_factory size > 0 include_locked = no }}
                    }}
                    add_building_construction = {{ type = arms_factory level = 1 instant_build = yes }}
                    EST = {{
                        set_country_flag = TFR_EST_ekre_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_ekre_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_ekre_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_ekre_2023_grant_industry = yes
    }
}
""")
    return "".join(out)


def build_localisation() -> str:
    entries = {}
    for p in POLICIES:
        ident = PREFIX + p.suffix
        entries[ident] = p.title
        entries[ident + "_desc"] = p.description
    entries.update({
        "TFR_EST_ekre_2023_governing_tt": "A confirmed EKRE-led cabinet has at least 51 coalition seats.",
        "TFR_EST_ekre_2023_all_policies_done_tt": "Complete every other focus in the 2023 EKRE government programme.",
        "TFR_EST_ekre_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three energy projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_ekre_2023.txt": build_focuses(),
        "common/scripted_triggers/TFR_EST_ekre_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_ekre_2023.txt": build_effects(),
        "localisation/english/TFR_EST_ekre_2023_l_english.yml": build_localisation(),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    for relative, text in outputs().items():
        path = ROOT / relative
        data = text.encode("utf-8-sig" if path.suffix == ".yml" else "utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Generated EKRE 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} EKRE 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

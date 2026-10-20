"""Build Eesti 200's conditional 2023 mandate: 32 compact, 35-day focuses.

The programme adapts the party's own 2023 election platform to TFR's alternate
timeline. Concrete sources, funding choices and adaptations are recorded in
docs/E200_2023_SOURCES.md. It does not claim a historical Eesti 200-led cabinet.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ratas_continuation import Policy
from focus_reward_model import concise_trigger, modifier_reward
from native_script_interface import amount_call


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_e200_2023_"
INDUSTRY_PROJECTS = ("ammunition", "maintenance")
ENERGY_STAGES = {"renewable_permits": 2, "grid_connection": 1, "renovation": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_e200_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "An Eesti 200 Long-Term Parliamentary Mandate",
           "The largest delegation must now turn a long-term programme into funded decisions. A confirmed majority will answer to parliament for education, resilient government and defence preparation.",
           "national_unity", (), 4, 0, cohesion=3,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Fund the Three-Percent Defence Commitment",
           "Approve a procurement and operating tranche toward the proposed defence commitment. Delivery schedules and continuing costs go before parliament for review.",
           "defence", ("new_mandate",), 0, 1, budget=125, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("air_defence", "Prepare the Kalevipoja Air-Defence Dome",
           "Survey sites and fund trained crews, communications and compatible purchases. The proposed integrated shield needs a staged procurement plan rather than a declaration that the sky is already secure.",
           "air_fighter", ("defence_commitment",), 0, 2, budget=105, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("reserve_muster", "Assign Every Citizen a Crisis Role",
           "Test the reserve call-up lists and coordinate civilian responsibilities with employers and councils. Exercises must reveal which plans can actually assemble and sustain the existing units.",
           "army_doctrines", ("air_defence",), 0, 3, budget=50, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("kaitseliit_instructors", "Fund Kaitseliit Instructors and Civil-Protection Training",
           "Commission professional instruction for volunteers in military and civilian emergencies. Inspect equipment upkeep and realistic arrangements for participants with civilian jobs.",
           "army_doctrines", ("reserve_muster",), 0, 4, budget=60, readiness=4,
           military=(("training_time_army_factor", -.04), ("dig_in_speed_factor", .10)),
           extra="army_experience = 10"),
    Policy("allied_reception", "Prepare Sustained Allied Reception",
           "Exercise ports, routes and dispersed stores with Estonia's available allies. Facilities support the reinforcement agreements that actually exist in this campaign.",
           "construct_military", ("kaitseliit_instructors",), 0, 5, budget=80, readiness=4,
           military=(("supply_consumption_factor", -.05), ("army_org_factor", .025))),
    Policy("civil_reserve", "Establish Civil Reserves and Tartu Disaster-Medicine Training",
           "Finance community exercises and a first training tranche for military and disaster medicine in Tartu. Local services must demonstrate warning, shelter and evacuation arrangements together.",
           "national_unity", ("allied_reception",), 0, 6, budget=70, cohesion=3, readiness=5,
           military=(("attrition", -.025), ("army_defence_factor", .025))),

    Policy("industrial_guarantees", "Capitalize Domestic Defence-Industry Projects",
           "Award assessed development finance to domestic suppliers. The state acts as an inspected development partner while firms remain responsible for delivery and usable products.",
           "small_arms", ("new_mandate",), 2, 1, budget=50,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Finance Domestic Ammunition Manufacturing",
           "Purchase a limited production facility and qualify its suppliers. Manufacturing still needs workers, materials and ordinary production orders.",
           "construct_mil_factory", ("industrial_guarantees",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_e200_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_e200_2023_factory_tt\nhidden_effect = { TFR_EST_e200_2023_grant_industry = yes }"),
    Policy("maintenance_workshop", "Equip a Defence Servicing and Components Workshop",
           "Finance overhaul tooling and domestic component supply alongside the production programme. This is capacity for equipment Estonia can procure and maintain.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_e200_2023_maintenance_factory_pending\ncustom_effect_tooltip = TFR_EST_e200_2023_factory_tt\nhidden_effect = { TFR_EST_e200_2023_grant_industry = yes }"),
    Policy("drone_development", "Commission Dual-Use Drone Development Trials",
           "Fund inspected prototypes and flight trials with domestic firms and researchers. Successful trials build expertise; they do not instantly supply combat aircraft.",
           "air_fighter", ("maintenance_workshop",), 2, 4, budget=65,
           economic=(("research_speed_factor", .03), ("production_factory_efficiency_gain_factor", .025))),
    Policy("research_tax_credit", "Introduce the Business Research Tax Incentive",
           "Publish eligible research costs and audit rules for the proposed incentive. Its recurring revenue cost enters the public ledger alongside the industrial benefit.",
           "scientific_exchange", ("drone_development",), 2, 5, budget=20,
           economic=(("research_speed_factor", .035), ("production_factory_efficiency_gain_factor", .025)),
           extra="set_temp_variable = { var = income_var_temp value = -0.020 }\nadd_income_with_inflation = yes"),
    Policy("simplified_business", "Simplify Small Companies and Raise the VAT Threshold",
           "Implement the proposed simpler company form and hundred-thousand-euro VAT-registration threshold. Revised filing guidance accompanies the recorded revenue cost.",
           "consumer_goods", ("research_tax_credit",), 2, 6, budget=25,
           economic=(("production_factory_max_efficiency_factor", .03),),
           extra="set_temp_variable = { var = income_var_temp value = -0.010 }\nadd_income_with_inflation = yes"),

    Policy("renewable_permits", "Create the Six-Month Renewable-Permit Procedure",
           "Resource coordinated planning and assessed generating projects toward the proposed shorter procedure. Speed requires capable reviewers, clear standards and reliable delivery obligations.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=70,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .05))),
    Policy("grid_connection", "Release Unused Grid Reservations and Fund Connections",
           "Apply deadlines to unused connection bookings and finance bottleneck upgrades. Operators must demonstrate which projects can connect safely to the network.",
           "construct_infrastructure", ("renewable_permits",), 4, 2, budget=65, readiness=2,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("renovation", "Expand the Residential Energy-Renovation Programme",
           "Commission supervised upgrades against verified heat losses. Funding covers a defined tranche toward the proposed larger renovation effort.",
           "construct_civ_factory", ("grid_connection",), 4, 3, budget=85, cohesion=3,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),
    Policy("storage_guarantees", "Offer Assessed Guarantees for Storage and Microgrids",
           "Share defined technology risks with private investors and energy communities. Contracts specify maintenance, balancing obligations and the limits of public liability.",
           "production", ("renovation",), 4, 4, budget=70,
           economic=(("industrial_capacity_factory", .03), ("local_resources_factor", .025))),
    Policy("interconnectors", "Design the Offshore Grid and Interconnector Programme",
           "Commission surveys, permits and technical agreements for stronger Baltic links. Design work advances the programme without pretending that every proposed cable is already built.",
           "construct_infrastructure", ("storage_guarantees",), 4, 5, budget=80, readiness=2,
           economic=(("industrial_capacity_factory", .025), ("production_speed_buildings_factor", .03))),
    Policy("climate_law", "Legislate the Climate Framework and Procurement Criteria",
           "Publish consistent environmental duties and measurable procurement standards. Firms need dependable rules and transparent assessments when planning investment.",
           "production", ("interconnectors",), 4, 6, budget=20, cohesion=2,
           economic=(("production_factory_efficiency_gain_factor", .025), ("consumer_goods_factor", -.01))),

    Policy("once_only_data", "Enact the Once-Only Data Submission Rule",
           "Connect eligible registries and remove repeated requests for information the state already holds. Test access controls and continuity before moving services to the new process.",
           "scientific_exchange", ("new_mandate",), 6, 1, budget=30, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .035),)),
    Policy("electronic_invoices", "Complete Public-Sector Electronic Invoicing",
           "Migrate procurement payments to compatible machine-readable invoices. Audited administrative savings receive an explicit public-ledger balance amount.",
           "production", ("once_only_data",), 6, 2, budget=25,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_temp_variable = { var = income_var_temp value = 0.012 }\nadd_income_with_inflation = yes"),
    Policy("zero_budget_review", "Rebuild Expenditure through the Zero-Based Budget Review",
           "Require departments to justify existing spending and publish the decisions. Only the reviewed savings enter the ledger; a review does not abolish public services by itself.",
           "consumer_goods", ("electronic_invoices",), 6, 3, budget=20,
           economic=(("consumer_goods_factor", -.02),),
           extra="set_temp_variable = { var = income_var_temp value = 0.025 }\nadd_income_with_inflation = yes"),
    Policy("health_accounts", "Launch Personal Health Accounts and the Employer Allowance",
           "Build the proposed personal health account and twelve-hundred-euro employer contribution allowance. Privacy controls and the recurring fiscal cost accompany the rollout.",
           "consumer_goods", ("zero_budget_review",), 6, 4, budget=35, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .03),),
           extra="set_temp_variable = { var = income_var_temp value = -0.012 }\nadd_income_with_inflation = yes"),
    Policy("care_coordinators", "Place Health and Care Coordinators in Primary Care",
           "Commission coordinators and interoperable case records across health and social services. Patients receive a practical route through services instead of disconnected referrals.",
           "consumer_goods", ("health_accounts",), 6, 5, budget=50, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("mental_health", "Fund Prevention and First-Line Mental-Health Services",
           "Finance assessed prevention programmes, school support and primary-care referrals. Service contracts include trained staff, access standards and regular outcome reviews.",
           "consumer_goods", ("care_coordinators",), 6, 6, budget=50, cohesion=4,
           economic=(("production_factory_efficiency_gain_factor", .03),)),

    Policy("education_investment", "Start the Additional Education Investment Programme",
           "Authorize the first funded stage toward the proposed annual education increase. Teacher recruitment, specialist support and regional delivery receive a common implementation plan.",
           "scientific_exchange", ("new_mandate",), 8, 1, budget=125, cohesion=3,
           economic=(("research_speed_factor", .04),)),
    Policy("teacher_careers", "Fund Teacher Careers toward the Three-Thousand-Euro Objective",
           "Negotiate salary stages, professional development and workload rules. Publish progress toward the proposed pay objective without treating every vacancy as already filled.",
           "scientific_exchange", ("education_investment",), 8, 2, budget=90, cohesion=3,
           economic=(("research_speed_factor", .045),)),
    Policy("common_school", "Finance the Shared Estonian-Language School Transition",
           "Provide language staff, learning materials and school support, including the Ida-Viru school-turnaround programme. Regional plans must support children with different home languages.",
           "scientific_exchange", ("teacher_careers",), 8, 3, budget=65, cohesion=4,
           economic=(("research_speed_factor", .035),)),
    Policy("learning_to_eighteen", "Extend Compulsory Learning to Eighteen",
           "Resource flexible study and workplace-learning routes for young people after basic school. The new obligation requires suitable places and practical support for completion.",
           "scientific_exchange", ("common_school",), 8, 4, budget=45, cohesion=2,
           economic=(("production_factory_efficiency_gain_factor", .03),)),
    Policy("student_loans", "Reform Six-Thousand-Euro Student Loans and Repayment",
           "Fund the revised loan scheme with a longer repayment period and clear eligibility. Publish the guarantee liability and terms so students can plan full-time study.",
           "consumer_goods", ("learning_to_eighteen",), 8, 5, budget=25, cohesion=3,
           economic=(("research_speed_factor", .03),)),
    Policy("e_university", "Launch the Shared Estonian e-University Platform",
           "Commission accessible digital courses across higher-education institutions. Academic quality and practical access matter as much as the platform that distributes them.",
           "scientific_exchange", ("student_loans",), 8, 6, budget=45,
           economic=(("research_speed_factor", .04), ("production_factory_max_efficiency_factor", .025))),

    Policy("account_to_parliament", "Present the Eesti 200 Government's Accounts",
           "Report funded reforms, defence preparation and outstanding commitments to parliament. The next mandate should inherit a clear account of delivery and remaining work.",
           "national_unity", ("civil_reserve", "simplified_business", "climate_law", "mental_health", "e_university"), 4, 7,
           cohesion=3, extra="set_country_flag = TFR_EST_e200_2023_programme_finished\nadd_political_power = 75"),
)

_EARLY_AI = ("new_mandate", "defence_commitment", "industrial_guarantees",
             "ammunition_workshop", "maintenance_workshop", "air_defence",
             "reserve_muster", "kaitseliit_instructors", "allied_reception", "civil_reserve",
             "renewable_permits", "grid_connection", "renovation")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_e200_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_e200_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = GFX_goal_generic_{p.icon}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_e200_2023_branch_visible = yes }}
    available = {{
        TFR_EST_e200_2023_governing = yes{extra}
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
    text = """# An Eesti 200 plurality in the validated 2023 ballot grants this mandate.
TFR_EST_e200_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_e200_2023_mandate
    has_country_flag = TFR_EST_e200_won_2023_election
    NOT = { has_country_flag = TFR_EST_e200_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 6 compare = equals }
}
TFR_EST_e200_2023_governing = {
    TFR_EST_e200_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 6 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 6 compare = equals }
    check_variable = { var = TFR_EST_coalition_e200 value = 1 compare = equals }
}
TFR_EST_e200_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_e200_2023_governing", "TFR_EST_e200_2023_all_policies_done"):
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
    out.append("""# Funded entitlements wait if all eligible states lack unlocked slots.
# Delivery flags change only after construction in an owned-controlled state.
TFR_EST_e200_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_e200_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_e200_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_e200_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_e200_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_e200_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_e200_2023_grant_industry = yes
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
        "TFR_EST_e200_2023_governing_tt": "A confirmed Eesti 200-led cabinet has at least 51 coalition seats.",
        "TFR_EST_e200_2023_all_policies_done_tt": "Complete every other focus in the 2023 Eesti 200 government programme.",
        "TFR_EST_e200_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three response projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_e200_2023.txt": build_focuses(),
        "common/scripted_triggers/TFR_EST_e200_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_e200_2023.txt": build_effects(),
        "localisation/english/TFR_EST_e200_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated Eesti 200 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} Eesti 200 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

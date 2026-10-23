"""Build Isamaa's conditional 2023 mandate: 32 compact, 35-day focuses.

The programme adapts the party's own 2023 election platform to TFR's alternate
timeline. Concrete sources, funding choices and adaptations are recorded in
docs/ISAMAA_2023_SOURCES.md. It does not claim a historical Isamaa-led cabinet.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ratas_continuation import Policy
from focus_reward_model import concise_trigger, modifier_reward
from native_script_interface import amount_call
from post2023_focus_art import build_focus_sprites, focus_sprite


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_isamaa_2023_"
INDUSTRY_PROJECTS = ("ammunition", "maintenance")
ENERGY_STAGES = {"dispatchable_reserve": 2, "grid_connection": 1, "renovation": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_isamaa_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "An Isamaa-Led Parliamentary Mandate",
           "Isamaa has secured the largest delegation. Helir-Valdor Seeder must turn that result into a majority programme with the coalition actually confirmed by parliament.",
           "national_unity", (), 4, 0, cohesion=3,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Fund the Independent Defence Establishment",
           "Authorize the next procurement instalments and publish a funded readiness plan. Estonia's defence commitments require contracts, instructors and dependable stores.",
           "defence", ("new_mandate",), 0, 1, budget=110, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("air_defence", "Prepare Integrated Air Defence Sites",
           "Fund crew instruction, communications and assessed procurement sites. This capability programme must account for operating costs before equipment can be fielded.",
           "air_fighter", ("defence_commitment",), 0, 2, budget=95, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("reserve_muster", "Rehearse the Reserve Mobilisation System",
           "Check call-up records, employers' arrangements and unit stores through scheduled exercises. A reliable muster makes existing formations more usable when warning time is short.",
           "army_doctrines", ("air_defence",), 0, 3, budget=55, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("kaitseliit_ranges", "Build Kaitseliit Training and Range Capacity",
           "Finance instructors and safe range access with local agreements. Territorial units need frequent practice and practical facilities to improve their small-unit work.",
           "army_doctrines", ("reserve_muster",), 0, 4, budget=60, readiness=4,
           military=(("training_time_army_factor", -.04), ("dig_in_speed_factor", .10)),
           extra="army_experience = 10"),
    Policy("allied_reception", "Prepare Allied Reception and Prepositioned Stores",
           "Tender reception facilities and dispersed storage with the allies available to Estonia. Exercise their use; the ordinary allied reinforcement arrangements still govern troop arrivals.",
           "construct_military", ("kaitseliit_ranges",), 0, 5, budget=80, readiness=4,
           military=(("supply_consumption_factor", -.05), ("army_org_factor", .025))),
    Policy("civil_protection", "Give Civil Protection a Funded Legal Basis",
           "Agree responsibilities for warning, evacuation and essential supplies. Councils and rescue services receive exercise funding and clear reporting duties.",
           "national_unity", ("allied_reception",), 0, 6, budget=50, cohesion=3, readiness=4,
           military=(("attrition", -.025), ("army_defence_factor", .025))),

    Policy("industrial_guarantees", "Back Defence-Industry Development Contracts",
           "Fund inspected prototypes and supply contracts with domestic firms. Publish the delivery standards so public development money supports production that the armed forces can maintain.",
           "small_arms", ("new_mandate",), 2, 1, budget=45,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Finance an Ammunition Production Workshop",
           "Pay for a limited production facility and its supplier qualification. The workshop adds industrial capacity; completed ammunition still comes through normal production or paid procurement.",
           "construct_mil_factory", ("industrial_guarantees",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_isamaa_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_isamaa_2023_factory_tt\nhidden_effect = { TFR_EST_isamaa_2023_grant_industry = yes }"),
    Policy("maintenance_workshop", "Finance an Equipment Maintenance Workshop",
           "Fund a second facility for overhaul work and replacement components. Sustainable servicing turns purchases into a usable force without awarding free equipment.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_isamaa_2023_maintenance_factory_pending\ncustom_effect_tooltip = TFR_EST_isamaa_2023_factory_tt\nhidden_effect = { TFR_EST_isamaa_2023_grant_industry = yes }"),
    Policy("regional_value_chains", "Finance Regional Manufacturing Partnerships",
           "Co-fund viable supplier projects with county development centres and researchers. Regional firms should gain skills, orders and access to higher-value work.",
           "construct_civ_factory", ("maintenance_workshop",), 2, 4, budget=70, cohesion=2,
           economic=(("industrial_capacity_factory", .035), ("production_factory_efficiency_gain_factor", .025))),
    Policy("credit_register", "Establish a Positive Credit Register",
           "Set consistent reporting and data-access rules for a responsible lending register. Better assessment should help sound borrowers obtain competing offers while preserving personal-data controls.",
           "scientific_exchange", ("regional_value_chains",), 2, 5, budget=20,
           economic=(("production_speed_buildings_factor", .04), ("production_factory_max_efficiency_factor", .025))),
    Policy("expense_allowances", "Update the Fixed Business-Expense Allowances",
           "Legislate revised travel and work-expense exemptions with clear payroll instructions. Record the revenue reduction alongside simpler administration for employers.",
           "production", ("credit_register",), 2, 6, budget=10,
           economic=(("production_factory_efficiency_gain_factor", .03),),
           extra="set_temp_variable = { var = income_var_temp value = -0.01 }\nadd_income_with_inflation = yes"),

    Policy("dispatchable_reserve", "Contract Dispatchable Domestic Power Reserves",
           "Fund available generating reserves and their fuel arrangements. Reliability contracts must cover maintenance and dispatch obligations while new supply is developed.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=85,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .05))),
    Policy("grid_connection", "Finance Secure Grid Connections",
           "Pay for assessed connection bottlenecks and network works with system operators. Agree technical tests before depending on an additional source of supply.",
           "construct_infrastructure", ("dispatchable_reserve",), 4, 2, budget=70, readiness=2,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("renovation", "Standardise and Fund Energy-Saving Renovation",
           "Give housing associations funded designs, technical supervision and predictable applications. Completed works reduce exposure to high energy bills over time.",
           "construct_civ_factory", ("grid_connection",), 4, 3, budget=75, cohesion=3,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),
    Policy("district_heating", "Modernise District-Heating Networks",
           "Tender viable pipe replacement and heating connections with municipalities. Review heat demand and maintenance before committing to each project.",
           "production", ("renovation",), 4, 4, budget=55,
           economic=(("industrial_capacity_factory", .025), ("production_factory_max_efficiency_factor", .025))),
    Policy("nuclear_studies", "Commission the Nuclear Feasibility and Safety Studies",
           "Finance independent technical, regulatory and waste-management assessments. Parliament receives the evidence for a later investment decision; a study does not deliver a power station.",
           "scientific_exchange", ("district_heating",), 4, 5, budget=30,
           economic=(("research_speed_factor", .035), ("local_resources_factor", .025))),
    Policy("universal_service", "Fund the Extended Electricity Universal Service",
           "Budget a defined support tranche for eligible households and smaller consumers. Publish the contract terms and review the public liability as market conditions change.",
           "consumer_goods", ("nuclear_studies",), 4, 6, budget=65, cohesion=3,
           economic=(("consumer_goods_factor", -.02),)),

    Policy("child_tax_allowance", "Legislate the Five-Thousand-Euro Child Allowance",
           "Prepare the proposed annual child-linked income exemption and payroll guidance. Household relief has a recurring public revenue cost that must be recorded.",
           "consumer_goods", ("new_mandate",), 6, 1, budget=15, cohesion=3,
           economic=(("consumer_goods_factor", -.02),),
           extra="set_temp_variable = { var = income_var_temp value = -0.035 }\nadd_income_with_inflation = yes"),
    Policy("joint_returns", "Permit Joint Income-Tax Returns for Spouses",
           "Update tax administration and the rules for joint declarations. Explain eligibility and the resulting public cost before the first filing period.",
           "consumer_goods", ("child_tax_allowance",), 6, 2, budget=10, cohesion=2,
           economic=(("consumer_goods_factor", -.01),),
           extra="set_temp_variable = { var = income_var_temp value = -0.015 }\nadd_income_with_inflation = yes"),
    Policy("child_benefit", "Fund Equal Hundred-Euro Child Benefits",
           "Finance the proposed first- and second-child benefit level with an administrative rollout. Review delivery with social-insurance officials and municipalities.",
           "consumer_goods", ("joint_returns",), 6, 3, budget=65, cohesion=4,
           economic=(("consumer_goods_factor", -.015),)),
    Policy("large_family_homes", "Launch the Large-Family Housing Grant Round",
           "Open an assessed grant round for eligible large families and rural housing. Public guarantees and grants require realistic valuations and construction supervision.",
           "construct_civ_factory", ("child_benefit",), 6, 4, budget=70, cohesion=3,
           economic=(("production_speed_buildings_factor", .04),)),
    Policy("care_leave", "Protect Care Benefits after Parental Leave",
           "Fund revised care-benefit calculations for parents returning to work. Clear employer guidance helps families respond when a child falls ill.",
           "consumer_goods", ("large_family_homes",), 6, 5, budget=35, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("maintenance_support", "Raise Child Maintenance Assistance to Two Hundred Euros",
           "Finance the proposed assistance ceiling and strengthen recovery from liable parents. Coordinate claims so children receive support without unnecessary administrative delay.",
           "consumer_goods", ("care_leave",), 6, 6, budget=25, cohesion=4,
           economic=(("consumer_goods_factor", -.01),)),

    Policy("estonian_schools", "Resource the Estonian-Language School Transition",
           "Contract teacher training, learning materials and school support. A funded transition needs qualified staff and practical help for pupils in each municipality.",
           "scientific_exchange", ("new_mandate",), 8, 1, budget=65, cohesion=2,
           economic=(("research_speed_factor", .035),)),
    Policy("teacher_pay", "Fund Steps toward the Teachers' Pay Objective",
           "Negotiate funded salary steps and training places with school owners. Publish progress toward the proposed minimum rather than declaring every staffing problem solved.",
           "scientific_exchange", ("estonian_schools",), 8, 2, budget=75, cohesion=3,
           economic=(("research_speed_factor", .04),)),
    Policy("research_compact", "Agree the Public-Private Research Funding Compact",
           "Award assessed research and industrial collaboration grants. Match public funding with credible private commitments and publish the results.",
           "scientific_exchange", ("teacher_pay",), 8, 3, budget=70,
           economic=(("research_speed_factor", .035), ("production_factory_efficiency_gain_factor", .025))),
    Policy("rural_internet", "Fund Reliable Rural Broadband Connections",
           "Target unserved connections with transparent tenders and shared civil works. Schools, firms and remote workers need a service that remains dependable in poor weather.",
           "construct_infrastructure", ("research_compact",), 8, 4, budget=45,
           economic=(("production_speed_buildings_factor", .03), ("production_factory_efficiency_gain_factor", .025))),
    Policy("digital_baseline", "Guarantee Core Digital-Service Maintenance Funding",
           "Budget security updates, continuity exercises and simpler data submission. Agencies must maintain the services already in use alongside new development.",
           "scientific_exchange", ("rural_internet",), 8, 5, budget=35, readiness=2,
           economic=(("research_speed_factor", .025), ("production_factory_max_efficiency_factor", .025))),
    Policy("home_care", "Expand Financed Home-Care Services",
           "Contract visits and support with councils and care providers. Review access and staffing so families can rely on practical help at home.",
           "consumer_goods", ("digital_baseline",), 8, 6, budget=45, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),

    Policy("account_to_parliament", "Present the Isamaa Government's Accounts",
           "Report the funded programme and remaining obligations to the Riigikogu. Parliament should be able to assess defence preparation and service delivery before the next mandate.",
           "national_unity", ("civil_protection", "expense_allowances", "universal_service", "maintenance_support", "home_care"), 4, 7,
           cohesion=3, extra="set_country_flag = TFR_EST_isamaa_2023_programme_finished\nadd_political_power = 75"),
)


_EARLY_AI = ("new_mandate", "defence_commitment", "industrial_guarantees",
             "ammunition_workshop", "maintenance_workshop", "air_defence",
             "reserve_muster", "kaitseliit_ranges", "allied_reception", "civil_protection",
             "dispatchable_reserve", "grid_connection", "renovation")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_isamaa_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_isamaa_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = {focus_sprite("isamaa", p.suffix)}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_isamaa_2023_branch_visible = yes }}
    available = {{
        TFR_EST_isamaa_2023_governing = yes{extra}
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
    text = """# A Isamaa plurality in the validated 2023 ballot grants this mandate.
TFR_EST_isamaa_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_isamaa_2023_mandate
    has_country_flag = TFR_EST_isamaa_won_2023_election
    NOT = { has_country_flag = TFR_EST_isamaa_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 4 compare = equals }
}
TFR_EST_isamaa_2023_governing = {
    TFR_EST_isamaa_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 4 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 4 compare = equals }
    check_variable = { var = TFR_EST_coalition_isamaa value = 1 compare = equals }
}
TFR_EST_isamaa_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_isamaa_2023_governing", "TFR_EST_isamaa_2023_all_policies_done"):
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
TFR_EST_isamaa_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_isamaa_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_isamaa_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_isamaa_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_isamaa_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_isamaa_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_isamaa_2023_grant_industry = yes
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
        "TFR_EST_isamaa_2023_governing_tt": "A confirmed Isamaa-led cabinet has at least 51 coalition seats.",
        "TFR_EST_isamaa_2023_all_policies_done_tt": "Complete every other focus in the 2023 Isamaa government programme.",
        "TFR_EST_isamaa_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three response projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_isamaa_2023.txt": build_focuses(),
        "interface/TFR_EST_isamaa_2023_focus_icons.gfx": build_focus_sprites(POLICIES, "isamaa", "build_isamaa_2023.py"),
        "common/scripted_triggers/TFR_EST_isamaa_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_isamaa_2023.txt": build_effects(),
        "localisation/english/TFR_EST_isamaa_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated Isamaa 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} Isamaa 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

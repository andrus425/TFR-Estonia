"""Build Centre's conditional 2023 mandate: 32 compact, 35-day focuses.

Contemporary Centre policy proposals and the gameplay adaptations are recorded
in docs/CENTRE_2023_SOURCES.md. This is a hypothetical parliamentary programme,
not an attribution of the historical Reform-led cabinet's actions to Centre.
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
PREFIX = "TFR_EST_centre_2023_"
INDUSTRY_PROJECTS = ("ammunition", "maintenance")
ENERGY_STAGES = {"power_reserves": 2, "local_chp": 1, "apartment_renovation": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_centre_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "A New Centre-Led Mandate",
           "Centre has won the largest delegation. Jüri Ratas must agree a funded programme with the actual coalition, linking public services and regional investment to defence preparation.",
           "national_unity", (), 4, 0, cohesion=3,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Fund the Cross-Party Defence Commitment",
           "Invite parliamentary parties to a common defence agreement and fund its first procurement instalments. Publish lifetime costs so a spending pledge supports usable capabilities.",
           "defence", ("new_mandate",), 0, 1, budget=110, cohesion=1, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("air_defence", "Finance Medium-Range Air Defence Preparation",
           "Budget sites, crews and joint procurement planning with available allies. An integrated protection plan must account for maintenance and deliveries before declaring a new capability.",
           "air_fighter", ("defence_commitment",), 0, 2, budget=95, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("reserve_expertise", "Put Reservists' Civilian Skills to Work",
           "Match reserve appointments to civilian expertise and fund refresher instruction. Engineers, medics and transport specialists need reliable records and ordinary recruitment arrangements.",
           "army_doctrines", ("air_defence",), 0, 3, budget=55, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("allied_basing", "Prepare Permanent Allied Reception Facilities",
           "Finance reception, communications and dispersed stores for allied troops. Existing reinforcement decisions remain separate; new facilities improve how Estonia sustains the forces that actually arrive.",
           "construct_military", ("reserve_expertise",), 0, 4, budget=75, readiness=4,
           military=(("supply_consumption_factor", -.05), ("army_org_factor", .025))),
    Policy("community_training", "Agree Training-Area Compensation with Communities",
           "Negotiate access, compensation and exercise arrangements with councils and residents. Defence training needs usable land and instructors alongside a settlement people can understand.",
           "army_doctrines", ("allied_basing",), 0, 5, budget=50, cohesion=2, readiness=4,
           military=(("training_time_army_factor", -.04), ("dig_in_speed_factor", .10)),
           extra="army_experience = 10"),
    Policy("civil_continuity", "Rehearse Municipal Civil Protection",
           "Fund municipal warning, evacuation and essential-service exercises. Coordinate councils, employers and rescue services so civilian preparation supports the army's ability to keep operating.",
           "national_unity", ("community_training",), 0, 6, budget=45, cohesion=3, readiness=4,
           military=(("attrition", -.025), ("army_defence_factor", .025))),

    # These two funded workshops compress the platform's domestic defence-
    # industry support into a limited, usable TFR preparation programme.
    Policy("industrial_guarantees", "Back Domestic Defence Suppliers",
           "Set aside guarantees and development funding for maintainable domestic contracts. Give suppliers clear inspection and delivery requirements instead of replacing procurement with announcements.",
           "small_arms", ("new_mandate",), 2, 1, budget=45,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Finance a Domestic Ammunition Workshop",
           "Fund one inspected production workshop and the supplier contracts needed to operate it. The project adds capacity; ammunition must still enter through ordinary production or paid procurement.",
           "construct_mil_factory", ("industrial_guarantees",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_centre_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_centre_2023_factory_tt\nhidden_effect = { TFR_EST_centre_2023_grant_industry = yes }"),
    Policy("maintenance_workshop", "Finance an Equipment Maintenance Workshop",
           "Pay for a second facility able to overhaul equipment and make replacement components. Domestic maintenance keeps purchases useful without awarding free vehicles or another army.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_centre_2023_maintenance_factory_pending\ncustom_effect_tooltip = TFR_EST_centre_2023_factory_tt\nhidden_effect = { TFR_EST_centre_2023_grant_industry = yes }"),
    Policy("ida_viru_innovation", "Fund New Technology in Ida-Viru Industry",
           "Select viable modernization projects with local employers and research institutions. Innovation funding should support productive jobs as the county's industrial base changes.",
           "scientific_exchange", ("maintenance_workshop",), 2, 4, budget=75,
           economic=(("industrial_capacity_factory", .035), ("research_speed_factor", .025))),
    Policy("regional_jobs", "Guarantee Investment in High-Unemployment Regions",
           "Offer assessed investment guarantees and retraining in regions with fewer jobs. Publish outcomes and risks so regional policy creates opportunities rather than concealing failing projects.",
           "construct_civ_factory", ("ida_viru_innovation",), 2, 5, budget=55, cohesion=3,
           economic=(("production_factory_efficiency_gain_factor", .03), ("industrial_capacity_factory", .025))),
    Policy("construction_orders", "Place the Funded Public Construction Orders",
           "Tender a staged public-building programme and disclose its financing. Predictable orders can sustain construction skills while delivering facilities that municipalities actually need.",
           "construct_infrastructure", ("regional_jobs",), 2, 6, budget=90,
           economic=(("production_speed_buildings_factor", .05),)),

    Policy("power_reserves", "Keep Dispatchable Generation and LNG Options Ready",
           "Fund reliable generating reserves and permanent-terminal preparation. Keep existing capacity usable while alternative supplies develop, with fuel and operating costs included.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=85,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .05))),
    Policy("local_chp", "Support Local Heat-and-Power Projects",
           "Finance viable combined heat-and-power projects and their network access. Local heat demand and sustainable fuel contracts should determine which schemes receive support.",
           "production", ("power_reserves",), 4, 2, budget=60,
           economic=(("industrial_capacity_factory", .03), ("production_factory_max_efficiency_factor", .025))),
    Policy("apartment_renovation", "Lower the Rural Renovation Contribution",
           "Fund apartment renovations outside the largest cities with a smaller local contribution. Technical supervision and affordable loans help associations deliver lasting energy savings.",
           "construct_civ_factory", ("local_chp",), 4, 3, budget=75, cohesion=3,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),
    Policy("weatherproof_grid", "Weatherproof the Distribution Grid",
           "Prioritize vulnerable lines and connection bottlenecks with transmission and distribution operators. Underground works and stronger substations need agreed sites, budgets and maintenance.",
           "construct_infrastructure", ("apartment_renovation",), 4, 4, budget=65, readiness=2,
           economic=(("industrial_capacity_factory", .025), ("production_speed_buildings_factor", .025))),
    Policy("rural_broadband", "Finish Affordable Last-Mile Connections",
           "Support household and enterprise connections where commercial rollout remains insufficient. Coordinate trenches and public works to reduce disruption and reach isolated settlements.",
           "scientific_exchange", ("weatherproof_grid",), 4, 5, budget=45,
           economic=(("research_speed_factor", .025), ("production_factory_efficiency_gain_factor", .025))),
    Policy("energy_cooperatives", "Finance Community Energy Cooperatives",
           "Offer assessed financing and technical advice for local generation and storage. Communities need viable projects and transparent ownership rather than a promise of unlimited cheap power.",
           "oil_refinery", ("rural_broadband",), 4, 6, budget=45, cohesion=2,
           economic=(("local_resources_factor", .04), ("consumer_goods_factor", -.01))),

    Policy("progressive_income_tax", "Introduce the Thirty-Percent Upper Income Band",
           "Legislate the higher band for income above twice the average wage and prepare tax administration. Budget additional receipts while accounting for opposition to the distributional change.",
           "political_pressure", ("new_mandate",), 6, 1, budget=15, cohesion=-2,
           extra="set_temp_variable = { var = income_var_temp value = 0.045 }\nadd_income_with_inflation = yes\nadd_political_power = -25"),
    Policy("minimum_tax_allowance", "Link the Tax Allowance to the Minimum Wage",
           "Apply the proposed minimum-wage exemption with clear payroll guidance. Lower earners retain more income, while the treasury records the recurring cost alongside the new upper band.",
           "consumer_goods", ("progressive_income_tax",), 6, 2, cohesion=3,
           economic=(("consumer_goods_factor", -.02),),
           extra="set_temp_variable = { var = income_var_temp value = -0.03 }\nadd_income_with_inflation = yes"),
    Policy("food_vat", "Reduce Food VAT to Five Percent",
           "Legislate the reduced food rate and check how retailers pass it through. Finance the revenue loss explicitly rather than assuming lower prices eliminate the budget tradeoff.",
           "consumer_goods", ("minimum_tax_allowance",), 6, 3, cohesion=3,
           economic=(("consumer_goods_factor", -.025),),
           extra="set_temp_variable = { var = income_var_temp value = -0.04 }\nadd_income_with_inflation = yes"),
    Policy("prescription_vat", "Remove VAT from Prescription Medicines",
           "Prepare the proposed exemption and lower rate for other medicines. Update pharmacy billing and monitor access while recording the reduction in public receipts.",
           "consumer_goods", ("food_vat",), 6, 4, cohesion=3,
           economic=(("consumer_goods_factor", -.01), ("production_factory_max_efficiency_factor", .025)),
           extra="set_temp_variable = { var = income_var_temp value = -0.012 }\nadd_income_with_inflation = yes"),
    Policy("pension_fifty", "Fund the Next Fifty-Euro Pension Step",
           "Finance the first extraordinary increase in the basic pension component. It is a funded step toward the party's longer-term pension objective, rather than an instant fulfilment of every future payment.",
           "consumer_goods", ("prescription_vat",), 6, 5, budget=70, cohesion=4,
           economic=(("consumer_goods_factor", -.015),)),
    Policy("home_care", "Expand Municipal Home Nursing and Care",
           "Contract more care at home with councils and health providers. Dependable visits and support for family carers can preserve independence and reduce pressure on institutional services.",
           "consumer_goods", ("pension_fifty",), 6, 6, budget=45, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),

    Policy("county_hospitals", "Give County Hospitals Predictable Budgets",
           "Fund county hospitals against assessed service needs, including areas with fewer patients. A dependable budget should preserve access while requiring reporting on staffing and treatment.",
           "consumer_goods", ("new_mandate",), 8, 1, budget=60, cohesion=3,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("second_day_sick_pay", "Restore Sick Pay from the Second Day",
           "Fund the proposed shared compensation arrangement with employers. Employees gain a clearer basis for staying home when ill, and the public contribution remains visible.",
           "consumer_goods", ("county_hospitals",), 8, 2, budget=40, cohesion=3,
           economic=(("industrial_capacity_factory", .025),)),
    Policy("free_kindergarten", "Compensate Councils for Free Kindergarten Places",
           "Finance the municipal cost of the promised places and review capacity. Fee relief must be accompanied by staff and premises so parents can actually use the service.",
           "consumer_goods", ("second_day_sick_pay",), 8, 3, budget=60, cohesion=3,
           economic=(("production_factory_efficiency_gain_factor", .025),)),
    Policy("teacher_pay", "Negotiate the Teachers' Pay Roadmap",
           "Agree funded pay steps with municipalities and unions. Staffing and support specialists must be included alongside the longer-term salary objective.",
           "scientific_exchange", ("free_kindergarten",), 8, 4, budget=55, cohesion=3,
           economic=(("research_speed_factor", .04),)),
    Policy("language_courses", "Offer Free Estonian Courses and Study Leave",
           "Finance language instruction adapted to work and daily life, including support for citizenship applicants. Clear access and paid learning time help residents participate in public institutions.",
           "scientific_exchange", ("teacher_pay",), 8, 5, budget=30, cohesion=4,
           economic=(("research_speed_factor", .025),)),
    Policy("minorities_council", "Convene the National-Minorities Advisory Council",
           "Create a consultative forum and support community cultural organizations. Publish its recommendations and connect them with practical public-service access without changing electoral eligibility.",
           "national_unity", ("language_courses",), 8, 6, budget=20, cohesion=4,
           extra="add_political_power = 35"),

    Policy("account_to_parliament", "Report on the Centre Government's Programme",
           "Present the investment, tax and service accounts to the Riigikogu. Assess defence readiness and the projects still in progress without calling an election or directing the European war.",
           "national_unity", ("civil_continuity", "construction_orders", "energy_cooperatives", "home_care", "minorities_council"), 4, 8,
           cohesion=3, extra="set_country_flag = TFR_EST_centre_2023_programme_finished\nadd_political_power = 75"),
)


_EARLY_AI = ("new_mandate", "defence_commitment", "industrial_guarantees",
             "ammunition_workshop", "maintenance_workshop", "air_defence",
             "reserve_expertise", "allied_basing", "community_training", "civil_continuity",
             "power_reserves", "local_chp", "apartment_renovation")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_centre_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_centre_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = {focus_sprite("centre", p.suffix)}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_centre_2023_branch_visible = yes }}
    available = {{
        TFR_EST_centre_2023_governing = yes{extra}
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
    text = """# A Centre plurality in the validated 2023 ballot grants this mandate.
TFR_EST_centre_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_centre_2023_mandate
    has_country_flag = TFR_EST_centre_won_2023_election
    NOT = { has_country_flag = TFR_EST_centre_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 2 compare = equals }
}
TFR_EST_centre_2023_governing = {
    TFR_EST_centre_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_coalition_centre value = 1 compare = equals }
}
TFR_EST_centre_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_centre_2023_governing", "TFR_EST_centre_2023_all_policies_done"):
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
TFR_EST_centre_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_centre_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_centre_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_centre_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_centre_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_centre_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_centre_2023_grant_industry = yes
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
        "TFR_EST_centre_2023_governing_tt": "A confirmed Centre-led cabinet has at least 51 coalition seats.",
        "TFR_EST_centre_2023_all_policies_done_tt": "Complete every other focus in the 2023 Centre government programme.",
        "TFR_EST_centre_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three response projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_centre_2023.txt": build_focuses(),
        "interface/TFR_EST_centre_2023_focus_icons.gfx": build_focus_sprites(POLICIES, "centre", "build_centre_2023.py"),
        "common/scripted_triggers/TFR_EST_centre_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_centre_2023.txt": build_effects(),
        "localisation/english/TFR_EST_centre_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated Centre 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} Centre 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

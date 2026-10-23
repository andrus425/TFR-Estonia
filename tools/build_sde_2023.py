"""Build SDE's conditional 2023 mandate: 32 compact, 35-day focuses.

The programme adapts the party's own 2023 election platform to TFR's alternate
timeline. Concrete sources, funding choices and adaptations are recorded in
docs/SDE_2023_SOURCES.md. It does not claim a historical SDE-led cabinet.
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
PREFIX = "TFR_EST_sde_2023_"
INDUSTRY_PROJECTS = ("ammunition", "maintenance")
ENERGY_STAGES = {"renewable_contracts": 2, "grid_connection": 1, "renovation": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_sde_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "A Social Democratic Parliamentary Mandate",
           "SDE has won the largest delegation. Lauri Läänemets must assemble a majority capable of funding social protection alongside credible national defence.",
           "national_unity", (), 4, 0, cohesion=3,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Finance the Critical Defence Capabilities",
           "Approve a funded procurement tranche and operating provision. Parliament will review deliveries and the next spending round before making further commitments.",
           "defence", ("new_mandate",), 0, 1, budget=115, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("air_defence", "Prepare Layered Air-Defence Procurement",
           "Assess sites, train crews and contract compatible communications. The armed forces receive preparation for purchases that still require equipment and sustained funding.",
           "air_fighter", ("defence_commitment",), 0, 2, budget=100, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("reserve_muster", "Reorganise Rapid Reserve Mobilisation",
           "Audit call-up assignments with employers and commanders. Exercises will test whether the existing reserve structure can assemble and sustain its units in time.",
           "army_doctrines", ("air_defence",), 0, 3, budget=55, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("kaitseliit_instructors", "Resource Kaitseliit Instructors and Volunteers",
           "Commission additional training sessions and inspected equipment maintenance. Volunteer defence needs predictable instruction and workable arrangements with civilian employment.",
           "army_doctrines", ("reserve_muster",), 0, 4, budget=60, readiness=4,
           military=(("training_time_army_factor", -.04), ("dig_in_speed_factor", .10)),
           extra="army_experience = 10"),
    Policy("allied_reception", "Prepare Reception Facilities for Allied Forces",
           "Exercise reception routes and dispersed stores with Estonia's available allies. Normal reinforcement agreements still determine which allied formations arrive.",
           "construct_military", ("kaitseliit_instructors",), 0, 5, budget=80, readiness=4,
           military=(("supply_consumption_factor", -.05), ("army_org_factor", .025))),
    Policy("civil_protection", "Fund Shelters, Sirens and Community Training",
           "Open a supervised civil-protection grant round. Rescue services and councils must demonstrate how warning systems, shelter access and evacuation exercises will work together.",
           "national_unity", ("allied_reception",), 0, 6, budget=65, cohesion=3, readiness=5,
           military=(("attrition", -.025), ("army_defence_factor", .025))),

    Policy("industrial_guarantees", "Back Joint Defence-Industry Development",
           "Select inspected prototypes and supplier partnerships with domestic firms. Contracts should retain technical knowledge and service capacity in Estonia.",
           "small_arms", ("new_mandate",), 2, 1, budget=45,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Finance an Ammunition Manufacturing Workshop",
           "Purchase a limited production facility and qualify its suppliers. Its output still depends on workers, materials and ordinary production orders.",
           "construct_mil_factory", ("industrial_guarantees",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_sde_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_sde_2023_factory_tt\nhidden_effect = { TFR_EST_sde_2023_grant_industry = yes }"),
    Policy("maintenance_workshop", "Finance Military Equipment Servicing Capacity",
           "Fund an overhaul workshop and replacement-component tooling. This investment adds capacity for the equipment Estonia can actually afford to procure.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_sde_2023_maintenance_factory_pending\ncustom_effect_tooltip = TFR_EST_sde_2023_factory_tt\nhidden_effect = { TFR_EST_sde_2023_grant_industry = yes }"),
    Policy("regional_jobs", "Launch the Regional Skilled-Jobs Investment Round",
           "Negotiate assessed projects with councils, employers and worker representatives. Publish the training obligations and employment results attached to each award.",
           "construct_civ_factory", ("maintenance_workshop",), 2, 4, budget=85, cohesion=3,
           economic=(("industrial_capacity_factory", .035), ("production_factory_efficiency_gain_factor", .025))),
    Policy("applied_research", "Fund Applied Research and Industrial Automation",
           "Award competitive grants against credible delivery milestones. Researchers and manufacturers should share the practical risks of bringing a new process into production.",
           "scientific_exchange", ("regional_jobs",), 2, 5, budget=80,
           economic=(("research_speed_factor", .04), ("production_factory_max_efficiency_factor", .03))),
    Policy("ultrafast_internet", "Tender the Unserved Broadband Connections",
           "Target connections that commercial rollout has left behind. Contracts need service standards, realistic maintenance obligations and access for local firms and schools.",
           "construct_infrastructure", ("applied_research",), 2, 6, budget=45,
           economic=(("production_speed_buildings_factor", .035), ("production_factory_efficiency_gain_factor", .025))),

    Policy("renewable_contracts", "Finance Assessed Renewable-Power Projects",
           "Contract viable generating capacity with clear delivery and reliability obligations. Investment must account for balancing needs and the networks serving each project.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=85,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .05))),
    Policy("grid_connection", "Fund Thirty-Kilowatt Household Grid Connections",
           "Finance the proposed connection allowance through transparent eligibility rules. Operators must assess network capacity before promising a household that it can export power.",
           "construct_infrastructure", ("renewable_contracts",), 4, 2, budget=65, readiness=2,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("renovation", "Open the Inclusive Energy-Renovation Grant Round",
           "Commission supervised building upgrades with accessible designs. The grant round targets high losses and practical savings instead of declaring the housing stock modernised at once.",
           "construct_civ_factory", ("grid_connection",), 4, 3, budget=85, cohesion=3,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),
    Policy("strategic_reserves", "Contract Strategic Energy Reserves and Storage",
           "Budget tested reserves and storage trials for interrupted supply. Stock management and replacement schedules must be included in every contract.",
           "production", ("renovation",), 4, 4, budget=65, readiness=3,
           economic=(("industrial_capacity_factory", .03), ("local_resources_factor", .025))),
    Policy("energy_cooperatives", "Support Community Energy Cooperatives",
           "Provide technical assistance and accountable finance for viable shared projects. Members receive clear contracts covering ownership, maintenance and their share of the risks.",
           "consumer_goods", ("strategic_reserves",), 4, 5, budget=35, cohesion=3,
           economic=(("consumer_goods_factor", -.015), ("production_factory_efficiency_gain_factor", .025))),
    Policy("district_heating", "Modernise District Heating with Reserve Capacity",
           "Tender heat-network upgrades against verified demand. Councils must preserve a workable fallback while replacing inefficient equipment and pipes.",
           "production", ("energy_cooperatives",), 4, 6, budget=60,
           economic=(("industrial_capacity_factory", .025), ("production_factory_max_efficiency_factor", .025))),

    Policy("progressive_tax", "Legislate the Twenty-Eight-Percent Upper Tax Band",
           "Publish the new income and dividend schedules with clear filing guidance. Additional receipts enter the public ledger alongside the administration costs.",
           "consumer_goods", ("new_mandate",), 6, 1, budget=20, cohesion=2,
           economic=(("production_factory_max_efficiency_factor", .025),),
           extra="set_temp_variable = { var = income_var_temp value = 0.055 }\nadd_income_with_inflation = yes"),
    Policy("minimum_wage", "Agree the Steps toward a Twelve-Hundred-Euro Minimum Wage",
           "Negotiate funded stages with the social partners and inspect implementation. Transitional assistance helps smaller employers adapt without treating a statutory target as instant prosperity.",
           "consumer_goods", ("progressive_tax",), 6, 2, budget=75, cohesion=4,
           economic=(("consumer_goods_factor", -.02), ("industrial_capacity_factory", .025))),
    Policy("collective_bargaining", "Extend Sectoral Collective Bargaining",
           "Resource mediation and enforcement so agreements can operate beyond the strongest workplaces. Publish coverage and compliance data with unions and employers.",
           "national_unity", ("minimum_wage",), 6, 3, budget=25, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .035),)),
    Policy("learning_leave", "Fund Working-Time Study and Career Changes",
           "Open assessed training places and agree study arrangements with employers. Public support follows completed learning and practical opportunities to change occupation.",
           "scientific_exchange", ("collective_bargaining",), 6, 4, budget=50,
           economic=(("research_speed_factor", .035), ("production_factory_efficiency_gain_factor", .03))),
    Policy("child_benefit", "Fund the Indexed Hundred-and-Fifty-Euro Child Benefit",
           "Finance the proposed benefit level with delivery checks and a published review. Families need predictable support and a service that handles their claims reliably.",
           "consumer_goods", ("learning_leave",), 6, 5, budget=80, cohesion=4,
           economic=(("consumer_goods_factor", -.02),)),
    Policy("rental_homes", "Commission the First Public Rental-Housing Tranche",
           "Assess sites, construction costs and long-term management before awarding the first projects. Housing providers remain accountable for upkeep and access.",
           "construct_civ_factory", ("child_benefit",), 6, 6, budget=95, cohesion=3,
           economic=(("production_speed_buildings_factor", .045),)),

    Policy("universal_health", "Finance Universal Health-Insurance Access",
           "Update eligibility, service purchasing and public funding together. Coverage must be supported by commissioned care and a practical route for patients to use it.",
           "consumer_goods", ("new_mandate",), 8, 1, budget=85, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("mental_health", "Commission Community Mental-Health Services",
           "Train and contract staff for accessible referrals, prioritising children and young people. Review waiting times and coordination with schools and primary care.",
           "consumer_goods", ("universal_health",), 8, 2, budget=45, cohesion=3,
           economic=(("production_factory_efficiency_gain_factor", .03),)),
    Policy("pension_base", "Fund a Step toward the Pension Objective",
           "Authorize an affordable increase and publish the outstanding liability. Pension policy needs dependable financing rather than an unfunded declaration that the target has been met.",
           "consumer_goods", ("mental_health",), 8, 3, budget=85, cohesion=4,
           economic=(("consumer_goods_factor", -.02),)),
    Policy("care_home", "Make Assessed Residential Care Affordable on a Pension",
           "Contract places against care-quality and staffing standards. Councils must explain assessed needs, fees and the public contribution to each family.",
           "consumer_goods", ("pension_base",), 8, 4, budget=65, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("teacher_pay", "Fund the Teachers' Salary and Career Agreement",
           "Negotiate salary stages, training places and manageable workloads with schools. Publish progress alongside vacancies and retention rather than promising staff who are not available.",
           "scientific_exchange", ("care_home",), 8, 5, budget=80, cohesion=3,
           economic=(("research_speed_factor", .045),)),
    Policy("inclusive_schools", "Resource Shared Estonian-Language Schooling",
           "Provide trained language staff, learning materials and specialist support. Schools need practical help to teach children from different home-language backgrounds together.",
           "scientific_exchange", ("teacher_pay",), 8, 6, budget=60, cohesion=4,
           economic=(("research_speed_factor", .035),)),

    Policy("account_to_parliament", "Present the Social Democratic Government's Accounts",
           "Report funded reforms, readiness and outstanding commitments to parliament. The next mandate should begin with an honest account of what has been delivered.",
           "national_unity", ("civil_protection", "ultrafast_internet", "district_heating", "rental_homes", "inclusive_schools"), 4, 7,
           cohesion=3, extra="set_country_flag = TFR_EST_sde_2023_programme_finished\nadd_political_power = 75"),
)

_EARLY_AI = ("new_mandate", "defence_commitment", "industrial_guarantees",
             "ammunition_workshop", "maintenance_workshop", "air_defence",
             "reserve_muster", "kaitseliit_instructors", "allied_reception", "civil_protection",
             "renewable_contracts", "grid_connection", "renovation")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_sde_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_sde_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = {focus_sprite("sde", p.suffix)}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_sde_2023_branch_visible = yes }}
    available = {{
        TFR_EST_sde_2023_governing = yes{extra}
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
    text = """# An SDE plurality in the validated 2023 ballot grants this mandate.
TFR_EST_sde_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_sde_2023_mandate
    has_country_flag = TFR_EST_sde_won_2023_election
    NOT = { has_country_flag = TFR_EST_sde_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 5 compare = equals }
}
TFR_EST_sde_2023_governing = {
    TFR_EST_sde_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 5 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 5 compare = equals }
    check_variable = { var = TFR_EST_coalition_sde value = 1 compare = equals }
}
TFR_EST_sde_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_sde_2023_governing", "TFR_EST_sde_2023_all_policies_done"):
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
TFR_EST_sde_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_sde_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_sde_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_sde_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_sde_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_sde_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_sde_2023_grant_industry = yes
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
        "TFR_EST_sde_2023_governing_tt": "A confirmed SDE-led cabinet has at least 51 coalition seats.",
        "TFR_EST_sde_2023_all_policies_done_tt": "Complete every other focus in the 2023 SDE government programme.",
        "TFR_EST_sde_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three response projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_sde_2023.txt": build_focuses(),
        "interface/TFR_EST_sde_2023_focus_icons.gfx": build_focus_sprites(POLICIES, "sde", "build_sde_2023.py"),
        "common/scripted_triggers/TFR_EST_sde_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_sde_2023.txt": build_effects(),
        "localisation/english/TFR_EST_sde_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated SDE 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} SDE 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

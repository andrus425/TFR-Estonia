"""Build Parempoolsed's conditional 2023 mandate: 32 compact, 35-day focuses.

The programme adapts the party's own 2023 election platform to TFR's alternate
timeline. Concrete sources, funding choices and adaptations are recorded in
docs/PP_2023_SOURCES.md. It does not claim a historical Parempoolsed-led cabinet.
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
PREFIX = "TFR_EST_pp_2023_"
INDUSTRY_PROJECTS = ("ammunition", "maintenance")
ENERGY_STAGES = {"renewable_permits": 2, "grid_connection": 1, "continuity_capacity": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_pp_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "A Parempoolsed Mandate for a Capable State",
           "The new majority must reconcile a smaller civilian state with stronger defence. Parliament will scrutinize the funding and consequences of each reform.",
           "national_unity", (), 4, 0, cohesion=3,
           extra="add_political_power = 50"),

    Policy("defence_commitment", "Fund the Three-Percent Defence Investment Agreement",
           "Approve the opening procurement tranche of a cross-party defence agreement. Allied reception remains a separate funding commitment.",
           "defence", ("new_mandate",), 0, 1, budget=125, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("air_defence", "Train Air-Defence Crews and Procure Communications",
           "Use the investment plan to prepare sites, train crews and purchase compatible communications. Delivering a functioning capability requires sustained procurement.",
           "air_fighter", ("defence_commitment",), 0, 2, budget=105, readiness=4,
           military=(("army_defence_factor", .05), ("attrition", -.025))),
    Policy("reserve_muster", "Open Defence Roles to More Skills",
           "Revise service rules and exercise existing call-up plans. Civilian specialists, alternative service and voluntary service can fill genuine capability gaps.",
           "army_doctrines", ("air_defence",), 0, 3, budget=50, readiness=6,
           military=(("mobilization_speed", .20), ("training_time_army_factor", -.05)),
           extra="set_country_flag = TFR_EST_reserve_plan\ncustom_effect_tooltip = TFR_EST_reserve_plan_tt"),
    Policy("civil_reserve", "Organize the Ten-Thousand-Person Civil Reserve",
           "Begin registering and training a nonmilitary reserve toward the proposed ten-thousand-person objective. Skills and civilian availability must be verified.",
           "army_doctrines", ("reserve_muster",), 0, 4, budget=60, readiness=4,
           military=(("training_time_army_factor", -.04), ("dig_in_speed_factor", .10)),
           extra="army_experience = 10"),
    Policy("allied_reception", "Fund Allied Reception Outside the Defence Baseline",
           "Prepare routes and dispersed stores with the allies available to Estonia. Reception funding supports the reinforcement agreements that actually exist.",
           "construct_military", ("civil_reserve",), 0, 5, budget=80, readiness=4,
           military=(("supply_consumption_factor", -.05), ("army_org_factor", .025))),
    Policy("service_continuity", "Exercise Estonia's Essential Services in Isolation",
           "Test dispersed stocks, emergency communications and private suppliers. Ministries must show how essential services would function while outside connections are interrupted.",
           "national_unity", ("allied_reception",), 0, 6, budget=70, cohesion=3, readiness=5,
           military=(("attrition", -.025), ("army_defence_factor", .025))),

    Policy("industrial_guarantees", "Open Defence Suppliers' Access to Capital",
           "Use competitive loan and equity finance for private suppliers. Procurement contracts specify deliverables, investment risk and the limits of public participation.",
           "small_arms", ("new_mandate",), 2, 1, budget=50,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_country_flag = TFR_EST_procurement_plan\ncustom_effect_tooltip = TFR_EST_procurement_plan_tt"),
    Policy("ammunition_workshop", "Contract a Domestic Ammunition Production Line",
           "Finance tooling against an inspected supply contract with domestic industry. The production line still needs materials, workers and ordinary military orders.",
           "construct_mil_factory", ("industrial_guarantees",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_pp_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_pp_2023_factory_tt\nhidden_effect = { TFR_EST_pp_2023_grant_industry = yes }"),
    Policy("maintenance_workshop", "Contract Military Servicing and Component Capacity",
           "Purchase overhaul tooling and qualified component capacity from domestic suppliers. Contract inspections must demonstrate that the investment can maintain Estonia's equipment.",
           "production", ("ammunition_workshop",), 2, 3, budget=115,
           economic=(("production_factory_max_efficiency_factor", .04),),
           military=(("attrition", -.025),),
           extra="set_country_flag = TFR_EST_pp_2023_maintenance_factory_pending\ncustom_effect_tooltip = TFR_EST_pp_2023_factory_tt\nhidden_effect = { TFR_EST_pp_2023_grant_industry = yes }"),
    Policy("research_agreement", "Sign the Three-Percent Research Agreement",
           "Agree a staged public-private research programme with business organizations. Contracts define measurable innovation outcomes and the responsibilities of participating firms.",
           "scientific_exchange", ("maintenance_workshop",), 2, 4, budget=65,
           economic=(("research_speed_factor", .03), ("production_factory_efficiency_gain_factor", .025))),
    Policy("knowledge_transfer", "Tie University Funding to Knowledge Transfer",
           "Commission joint university-industry development projects and publish their results. Funding rewards usable knowledge transfer rather than disconnected research and production plans.",
           "scientific_exchange", ("research_agreement",), 2, 5, budget=80,
           economic=(("research_speed_factor", .035), ("production_factory_efficiency_gain_factor", .025))),
    Policy("skilled_migration", "Introduce the Skilled-Migration Points System",
           "Create a transparent admission system for qualifications and labour-market needs. Language support and assessed security conditions accompany skilled-worker recruitment.",
           "consumer_goods", ("knowledge_transfer",), 2, 6, budget=35, cohesion=2,
           economic=(("production_factory_max_efficiency_factor", .03), ("research_speed_factor", .025))),

    Policy("renewable_permits", "Clear Planning Barriers to Private Renewable Projects",
           "Simplify spatial planning and resource permit review. Stable rules and competent decisions support private investment without introducing a new blanket generation subsidy.",
           "oil_refinery", ("new_mandate",), 4, 1, budget=65,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .05))),
    Policy("grid_connection", "Co-Finance Offshore-Wind Grid Connections",
           "Prepare assessed connections and seek available European co-financing. Operators must demonstrate safe integration and credible delivery schedules for new capacity.",
           "construct_infrastructure", ("renewable_permits",), 4, 2, budget=70, readiness=2,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("continuity_capacity", "Keep Dispatchable Capacity Ready During the Transition",
           "Fund maintenance and demand-management readiness while replacement capacity develops. Dependable existing generation remains available during the energy emergency.",
           "production", ("grid_connection",), 4, 3, budget=70, readiness=3,
           economic=(("industrial_capacity_factory", .04), ("local_resources_factor", .025))),
    Policy("nuclear_framework", "Prepare Nuclear Licensing and Independent Oversight",
           "Draft the rules and recruit supervisory expertise for possible private nuclear development. Licensing preparation creates no reactor or nuclear weapons.",
           "scientific_exchange", ("continuity_capacity",), 4, 4, budget=35,
           economic=(("research_speed_factor", .035),)),
    Policy("renovation", "Simplify Residential Energy Renovation",
           "Coordinate renovation procedures and technical advice. Homeowners and qualified firms gain a clearer route to investments that reduce wasted heat.",
           "construct_civ_factory", ("nuclear_framework",), 4, 5, budget=40, cohesion=2,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),
    Policy("timber_construction", "Specify Timber for Public Construction",
           "Qualify durable timber construction and transparent procurement criteria. Public contracts support higher-value materials while retaining safety and building-performance standards.",
           "production", ("renovation",), 4, 6, budget=55,
           economic=(("production_speed_buildings_factor", .035), ("production_factory_efficiency_gain_factor", .025))),

    Policy("expenditure_audit", "Audit the State's Activities and Duplicated Agencies",
           "Publish service costs and review overlapping responsibilities. Ministers must identify actual savings and the services affected before presenting a revised budget.",
           "scientific_exchange", ("new_mandate",), 6, 1, budget=25, cohesion=2,
           economic=(("production_factory_max_efficiency_factor", .035),)),
    Policy("supplementary_budget", "Pass the Negative Supplementary Budget",
           "Cancel reviewed low-priority spending and consolidate duplicated functions. The reduction improves the ledger but creates disputes over withdrawn public commitments.",
           "consumer_goods", ("expenditure_audit",), 6, 2, budget=20, cohesion=-3,
           economic=(("consumer_goods_factor", -.02),),
           extra="set_temp_variable = { var = income_var_temp value = 0.040 }\nadd_income_with_inflation = yes"),
    Policy("transparent_budget", "Publish Understandable Budgets and Traceable Services",
           "Make expenditure decisions and service progress visible to citizens. Departmental reporting must explain public costs and permit meaningful parliamentary scrutiny.",
           "production", ("supplementary_budget",), 6, 3, budget=15, cohesion=4,
           economic=(("production_factory_efficiency_gain_factor", .035),)),
    Policy("labour_taxes", "Stage the Eighteen-Percent Income Tax and Social-Tax Cap",
           "Schedule lower income tax and a social-tax ceiling at three average wages. Record the revenue reduction alongside the expected competitiveness gain.",
           "consumer_goods", ("transparent_budget",), 6, 4, budget=20,
           economic=(("production_factory_max_efficiency_factor", .04), ("consumer_goods_factor", -.015)),
           extra="set_temp_variable = { var = income_var_temp value = -0.035 }\nadd_income_with_inflation = yes"),
    Policy("fringe_benefits", "Exempt Employee Transport, Meals and Health Benefits",
           "Remove fringe-benefit tax from specified employee costs. Publish eligibility and anti-abuse rules together with the recurring revenue reduction.",
           "consumer_goods", ("labour_taxes",), 6, 5, budget=20, cohesion=2,
           economic=(("production_factory_efficiency_gain_factor", .035),),
           extra="set_temp_variable = { var = income_var_temp value = -0.015 }\nadd_income_with_inflation = yes"),
    Policy("no_earmarks", "End Parliamentary Earmarks and Political Slush Funds",
           "Replace discretionary political grants with transparent appropriations and stronger local oversight. Public money requires a defensible purpose and a visible recipient.",
           "national_unity", ("fringe_benefits",), 6, 6, budget=15, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .025),),
           extra="set_temp_variable = { var = income_var_temp value = 0.012 }\nadd_income_with_inflation = yes"),

    Policy("teaching_priority", "Direct Seventy Percent of Education Spending to Teachers",
           "Rebalance school budgets toward teaching and give principals responsibility for rewarding performance. Training and modern learning platforms accompany the proposed pay reforms.",
           "scientific_exchange", ("new_mandate",), 8, 1, budget=65, cohesion=2,
           economic=(("research_speed_factor", .04),)),
    Policy("common_school", "Support the Common Estonian-Language School",
           "Fund language support and teaching materials for a shared school system. Integration must preserve teaching quality and help pupils participate in Estonian society.",
           "scientific_exchange", ("teaching_priority",), 8, 2, budget=70, cohesion=4,
           economic=(("research_speed_factor", .045),)),
    Policy("vocational_training", "Commission Vocational and Mid-Career Retraining",
           "Expand assessed vocational places and competitive training contracts. Working adults need practical access to new skills while maintaining employment.",
           "scientific_exchange", ("common_school",), 8, 3, budget=55, cohesion=2,
           economic=(("production_factory_efficiency_gain_factor", .03),)),
    Policy("university_contribution", "Pair University Contributions with Student Assistance",
           "Introduce partial tuition with revised loans, grants and employer-paid study. Additional university resources come with public concern over affordability.",
           "scientific_exchange", ("vocational_training",), 8, 4, budget=40, cohesion=-2,
           economic=(("research_speed_factor", .04),),
           extra="set_temp_variable = { var = income_var_temp value = 0.008 }\nadd_income_with_inflation = yes"),
    Policy("targeted_support", "Replace Blanket Benefits with Needs-Based Assistance",
           "Use safeguarded public records to direct support toward households in need. Reassessment saves expenditure but unsettles families losing universal entitlements.",
           "consumer_goods", ("university_contribution",), 8, 5, budget=50, cohesion=-2,
           economic=(("consumer_goods_factor", -.015), ("production_factory_max_efficiency_factor", .025)),
           extra="set_temp_variable = { var = income_var_temp value = 0.010 }\nadd_income_with_inflation = yes"),
    Policy("patient_choice", "Open Care Contracts and Reduce Medical Paperwork",
           "Commission care competitively and expand electronic referrals with administrative support. Contracts must preserve access while clinicians spend more time treating patients.",
           "consumer_goods", ("targeted_support",), 8, 6, budget=45, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .035),)),

    Policy("account_to_parliament", "Present the Parempoolsed Government's Accounts",
           "Present defence deliveries, tax receipts and the costs of structural reform. Parliament must assess the remaining commitments before another mandate.",
           "national_unity", ("service_continuity", "skilled_migration", "timber_construction", "no_earmarks", "patient_choice"), 4, 7,
           cohesion=3, extra="set_country_flag = TFR_EST_pp_2023_programme_finished\nadd_political_power = 75"),
)

_EARLY_AI = ("new_mandate", "defence_commitment", "industrial_guarantees",
             "ammunition_workshop", "maintenance_workshop", "air_defence",
             "reserve_muster", "civil_reserve", "allied_reception", "service_continuity",
             "renewable_permits", "grid_connection", "continuity_capacity")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_pp_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_pp_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = {focus_sprite("pp", p.suffix)}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_pp_2023_branch_visible = yes }}
    available = {{
        TFR_EST_pp_2023_governing = yes{extra}
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
    text = """# A Parempoolsed plurality in the validated 2023 ballot grants this mandate.
TFR_EST_pp_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_pp_2023_mandate
    has_country_flag = TFR_EST_pp_won_2023_election
    NOT = { has_country_flag = TFR_EST_pp_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 7 compare = equals }
}
TFR_EST_pp_2023_governing = {
    TFR_EST_pp_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 7 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 7 compare = equals }
    check_variable = { var = TFR_EST_coalition_pp value = 1 compare = equals }
}
TFR_EST_pp_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_pp_2023_governing", "TFR_EST_pp_2023_all_policies_done"):
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
TFR_EST_pp_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_pp_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_pp_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_pp_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_pp_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_pp_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_pp_2023_grant_industry = yes
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
        "TFR_EST_pp_2023_governing_tt": "A confirmed Parempoolsed-led cabinet has at least 51 coalition seats.",
        "TFR_EST_pp_2023_all_policies_done_tt": "Complete every other focus in the 2023 Parempoolsed government programme.",
        "TFR_EST_pp_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Earlier equivalent preparations count once. Completing all three response projects removes the spirit; preparation also applies if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_pp_2023.txt": build_focuses(),
        "interface/TFR_EST_pp_2023_focus_icons.gfx": build_focus_sprites(POLICIES, "pp", "build_pp_2023.py"),
        "common/scripted_triggers/TFR_EST_pp_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_pp_2023.txt": build_effects(),
        "localisation/english/TFR_EST_pp_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated Parempoolsed 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} Parempoolsed 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

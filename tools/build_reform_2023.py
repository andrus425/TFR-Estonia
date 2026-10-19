"""Build Reform's 2023 mandate: thirty-two compact, 35-day focuses.

Primary sources and the distinction between enacted policies, inherited
programmes and TFR adaptations are recorded in docs/REFORM_2023_SOURCES.md.
The programme survives Kallas's scripted handover to Michal and an early war.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ratas_continuation import Policy
from focus_reward_model import concise_trigger, modifier_reward
from native_script_interface import amount_call


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_reform_2023_"
INDUSTRY_PROJECTS = ("ammunition", "drones")
ENERGY_STAGES = {"grid_connection": 2, "wind_permits": 1, "renovation": 2}


def done(suffix: str) -> str:
    return "TFR_EST_done_reform_2023_" + suffix


POLICIES = (
    Policy("new_mandate", "A New Reform Mandate",
           "The election has given Reform the largest delegation in the Riigikogu. Agree a programme with the parties that actually support our cabinet, placing defence, public finances and public services before the new parliament. This programme belongs to the elected government and can continue under its designated successor.",
           "national_unity", (), 4, 0, cohesion=2,
           extra="add_political_power = 50"),

    # Defence is available after the root. No civilian branch or report blocks
    # the funding, reserve, air-defence or defensive-line preparations.
    Policy("defence_three_percent", "Three Percent for National Defence",
           "Adopt the government's three-percent defence-spending commitment and fund the first procurement instalments. Give the Defence Forces a dependable planning horizon instead of announcing capabilities without money. The higher spending is a continuing obligation on Estonia's small economy.",
           "defence", ("new_mandate",), 0, 1, budget=120, readiness=5,
           military=(("army_org_factor", .04), ("supply_consumption_factor", -.03))),
    Policy("territorial_twenty_thousand", "Equip a 20,000-Strong Territorial Defence",
           "Support the expanded territorial-defence structure through instructors, stores and reserve appointments. Kaitseliit units need reliable equipment accounting and rehearsed reporting arrangements. Fund organisation and training within existing recruitment and production; a paper establishment does not supply twenty thousand new soldiers.",
           "army_doctrines", ("defence_three_percent",), 0, 2, budget=75, readiness=6,
           military=(("mobilization_speed", .20), ("army_defence_factor", .04))),
    Policy("layered_air_defence", "Procure Layered Air Defence",
           "Advance the medium-range air-defence procurement undertaken with Latvia, alongside short-range protection, radar links and trained crews. Coordinate contracts with partners able to supply them in this timeline. Procurement preparation improves the army's resilience without conjuring a battery or bypassing equipment production.",
           "air_fighter", ("territorial_twenty_thousand",), 0, 3, budget=100, readiness=4,
           military=(("army_defence_factor", .04), ("attrition", -.025))),
    Policy("baltic_defence_line", "Prepare the Baltic Defence Line",
           "Survey defensive positions and storage sites with the other Baltic states. Arrange land agreements and stockpile obstacles and construction material for a dispersed defensive line. These works strengthen planned positions; they do not make Estonia's entire border an impassable wall.",
           "construct_military", ("layered_air_defence",), 0, 4, budget=65, readiness=5,
           military=(("dig_in_speed_factor", .15), ("army_defence_factor", .05))),
    Policy("nursipalu", "Expand Nursipalu and Compensate Residents",
           "Carry out the decision to enlarge the Nursipalu training area. Finance exercises and facilities for Estonian and allied units while paying fair compensation and supporting affected municipalities. More demanding training should be accompanied by a credible agreement with the people who live beside it.",
           "army_doctrines", ("baltic_defence_line",), 0, 5, budget=65, cohesion=1, readiness=4,
           military=(("training_time_army_factor", -.06), ("army_org_factor", .03)),
           extra="army_experience = 15"),
    Policy("allied_logistics", "Stock the Reception Areas for Allied Forces",
           "Prepare reception areas, transport schedules and dispersed stores for allied reinforcements. Coordinate ammunition compatibility and host-nation support with the partners available to Estonia. This improves our ability to sustain operations without duplicating allied divisions supplied by TFR's existing reinforcement decisions.",
           "construct_infrastructure", ("nursipalu",), 0, 6, budget=60, readiness=4,
           military=(("supply_consumption_factor", -.05), ("attrition", -.025))),

    # Two paid, bounded military factories are early in this column: the
    # second and third nodes, available after 105 and 140 total focus-days.
    Policy("industrial_park", "Plan a Defence Industrial Park",
           "Use the national special-planning procedure to identify sites for ammunition, explosives and defence technology. Resolve access, utilities, safety distances and environmental assessment before promising production. The state prepares the site; firms still need contracts, workers and equipment.",
           "construct_mil_factory", ("new_mandate",), 2, 1, budget=70,
           economic=(("production_speed_buildings_factor", .04),)),
    Policy("ammunition_line", "Finance an Ammunition Production Line",
           "Finance one first-stage ammunition workshop on a serviced defence-industry site. Pair the investment with procurement commitments and inspection capacity. This is an accelerated TFR adaptation of the industrial-park programme, not a claim that the historical park opened in thirty-five days.",
           "production", ("industrial_park",), 2, 2, budget=140,
           economic=(("industrial_capacity_factory", .04),),
           extra="set_country_flag = TFR_EST_reform_2023_ammunition_factory_pending\ncustom_effect_tooltip = TFR_EST_reform_2023_factory_tt\nhidden_effect = { TFR_EST_reform_2023_grant_industry = yes }"),
    Policy("drone_workshops", "Contract Domestic Drone and Repair Workshops",
           "Place defence-industry orders for drone assembly, inspection and field repairs. Give domestic suppliers a second funded production facility while keeping designs and deliveries subject to ordinary procurement. The investment adds production capacity rather than free aircraft, ammunition or divisions.",
           "production", ("ammunition_line",), 2, 3, budget=120,
           economic=(("production_factory_efficiency_gain_factor", .05),),
           extra="set_country_flag = TFR_EST_reform_2023_drones_factory_pending\ncustom_effect_tooltip = TFR_EST_reform_2023_factory_tt\nhidden_effect = { TFR_EST_reform_2023_grant_industry = yes }"),
    Policy("grid_connection", "Complete the Grid's European Connection Works",
           "Fund the remaining connection and control-system works needed for a secure European electricity system. The Baltic transmission operators have already undertaken extensive preparations. Finish the practical work and strengthen reserve arrangements without assuming that every neighbouring country has followed its historical path.",
           "construct_infrastructure", ("drone_workshops",), 2, 4, budget=70,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("wind_permits", "Clear the Wind-Power Permit Backlog",
           "Resource municipal planning teams and simplify the permit stages that delay viable wind developments. Keep the environmental assessment and local consultation that projects require. Faster decisions and stronger networks can attract new generation without declaring every proposed wind farm complete.",
           "oil_refinery", ("grid_connection",), 2, 5, budget=40,
           economic=(("local_resources_factor", .05), ("industrial_capacity_factory", .03))),
    Policy("renovation", "Open the Regional Apartment-Renovation Round",
           "Continue the large apartment-building renovation programme with regional allocations. Help associations prepare technically sound insulation, heating and ventilation projects, including outside the largest cities. Lower energy demand and dependable construction contracts strengthen households and local businesses together.",
           "construct_civ_factory", ("wind_permits",), 2, 6, budget=75, cohesion=3,
           economic=(("production_speed_buildings_factor", .04), ("consumer_goods_factor", -.015))),

    Policy("estonian_education", "Fund the Transition to Estonian Education",
           "Prepare kindergartens and the first and fourth grades for the transition to Estonian-language instruction. Fund materials, language support and school-level implementation. Starting the transition is a practical programme; the full school system cannot be transformed in a single term of office.",
           "scientific_exchange", ("new_mandate",), 4, 1, budget=55, cohesion=2,
           economic=(("research_speed_factor", .02),)),
    Policy("ida_viru_teachers", "Recruit Teachers for Ida-Viru Schools",
           "Use additional pay, mentoring and teacher training to fill posts in Ida-Viru County. Schools need qualified staff who can teach their subject in Estonian and help pupils learn it. Direct resources toward the shortage instead of treating a change of classroom language as a completed staffing plan.",
           "scientific_exchange", ("estonian_education",), 4, 2, budget=40, cohesion=3,
           economic=(("research_speed_factor", .02),)),
    Policy("teacher_agreement", "Negotiate Teachers' Pay and Career Progression",
           "Negotiate with teachers and school owners on pay, workload and a clear career framework. Back the settlement with funding and transparent responsibilities. The real negotiations involved disputes and limited resources; an agreement must be affordable as well as attractive to the next generation of teachers.",
           "political_pressure", ("ida_viru_teachers",), 4, 3, budget=50, cohesion=3,
           economic=(("research_speed_factor", .025),)),
    Policy("learning_eighteen", "Keep Young People Learning Until Eighteen",
           "Replace the school-attendance obligation with a broader obligation to learn until eighteen. Prepare flexible general and vocational routes, guidance and municipal follow-up. The purpose is to prevent pupils leaving basic school without a useful next step, rather than merely extending time spent in a classroom.",
           "scientific_exchange", ("teacher_agreement",), 4, 4, budget=35, cohesion=2,
           economic=(("production_factory_efficiency_gain_factor", .025),)),
    Policy("vocational_places", "Align Vocational Places with Employer Demand",
           "Rework vocational admissions and practical courses with employers and schools. Expand places where Estonia lacks technical skills and strengthen routes into further study. Better preparation helps workshops and public services recruit qualified people without granting the state an unlimited labour reserve.",
           "production", ("learning_eighteen",), 4, 5, budget=40,
           economic=(("production_factory_max_efficiency_factor", .04), ("production_factory_efficiency_gain_factor", .025))),
    Policy("applied_research", "Build Metrosert's Applied-Research Capacity",
           "Equip Metrosert's new applied-research unit and connect its specialists with Estonian firms. Support testing and development in fields such as drones, autonomous systems and health data. The centre closes practical gaps between a promising design and a product that a company can make reliably.",
           "scientific_exchange", ("vocational_places",), 4, 6, budget=55,
           economic=(("research_speed_factor", .035), ("production_factory_max_efficiency_factor", .025))),

    Policy("real_time_economy", "Replace Repeated Reports with Data Exchange",
           "Implement the real-time-economy programme through common data standards and automatic reporting. Firms should send accurate information once and know how the state uses it. Begin with workable reporting flows and reliable registers instead of replacing every form with another disconnected portal.",
           "political_pressure", ("new_mandate",), 6, 1, budget=30,
           economic=(("production_factory_efficiency_gain_factor", .03),),
           extra="add_political_power = 35"),
    Policy("enterprise_digital", "Take Firms Through the Digitalisation Masterclass",
           "Support businesses in mapping production bottlenecks and adopting useful digital systems. The enterprise programme should combine training with a practical investment plan, especially for smaller firms. Productivity gains come from changes on the shop floor and in administration, not from purchasing software alone.",
           "production", ("real_time_economy",), 6, 2, budget=40,
           economic=(("industrial_capacity_factory", .03), ("production_factory_efficiency_gain_factor", .03))),
    Policy("cyber_reserve", "Organise the Digital Defence Reserve",
           "Connect Defence Forces and Kaitseliit specialists with the operators of essential public systems. Rehearse restoration from backups and a common response to hostile information operations. Estonia's electronic services must remain useful when ordinary communications and institutions come under pressure.",
           "intelligence_exchange", ("enterprise_digital",), 6, 3, budget=35, readiness=4,
           military=(("army_org_factor", .025), ("mobilization_speed", .10))),
    Policy("research_one_percent", "Protect One Percent for Public Research",
           "Keep public research and development funding at the government's one-percent-of-GDP commitment and encourage private investment alongside it. Publish priorities and review results while preserving stable support for research institutions. Fiscal consolidation should not leave essential technical work without a planning horizon.",
           "scientific_exchange", ("cyber_reserve",), 6, 4, budget=60,
           economic=(("research_speed_factor", .035),)),
    Policy("regional_exporters", "Back Regional Exporters and Investment Projects",
           "Use enterprise support and economic diplomacy to help firms outside the largest cities reach new customers. Assess projects for viable products, skilled jobs and access to services. Regional investment should complement private decisions rather than preserve every uneconomic business indefinitely.",
           "construct_civ_factory", ("research_one_percent",), 6, 5, budget=50,
           economic=(("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03))),
    Policy("civil_reserve", "Fund the Civil-Protection Reserve",
           "Train a community-based reserve to support rescue and health services during serious emergencies. Municipalities need agreed responsibilities, communications and supplies for evacuation and shelter. Civil preparation helps the country endure the opening of a European war without turning volunteers into unprovided army formations.",
           "national_unity", ("regional_exporters",), 6, 6, budget=40, cohesion=4, readiness=4,
           military=(("dig_in_speed_factor", .05), ("attrition", -.025))),

    Policy("vat_twenty_two", "Raise VAT to Twenty-Two Percent",
           "Legislate the increase in the standard VAT rate from twenty to twenty-two percent and fund the Tax and Customs Board's implementation. Additional receipts help finance defence and public services, while the higher consumption tax imposes a real cost on households. Account for both sides of the measure.",
           "political_pressure", ("new_mandate",), 8, 1, cohesion=-3,
           economic=(("consumer_goods_factor", .015),),
           extra="set_temp_variable = { var = income_var_temp value = 0.025 }\nadd_income_with_inflation = yes"),
    Policy("spending_reviews", "Review Ministry Spending Before New Commitments",
           "Review recurrent spending and procurement across ministries, distinguishing avoidable overhead from services that still need funding. Publish the savings and their consequences. A spending review provides fiscal room only where government actually changes how money is used.",
           "political_pressure", ("vat_twenty_two",), 8, 2, cohesion=-1,
           economic=(("consumer_goods_factor", -.015),),
           extra="set_temp_variable = { var = income_var_temp value = 0.015 }\nadd_income_with_inflation = yes"),
    Policy("municipal_revenue", "Strengthen the Municipal Revenue Base",
           "Rebalance municipal revenue so that local services do not depend entirely on the number of high earners living nearby. Coordinate the transition with councils and publish the distribution. Small municipalities need a dependable basis for schools, care and crisis duties.",
           "construct_infrastructure", ("spending_reviews",), 8, 3, budget=35, cohesion=3,
           economic=(("production_speed_buildings_factor", .025),)),
    Policy("care_reform", "Put Municipal Funding Behind Care Reform",
           "Implement the care reform with local authorities paying the care component of general residential care. Inspect staffing, fees and access so that families see the support in practice. Continue a reform legislated before this cabinet and bring its administration into the new government's programme.",
           "consumer_goods", ("municipal_revenue",), 8, 4, budget=45, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .03),)),
    Policy("marriage_equality", "Enact Marriage Equality",
           "Amend the Family Law Act so that two adults may marry and provide the implementing rules that registrars and families require. The law replaces the earlier referendum dispute with a parliamentary settlement. Publish clear arrangements for existing partnerships and equal treatment before the law.",
           "national_unity", ("care_reform",), 8, 5, cohesion=2,
           extra="add_stability = 0.03\nadd_political_power = 40"),
    Policy("mental_health", "Keep Mental-Health Support Close to Home",
           "Continue grants for municipal counselling and psychologists in primary care. Link local help with specialist treatment and review whether residents can actually obtain an appointment. Accessible support matters to daily life and becomes more valuable when families face mobilisation, displacement or bereavement.",
           "consumer_goods", ("marriage_equality",), 8, 6, budget=35, cohesion=4,
           economic=(("production_factory_max_efficiency_factor", .025),)),

    Policy("account_to_parliament", "Report to the Riigikogu on the Mandate",
           "Present the completed government's programme to parliament: the tax choices, schools and services funded, energy security improved and defence preparations delivered. Review what remains unfinished beyond these initial projects. This report neither starts a war nor calls an election; the postwar parliament will judge the cabinet when independent politics can resume.",
           "national_unity", ("allied_logistics", "renovation", "applied_research", "civil_reserve", "mental_health"), 4, 8,
           cohesion=3, extra="set_country_flag = TFR_EST_reform_2023_programme_finished\nadd_political_power = 75"),
)

# A deterministic topological AI order puts paid production and battlefield
# preparations before the longer civilian programme. The final report is last.
_EARLY_AI = ("new_mandate", "defence_three_percent", "industrial_park",
             "ammunition_line", "drone_workshops", "territorial_twenty_thousand",
             "layered_air_defence", "baltic_defence_line", "nursipalu", "allied_logistics",
             "real_time_economy", "enterprise_digital", "cyber_reserve")
AI_ORDER = _EARLY_AI + tuple(p.suffix for p in POLICIES if p.suffix not in _EARLY_AI)


def build_focuses() -> str:
    out = ["# Generated by tools/build_reform_2023.py. 32 focuses, 1120 days.\n"]
    for index, p in enumerate(POLICIES):
        parents = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_reform_2023_all_policies_done = yes" if p.suffix == "account_to_parliament" else ""
        priority = 120 - p.y * 3 if p.x in (0, 2) else 85 - index
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = GFX_goal_generic_{p.icon}
    x = {p.x}
    y = {p.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_reform_2023_branch_visible = yes }}
    available = {{
        TFR_EST_reform_2023_governing = yes{extra}
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
    text = """# A Reform plurality in the 2023 election grants this programme.
TFR_EST_reform_2023_branch_visible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_reform_2023_mandate
    has_country_flag = TFR_EST_reform_won_2023_election
    NOT = { has_country_flag = TFR_EST_reform_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 1 compare = equals }
}
TFR_EST_reform_2023_governing = {
    TFR_EST_reform_2023_branch_visible = yes
    TFR_EST_coalition_majority = yes
    TFR_EST_confirmed_cabinet = yes
    check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_reform value = 1 compare = equals }
}
TFR_EST_reform_2023_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    text += "}\n"
    for name in ("TFR_EST_reform_2023_governing", "TFR_EST_reform_2023_all_policies_done"):
        text = concise_trigger(name, text)
    return text


def build_effects() -> str:
    out = ["# Each focus guards its persistent reward with its own completion flag.\n"]
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
    out.append("""# Funded projects wait if all owned-controlled core slots are occupied.
# A pending entitlement is fulfilled only inside the eligible state scope.
TFR_EST_reform_2023_grant_industry = {
    if = {
        limit = { TFR_EST_independent_parliament = yes }
""")
    for project in INDUSTRY_PROJECTS:
        for state in ((13, 191, 1329, 840) if project == "ammunition" else (191, 13, 1329, 840)):
            out.append(f"""        if = {{
            limit = {{
                has_country_flag = TFR_EST_reform_2023_{project}_factory_pending
                NOT = {{ has_country_flag = TFR_EST_reform_2023_{project}_factory_granted }}
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
                        set_country_flag = TFR_EST_reform_2023_{project}_factory_granted
                        clr_country_flag = TFR_EST_reform_2023_{project}_factory_pending
                    }}
                }}
            }}
        }}
""")
    out.append("""    }
}

TFR_EST_reform_2023_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_reform_2023_grant_industry = yes
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
        "TFR_EST_reform_2023_governing_tt": "A confirmed Reform-led cabinet has at least 51 coalition seats.",
        "TFR_EST_reform_2023_all_policies_done_tt": "Complete every other focus in the 2023 government programme.",
        "TFR_EST_reform_2023_factory_tt": "Gain §G1§! §YMilitary Factory§! in an owned and controlled Estonian core with a free building slot. If no suitable slot is available, the funded project waits until one becomes available. Each of the two funded projects grants one factory only.",
    })
    for suffix, stages in ENERGY_STAGES.items():
        entries[PREFIX + suffix + "_energy_tt"] = f"Complete {stages} of the 5 preparation slots for §YThe Oil Crash§!, advancing recovery by up to §G{stages}§! stage(s). Preparations funded by an earlier government count once. Completing the whole energy branch removes the spirit; preparations also apply if the crisis begins later."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_reform_2023.txt": build_focuses(),
        "common/scripted_triggers/TFR_EST_reform_2023.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_reform_2023.txt": build_effects(),
        "localisation/english/TFR_EST_reform_2023_l_english.yml": build_localisation(),
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
                raise SystemExit(f"Generated Reform 2023 programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} Reform 2023 focuses, triggers, rewards and 70 English keys.")


if __name__ == "__main__":
    main()

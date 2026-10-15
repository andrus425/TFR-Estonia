"""Build the retained Ratas coalition's 2021-2023 programme.

Sources and the distinction between 2019 commitments and pandemic adaptations
are recorded in docs/RATAS_CONTINUATION_SOURCES.md. All twenty focuses take 35
days; energy projects prepare a response even before the parent crisis begins.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

from native_script_interface import amount_call


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_ratas_"
COVID_POLICIES = ("hospital_covid", "testing_tracing", "vaccinate_risk_groups")


@dataclass(frozen=True)
class Policy:
    suffix: str
    title: str
    description: str
    icon: str
    parents: tuple[str, ...]
    x: int
    y: int
    budget: float = 0
    cohesion: int = 0
    readiness: int = 0
    economic: tuple[tuple[str, float], ...] = ()
    military: tuple[tuple[str, float], ...] = ()
    extra: str = ""
    benefit: str = ""


POLICIES = (
    Policy("renew_agreement", "Renew the 2019 Coalition Agreement",
           "Jüri Ratas has chosen to remain prime minister. Centre, Isamaa and EKRE must now agree which unfinished commitments they will carry through the remainder of the parliamentary term. Publish a legislative and funding programme, keep the investigation independent, and return ministers to the practical work promised in 2019.",
           "national_unity", ("opening_marriage_referendum",), 8, 7,
           cohesion=1, extra="add_political_power = 25", benefit="Gain 25 political power."),
    Policy("family_home_guarantees", "KredEx Guarantees for Family Homes",
           "Extend the coalition's promised housing guarantees for young and large families. KredEx should support viable home purchases and renovation, with income checks and clear limits on public exposure. A guarantee helps a household obtain a loan; it does not make the state the owner of every home.",
           "construct_civ_factory", ("renew_agreement",), 0, 9,
           budget=35, cohesion=2),
    Policy("child_tax_allowance", "A Larger Child-Based Tax Allowance",
           "Bring forward the coalition agreement's child-based income-tax relief. Explain who qualifies, update the Tax and Customs Board's administration, and account for the revenue forgone. The measure offers working families predictable assistance without disguising its budget cost.",
           "consumer_goods", ("family_home_guarantees",), 0, 11,
           budget=30, cohesion=2),
    Policy("home_care", "Home Nursing Instead of an Institution",
           "The 2019 agreement promises more support for people who need nursing and everyday care. Fund municipal home services and coordinate them with family doctors so relatives are not forced to carry every responsibility alone. Contracts must specify staffing and access beyond the largest towns.",
           "consumer_goods", ("child_tax_allowance",), 0, 13,
           budget=35, cohesion=3),
    Policy("state_jobs_counties", "Move 1,000 State Jobs Beyond Tallinn",
           "Continue the agreement's plan to move one thousand state jobs outside the capital. Select functions that can operate reliably in the counties, provide secure connections, and support staff through the transition. The programme redistributes public employment; it does not create a thousand additional posts.",
           "political_pressure", ("renew_agreement",), 4, 9,
           budget=25, cohesion=2),
    Policy("rural_broadband", "The Last Mile of Rural Broadband",
           "Fund the fixed-network connections promised to rural homes and businesses. Work with municipalities and network operators to reach settlements where commercial deployment alone is insufficient. Reliable connections support remote work, schools and public services when travel is disrupted.",
           "scientific_exchange", ("state_jobs_counties",), 4, 11,
           budget=50, economic=(("research_speed_factor", .01),),
           benefit="Research speed: +1%."),
    Policy("industrial_parks", "Serviced Industrial Parks in the Counties",
           "Prepare regional industrial sites with access, utilities and transparent tenancy rules, as envisaged in the coalition agreement. Support local production and employment without promising that one government programme can replace every private investment decision.",
           "construct_civ_factory", ("rural_broadband",), 4, 13,
           budget=80, economic=(("industrial_capacity_factory", .015),),
           benefit="Factory output: +1.5%."),
    Policy("worker_retraining", "Retraining for Estonia's Working Adults",
           "Connect the agreement's adult-learning commitment to real employer demand. Offer retraining in technical, care and digital occupations, with places for workers affected by regional industrial change. Training providers must report completion and employment outcomes.",
           "production", ("industrial_parks",), 4, 15,
           budget=35, economic=(("production_factory_efficiency_gain_factor", .015),),
           benefit="Production efficiency growth: +1.5%."),
    Policy("hospital_covid", "County Hospitals Need COVID Wards",
           "Put the cabinet's December 2020 health-system plan into operation under the renewed coalition. Finance isolation capacity, oxygen supplies, protective equipment and reserve staffing in county hospitals. These measures respond to an outbreak already present in Estonia; ordinary care must remain available alongside them.",
           "consumer_goods", ("renew_agreement",), 8, 9,
           budget=60, cohesion=2),
    Policy("testing_tracing", "Keep Testing and Contact Tracing Working",
           "Fund laboratories, sample collection and the Health Board's tracing teams in line with the December 2020 plan. Testing only helps if results reach patients and contacts promptly. Coordinate local staffing and clear public instructions while protecting the information collected during the response.",
           "scientific_exchange", ("hospital_covid",), 8, 11,
           budget=35, cohesion=2),
    Policy("family_doctors", "Family Doctors in the Evening and at Weekends",
           "Implement the coalition agreement's promise of better access to primary care outside ordinary working hours. Arrange evening and weekend appointments, referral advice and cooperation with county hospitals. This service commitment remains useful after the immediate pandemic emergency has passed.",
           "consumer_goods", ("testing_tracing",), 8, 13,
           budget=40, cohesion=2),
    Policy("vaccinate_risk_groups", "Vaccinate Risk Groups Through Family Doctors",
           "Carry out the vaccination plan prepared in December 2020: prioritize risk groups, coordinate care homes and family doctors, and maintain the cold chain and appointment records. A practical rollout can ease the current outbreak. It cannot promise an immediate end to every future infection.",
           "consumer_goods", ("family_doctors",), 8, 15,
           budget=45, cohesion=2, extra="TFR_EST_ratas_reduce_covid = yes",
           benefit="Improve an existing COVID severity by one level. Remove the lowest level only if it is Estonia's own seeded outbreak."),
    Policy("lng_connection", "Finance an Estonian LNG Connection",
           "Develop the agreement's proposal for a regional LNG terminal in Estonia. Finance connection studies, access arrangements and a practical share of the enabling works. Diversified supply can cushion the Saudi-war energy shock; this programme does not finish an entire terminal in thirty-five days.",
           "oil_refinery", ("renew_agreement",), 12, 9,
           budget=80, benefit="While TFR's Saudi-war energy crisis is active, reduce Estonia's factory-output penalty by 1 percentage point."),
    Policy("grid_synchronisation", "Fund European-Grid Synchronisation",
           "Maintain financing and coordination for the coalition's promised connection to the European electricity system. Work with grid operators and Baltic partners on equipment, reserve requirements and the transition programme. The focus advances a long project rather than declaring immediate synchronisation.",
           "construct_infrastructure", ("lng_connection",), 12, 11,
           budget=70, readiness=1, benefit="While the energy crisis is active, reduce Estonia's factory-output penalty by 1 percentage point."),
    Policy("renewable_chp", "Renewable Heat and Power for Towns",
           "Support efficient combined heat and power using suitable local renewable fuels, following the coalition's energy commitments. Assess fuel supply and district-heating demand before approving projects. Reliable local heat and generation reduce exposure to disrupted imported energy.",
           "production", ("grid_synchronisation",), 12, 13,
           budget=55, benefit="While the energy crisis is active, reduce Estonia's factory-output penalty by 1 percentage point."),
    Policy("building_renovation", "Renovation Grants for Warm Homes",
           "Expand the building-renovation grants promised in the agreement. Insulation, efficient heating and sound project supervision can reduce household energy use for years. Prioritize viable apartment-building projects and make assistance accessible outside Tallinn.",
           "construct_infrastructure", ("renewable_chp",), 12, 15,
           budget=55, economic=(("production_speed_buildings_factor", .01),),
           benefit="Construction speed: +1%. While the energy crisis is active, reduce its consumer-goods penalty by 1.5 percentage points."),
    Policy("network_charge_relief", "Temporary Electricity Network-Charge Relief",
           "Use the coalition agreement's network-charge proposal to cushion household and enterprise bills during the energy shock. Authorize a funded relief reserve that activates when supplies are disrupted. This concerns network charges, separately from the electricity excise cut enacted in the opening programme.",
           "consumer_goods", ("building_renovation",), 12, 17,
           budget=45, cohesion=2, benefit="While the energy crisis is active, reduce its consumer-goods penalty by 1.5 percentage points. Preparation remains effective if the crisis begins later."),
    Policy("police_reserve", "A Police and Border-Guard Crisis Reserve",
           "Organize the police and border-guard reserve envisaged in the coalition agreement. Recruit and train suitable volunteers, specify command responsibilities, and rehearse support to regular officers. The reserve assists lawful emergency duties rather than creating an additional field army.",
           "defence", ("renew_agreement",), 16, 9,
           budget=30, readiness=3),
    Policy("territorial_training", "Conscript and Kaitseliit Training Places",
           "Fund the coalition's commitment to conscript training and the Defence League. Improve instructor availability, training schedules and coordination with employers. The programme strengthens readiness within existing recruitment and equipment limits.",
           "army_doctrines", ("police_reserve",), 16, 11,
           budget=40, readiness=4, military=(("training_time_army_factor", -.02),),
           benefit="Army training time: −2%. No free divisions, manpower or equipment."),
    Policy("account_to_voters", "Account for the Coalition's Promises",
           "Present the results of the renewed coalition programme to the Riigikogu and the public. Explain the commitments fulfilled, the costs incurred and the emergency measures that still require review. The next regular parliamentary election remains in March 2023; completing this report neither calls an early vote nor guarantees another Centre-led cabinet.",
           "national_unity", ("home_care", "worker_retraining", "vaccinate_risk_groups", "network_charge_relief", "territorial_training"), 8, 20,
           cohesion=3, extra="set_country_flag = TFR_EST_ratas_programme_finished\nadd_political_power = 50",
           benefit="Gain 50 political power. Preserve the regular election calendar."),
)


def done(suffix: str) -> str:
    return "TFR_EST_done_ratas_" + suffix


def build_focuses() -> str:
    out = ["# Generated by tools/build_ratas_continuation.py. Twenty 35-day focuses.\n"]
    for index, policy in enumerate(POLICIES):
        parents = "".join(
            f"    prerequisite = {{ focus = {'TFR_EST_' + parent if parent.startswith('opening_') else PREFIX + parent} }}\n"
            for parent in policy.parents
        )
        case = "\n        generic_has_corona = yes" if policy.suffix in COVID_POLICIES else ""
        if policy.suffix == "account_to_voters":
            case += "\n        TFR_EST_ratas_all_policies_done = yes"
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{policy.suffix}
    icon = GFX_goal_generic_{policy.icon}
    x = {policy.x}
    y = {policy.y}
    cost = 5
{parents}    allow_branch = {{ TFR_EST_ratas_branch_visible = yes }}
    available = {{
        TFR_EST_ratas_governing = yes{case}
    }}
    bypass = {{ has_country_flag = {done(policy.suffix)} }}
    cancel_if_invalid = yes
    continue_if_invalid = no
    ai_will_do = {{ factor = {90 - index} }}
    completion_reward = {{
        if = {{
            limit = {{ NOT = {{ has_country_flag = {done(policy.suffix)} }} }}
            set_country_flag = {done(policy.suffix)}
            {PREFIX}reward_{policy.suffix} = yes
        }}
    }}
}}
""")
    return "".join(out)


def build_triggers() -> str:
    text = """# Only the historical 2019 coalition mandate uses this continuation.
TFR_EST_ratas_branch_visible = {
    tag = EST
    has_country_flag = TFR_EST_ratas_retained
    NOT = { has_country_flag = TFR_EST_ratas_mandate_ended }
    NOT = { has_country_flag = TFR_EST_occupied }
}
TFR_EST_ratas_governing = {
    TFR_EST_ratas_branch_visible = yes
    TFR_EST_coalition_majority = yes
    has_country_flag = TFR_EST_opening_complete
    NOT = { has_country_flag = TFR_EST_caretaker }
    check_variable = { var = TFR_EST_pm_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_coalition_centre value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_ekre value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_isamaa value = 1 compare = equals }
}
TFR_EST_show_legacy_domestic_tree = {
    OR = {
        NOT = { has_country_flag = TFR_EST_ratas_retained }
        has_country_flag = TFR_EST_ratas_mandate_ended
    }
    OR = {
        NOT = { has_country_flag = TFR_EST_ratas_resigned }
        NOT = { has_country_flag = TFR_EST_referendum_failed }
        has_country_flag = TFR_EST_kallas_mandate_ended
    }
}
# This is TFR's Saudi-war supply shock, not Germany's country-only oil spirit.
TFR_EST_energy_crisis_active = {
    NOT = { has_global_flag = SAU_saudi_civil_war_over_global }
    OR = {
        has_global_flag = SAU_saudi_civil_war_global
        has_global_flag = saudi_civil_war_flag
    }
}
"""
    text += "TFR_EST_ratas_all_policies_done = {\n"
    # A recovered case-specific leaf may be bypassed before its ordinary
    # ancestors. Check every policy explicitly before the common conclusion.
    for policy in POLICIES[:-1]:
        text += f"    OR = {{ has_completed_focus = {PREFIX}{policy.suffix} has_country_flag = {done(policy.suffix)} }}\n"
    return text + "}\n"


def build_effects() -> str:
    out = ["# Generated rewards run inside the focus's persistent once-only guard.\n"]
    for policy in POLICIES:
        effects = ["TFR_EST_initialize_country_modifiers = yes",
                   f"custom_effect_tooltip = {PREFIX}{policy.suffix}_reward_tt"]
        for value, helper in ((policy.budget, "TFR_EST_spend_budget"),
                              (policy.cohesion, "TFR_EST_change_cohesion"),
                              (policy.readiness, "TFR_EST_change_readiness")):
            if value:
                effects.append(amount_call(helper, value))
        for group, modifiers in (("economy", policy.economic), ("military", policy.military)):
            effects.extend(f"add_to_variable = {{ TFR_EST_{group}_{key}_var = {value} }}"
                           for key, value in modifiers)
        if policy.extra:
            effects.append(policy.extra)
        effects.extend(("TFR_EST_reconcile_energy_crisis = yes", "TFR_EST_refresh_country_modifiers = yes"))
        out.append(f"{PREFIX}reward_{policy.suffix} = {{\n    " + "\n    ".join(effects) + "\n}\n\n")
    out.append("""# Never call the parent's unsafe generic decrease_corona fallback.
TFR_EST_ratas_reduce_covid = {
    if = {
        limit = { tag = EST }
        if = {
            limit = { has_country_flag = TFR_EST_covid_seed_owned NOT = { has_idea = lower_covid_cases } }
            clr_country_flag = TFR_EST_covid_seed_owned
        }
        if = { limit = { has_idea = higher_covid_cases } swap_ideas = { remove_idea = higher_covid_cases add_idea = high_covid_cases } }
        else_if = { limit = { has_idea = high_covid_cases } swap_ideas = { remove_idea = high_covid_cases add_idea = medium_covid_cases } }
        else_if = { limit = { has_idea = medium_covid_cases } swap_ideas = { remove_idea = medium_covid_cases add_idea = low_covid_cases } }
        else_if = { limit = { has_idea = low_covid_cases } swap_ideas = { remove_idea = low_covid_cases add_idea = lower_covid_cases } }
        else_if = {
            limit = { has_idea = lower_covid_cases has_country_flag = TFR_EST_covid_seed_owned }
            remove_ideas = lower_covid_cases
            clr_country_flag = TFR_EST_covid_seed_owned
        }
    }
}

# Separate contribution variables preserve all permanent economy reforms.
TFR_EST_reconcile_energy_crisis = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_initialize_country_modifiers = yes
        if = { limit = { NOT = { has_variable = TFR_EST_energy_factory_applied } } set_variable = { TFR_EST_energy_factory_applied = 0 } }
        if = { limit = { NOT = { has_variable = TFR_EST_energy_goods_applied } } set_variable = { TFR_EST_energy_goods_applied = 0 } }
        set_temp_variable = { TFR_EST_energy_factory_target = 0 }
        set_temp_variable = { TFR_EST_energy_goods_target = 0 }
        if = {
            limit = { TFR_EST_energy_crisis_active = yes }
            if = {
                limit = { NOT = { has_country_flag = TFR_EST_energy_crisis_seen } }
                set_country_flag = TFR_EST_energy_crisis_seen
                country_event = { id = tfr_estonia_ratas.1 }
            }
            set_temp_variable = { TFR_EST_energy_factory_target = -0.04 }
            set_temp_variable = { TFR_EST_energy_goods_target = 0.03 }
            if = { limit = { OR = { has_country_flag = TFR_EST_done_ratas_lng_connection has_country_flag = TFR_EST_done_kallas_lng_connection } } add_to_temp_variable = { TFR_EST_energy_factory_target = 0.01 } }
            if = { limit = { OR = { has_country_flag = TFR_EST_done_ratas_grid_synchronisation has_country_flag = TFR_EST_done_kallas_gas_reserve } } add_to_temp_variable = { TFR_EST_energy_factory_target = 0.01 } }
            if = { limit = { OR = { has_country_flag = TFR_EST_done_ratas_renewable_chp has_country_flag = TFR_EST_done_kallas_energy_networks } } add_to_temp_variable = { TFR_EST_energy_factory_target = 0.01 } }
            if = { limit = { OR = { has_country_flag = TFR_EST_done_ratas_building_renovation has_country_flag = TFR_EST_done_kallas_energy_households } } add_to_temp_variable = { TFR_EST_energy_goods_target = -0.015 } }
            if = { limit = { OR = { has_country_flag = TFR_EST_done_ratas_network_charge_relief has_country_flag = TFR_EST_done_kallas_energy_networks } } add_to_temp_variable = { TFR_EST_energy_goods_target = -0.015 } }
        }
        if = {
            limit = {
                OR = {
                    NOT = { check_variable = { var = TFR_EST_energy_factory_applied value = TFR_EST_energy_factory_target compare = equals } }
                    NOT = { check_variable = { var = TFR_EST_energy_goods_applied value = TFR_EST_energy_goods_target compare = equals } }
                }
            }
            subtract_from_variable = { var = TFR_EST_economy_industrial_capacity_factory_var value = TFR_EST_energy_factory_applied }
            subtract_from_variable = { var = TFR_EST_economy_consumer_goods_factor_var value = TFR_EST_energy_goods_applied }
            add_to_variable = { var = TFR_EST_economy_industrial_capacity_factory_var value = TFR_EST_energy_factory_target }
            add_to_variable = { var = TFR_EST_economy_consumer_goods_factor_var value = TFR_EST_energy_goods_target }
            set_variable = { var = TFR_EST_energy_factory_applied value = TFR_EST_energy_factory_target }
            set_variable = { var = TFR_EST_energy_goods_applied value = TFR_EST_energy_goods_target }
            TFR_EST_refresh_country_modifiers = yes
        }
    }
}

TFR_EST_ratas_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_reconcile_energy_crisis = yes
        # A recovered outbreak bypasses unneeded emergency interventions without
        # paying their rewards. Ordinary family-doctor reform remains available.
        if = {
            limit = {
                TFR_EST_ratas_branch_visible = yes
                TFR_EST_independent_parliament = yes
                has_country_flag = TFR_EST_opening_complete
                OR = {
                    has_country_flag = TFR_EST_done_ratas_renew_agreement
                    has_completed_focus = TFR_EST_ratas_renew_agreement
                }
                has_country_flag = TFR_EST_covid_first_case_recorded
                NOT = { generic_has_corona = yes }
            }
            set_country_flag = TFR_EST_done_ratas_hospital_covid
            set_country_flag = TFR_EST_done_ratas_testing_tracing
            set_country_flag = TFR_EST_done_ratas_vaccinate_risk_groups
        }
    }
}
""")
    return "".join(out)


def build_localisation() -> str:
    entries = {}
    for policy in POLICIES:
        ident = PREFIX + policy.suffix
        text = policy.description + " The original three-party cabinet must hold at least 51 coalition seats."
        if policy.suffix in COVID_POLICIES:
            text += " Requires COVID cases in Estonia. If the outbreak has already recovered, this emergency measure is bypassed without its reward."
        entries[ident] = policy.title
        entries[ident + "_desc"] = text
        benefit = []
        if policy.budget:
            benefit.append(f"Budget: €{policy.budget:g} million, financed through public debt.")
        if policy.cohesion:
            benefit.append(f"National cohesion: +{policy.cohesion}.")
        if policy.readiness:
            benefit.append(f"Defense readiness: +{policy.readiness}.")
        if policy.benefit:
            benefit.append(policy.benefit)
        entries[ident + "_reward_tt"] = "\n".join(benefit)
    entries.update({
        "TFR_EST_ratas_energy_title": "The Energy Shock Reaches Estonia",
        "TFR_EST_ratas_energy_desc": "The Saudi civil war is disrupting international energy supplies. Estonia must protect essential services and help firms absorb higher costs. Without preparation, the shock reduces factory output by 4% and adds 3% to the consumer-goods factor until supplies recover. Funded LNG, grid and local-generation preparations reduce the output penalty; renovation and network-charge relief ease the burden on consumers. These measures support Estonia while the wider crisis follows its own course.",
        "TFR_EST_ratas_energy_option": "Review supply security and household bills.",
    })
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def outputs() -> dict[str, str]:
    return {
        "common/national_focus/TFR_EST_ratas.txt": build_focuses(),
        "common/scripted_triggers/TFR_EST_ratas.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_ratas.txt": build_effects(),
        "events/TFR_EST_ratas.txt": """add_namespace = tfr_estonia_ratas
country_event = {
    id = tfr_estonia_ratas.1
    title = TFR_EST_ratas_energy_title
    desc = TFR_EST_ratas_energy_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    option = { name = TFR_EST_ratas_energy_option }
}
""",
        "localisation/english/TFR_EST_ratas_l_english.yml": build_localisation(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for relative, value in outputs().items():
        path = ROOT / relative
        data = value.encode("utf-8-sig" if path.suffix == ".yml" else "utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Generated continuation is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(POLICIES)} retained-Ratas focuses, triggers, rewards, a crisis notice and 63 English keys.")


if __name__ == "__main__":
    main()

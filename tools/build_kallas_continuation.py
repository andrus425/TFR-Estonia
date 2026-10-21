"""Build Kallas's 2021-2023 Reform-Centre programme from enacted policy.

See docs/KALLAS_GOVERNMENT_SOURCES.md. Twenty 35-day focuses fit between
the January 2021 cabinet confirmation and the March 2023 regular election.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_ratas_continuation import Policy
from native_script_interface import amount_call
from focus_reward_model import rebalance_policies, modifier_reward, energy_progress_tooltip, concise_trigger


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_kallas_"
COVID_POLICIES = ("sick_pay", "hospital_support", "frontline_vaccination")
COMPACT_ROWS = {0: 0, 2: 1, 4: 2, 6: 3, 8: 4, 11: 6}

POLICIES = (
    Policy("govern_together", "A Reform-Centre Government",
           "Kaja Kallas takes office with Reform and Centre holding sixty seats in the existing Riigikogu. The abandoned marriage-referendum proposal gives way to a joint programme of public health, recovery and accountable government. Agree the legislative calendar and funding priorities without calling an early election.",
           "national_unity", (), 8, 0, cohesion=2, extra="add_political_power = 25", benefit="Gain 25 political power."),
    Policy("sick_pay", "Extend Sick Pay from the Second Day",
           "Extend the temporary sick-pay arrangement so workers can isolate without losing the first days of support. Employers cover days two to five and the Health Insurance Fund begins on day six. Kallas's government extended and funded this arrangement in its 2021 pandemic response.",
           "consumer_goods", ("govern_together",), 0, 2, budget=25, cohesion=2),
    Policy("hospital_support", "Fund the EUR 52 Million Hospital Package",
           "Implement the exceptional hospital and emergency-care funding adopted in the 2021 supplementary budget. Cover COVID treatment costs and coordinate the separately funded testing and vaccination work. Hospitals must retain staff and supplies while continuing essential non-COVID care.",
           "consumer_goods", ("sick_pay",), 0, 4, budget=52, cohesion=2),
    Policy("frontline_vaccination", "Vaccinate Frontline Workers",
           "Carry out the government's decision to continue vaccinating workers whose duties expose them to infection. Coordinate appointments, employers and reliable deliveries after supply interruptions. A funded rollout can improve the current outbreak while preserving vaccination records for later public-health work.",
           "consumer_goods", ("hospital_support",), 0, 6, budget=30, cohesion=2,
           extra="TFR_EST_kallas_reduce_covid = yes", benefit="Improve one existing COVID severity level. The lowest level is removed only for Estonia's own seeded outbreak."),
    Policy("covid_certificates", "Digital COVID Certificates and Verification",
           "Introduce patient-portal COVID certificates and a practical verification service, following the system implemented in 2021. Provide clear access, reliable records and help for people who need a printed certificate. The service remains useful after the immediate outbreak has recovered.",
           "scientific_exchange", ("frontline_vaccination",), 0, 8, budget=10,
           economic=(("research_speed_factor", .005),), benefit="Research speed: +0.5%."),
    Policy("pension_twenty", "Legislate the EUR 20 Pension Increase",
           "Enact and finance the extraordinary twenty-euro increase in the pension base and national-pension rate, as Parliament did in January 2022. Prepare the change for its scheduled January 2023 introduction. Passing the law creates a funded commitment before the higher payments begin.",
           "consumer_goods", ("govern_together",), 4, 2, budget=35, cohesion=3),
    Policy("pension_tax_allowance", "Exempt the Average Pension from Income Tax",
           "Implement the income-tax amendment adopted in December 2021, providing a pension-age allowance up to the average old-age pension from January 2023. Prepare payment administration and clear guidance so pensioners understand the difference between tax relief and the separate pension increase.",
           "consumer_goods", ("pension_twenty",), 4, 4, budget=25, cohesion=2),
    Policy("teacher_pay", "Teachers' Minimum Pay: EUR 1,412",
           "Fund the regulation raising teachers' minimum monthly pay from 1,315 to 1,412 euros in the 2022 budget. Coordinate the additional allocations with school owners and make the commitment visible in employment contracts. This advances the earlier teacher-pay policy through a concrete further increase.",
           "consumer_goods", ("pension_tax_allowance",), 4, 6, budget=30, cohesion=2),
    Policy("school_catch_up", "EUR 12 Million for Learning Gaps",
           "Put the twelve-million-euro school catch-up allocation from the adopted 2022 budget into operation. Support pupils whose learning suffered during remote schooling through targeted teaching and assessment. Schools should identify gaps and report how the extra support reaches those pupils.",
           "scientific_exchange", ("teacher_pay",), 4, 8, budget=12,
           economic=(("research_speed_factor", .01),), benefit="Research speed: +1%."),
    Policy("recovery_plan", "Adopt the Recovery Investment Programme",
           "Carry forward the recovery and resilience plan approved by the cabinet in June 2021. Set priorities, prepare co-financing and supervise projects for the green and digital transition. The near-billion-euro multi-year plan provides a programme of investment; this focus funds its preparation and implementation capacity.",
           "construct_infrastructure", ("govern_together",), 8, 2, budget=40,
           economic=(("production_speed_buildings_factor", .01),), benefit="Construction speed: +1%."),
    Policy("enterprise_digital", "Digitise Estonian Enterprise",
           "Use the approved recovery programme to prepare enterprise investment in digital processes, automation and the skills to operate them. Select workable projects with transparent conditions and measurable improvements. The public contribution supports firms' own investment and implementation.",
           "production", ("recovery_plan",), 8, 4, budget=40,
           economic=(("production_factory_efficiency_gain_factor", .015),), benefit="Production efficiency growth: +1.5%."),
    Policy("rural_broadband", "Broadband Access Beyond the Cities",
           "Continue the access-network support funded in the 2022 budget, with its objective of enabling nearly forty thousand rural households to connect by the end of 2023. Finance the next construction and connection programme with local authorities and operators. Longer projects continue beyond this focus.",
           "scientific_exchange", ("enterprise_digital",), 8, 6, budget=45, cohesion=2),
    Policy("mental_health", "Community Mental-Health Services",
           "Implement the three-million-euro mental-health allocation in the 2022 budget. Support children's mental-health centres, professional training for clinical psychologists and municipal community-psychologist services. Reliable local help is part of recovery from prolonged disruption.",
           "consumer_goods", ("rural_broadband",), 8, 8, budget=3, cohesion=3),
    Policy("energy_households", "Compensate Eligible Household Energy Bills",
           "Fund the means-tested relief that compensates eighty percent of eligible energy-price increases for households up to median income. Set up municipal applications and clear eligibility checks. Prepare the scheme for TFR's supply shock so relief can operate when households need it.",
           "consumer_goods", ("govern_together",), 12, 2, budget=50, cohesion=2,
           benefit="Reduce the local energy crisis's consumer-goods penalty by 1.5 percentage points, including if prepared before onset."),
    Policy("energy_networks", "Cut Electricity and Gas Network Charges",
           "Implement the electricity and gas network-charge support used by the government during the energy-price crisis. The historical package reduced household electricity-network charges by half and gas-network charges entirely, with additional support for firms. Authorize a funded response to disrupted supplies.",
           "consumer_goods", ("energy_households",), 12, 4, budget=45,
           benefit="Reduce the local energy crisis's factory-output penalty by 1 percentage point and its consumer-goods penalty by 1.5 points."),
    Policy("gas_reserve", "Procure a Strategic Gas Reserve",
           "Use the strategic gas-reserve authority adopted in the May 2022 supplementary budget, which provided up to 170 million euros and excluded Russian gas. Arrange purchasing, storage and access for essential users. Adapt the supply diversification to TFR's energy disruption while retaining the procurement limits.",
           "oil_refinery", ("energy_networks",), 12, 6, budget=170,
           benefit="Reduce the local energy crisis's factory-output penalty by 1 percentage point."),
    Policy("lng_connection", "Fund LNG Connection Capability",
           "Implement the LNG-capability funding adopted in the May 2022 supplementary budget, with an allocation of up to thirty million euros. Finance enabling works and connection arrangements with energy operators. The focus advances access to diversified supply while the larger infrastructure programme continues.",
           "construct_infrastructure", ("gas_reserve",), 12, 8, budget=30,
           benefit="Reduce the local energy crisis's factory-output penalty by 1 percentage point."),
    Policy("defence_budget", "The 2022 Defence Funding Commitment",
           "Maintain the adopted 2022 defence allocation of approximately 750 million euros, above 2.3 percent of GDP. Fund an additional priority package for readiness, procurement preparation and allied facilities within that programme. Estonia still recruits and equips its forces through normal systems.",
           "defence", ("govern_together",), 16, 2, budget=70, readiness=4,
           military=(("training_time_army_factor", -.02),), benefit="Army training time: −2%. No free troops or equipment."),
    Policy("civil_protection", "Mark Shelters and Rehearse Evacuation",
           "Put the 2022 civil-protection reinforcement into practical service: public shelter marking, warning systems, evacuation arrangements and emergency stocks. Coordinate the Rescue Board and municipalities against the threats that actually develop in TFR's Europe.",
           "national_unity", ("defence_budget",), 16, 4, budget=45, readiness=3, cohesion=2),
    Policy("account_to_voters", "Present the Government's Record",
           "Report the government's health, recovery, social and security programme to Parliament and the public. Explain costs, remaining commitments and the measures still needed under emergency conditions. The regular March 2023 election will decide the next mandate; this report calls no early vote.",
           "national_unity", ("covid_certificates", "school_catch_up", "mental_health", "lng_connection", "civil_protection"), 8, 11,
           cohesion=3, extra="set_country_flag = TFR_EST_kallas_programme_finished\nadd_political_power = 50", benefit="Gain 50 political power. Preserve the regular election calendar."),
)


POLICIES = rebalance_policies(POLICIES, "kallas")


def done(suffix):
    return "TFR_EST_done_kallas_" + suffix


def build_focuses():
    out = ["# Generated by tools/build_kallas_continuation.py.\n"]
    for index, p in enumerate(POLICIES):
        pre = "".join(f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n" for parent in p.parents)
        extra = "\n        TFR_EST_has_covid = yes" if p.suffix in COVID_POLICIES else ""
        if p.suffix == "account_to_voters":
            extra += "\n        TFR_EST_kallas_all_policies_done = yes"
        out.append(f"""
shared_focus = {{
    id = {PREFIX}{p.suffix}
    icon = GFX_goal_{PREFIX}{p.suffix}
    x = {p.x // 2}
    y = {COMPACT_ROWS[p.y]}
    cost = 5
{pre}    allow_branch = {{ TFR_EST_kallas_branch_visible = yes }}
    available = {{
        TFR_EST_kallas_governing = yes{extra}
    }}
    bypass = {{ has_country_flag = {done(p.suffix)} }}
    cancel_if_invalid = yes
    continue_if_invalid = no
    ai_will_do = {{ factor = {90-index} }}
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


def build_triggers():
    out = """TFR_EST_kallas_branch_visible = {
    tag = EST
    has_country_flag = TFR_EST_ratas_resigned
    has_country_flag = TFR_EST_referendum_failed
    NOT = { has_country_flag = TFR_EST_kallas_mandate_ended }
    NOT = { has_country_flag = TFR_EST_occupied }
}
TFR_EST_kallas_governing = {
    TFR_EST_kallas_branch_visible = yes
    TFR_EST_coalition_majority = yes
    has_country_flag = TFR_EST_opening_complete
    has_country_flag = TFR_EST_reform_centre_formed
    NOT = { has_country_flag = TFR_EST_caretaker }
    check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_reform value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_centre value = 1 compare = equals }
}
TFR_EST_kallas_all_policies_done = {
"""
    for p in POLICIES[:-1]:
        out += f"    OR = {{ has_completed_focus = {PREFIX}{p.suffix} has_country_flag = {done(p.suffix)} }}\n"
    out += "}\n"
    for name in ("TFR_EST_kallas_governing", "TFR_EST_kallas_all_policies_done"):
        out = concise_trigger(name, out)
    return out


def build_effects():
    out = []
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
        energy = energy_progress_tooltip("kallas", p.suffix)
        if energy:
            effects.append(energy)
        effects.append("hidden_effect = { TFR_EST_reconcile_energy_crisis = yes TFR_EST_refresh_country_modifiers = yes }")
        out.append(f"{PREFIX}reward_{p.suffix} = {{\n    " + "\n    ".join(effects) + "\n}\n\n")
    out.append("""# Both routes use the same guarded case-tier improvement.
TFR_EST_kallas_reduce_covid = { TFR_EST_ratas_reduce_covid = yes }
TFR_EST_kallas_tick = {
    if = {
        limit = {
            TFR_EST_kallas_governing = yes
            OR = {
                has_country_flag = TFR_EST_done_kallas_govern_together
                has_completed_focus = TFR_EST_kallas_govern_together
            }
            has_country_flag = TFR_EST_covid_first_case_recorded
            NOT = { generic_has_corona = yes }
        }
        set_country_flag = TFR_EST_done_kallas_sick_pay
        set_country_flag = TFR_EST_done_kallas_hospital_support
        set_country_flag = TFR_EST_done_kallas_frontline_vaccination
    }
}
""")
    return "".join(out)


def build_localisation():
    entries = {}
    for p in POLICIES:
        ident = PREFIX + p.suffix
        desc = p.description + " Requires a confirmed Reform-Centre cabinet with at least 51 coalition seats."
        if p.suffix in COVID_POLICIES:
            desc += " Requires COVID cases in Estonia. An already recovered outbreak bypasses this intervention without its reward."
        entries[ident] = p.title
        entries[ident + "_desc"] = desc
        benefit = []
        if p.budget:
            benefit.append(f"Budget: €{p.budget:g} million, financed through public debt.")
        if p.cohesion:
            benefit.append(f"National cohesion: +{p.cohesion}.")
        if p.readiness:
            benefit.append(f"Defense readiness: +{p.readiness}.")
        if p.benefit:
            benefit.append(p.benefit)
        entries[ident + "_reward_tt"] = "\n".join(benefit)
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in entries.items())


def build_sprites():
    """Register continuation art and the two-pass highlight used by TFR focuses."""
    pieces = [
        "# Generated by tools/build_kallas_continuation.py.\n"
        "# Shine animation matches TFR_goals_shine.gfx in the parent mod.\n"
        "spriteTypes = {\n"
    ]
    for policy in POLICIES:
        name = "GFX_goal_" + PREFIX + policy.suffix
        texture = f"gfx/interface/goals/EST/EST_kallas_{policy.suffix}.png"
        pieces.append(
            f"    SpriteType = {{\n"
            f'        name = "{name}"\n'
            f'        texturefile = "{texture}"\n'
            f"    }}\n"
            f"    SpriteType = {{\n"
            f'        name = "{name}_shine"\n'
            f'        texturefile = "{texture}"\n'
            f'        effectFile = "gfx/FX/buttonstate.lua"\n'
        )
        for rotation in (-90.0, 90.0):
            pieces.append(
                f"        animation = {{\n"
                f'            animationmaskfile = "{texture}"\n'
                f'            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"\n'
                f"            animationrotation = {rotation}\n"
                f"            animationlooping = no\n"
                f"            animationtime = 0.75\n"
                f"            animationdelay = 0\n"
                f'            animationblendmode = "add"\n'
                f'            animationtype = "scrolling"\n'
                f"            animationrotationoffset = {{ x = 0.0 y = 0.0 }}\n"
                f"            animationtexturescale = {{ x = 1.0 y = 1.0 }}\n"
                f"        }}\n"
            )
        pieces.append("        legacy_lazy_load = no\n    }\n")
    pieces.append("}\n")
    return "".join(pieces)


def outputs():
    return {
        "common/national_focus/TFR_EST_kallas.txt": build_focuses(),
        "interface/TFR_EST_kallas_focus_icons.gfx": build_sprites(),
        "common/scripted_triggers/TFR_EST_kallas.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_kallas.txt": build_effects(),
        "localisation/english/TFR_EST_kallas_l_english.yml": build_localisation(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    for relative, text in outputs().items():
        path = ROOT / relative
        data = text.encode("utf-8-sig" if path.suffix == ".yml" else "utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Generated Kallas programme is stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + " 20 Kallas focuses, 40 focus sprites, triggers, rewards and 60 English keys.")


if __name__ == "__main__":
    main()

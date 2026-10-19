"""Build Estonia's coalition-controlled TFR cabinet and sourced candidate register.

Use native minister slots, native trait modifiers and native timed cost factors.
The prime minister remains owned exclusively by the parliamentary story ledger.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTIES = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")
PARTY_NAMES = dict(zip(PARTIES, ("Reform", "Keskerakond", "EKRE", "Isamaa", "Social Democrats", "Eesti 200", "Parempoolsed")))
PORTFOLIOS = {"foreign": "foreign_minister", "economic": "economic_minister", "interior": "interior_minister", "intelligence": "intelligence_minister", "defence": "theorist_minister"}
PORTFOLIO_NAMES = {"foreign": "Foreign Minister", "economic": "Economic Minister", "interior": "Interior Minister", "intelligence": "Intelligence Minister", "defence": "Defence Minister"}
CANDIDATES = tuple(
    entry for filename in ("minister_roster_established.json", "minister_roster_newer.json")
    for entry in json.loads((ROOT / "tools" / filename).read_text(encoding="utf-8-sig"))
)
PM_PEOPLE = {"mart_helme": "ekre"}
# Future authored leadership changes must identify the person explicitly.
# Isamaa/EKRE having a PM does not make Reinsalu/Martin the incumbent by itself.
NAMED_PM_PEOPLE = {"urmas_reinsalu": "isamaa", "martin_helme": "ekre"}
OPENING = ("urmas_reinsalu_foreign", "taavi_aas_economic", "mart_helme_interior", "raivo_aeg_intelligence", "juri_luik_defence")
PROFILES = {
    "diplomat": ("Experienced Diplomat", {"opinion_gain_monthly_factor": .15, "trade_opinion_factor": .15}),
    "cooperation": ("International Cooperation", {"opinion_gain_monthly_factor": .10, "research_speed_factor": .025}),
    "sovereignty": ("Security Diplomacy", {"war_support_factor": .05, "opinion_gain_monthly_factor": .10}),
    "enterprise": ("Enterprise and Investment", {"production_speed_buildings_factor": .06, "industrial_capacity_factory": .03}),
    "fiscal": ("Fiscal Administration", {"consumer_goods_factor": -.025, "political_power_gain": .10}),
    "regional": ("Regional Development", {"production_speed_buildings_factor": .04, "local_resources_factor": .05}),
    "administration": ("Experienced Administrator", {"stability_factor": .05, "political_power_gain": .05}),
    "emergency": ("Emergency Coordination", {"stability_factor": .03, "mobilization_speed": .10}),
    "civic": ("Community Security", {"stability_factor": .04, "war_support_factor": .03}),
    "intelligence": ("Intelligence Professional", {"encryption_factor": .10, "decryption_factor": .15}),
    "oversight": ("Civilian Security Oversight", {"encryption_factor": .10, "stability_factor": .025}),
    "counterintelligence": ("Counterintelligence Experience", {"encryption_factor": .15, "decryption_factor": .10}),
    "territorial": ("Territorial Defence Planner", {"army_defence_factor": .05, "army_org_factor": .03}),
    "professional": ("Professional Force Development", {"training_time_army_factor": -.08, "army_org_factor": .04}),
    "allied": ("Allied Defence Coordination", {"supply_consumption_factor": -.04, "army_org_factor": .04}),
}
PERSON_PROFILES = {
    "urmas_paet": "diplomat", "jurgen_ligi": "fiscal", "hanno_pevkur": "administration", "eerik_niiles_kross": "intelligence", "kalle_laanet": "professional",
    "enn_eesmaa": "cooperation", "taavi_aas": "regional", "jaak_aab": "administration", "kalle_klandorf": "counterintelligence", "tiit_terik": "territorial",
    "urmas_reinsalu": "sovereignty", "sven_sester": "fiscal", "marko_pomerants": "administration", "raivo_aeg": "counterintelligence", "juri_luik": "allied",
    "marina_kaljurand": "diplomat", "ivari_padar": "regional", "katri_raik": "civic", "andres_anvelt": "counterintelligence", "sven_mikser": "allied",
    "martin_helme": "fiscal", "jaak_madison": "sovereignty", "alar_laneman": "emergency", "ants_frosch": "intelligence", "leo_kunnas": "territorial",
    "margus_tsahkna": "cooperation", "tiit_riisalo": "enterprise", "igor_taro": "emergency", "liisa_ly_pakosta": "oversight", "kalev_stoicescu": "allied",
    "tiit_naber": "diplomat", "kristjan_vanaselja": "enterprise", "siim_valmar_kiisler": "administration", "rainer_saks": "intelligence", "ilmar_raag": "territorial",
    "trivimi_velliste": "diplomat", "rene_kokk": "regional",
}
FEMALE_PEOPLE = {"marina_kaljurand", "katri_raik", "liisa_ly_pakosta"}


def candidate_id(candidate):
    return f"TFR_EST_minister_{candidate['person']}_{candidate['portfolio']}"


def eligibility(candidate):
    return f"TFR_EST_can_appoint_{candidate['person']}_{candidate['portfolio']}"


def profile(candidate):
    if candidate["person"] == "mart_helme":
        return "sovereignty" if candidate["portfolio"] == "foreign" else "emergency"
    return PERSON_PROFILES[candidate["person"]]


def people():
    result = defaultdict(list)
    for candidate in CANDIDATES:
        result[candidate["person"]].append(candidate)
    return result


def build_triggers():
    out = ["""# Cabinet appointments use the seven-party ledger, never ideology groups.
TFR_EST_can_manage_ministers = {
    custom_trigger_tooltip = {
        tooltip = TFR_EST_minister_confirmed_tt
        TFR_EST_confirmed_cabinet = yes
    }
}
"""]
    for person, party in NAMED_PM_PEOPLE.items():
        out.append(f"""TFR_EST_person_is_pm_{person} = {{
    TFR_EST_constitutional_executive = yes
    has_country_flag = TFR_EST_pm_person_{person}
    check_variable = {{ var = TFR_EST_pm_party value = {PARTIES.index(party) + 1} compare = equals }}
}}
""")
    out.append("""TFR_EST_person_is_pm_mart_helme = {
    TFR_EST_constitutional_executive = yes
    OR = {
        has_idea = TFR_EST_pm_ekre
        check_variable = { var = TFR_EST_pm_party value = 3 compare = equals }
    }
    NOT = { TFR_EST_person_is_pm_martin_helme = yes }
}
""")
    for party in PARTIES:
        out.append(f"""TFR_EST_minister_coalition_{party} = {{
    custom_trigger_tooltip = {{
        tooltip = TFR_EST_minister_coalition_{party}_tt
        check_variable = {{ var = TFR_EST_active_{party} value = 1 compare = equals }}
        check_variable = {{ var = TFR_EST_coalition_{party} value = 1 compare = equals }}
    }}
}}
""")
    for candidate in CANDIDATES:
        exclusions = [candidate_id(other) for other in people()[candidate["person"]] if other is not candidate]
        free = "\n".join(f"            NOT = {{ has_idea = {ident} }}" for ident in exclusions)
        if candidate["person"] in PM_PEOPLE or candidate["person"] in NAMED_PM_PEOPLE:
            free += f"\n            NOT = {{ TFR_EST_person_is_pm_{candidate['person']} = yes }}"
        out.append(f"""{eligibility(candidate)} = {{
    TFR_EST_can_manage_ministers = yes
    TFR_EST_minister_coalition_{candidate['party']} = yes
    custom_trigger_tooltip = {{
        tooltip = TFR_EST_minister_one_office_tt
        AND = {{
            always = yes
{free}
        }}
    }}
}}
""")
    return "".join(out)


def build_ideas():
    out = ["# Generated native TFR cabinet candidates. Head minister is deliberately absent.\nideas = {\n"]
    for portfolio, slot in PORTFOLIOS.items():
        out.append(f"    {slot} = {{\n")
        for candidate in CANDIDATES:
            if candidate["portfolio"] != portfolio:
                continue
            party = candidate["party"]
            out.append(f"""        {candidate_id(candidate)} = {{
            picture = TFR_EST_person_{candidate['person']}
            allowed = {{ original_tag = EST }}
            visible = {{
                TFR_EST_constitutional_executive = yes
                check_variable = {{ var = TFR_EST_active_{party} value = 1 compare = equals }}
            }}
            available = {{ {eligibility(candidate)} = yes }}
            allowed_to_remove = {{ TFR_EST_can_manage_ministers = yes }}
            cost = 100
            removal_cost = -1
            traits = {{ TFR_EST_minister_party_{party} TFR_EST_minister_trait_{profile(candidate)} }}
            on_add = {{ hidden_effect = {{ TFR_EST_reconcile_ministers = yes }} }}
            ai_will_do = {{
                base = 2
                modifier = {{ factor = 4 has_idea = TFR_EST_cabinet_formation }}
                modifier = {{ factor = 2 check_variable = {{ var = TFR_EST_pm_party value = {PARTIES.index(party) + 1} compare = equals }} }}
            }}
        }}
""")
        out.append("    }\n")
    out.append("""    country = {
        TFR_EST_cabinet_formation = {
            picture = generic_emerging_economy
            allowed = { original_tag = EST }
            removal_cost = -1
            modifier = {
                foreign_minister_cost_factor = -0.8
                economic_minister_cost_factor = -0.8
                interior_minister_cost_factor = -0.8
                intelligence_minister_cost_factor = -0.8
                theorist_minister_cost_factor = -0.8
            }
        }
    }
}
""")
    return "".join(out)


def build_traits():
    out = ["# Party labels are cosmetic; professional traits supply native country modifiers.\nleader_traits = {\n"]
    for party in PARTIES:
        out.append(f"    TFR_EST_minister_party_{party} = {{ random = no }}\n")
    for key, (_, modifiers) in PROFILES.items():
        out.append(f"    TFR_EST_minister_trait_{key} = {{\n        random = no\n")
        out.extend(f"        {field} = {amount:g}\n" for field, amount in modifiers.items())
        out.append("    }\n")
    return "".join(out) + "}\n"


def build_effects():
    all_ids = "\n        ".join(candidate_id(candidate) for candidate in CANDIDATES)
    opening = "\n            ".join("add_ideas = TFR_EST_minister_" + suffix for suffix in OPENING)
    clear_markers = "\n    ".join(f"clr_country_flag = TFR_EST_pm_person_{person}" for person in NAMED_PM_PEOPLE)
    stale_markers = "\n".join(
        f"            if = {{ limit = {{ NOT = {{ check_variable = {{ var = TFR_EST_pm_party value = {PARTIES.index(party) + 1} compare = equals }} }} }} clr_country_flag = TFR_EST_pm_person_{person} }}"
        for person, party in NAMED_PM_PEOPLE.items()
    )
    out = [f"""# Named-PM metadata belongs to authored government changes.
# The 2023 EKRE mandate derives Martin's marker from persistent party history.
# No player appointment can set these flags.
TFR_EST_clear_pm_person_markers = {{
    {clear_markers}
}}

# Native timed cost factors expire and save/load without a custom timer.
TFR_EST_begin_minister_formation = {{
    if = {{
        limit = {{ TFR_EST_independent_parliament = yes }}
        remove_ideas = TFR_EST_cabinet_formation
        add_timed_idea = {{ idea = TFR_EST_cabinet_formation days = 90 }}
    }}
}}

# Seed the real opening portfolio holders once. Intelligence is a TFR abstraction
# represented by Justice Minister/former security-service director Raivo Aeg.
TFR_EST_initialize_ministers = {{
    if = {{
        limit = {{ tag = EST has_country_flag = TFR_EST_initialized NOT = {{ has_country_flag = TFR_EST_ministers_initialized }} }}
        set_country_flag = TFR_EST_ministers_initialized
        if = {{
            limit = {{
                TFR_EST_confirmed_cabinet = yes
                date < 2020.2.1
                check_variable = {{ var = TFR_EST_pm_party value = 2 compare = equals }}
                TFR_EST_minister_coalition_centre = yes
                TFR_EST_minister_coalition_ekre = yes
                TFR_EST_minister_coalition_isamaa = yes
            }}
            {opening}
        }}
    }}
}}

TFR_EST_suspend_ministers = {{
    TFR_EST_clear_pm_person_markers = yes
    clr_country_flag = TFR_EST_pm_person_tanel_kiik
    clr_country_flag = TFR_EST_pm_person_mihhail_kolvart
    remove_ideas = {{
        {all_ids}
        TFR_EST_cabinet_formation
    }}
}}

# Repair never appoints replacements or reruns a valid incumbent's on_add.
TFR_EST_reconcile_ministers = {{
    if = {{
        limit = {{ tag = EST has_country_flag = TFR_EST_initialized }}
        # Confirmation recounts confidence before repairing the executive UI.
        # Identify the actual PM before excluding any portfolio candidate.
        TFR_EST_reconcile_ekre_pm_identity = yes
        TFR_EST_reconcile_centre_pm_identity = yes
        if = {{
            limit = {{ NOT = {{ TFR_EST_independent_parliament = yes }} }}
            TFR_EST_suspend_ministers = yes
        }}
        else = {{
{stale_markers}
            # Outgoing caretaker ministers retain their offices during talks.
            # Once a cabinet is confirmed, only its coalition supplies ministers.
            if = {{
                limit = {{ NOT = {{ has_country_flag = TFR_EST_caretaker }} }}
"""]
    for candidate in CANDIDATES:
        out.append(f"                if = {{ limit = {{ has_idea = {candidate_id(candidate)} NOT = {{ TFR_EST_minister_coalition_{candidate['party']} = yes }} }} remove_ideas = {candidate_id(candidate)} }}\n")
    out.append("            }\n")
    for person, candidates in people().items():
        if person in PM_PEOPLE or person in NAMED_PM_PEOPLE:
            tokens = " ".join(candidate_id(candidate) for candidate in candidates)
            out.append(f"            if = {{ limit = {{ TFR_EST_person_is_pm_{person} = yes }} remove_ideas = {{ {tokens} }} }}\n")
        for index, candidate in enumerate(candidates[1:], 1):
            earlier = " ".join(f"has_idea = {candidate_id(other)}" for other in candidates[:index])
            out.append(f"            if = {{ limit = {{ has_idea = {candidate_id(candidate)} OR = {{ {earlier} }} }} remove_ideas = {candidate_id(candidate)} }}\n")
    out.append("        }\n    }\n}\n")
    return "".join(out)


def build_sprites():
    out = ["# Existing TFR generic portraits; no third-party portrait assets redistributed.\nspriteTypes = {\n"]
    for index, (person, candidates) in enumerate(people().items()):
        portrait = f"politician_female{index % 3 + 1}.png" if person in FEMALE_PEOPLE else f"politician{index % 33 + 1}.png"
        out.append(f'    spriteType = {{ name = "GFX_idea_TFR_EST_person_{person}" texturefile = "gfx/leaders/Europe/{portrait}" legacy_lazy_load = no }}\n')
    return "".join(out) + "}\n"


def build_localisation():
    loc = {
        "TFR_EST_minister_confirmed_tt": "An independent, confirmed cabinet has at least 51 confidence votes.",
        "TFR_EST_minister_one_office_tt": "This person holds no other cabinet portfolio and is not prime minister.",
        "TFR_EST_cabinet_formation": "Forming the Post-Election Cabinet",
        "TFR_EST_cabinet_formation_desc": "For 90 days after a valid parliamentary election, appointments and replacements in the five minister portfolios cost 80% less political power. The normal 100 PP becomes 20 PP before other modifiers. Only coalition parties may provide ministers. The prime minister remains determined by the parliamentary mandate and scripted government changes.",
    }
    for party, name in PARTY_NAMES.items():
        loc[f"TFR_EST_minister_coalition_{party}_tt"] = f"{name} is active and belongs to the governing coalition."
        loc[f"TFR_EST_minister_party_{party}"] = name + " Nominee"
        loc[f"TFR_EST_minister_party_{party}_desc"] = "Nominated by " + name + ". Confidence-and-supply support alone does not permit cabinet appointments."
    for key, (title, _) in PROFILES.items():
        loc[f"TFR_EST_minister_trait_{key}"] = title
        loc[f"TFR_EST_minister_trait_{key}_desc"] = "Professional experience applied to the work of the cabinet."
    for candidate in CANDIDATES:
        ident = candidate_id(candidate)
        loc[ident] = candidate["name"]
        basis = "Historical portfolio experience." if candidate["basis"] == "exactfit" else "Plausible alternate-history appointment."
        loc[ident + "_desc"] = f"§Y{PARTY_NAMES[candidate['party']]} nominee — {PORTFOLIO_NAMES[candidate['portfolio']]}§!\n{basis} {candidate['rationale']}\nRequires the nominating party in the coalition and a confirmed cabinet. A person can hold one cabinet office at a time."
    return "l_english:\n" + "".join(f" {key}:0 {json.dumps(value, ensure_ascii=False)}\n" for key, value in loc.items())


def build_register():
    out = ["# Estonia minister roster and sources\n\n",
           "This register distinguishes historical experience from inferred appointments in TFR's alternate timeline. Party association is anchored to the 2020 campaign where possible. Later documented associations support plausible recruitment; they do not assert membership or incumbency on 1 January 2020. No automatic real-world defections are imposed.\n\n",
           "TFR's five editable portfolios are foreign, economic, interior, intelligence and defence (`theorist_minister`). Its economic slot covers fiscal and economic policy. Estonia has no separate cabinet-level intelligence ministry: these nominees represent political oversight and professional security experience. All intelligence appointments are inferences, including former intelligence directors.\n\n",
           "The opening appoints Urmas Reinsalu, Taavi Aas, Mart Helme, Raivo Aeg and Jüri Luik. Aeg's slot is an abstraction of his justice/security responsibilities. The [official cabinet register](https://www.valitsus.ee/vabariigi-valitsuse-50-koosseis) records the historical government.\n\n",
           "Appointments use the party ledger, require a confirmed independent cabinet and coalition membership, and cost 100 PP before modifiers. A valid election grants a 90-day, 80% appointment discount, normally reducing the price to 20 PP. Caretakers retain outgoing ministers but cannot appoint replacements. A confirmed coalition change removes outgoing parties' ministers; occupation clears all five portfolios and the discount. Portfolios vacated by the player are never automatically refilled.\n\n",
           "Mart Helme has two possible portfolios; reciprocal exclusions permit only one. Both are blocked while he is PM. Jaak Madison and Alar Laneman preserve EKRE's alternatives. Trivimi Velliste and Rene Kokk provide alternatives if Reinsalu or Martin Helme becomes PM. Reinsalu remains appointable under Seeder and Martin under Mart; their parties supplying a PM does not identify them as that person. Once a confirmed EKRE government serves its 2023 mandate, Martin becomes prime minister and Rene Kokk remains eligible for the economic portfolio. Mart's foreign and interior candidacies then become available subject to their mutual office restriction. Portraits currently reuse TFR's generic European political portraits.\n\n",
           "The 2023 EKRE government records `TFR_EST_martin_leads_ekre` only after cabinet confirmation. This career history survives later elections and occupation, restores `TFR_EST_pm_person_martin_helme` while EKRE supplies the incumbent, and keeps Martin as the head of later EKRE governments. Future leadership events may set `TFR_EST_pm_person_urmas_reinsalu` or `TFR_EST_pm_person_martin_helme` after confirming the appropriate party's cabinet and updating its executive display. Minister eligibility excludes the named incumbent, and a Martin marker supersedes Mart's default personal exclusion. Reconciliation clears stale wrong-party markers; occupation clears both personal markers while preserving career history. A successful new electoral or scripted mandate clears outgoing personal markers, and reconciliation restores the recorded EKRE leader. Confidence recovery and caretaker continuity preserve the incumbent. Personal markers never change parties, seats or parliamentary mandates.\n\n",
           "After a valid Centre defeat in 2023, its September congress chooses Tanel Kiik or Mihhail Kõlvart as party leader. Neither is a portfolio nominee in this roster, so all five Centre portfolios retain eligible candidates. The choice does not replace another party's prime minister or alter portfolio appointments; an outgoing Ratas caretaker waits for cabinet confirmation. Selected party leadership survives future elections and occupation, while current Centre PM markers are cleared during occupation.\n\n",
           "| Party | Foreign | Economy | Interior | Intelligence | Defence |\n|---|---|---|---|---|---|\n"]
    for party in PARTIES:
        cells = [PARTY_NAMES[party]]
        for portfolio in PORTFOLIOS:
            cells.append("; ".join(c["name"] for c in CANDIDATES if c["party"] == party and c["portfolio"] == portfolio))
        out.append("| " + " | ".join(cells) + " |\n")
    for candidate in CANDIDATES:
        label = "Historical portfolio experience" if candidate["basis"] == "exactfit" else "Inferred appointment"
        out.append(f"\n## {candidate['name']} — {PORTFOLIO_NAMES[candidate['portfolio']]} ({PARTY_NAMES[candidate['party']]})\n\n{label}. {candidate['rationale']}\n\n")
        out.extend(f"- [{source['title']}]({source['url']})\n" for source in candidate["sources"])
    out.append("\nTrait modifiers, appointment prices and the election window are game balance choices. They are not historical estimates of individual competence.\n")
    return "".join(out)


def outputs():
    return {
        "common/ideas/TFR_EST_ministers.txt": build_ideas(),
        "common/country_leader/TFR_EST_ministers.txt": build_traits(),
        "common/scripted_triggers/TFR_EST_ministers.txt": build_triggers(),
        "common/scripted_effects/TFR_EST_ministers.txt": build_effects(),
        "interface/TFR_EST_ministers.gfx": build_sprites(),
        "localisation/english/TFR_EST_ministers_l_english.yml": build_localisation(),
        "docs/MINISTER_ROSTER.md": build_register(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    seen = set()
    for candidate in CANDIDATES:
        ident = candidate_id(candidate)
        if ident in seen:
            raise SystemExit("Duplicate cabinet candidate: " + ident)
        seen.add(ident)
    for party in PARTIES:
        for portfolio in PORTFOLIOS:
            if not any(c["party"] == party and c["portfolio"] == portfolio for c in CANDIDATES):
                raise SystemExit(f"Missing nominee: {party}/{portfolio}")
    for relative, text in outputs().items():
        path = ROOT / relative
        data = text.encode("utf-8-sig" if path.suffix == ".yml" else "utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit("Generated minister content is stale: " + relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(("Verified" if args.check else "Wrote") + f" {len(CANDIDATES)} cabinet candidacies for {len(people())} people across five TFR portfolios.")


if __name__ == "__main__":
    main()

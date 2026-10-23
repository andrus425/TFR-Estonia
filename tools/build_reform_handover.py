"""Build the guarded 2024 Kallas--Michal succession for the 2023 mandate.

Historical basis (the mod deliberately preserves its alternate coalition):
https://www.consilium.europa.eu/en/meetings/european-council/2024/06/27/
https://valitsus.ee/en/news/new-government-office-and-will-hold-sitting-thursday

Kallas was nominated in June; Michal took office on 23 July. She did not become
High Representative until December, so the event refers to her nomination.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def outputs():
    triggers = '''# A European nomination requires Estonia's actual TFR EU membership.
# The 2023 mandate is authored by the validated election controller.
TFR_EST_reform_handover_eligible = {
    TFR_EST_confirmed_cabinet = yes
    has_country_flag = TFR_EST_reform_2023_mandate
    NOT = { has_country_flag = TFR_EST_reform_2023_mandate_ended }
    check_variable = { var = TFR_EST_mandate_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_reform value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_seats value = 51 compare = greater_than_or_equals }
    has_dynamic_modifier = { modifier = EU_member_dynamic }
    date > 2024.7.22
    NOT = { has_country_flag = TFR_EST_kallas_departed_for_europe }
}
'''
    effects = '''# Career history survives elections, occupation and restoration. The personal
# marker identifies only the current officeholder and is repeat-safe to repair.
TFR_EST_reconcile_reform_pm_identity = {
    if = {
        limit = {
            TFR_EST_constitutional_executive = yes
            check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
            has_country_flag = TFR_EST_kallas_departed_for_europe
        }
        set_country_flag = TFR_EST_pm_person_kristen_michal
    }
    else = { clr_country_flag = TFR_EST_pm_person_kristen_michal }
}

# No seats, coalition partners, election dates, popularity or rewards change.
# An obsolete delayed event cannot replace a successor or an occupation leader.
TFR_EST_complete_reform_handover = {
    if = {
        limit = { TFR_EST_reform_handover_eligible = yes }
        set_country_flag = TFR_EST_kallas_departed_for_europe
        set_country_flag = TFR_EST_pm_person_kristen_michal
        clr_country_flag = TFR_EST_reform_2024_handover_pending
        TFR_EST_reconcile_executive_display = yes
    }
}

TFR_EST_reform_handover_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        if = {
            limit = { TFR_EST_reform_handover_eligible = yes }
            if = {
                limit = { NOT = { has_country_flag = TFR_EST_reform_2024_handover_pending } }
                set_country_flag = TFR_EST_reform_2024_handover_pending
                country_event = { id = tfr_estonia_reform_handover.1 days = 1 }
            }
        }
        else = { clr_country_flag = TFR_EST_reform_2024_handover_pending }
    }
}
'''
    events = '''add_namespace = tfr_estonia_reform_handover
country_event = {
    id = tfr_estonia_reform_handover.1
    title = TFR_EST_reform_handover_title
    desc = TFR_EST_reform_handover_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_reform_handover_eligible = yes
        has_country_flag = TFR_EST_reform_2024_handover_pending
    }
    option = {
        name = TFR_EST_reform_handover_option
        custom_effect_tooltip = TFR_EST_reform_handover_tt
        hidden_effect = { TFR_EST_complete_reform_handover = yes }
    }
}
'''
    loc = {
        'TFR_EST_kristen_michal': 'Kristen Michal',
        'TFR_EST_kristen_michal_desc': "Kristen Michal has served as justice minister, minister of economic affairs and infrastructure, and climate minister. He succeeds Kaja Kallas as prime minister while Reform retains its parliamentary mandate. Existing coalition agreements and enacted policies continue under his cabinet.",
        'TFR_EST_pm_reform_michal': '$TFR_EST_kristen_michal$',
        'TFR_EST_pm_reform_michal_desc': 'Prime Minister: §H$TFR_EST_kristen_michal$§!\n[TFR_EST_hog_cabinet_status]\n\n$TFR_EST_kristen_michal_desc$',
        'TFR_EST_hog_reform_michal': 'Prime Minister: §H$TFR_EST_kristen_michal$§!\n[TFR_EST_hog_cabinet_status]\n\n\n\n\n\n\n   £GFX_TFR_EST_hog_portrait_reform_michal\n\n\n\n\n\n\n\n\n-------------------------------------\n§L$TFR_EST_kristen_michal_desc$§!',
        'TFR_EST_reform_handover_title': 'Kallas Heads to Europe',
        'TFR_EST_reform_handover_desc': "Kaja Kallas is leaving the prime minister's office after receiving a nomination to become the European Union's High Representative for Foreign Affairs and Security Policy. The appointment process will continue in Europe, while responsibility for Estonia's government passes to Kristen Michal.\n\nReform and its governing partners have agreed to continue their parliamentary programme under Michal. The president remains in office, the Riigikogu keeps its existing seats, and the cabinet's preparation for the European crisis continues. A change of prime minister within the governing majority does not require an election.",
        'TFR_EST_reform_handover_option': 'Michal takes responsibility for the government.',
        'TFR_EST_reform_handover_tt': '§YKristen Michal§! succeeds §YKaja Kallas§! as prime minister. Preserve the coalition, parliamentary seats, election calendar, ministers and completed policies. Future Reform-led cabinets will be led by Michal.',
    }
    localization = 'l_english:\n' + ''.join(f' {key}:0 {json.dumps(value, ensure_ascii=False)}\n' for key, value in loc.items())
    return {
        'common/scripted_triggers/TFR_EST_reform_handover.txt': triggers,
        'common/scripted_effects/TFR_EST_reform_handover.txt': effects,
        'events/TFR_EST_reform_handover.txt': events,
        'localisation/english/TFR_EST_reform_handover_l_english.yml': localization,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for relative, content in outputs().items():
        path = ROOT / relative
        data = content.encode('utf-8-sig' if path.suffix == '.yml' else 'utf-8')
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'Generated Reform handover differs: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('Reform 2024 handover ' + ('verified.' if args.check else 'written.'))


if __name__ == '__main__':
    main()

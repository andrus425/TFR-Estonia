"""Build the automatic 5 February 2022 Saar--Laanemets party succession.

Primary historical sources:
https://www.sotsid.ee/sotsiaaldemokraatide-uus-esimees-on-lauri-laanemets/
https://www.valitsus.ee/lauri-laanemets

The party elected Lauri Laanemets on 5 February 2022. Party leadership changes
on the daily hook, independently of acknowledging the informational event.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def outputs():
    triggers = '''# The first independent daily update on/after the historical congress date.
# Opposition status and the identity of coalition partners do not block it.
TFR_EST_sde_handover_eligible = {
    TFR_EST_independent_parliament = yes
    date > 2022.2.4
    NOT = { has_country_flag = TFR_EST_laanemets_leads_sde }
}

TFR_EST_sde_handover_notice_eligible = {
    TFR_EST_independent_parliament = yes
    date > 2022.2.4
    has_country_flag = TFR_EST_laanemets_leads_sde
    NOT = { has_country_flag = TFR_EST_sde_handover_presented }
}
'''
    effects = '''# Party career history and the incumbent PM are different records. A Saar
# caretaker remains in office until an actual cabinet confirmation. Occupation
# hides the current personal marker but retains both career and waiting state.
TFR_EST_reconcile_sde_pm_identity = {
    if = {
        limit = {
            TFR_EST_constitutional_executive = yes
            check_variable = { var = TFR_EST_pm_party value = 5 compare = equals }
        }
        if = {
            limit = { NOT = { has_country_flag = TFR_EST_caretaker } }
            clr_country_flag = TFR_EST_sde_handover_waiting_confirmation
        }
        if = {
            limit = { NOT = { has_country_flag = TFR_EST_sde_handover_waiting_confirmation } }
            if = {
                limit = { has_country_flag = TFR_EST_laanemets_leads_sde }
                set_country_flag = TFR_EST_pm_person_lauri_laanemets
            }
            else = { clr_country_flag = TFR_EST_pm_person_lauri_laanemets }
        }
    }
    else = {
        clr_country_flag = TFR_EST_pm_person_lauri_laanemets
        if = {
            limit = { NOT = { check_variable = { var = TFR_EST_pm_party value = 5 compare = equals } } }
            clr_country_flag = TFR_EST_sde_handover_waiting_confirmation
        }
    }
}

# No player choice, event acknowledgement, election result or focus is required.
# This effect deliberately does not change seats, polls, coalition membership,
# ministers, the election timer, political power or the constitutional president.
TFR_EST_complete_sde_handover = {
    if = {
        limit = { TFR_EST_sde_handover_eligible = yes }
        set_country_flag = TFR_EST_laanemets_leads_sde
        if = {
            limit = {
                check_variable = { var = TFR_EST_pm_party value = 5 compare = equals }
                has_country_flag = TFR_EST_caretaker
            }
            set_country_flag = TFR_EST_sde_handover_waiting_confirmation
        }
        else = { clr_country_flag = TFR_EST_sde_handover_waiting_confirmation }
        TFR_EST_reconcile_sde_pm_identity = yes
        TFR_EST_reconcile_executive_display = yes
    }
}

# Record the historical succession before queueing its optional notification.
# An undelivered queue expires after two days and can retry after restoration.
# A delivered notice stays delivered even when Estonia is occupied afterward.
TFR_EST_sde_handover_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        TFR_EST_complete_sde_handover = yes
        if = {
            limit = { TFR_EST_sde_handover_notice_eligible = yes }
            if = {
                limit = { NOT = { has_country_flag = TFR_EST_sde_handover_pending } }
                set_country_flag = { flag = TFR_EST_sde_handover_pending days = 2 }
                country_event = { id = tfr_estonia_sde_handover.1 hours = 1 }
            }
        }
        else = { clr_country_flag = TFR_EST_sde_handover_pending }
    }
}
'''
    events = '''add_namespace = tfr_estonia_sde_handover
country_event = {
    id = tfr_estonia_sde_handover.1
    title = TFR_EST_sde_handover_title
    desc = TFR_EST_sde_handover_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_sde_handover_notice_eligible = yes
        has_country_flag = TFR_EST_sde_handover_pending
    }
    immediate = {
        set_country_flag = TFR_EST_sde_handover_presented
        clr_country_flag = TFR_EST_sde_handover_pending
    }
    option = {
        name = TFR_EST_sde_handover_option
        custom_effect_tooltip = TFR_EST_sde_handover_tt
    }
}
'''
    loc = {
        'TFR_EST_lauri_laanemets': 'Lauri Läänemets',
        'TFR_EST_lauri_laanemets_desc': 'Lauri Läänemets succeeds Indrek Saar as Social Democratic Party chairman after the February 2022 congress. His experience includes local government, parliamentary constitutional work and the Defence League. He leads the cabinet when the Social Democrats supply the confirmed prime minister; the president retains the constitutional head-of-state role.',
        'TFR_EST_pm_sde_laanemets': '$TFR_EST_lauri_laanemets$',
        'TFR_EST_pm_sde_laanemets_desc': 'Prime Minister: §H$TFR_EST_lauri_laanemets$§!\n[TFR_EST_hog_cabinet_status]\n\n$TFR_EST_lauri_laanemets_desc$',
        'TFR_EST_hog_sde_laanemets': 'Prime Minister: §H$TFR_EST_lauri_laanemets$§!\n[TFR_EST_hog_cabinet_status]\n\n\n\n\n\n\n   £GFX_TFR_EST_hog_portrait_sde_laanemets\n\n\n\n\n\n\n\n\n-------------------------------------\n§L$TFR_EST_lauri_laanemets_desc$§!',
        'TFR_EST_sde_handover_title': 'Läänemets Leads the Social Democrats',
        'TFR_EST_sde_handover_desc': 'The Social Democrats have elected Lauri Läänemets to succeed Indrek Saar as party chairman. The new leader places affordable housing, accessible services, higher wages and a fairer tax system at the centre of his programme.\n\nThe congress determines the party leadership and its future candidate for prime minister. Existing parliamentary seats and coalition agreements continue. Another party’s prime minister remains in office; an outgoing Social Democratic caretaker serves until parliamentary cabinet confirmation.',
        'TFR_EST_sde_handover_option': 'The party enters a new chapter.',
        'TFR_EST_sde_handover_tt': '§YLauri Läänemets§! has succeeded §YIndrek Saar§! as Social Democratic Party chairman. Future Social Democratic governments are led by Läänemets. A confirmed Social Democratic cabinet changes prime minister; an outgoing caretaker awaits cabinet confirmation. Parliamentary seats, polls, ministers, coalition agreements and the election calendar are preserved.',
        'TFR_EST_sde_party_leader_tt': '§YSocial Democratic Party chair: [TFR_EST_sde_party_leader]§!\nParty leadership is separate from the parliamentary mandate and the current prime minister.',
    }
    localization = 'l_english:\n' + ''.join(f' {key}:0 {json.dumps(value, ensure_ascii=False)}\n' for key, value in loc.items())
    party_name = '''defined_text = {
    name = TFR_EST_sde_party_leader
    text = { trigger = { has_country_flag = TFR_EST_laanemets_leads_sde } localization_key = TFR_EST_lauri_laanemets }
    text = { trigger = { always = yes } localization_key = TFR_EST_indrek_saar }
}
'''
    return {
        'common/scripted_triggers/TFR_EST_sde_handover.txt': triggers,
        'common/scripted_effects/TFR_EST_sde_handover.txt': effects,
        'events/TFR_EST_sde_handover.txt': events,
        'localisation/english/TFR_EST_sde_handover_l_english.yml': localization,
        'common/scripted_localisation/TFR_EST_sde_handover.txt': party_name,
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
                raise SystemExit(f'Generated SDE handover differs: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('SDE leadership handover ' + ('verified.' if args.check else 'written.'))


if __name__ == '__main__':
    main()

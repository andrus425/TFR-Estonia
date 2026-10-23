"""Build Centre's September 2023 opposition leadership congress.

Historical anchors, distinct from the mod's alternate electoral outcomes:
https://vana.keskerakond.ee/et/meedia/3366-j%C3%BCri-ratase-k%C3%B5ne-eesti-keskerakonna-erakorralisel-kongressil.html
https://www.riigikogu.ee/pressiteated/riigikogu-juhatus-registreeris-kuus-fraktsiooni/

Ratas did not seek the chair at the 10 September congress. Kiik and Kolvart
were the two candidates; choosing Kiik is the playable alternate outcome.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEADERS = ('kiik', 'kolvart')
PEOPLE = {'kiik': 'tanel_kiik', 'kolvart': 'mihhail_kolvart'}


def outputs():
    triggers = '''# A valid 2023 defeat is recorded by the election commit hook. March's
# result does not change the party chair; the congress is held in September.
TFR_EST_centre_leadership_eligible = {
    TFR_EST_independent_parliament = yes
    has_country_flag = TFR_EST_centre_lost_2023_election
    NOT = { has_country_flag = TFR_EST_centre_won_2023_election }
    NOT = { has_country_flag = TFR_EST_centre_leadership_resolved }
    date > 2023.9.9
}
'''
    effects = '''# Party office and the incumbent prime minister are separate records. An
# opposition congress never changes the country's cabinet or parliamentary
# mandate. An outgoing Ratas caretaker waits for actual cabinet confirmation.
TFR_EST_reconcile_centre_pm_identity = {
    if = {
        limit = {
            TFR_EST_constitutional_executive = yes
            check_variable = { var = TFR_EST_pm_party value = 2 compare = equals }
        }
        if = {
            limit = { NOT = { has_country_flag = TFR_EST_caretaker } }
            clr_country_flag = TFR_EST_centre_leadership_waiting_confirmation
        }
        if = {
            limit = { NOT = { has_country_flag = TFR_EST_centre_leadership_waiting_confirmation } }
            if = {
                limit = { has_country_flag = TFR_EST_centre_leader_kiik }
                set_country_flag = TFR_EST_pm_person_tanel_kiik
                clr_country_flag = TFR_EST_pm_person_mihhail_kolvart
            }
            else_if = {
                limit = { has_country_flag = TFR_EST_centre_leader_kolvart }
                set_country_flag = TFR_EST_pm_person_mihhail_kolvart
                clr_country_flag = TFR_EST_pm_person_tanel_kiik
            }
            else = {
                clr_country_flag = TFR_EST_pm_person_tanel_kiik
                clr_country_flag = TFR_EST_pm_person_mihhail_kolvart
            }
        }
    }
    else = {
        clr_country_flag = TFR_EST_pm_person_tanel_kiik
        clr_country_flag = TFR_EST_pm_person_mihhail_kolvart
        if = {
            limit = { NOT = { check_variable = { var = TFR_EST_pm_party value = 2 compare = equals } } }
            clr_country_flag = TFR_EST_centre_leadership_waiting_confirmation
        }
    }
}

'''
    for leader in LEADERS:
        other = 'kolvart' if leader == 'kiik' else 'kiik'
        effects += f'''TFR_EST_choose_centre_leader_{leader} = {{
    if = {{
        limit = {{ TFR_EST_centre_leadership_eligible = yes }}
        set_country_flag = TFR_EST_centre_leadership_resolved
        set_country_flag = TFR_EST_centre_leader_{leader}
        clr_country_flag = TFR_EST_centre_leader_{other}
        clr_country_flag = TFR_EST_centre_leadership_pending
        if = {{
            limit = {{
                check_variable = {{ var = TFR_EST_pm_party value = 2 compare = equals }}
                has_country_flag = TFR_EST_caretaker
            }}
            set_country_flag = TFR_EST_centre_leadership_waiting_confirmation
        }}
        else = {{ clr_country_flag = TFR_EST_centre_leadership_waiting_confirmation }}
        TFR_EST_reconcile_centre_pm_identity = yes
        TFR_EST_reconcile_executive_display = yes
    }}
}}

'''
    effects += '''TFR_EST_centre_leadership_tick = {
    if = {
        limit = { tag = EST has_country_flag = TFR_EST_initialized }
        if = {
            limit = { TFR_EST_centre_leadership_eligible = yes }
            if = {
                limit = {
                    NOT = { has_country_flag = TFR_EST_centre_leadership_pending }
                    NOT = { has_country_flag = TFR_EST_centre_leadership_presented }
                }
                set_country_flag = { flag = TFR_EST_centre_leadership_pending days = 2 }
                country_event = { id = tfr_estonia_centre_leadership.1 hours = 1 }
            }
        }
        else = {
            clr_country_flag = TFR_EST_centre_leadership_pending
            if = {
                limit = { NOT = { has_country_flag = TFR_EST_centre_leadership_resolved } }
                clr_country_flag = TFR_EST_centre_leadership_presented
            }
        }
    }
}
'''
    events = '''add_namespace = tfr_estonia_centre_leadership
country_event = {
    id = tfr_estonia_centre_leadership.1
    title = TFR_EST_centre_congress_title
    desc = TFR_EST_centre_congress_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_centre_leadership_eligible = yes
        has_country_flag = TFR_EST_centre_leadership_pending
        NOT = { has_country_flag = TFR_EST_centre_leadership_presented }
    }
    immediate = {
        set_country_flag = TFR_EST_centre_leadership_presented
        clr_country_flag = TFR_EST_centre_leadership_pending
    }
    option = {
        name = TFR_EST_centre_congress_kiik
        ai_chance = { factor = 45 }
        custom_effect_tooltip = TFR_EST_centre_congress_kiik_tt
        hidden_effect = { TFR_EST_choose_centre_leader_kiik = yes }
    }
    option = {
        name = TFR_EST_centre_congress_kolvart
        ai_chance = { factor = 55 }
        custom_effect_tooltip = TFR_EST_centre_congress_kolvart_tt
        hidden_effect = { TFR_EST_choose_centre_leader_kolvart = yes }
    }
}
'''
    loc = {
        'TFR_EST_tanel_kiik': 'Tanel Kiik',
        'TFR_EST_tanel_kiik_desc': 'Tanel Kiik has served as social affairs minister, health and labour minister and Centre parliamentary group chairman. Elected party leader after its 2023 defeat, he seeks to rebuild national support through public services, parliamentary work and agreements with partners.',
        'TFR_EST_mihhail_kolvart': 'Mihhail Kõlvart',
        'TFR_EST_mihhail_kolvart_desc': "Mihhail Kõlvart succeeds Jüri Ratas following Centre's extraordinary leadership congress. He brings experience in municipal government and the party's local organisation. His appointment as prime minister requires a Centre-led government; party leadership alone does not confer control of the cabinet.",
        'TFR_EST_centre_congress_title': 'Centre Chooses a New Leader',
        'TFR_EST_centre_congress_desc': "Following Centre's defeat in the parliamentary election, delegates assemble for an extraordinary congress. Jüri Ratas is leaving the party chairmanship and will not stand again. The choice is between Tanel Kiik and Mihhail Kõlvart.\n\nKiik brings national cabinet and parliamentary experience, with Ratas backing his candidacy. Kõlvart calls for rebuilding the party through its local organisation and bringing its different supporters together. The delegates' decision selects Centre's future leader. It does not change the result of the Riigikogu election or transfer another party's premiership to Centre.",
        'TFR_EST_centre_congress_kiik': 'Elect Tanel Kiik.',
        'TFR_EST_centre_congress_kolvart': 'Elect Mihhail Kõlvart.',
        'TFR_EST_centre_party_leader_tt': '§YKeskerakond chair: [TFR_EST_centre_party_leader]§!\nParty leadership is separate from the parliamentary mandate and the current prime minister.',
    }
    for leader, person in PEOPLE.items():
        title = 'Tanel Kiik' if leader == 'kiik' else 'Mihhail Kõlvart'
        loc[f'TFR_EST_pm_centre_{leader}'] = f'$TFR_EST_{person}$'
        loc[f'TFR_EST_pm_centre_{leader}_desc'] = f'Prime Minister: §H$TFR_EST_{person}$§!\n[TFR_EST_hog_cabinet_status]\n\n$TFR_EST_{person}_desc$'
        loc[f'TFR_EST_hog_centre_{leader}'] = f'Prime Minister: §H$TFR_EST_{person}$§!\n[TFR_EST_hog_cabinet_status]\n\n\n\n\n\n\n   £GFX_TFR_EST_hog_portrait_centre_{leader}\n\n\n\n\n\n\n\n\n-------------------------------------\n§L$TFR_EST_{person}_desc$§!'
        loc[f'TFR_EST_centre_congress_{leader}_tt'] = f"§Y{title}§! becomes Centre's party leader and future candidate for prime minister. Preserve parliamentary seats, polls, coalition agreements, portfolio ministers and the election calendar. Another party's prime minister stays in office. An outgoing Centre caretaker stays until cabinet confirmation; a confirmed Centre-led government adopts its new party leader."
    localization = 'l_english:\n' + ''.join(f' {key}:0 {json.dumps(value, ensure_ascii=False)}\n' for key, value in loc.items())
    party_name = '''defined_text = {
    name = TFR_EST_centre_party_leader
    text = { trigger = { has_country_flag = TFR_EST_centre_leader_kiik } localization_key = TFR_EST_tanel_kiik }
    text = { trigger = { has_country_flag = TFR_EST_centre_leader_kolvart } localization_key = TFR_EST_mihhail_kolvart }
    text = { trigger = { always = yes } localization_key = TFR_EST_juri_ratas }
}
'''
    return {
        'common/scripted_triggers/TFR_EST_centre_leadership.txt': triggers,
        'common/scripted_effects/TFR_EST_centre_leadership.txt': effects,
        'events/TFR_EST_centre_leadership.txt': events,
        'localisation/english/TFR_EST_centre_leadership_l_english.yml': localization,
        'common/scripted_localisation/TFR_EST_centre_leadership.txt': party_name,
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
                raise SystemExit(f'Generated Centre leadership differs: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('Centre leadership congress ' + ('verified.' if args.check else 'written.'))


if __name__ == '__main__':
    main()

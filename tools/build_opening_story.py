"""Build the 2020 coalition rewards and guarded Porto Franco story controller."""
from pathlib import Path
import argparse
import json
from build_opening_content import POLICIES
from native_script_interface import amount_call
from focus_reward_model import OPENING_ECONOMIC, OPENING_MILITARY, modifier_reward, concise_trigger

ROOT = Path(__file__).resolve().parents[1]


def co(value):
    return amount_call('TFR_EST_change_cohesion', value)


def budget(value):
    return amount_call('TFR_EST_spend_budget', value)


def variable(name, value):
    return f'add_to_variable = {{ {name} = {value} }}'


def outputs():
    triggers = '''# Coalition seats are distinct from confidence-and-supply votes.
TFR_EST_coalition_majority = {
    TFR_EST_independent_parliament = yes
    check_variable = { var = TFR_EST_coalition_seats value = 51 compare = greater_than_or_equals }
}
TFR_EST_opening_resolved = {
    has_country_flag = TFR_EST_opening_complete
}
# A new valid assembly retires these 2019-government events even if an old
# popup is still open. Current party IDs cannot establish assembly identity.
TFR_EST_opening_assembly_current = {
    TFR_EST_independent_parliament = yes
    NOT = { has_country_flag = TFR_EST_opening_assembly_ended }
}
TFR_EST_opening_coalition_majority = {
    TFR_EST_opening_assembly_current = yes
    TFR_EST_coalition_majority = yes
    NOT = { has_country_flag = TFR_EST_caretaker }
    NOT = { has_country_flag = TFR_EST_opening_complete }
    check_variable = { var = TFR_EST_pm_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_mandate_party value = 2 compare = equals }
    check_variable = { var = TFR_EST_coalition_centre value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_ekre value = 1 compare = equals }
    check_variable = { var = TFR_EST_coalition_isamaa value = 1 compare = equals }
}
TFR_EST_can_start_referendum = {
    TFR_EST_opening_coalition_majority = yes
    NOT = { has_country_flag = TFR_EST_referendum_failed }
    # Even 14 saved focus days leave the focus running on 12 and 13 January.
    date > 2020.12.23
'''
    for policy in POLICIES[:-1]:
        triggers += f'''    OR = {{
        has_completed_focus = TFR_EST_opening_{policy.suffix}
        has_country_flag = TFR_EST_done_opening_{policy.suffix}
    }}
'''
    triggers += '}\n'
    triggers += '''TFR_EST_has_covid = {
    custom_trigger_tooltip = {
        tooltip = TFR_EST_has_covid_tt
        generic_has_corona = yes
    }
}
TFR_EST_referendum_available = {
    TFR_EST_opening_assembly_current = yes
    NOT = { has_country_flag = TFR_EST_referendum_failed }
    OR = {
        has_country_flag = TFR_EST_referendum_active
        TFR_EST_can_start_referendum = yes
    }
}
'''
    for name in ('TFR_EST_opening_coalition_majority', 'TFR_EST_can_start_referendum', 'TFR_EST_referendum_available'):
        triggers = concise_trigger(name, triggers)

    rewards = {
        'pension_reform': co(-1) + '\nadd_political_power = 40',
        'teacher_pay': budget(20) + '\n' + co(3),
        'covid_emergency': budget(25) + '\n' + co(3),
        'pension_increase': budget(20.8) + '\n' + co(4),
        'wage_compensation': budget(147.9) + '\n' + co(4),
        'excise_relief': budget(25),
        'eastern_border': budget(40) + '\n' + amount_call('TFR_EST_change_readiness', 6),
        'kose_voobu': budget(30),
        'three_seas': 'add_political_power = 40',
        'research_budget': budget(35),
    }
    effects = '# Rewards are called inside each focus\'s persistent once-only guard.\n'
    for suffix, reward in rewards.items():
        for group, mapping in (('economy', OPENING_ECONOMIC), ('military', OPENING_MILITARY)):
            preview = modifier_reward('TFR_EST_opening_' + suffix, group, mapping.get(suffix, ()))
            if preview:
                reward += '\n    ' + preview
        effects += f'''TFR_EST_opening_reward_{suffix} = {{
    hidden_effect = {{ TFR_EST_initialize_country_modifiers = yes }}
    {reward}
    hidden_effect = {{ TFR_EST_refresh_country_modifiers = yes }}
}}\n\n'''
    effects += '''TFR_EST_begin_covid_response = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            generic_has_corona = yes
            NOT = { has_country_flag = TFR_EST_opening_covid_announced }
        }
        set_country_flag = TFR_EST_opening_covid_announced
        country_event = { id = tfr_estonia_opening.1 }
    }
}

TFR_EST_begin_referendum = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            NOT = { has_country_flag = TFR_EST_done_opening_marriage_referendum }
            NOT = { has_country_flag = TFR_EST_referendum_failed }
        }
        set_country_flag = TFR_EST_referendum_active
        TFR_EST_opening_tick = yes
    }
}

# A successful bill or its explicit abandonment can end the opening stage.
# Abandonment never records referendum success or grants its completion reward.
TFR_EST_reveal_after_opening = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            has_country_flag = TFR_EST_porto_choice_resolved
            OR = {
                has_country_flag = TFR_EST_done_opening_marriage_referendum
                AND = {
                    has_country_flag = TFR_EST_referendum_failed
                    has_country_flag = TFR_EST_ratas_resigned
                }
            }
            NOT = { has_country_flag = TFR_EST_opening_complete }
        }
        set_country_flag = TFR_EST_opening_complete
        clr_country_flag = TFR_EST_referendum_active
        TFR_EST_refresh_focus_visibility = yes
    }
}
TFR_EST_finish_opening = {
    TFR_EST_reveal_after_opening = yes
    TFR_EST_opening_tick = yes
}

# Removing the availability condition aborts an active focus through the
# engine's native cancel_if_invalid handling. A delayed event choice can also
# arrive after native completion; undo only the abandoned referendum in that
# case, preserving all ten earlier policies and their persistent rewards.
TFR_EST_fail_referendum = {
    if = {
        limit = { TFR_EST_opening_assembly_current = yes }
        set_country_flag = TFR_EST_referendum_failed
        clr_country_flag = TFR_EST_referendum_active
        clr_country_flag = TFR_EST_done_opening_marriage_referendum
        if = {
            limit = { has_completed_focus = TFR_EST_opening_marriage_referendum }
            uncomplete_national_focus = {
                focus = TFR_EST_opening_marriage_referendum
                uncomplete_children = no
                refund_political_power = no
            }
        }
    }
}

# A narrative choice may restore the original 57-seat cabinet, never its seats.
TFR_EST_keep_ratas = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            has_country_flag = TFR_EST_porto_investigation_seen
            NOT = { has_country_flag = TFR_EST_porto_choice_resolved }
        }
        set_country_flag = TFR_EST_porto_choice_resolved
        set_country_flag = TFR_EST_ratas_retained
        set_country_flag = TFR_EST_scripted_cabinet_change
        TFR_EST_nominate_centre = yes
        set_variable = { TFR_EST_coalition_ekre = 1 }
        set_variable = { TFR_EST_coalition_isamaa = 1 }
        TFR_EST_recount_confidence = yes
        TFR_EST_confirm_cabinet = yes
        set_temp_variable = { var = TFR_EST_cohesion_delta value = -6 }
        TFR_EST_change_cohesion = yes
        TFR_EST_reveal_after_opening = yes
        TFR_EST_refresh_focus_visibility = yes
    }
}

# Ratas remains caretaker until a successor is confirmed by the same parliament.
TFR_EST_ratas_steps_back = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            has_country_flag = TFR_EST_porto_investigation_seen
            NOT = { has_country_flag = TFR_EST_porto_choice_resolved }
        }
        set_country_flag = TFR_EST_porto_choice_resolved
        set_country_flag = TFR_EST_ratas_resigned
        TFR_EST_fail_referendum = yes
        set_country_flag = TFR_EST_reform_handover_pending
        set_variable = { TFR_EST_reform_handover_days = 13 }
        TFR_EST_enter_caretaker = yes
        set_temp_variable = { var = TFR_EST_cohesion_delta value = -2 }
        TFR_EST_change_cohesion = yes
        TFR_EST_reveal_after_opening = yes
        TFR_EST_refresh_focus_visibility = yes
    }
}

TFR_EST_form_reform_centre_cabinet = {
    if = {
        limit = {
            TFR_EST_opening_assembly_current = yes
            has_country_flag = TFR_EST_reform_handover_pending
            NOT = { has_country_flag = TFR_EST_reform_centre_formed }
            NOT = { has_country_flag = TFR_EST_kallas_mandate_ended }
        }
        set_country_flag = TFR_EST_scripted_cabinet_change
        TFR_EST_nominate_reform = yes
        set_variable = { TFR_EST_coalition_centre = 1 }
        TFR_EST_recount_confidence = yes
        TFR_EST_confirm_cabinet = yes
        if = {
            limit = {
                check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
                NOT = { has_country_flag = TFR_EST_caretaker }
            }
            set_country_flag = TFR_EST_reform_centre_formed
            clr_country_flag = TFR_EST_reform_handover_pending
            TFR_EST_refresh_focus_visibility = yes
        }
    }
}

TFR_EST_opening_tick = {
    if = {
        limit = { TFR_EST_opening_assembly_current = yes }
        if = {
            limit = {
                has_country_flag = TFR_EST_reform_handover_pending
                check_variable = { var = TFR_EST_pm_party value = 1 compare = equals }
                NOT = { has_country_flag = TFR_EST_caretaker }
            }
            set_country_flag = TFR_EST_reform_centre_formed
            clr_country_flag = TFR_EST_reform_handover_pending
        }
        if = {
            limit = {
                has_country_flag = TFR_EST_referendum_active
                date > 2021.1.11
                NOT = { has_country_flag = TFR_EST_porto_investigation_seen }
                NOT = { has_country_flag = TFR_EST_porto_notice_pending }
            }
            # Short-lived queue guards recover if occupation drops a queued event.
            set_country_flag = { flag = TFR_EST_porto_notice_pending days = 2 }
            country_event = { id = tfr_estonia_opening.10 }
        }
        if = {
            limit = {
                has_country_flag = TFR_EST_porto_investigation_seen
                NOT = { has_country_flag = TFR_EST_porto_choice_resolved }
                NOT = { has_country_flag = TFR_EST_porto_choice_presented }
                NOT = { has_country_flag = TFR_EST_porto_choice_pending }
            }
            set_country_flag = { flag = TFR_EST_porto_choice_pending days = 3 }
            country_event = { id = tfr_estonia_opening.11 days = 1 }
        }
        if = {
            limit = { has_country_flag = TFR_EST_reform_handover_pending }
            if = {
                limit = { check_variable = { var = TFR_EST_reform_handover_days value = 0 compare = greater_than } }
                subtract_from_variable = { TFR_EST_reform_handover_days = 1 }
            }
            if = {
                limit = {
                    check_variable = { var = TFR_EST_reform_handover_days value = 0 compare = less_than_or_equals }
                    NOT = { has_country_flag = TFR_EST_new_cabinet_notice_presented }
                    NOT = { has_country_flag = TFR_EST_new_cabinet_notice_pending }
                }
                set_country_flag = { flag = TFR_EST_new_cabinet_notice_pending days = 3 }
                country_event = { id = tfr_estonia_opening.12 }
            }
        }
        TFR_EST_reveal_after_opening = yes
    }
}
'''
    events = '''add_namespace = tfr_estonia_opening
country_event = {
    id = tfr_estonia_opening.1
    title = TFR_EST_opening_covid_title
    desc = TFR_EST_opening_covid_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    option = { name = TFR_EST_opening_covid_option }
}
country_event = {
    id = tfr_estonia_opening.10
    title = TFR_EST_porto_investigation_title
    desc = TFR_EST_porto_investigation_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_opening_assembly_current = yes
        has_country_flag = TFR_EST_referendum_active
        NOT = { has_country_flag = TFR_EST_porto_investigation_seen }
    }
    immediate = {
        set_country_flag = TFR_EST_porto_investigation_seen
        clr_country_flag = TFR_EST_porto_notice_pending
    }
    option = {
        name = TFR_EST_porto_investigation_option
        TFR_EST_opening_tick = yes
    }
}
country_event = {
    id = tfr_estonia_opening.11
    title = TFR_EST_porto_choice_title
    desc = TFR_EST_porto_choice_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_opening_assembly_current = yes
        has_country_flag = TFR_EST_porto_investigation_seen
        NOT = { has_country_flag = TFR_EST_porto_choice_resolved }
        NOT = { has_country_flag = TFR_EST_porto_choice_presented }
    }
    immediate = { set_country_flag = TFR_EST_porto_choice_presented }
    option = {
        name = TFR_EST_porto_keep_ratas
        ai_chance = { factor = 20 }
        custom_effect_tooltip = TFR_EST_keep_ratas_tt
        TFR_EST_keep_ratas = yes
    }
    option = {
        name = TFR_EST_porto_step_back
        ai_chance = { factor = 80 }
        custom_effect_tooltip = TFR_EST_step_back_tt
        TFR_EST_ratas_steps_back = yes
    }
}
country_event = {
    id = tfr_estonia_opening.12
    title = TFR_EST_reform_centre_title
    desc = TFR_EST_reform_centre_desc
    picture = GFX_report_event_generic_handshake
    is_triggered_only = yes
    trigger = {
        TFR_EST_opening_assembly_current = yes
        has_country_flag = TFR_EST_reform_handover_pending
        NOT = { has_country_flag = TFR_EST_reform_centre_formed }
        NOT = { has_country_flag = TFR_EST_kallas_mandate_ended }
        NOT = { has_country_flag = TFR_EST_new_cabinet_notice_presented }
    }
    immediate = { set_country_flag = TFR_EST_new_cabinet_notice_presented }
    option = {
        name = TFR_EST_reform_centre_option
        custom_effect_tooltip = TFR_EST_reform_centre_tt
        TFR_EST_form_reform_centre_cabinet = yes
    }
}
'''
    loc = {
        'TFR_EST_opening_coalition_majority_tt': 'Centre–Isamaa–EKRE cabinet with at least 51 coalition seats.',
        'TFR_EST_can_start_referendum_tt': 'Complete the opening programme; retain 51 coalition seats; 24 December 2020 or later.',
        'TFR_EST_referendum_available_tt': 'Complete the opening programme; retain 51 coalition seats; 24 December 2020 or later. Once begun, continues unless Ratas steps back.',
        'TFR_EST_has_covid_tt': 'COVID-19 cases are present in Estonia.',
        'TFR_EST_ratas_governing_tt': 'Ratas leads the Centre–Isamaa–EKRE cabinet with at least 51 coalition seats.',
        'TFR_EST_kallas_governing_tt': 'Kallas leads a confirmed Reform–Centre cabinet with at least 51 coalition seats.',
        'TFR_EST_ratas_all_policies_done_tt': 'Complete the other 19 coalition programme focuses.',
        'TFR_EST_kallas_all_policies_done_tt': 'Complete the other 19 government programme focuses.',
        'TFR_EST_energy_one_stage_tt': 'Advance recovery from §YThe Oil Crash§! by §G1 stage§! (5 stages remove the spirit). Preparation also applies if the crisis begins later.',
        'TFR_EST_energy_two_stages_tt': 'Advance recovery from §YThe Oil Crash§! by §G2 stages§! (5 stages remove the spirit). Preparation also applies if the crisis begins later.',
        'TFR_EST_opening_covid_title': 'The COVID-19 Emergency',
        'TFR_EST_opening_covid_desc': 'The government has declared an emergency situation in response to COVID-19. Schools must move to distance learning, public gatherings face restrictions, and hospitals need coordinated supplies. The cabinet must work with local authorities while the Riigikogu continues to scrutinize emergency powers. Wage compensation and tax relief will require separate funding decisions.',
        'TFR_EST_opening_covid_option': 'Put the emergency orders into effect.',
        'TFR_EST_porto_investigation_title': 'The Porto Franco Investigation',
        'TFR_EST_porto_investigation_desc': 'Prosecutors and the Internal Security Service have announced corruption suspicions connected to the Porto Franco development. The reported allegations concern party donations and access-road arrangements, alongside a separate suspected attempt to obtain favourable decisions on crisis lending. Centre secretary-general Mihhail Korb and Finance Minister Martin Helme\'s adviser Kersti Kracht are among those named by investigators.\n\nThese are allegations under investigation, not findings of guilt. Jüri Ratas has not been personally named as a suspect in this announcement. Nevertheless, the cabinet faces a political crisis while parliament debates the marriage referendum bill.',
        'TFR_EST_porto_investigation_option': 'Convene the coalition leaders.',
        'TFR_EST_porto_choice_title': 'Ratas Must Decide',
        'TFR_EST_porto_choice_desc': 'The prime minister must decide whether taking political responsibility requires his resignation. Remaining in office would require Centre, Isamaa and EKRE to renew their support while the investigation proceeds independently. Stepping back would leave Ratas leading a caretaker administration as a successor is negotiated in the existing Riigikogu.\n\nResignation automatically fails the marriage-referendum focus and abandons the proposal. Reform and Centre would negotiate a government under Kaja Kallas. The cabinet change does not require an election.',
        'TFR_EST_porto_keep_ratas': 'Ratas stays; renew the coalition agreement.',
        'TFR_EST_porto_step_back': 'Ratas takes political responsibility and steps back.',
        'TFR_EST_keep_ratas_tt': 'Ratas remains prime minister of the Centre–Isamaa–EKRE cabinet. Renew its parliamentary support and lose 6 cohesion. Reveal the coalition agreement programme through the March 2023 election. Its first focus requires the active referendum focus to finish; the referendum proposal remains the responsibility of this government.',
        'TFR_EST_step_back_tt': 'Ratas resigns and remains caretaker until a successor is confirmed. Lose 2 cohesion. Automatically fail the marriage-referendum focus and reveal Kaja Kallas\'s government programme. Reform and Centre will negotiate a cabinet in the existing parliament over the next 13 days; its focuses require confirmation. Preserve all earlier policies and their rewards. No election is called.',
        'TFR_EST_reform_centre_title': 'A Reform–Centre Cabinet',
        'TFR_EST_reform_centre_desc': 'Reform and Centre have agreed to form a government under Kaja Kallas. Their original parliamentary delegations hold 60 of the 101 seats. Kersti Kaljulaid remains president, while Ratas hands over the prime minister\'s office after confirmation. This is a cabinet change within the existing assembly. The outgoing coalition\'s marriage-referendum proposal will not proceed.',
        'TFR_EST_reform_centre_option': 'Confirm the new cabinet in the Riigikogu.',
        'TFR_EST_reform_centre_tt': 'Confirm Kaja Kallas if Reform and Centre provide at least 51 confidence votes. Preserve parliamentary seats, polls and the March 2023 election calendar. Her government can now begin its programme, while the abandoned marriage referendum remains failed.',
    }
    loc_text = 'l_english:\n' + ''.join(f' {key}:0 {json.dumps(value, ensure_ascii=False)}\n' for key, value in loc.items())
    return {
        'common/scripted_triggers/TFR_EST_opening.txt': triggers,
        'common/scripted_effects/TFR_EST_opening.txt': effects,
        'events/TFR_EST_opening.txt': events,
        'localisation/english/TFR_EST_opening_events_l_english.yml': loc_text,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for relative, content in outputs().items():
        path = ROOT / relative
        encoding = 'utf-8-sig' if path.suffix == '.yml' else 'utf-8'
        data = content.encode(encoding)
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'Generated opening story differs: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('Opening coalition rewards, controller, four events and localization ' + ('verified.' if args.check else 'written.'))


if __name__ == '__main__':
    main()

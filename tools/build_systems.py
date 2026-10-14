"""Generate Estonia's shared mechanics, lifecycle and native decisions.

Run from any directory with Python 3. This only writes our additive systems files.
Budget temporary-variable inputs are millions; TFR's debt ledger uses billions.
"""
from pathlib import Path
import textwrap
from native_script_interface import native_amount_calls

ROOT = Path(__file__).resolve().parents[1]
LOC = {}


def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native_amount_calls(textwrap.dedent(content).strip()) + "\n", encoding="utf-8")


def loc(key, title, desc=None):
    LOC[key] = title
    if desc is not None:
        LOC[key + "_desc"] = desc


def main():
    effects = '''
    # Public API. All callers operate in EST country scope.
    TFR_EST_change_cohesion = {
        add_to_variable = { var = TFR_EST_cohesion value = TFR_EST_cohesion_delta }
        clamp_variable = { var = TFR_EST_cohesion min = 0 max = 100 }
        TFR_EST_refresh_meters = yes
    }
    TFR_EST_change_readiness = {
        add_to_variable = { var = TFR_EST_readiness value = TFR_EST_readiness_delta }
        clamp_variable = { var = TFR_EST_readiness min = 0 max = 100 }
        TFR_EST_refresh_meters = yes
    }
    TFR_EST_spend_budget = {
        custom_effect_tooltip = TFR_EST_budget_cost_tt
        hidden_effect = {
            set_temp_variable = { var = debt_var_temp value = TFR_EST_budget_cost }
            multiply_temp_variable = { var = debt_var_temp value = 0.001 }
            add_debt_with_inflation = yes
        }
    }
    TFR_EST_initialize_systems = {
        if = {
            limit = { NOT = { has_country_flag = TFR_EST_initialized } }
            set_country_flag = TFR_EST_initialized
            clr_country_flag = TFR_EST_init_pending
            set_variable = { TFR_EST_cohesion = 55 }
            set_variable = { TFR_EST_readiness = 25 }
            set_variable = { TFR_EST_campaign_stage = 0 }
            set_variable = { TFR_EST_cohesion_weekly = 0 }
            set_variable = { TFR_EST_readiness_weekly = 0 }
            TFR_EST_initialize_parliament = yes
            TFR_EST_refresh_meters = yes
            TFR_EST_initialize_country_modifiers = yes
            TFR_EST_reconcile_campaign = yes
            log = "TFR Estonia: initialized 2020 government, parliament and national systems."
            if = {
                limit = { is_ai = no }
                country_event = { id = tfr_estonia_systems.2 days = 1 }
            }
        }
    }
    TFR_EST_reconcile_campaign = {
        # Occupation owns tree selection while the occupied flag is present.
        if = {
            limit = { has_global_flag = SOV_nato_war_begins_global }
            set_country_flag = TFR_EST_first_war_seen
        }
        if = {
            limit = { has_global_flag = second_nato_war_flag }
            set_country_flag = TFR_EST_second_war_seen
        }
        if = {
            limit = { has_country_flag = TFR_EST_second_war_seen }
            if = {
                limit = { OR = { has_war = yes SOV = { has_war_with = GER } GER = { has_war_with = SOV } } }
                set_variable = { TFR_EST_campaign_stage = 3 }
            }
            else = { set_variable = { TFR_EST_campaign_stage = 4 } }
        }
        else_if = {
            limit = { has_country_flag = TFR_EST_first_war_seen }
            if = {
                limit = { OR = { has_war = yes SOV = { has_war_with = GER } GER = { has_war_with = SOV } } }
                set_variable = { TFR_EST_campaign_stage = 1 }
            }
            else = { set_variable = { TFR_EST_campaign_stage = 2 } }
        }
        if = {
            limit = {
                NOT = { has_country_flag = TFR_EST_occupied }
                is_subject = no
                NOT = { has_focus_tree = TFR_EST_main_tree }
            }
            load_focus_tree = { tree = TFR_EST_main_tree keep_completed = yes }
        }
    }
    TFR_EST_weekly_systems = {
        set_variable = { TFR_EST_cohesion_weekly = 0 }
        set_variable = { TFR_EST_readiness_weekly = 0 }
        if = {
            limit = { has_country_flag = TFR_EST_caretaker }
            add_to_variable = { TFR_EST_cohesion_weekly = -0.5 }
        }
        if = {
            limit = { has_war = yes }
            add_to_variable = { TFR_EST_cohesion_weekly = -0.15 }
            add_to_variable = { TFR_EST_readiness_weekly = -0.20 }
        }
        if = {
            limit = { has_country_flag = TFR_EST_consultation_active }
            add_to_variable = { TFR_EST_cohesion_weekly = 0.75 }
        }
        if = {
            limit = { has_country_flag = TFR_EST_exercises_active }
            add_to_variable = { TFR_EST_readiness_weekly = 1.25 }
        }
        if = {
            limit = { has_country_flag = TFR_EST_relief_active }
            add_to_variable = { TFR_EST_cohesion_weekly = 0.50 }
        }
        add_to_variable = { var = TFR_EST_cohesion value = TFR_EST_cohesion_weekly }
        add_to_variable = { var = TFR_EST_readiness value = TFR_EST_readiness_weekly }
        clamp_variable = { var = TFR_EST_cohesion min = 0 max = 100 }
        clamp_variable = { var = TFR_EST_readiness min = 0 max = 100 }
        TFR_EST_refresh_meters = yes
        TFR_EST_parliament_tick = yes
        TFR_EST_content_tick = yes
        if = {
            limit = { has_country_flag = TFR_EST_occupied }
            TFR_EST_occupation_weekly = yes
        }
        if = {
            limit = { is_ai = yes TFR_EST_can_mobilize = yes }
            TFR_EST_mobilize_reserves = yes
        }
    }
    TFR_EST_lift_nato_restrictions = {
        if = {
            limit = {
                NOT = { has_country_flag = TFR_EST_nato_restrictions_lifted }
                NOT = { has_country_flag = TFR_EST_occupied }
                OR = { has_war = yes check_variable = { TFR_EST_readiness > 49 } }
            }
            set_country_flag = TFR_EST_nato_restrictions_lifted
            remove_ideas = NATO_anti_militarists_idea
            remove_ideas = NATO_anti_militarists_idea1
            add_ideas = TFR_EST_defense_commitment
            custom_effect_tooltip = TFR_EST_nato_restrictions_tt
        }
    }
    TFR_EST_mobilize_reserves = {
        if = {
            limit = { TFR_EST_can_mobilize = yes }
            set_country_flag = TFR_EST_reserves_mobilized
            division_template = {
                name = "Kaitseliidu reservbrigaad"
                regiments = {
                    militia = { x = 0 y = 0 }
                    militia = { x = 0 y = 1 }
                }
            }
            add_timed_idea = { idea = TFR_EST_reserve_training days = 90 }
            TFR_EST_lift_nato_restrictions = yes
            custom_effect_tooltip = TFR_EST_reserve_template_tt
        }
    }
    '''
    tiers = {
        "cohesion": [("fragile", {"stability_factor": -0.10, "political_power_gain": -0.10}),
                     ("divided", {"stability_factor": -0.04}),
                     ("functional", {"political_power_gain": 0.05}),
                     ("united", {"stability_factor": 0.05, "political_power_gain": 0.10})],
        "readiness": [("unprepared", {"mobilization_speed": -0.15}),
                      ("developing", {"mobilization_speed": 0.05}),
                      ("prepared", {"mobilization_speed": 0.10, "army_core_defence_factor": 0.03}),
                      ("resilient", {"mobilization_speed": 0.15, "army_core_defence_factor": 0.06, "dig_in_speed_factor": 0.10})],
    }
    refresh = ["TFR_EST_refresh_meters = {"]
    idea_blocks = []
    for meter, entries in tiers.items():
        for index, (name, modifiers) in enumerate(entries):
            conditions = []
            if index:
                conditions.append(f"check_variable = {{ TFR_EST_{meter} > {index * 25 - 1} }}")
            if index < 3:
                conditions.append(f"check_variable = {{ TFR_EST_{meter} < {(index + 1) * 25} }}")
            id_ = f"TFR_EST_{meter}_{name}"
            refresh += ["    if = {", "        limit = { " + " ".join(conditions) + " }",
                        "        if = {", f"            limit = {{ NOT = {{ has_idea = {id_} }} }}"]
            refresh += [f"            remove_ideas = TFR_EST_{meter}_{other}" for other, _ in entries]
            refresh += [f"            add_ideas = {id_}", "        }", "    }"]
            mods = " ".join(f"{k} = {v}" for k, v in modifiers.items())
            idea_blocks.append(f"    {id_} = {{ picture = generic_political_disaster allowed = {{ original_tag = EST }} removal_cost = -1 modifier = {{ {mods} }} }}")
            loc(id_, ("National Cohesion: " if meter == "cohesion" else "Defense Readiness: ") + name.title(),
                f"The current {meter} tier is derived from the national meter. Thresholds are 25, 50 and 75; focuses and decisions can improve it. This spirit is refreshed automatically when the meter crosses a threshold.")
    refresh += ["}"]
    write("common/scripted_effects/TFR_EST_systems.txt", effects + "\n" + "\n".join(refresh))
    write("common/scripted_triggers/TFR_EST_systems.txt", '''
    TFR_EST_can_mobilize = {
        original_tag = EST
        is_subject = no
        NOT = { has_country_flag = TFR_EST_occupied }
        NOT = { has_country_flag = TFR_EST_reserves_mobilized }
        13 = { is_owned_by = EST is_controlled_by = EST }
        OR = { has_war = yes check_variable = { TFR_EST_readiness > 49 } }
    }
    TFR_EST_independent_politics = {
        original_tag = EST
        has_country_flag = TFR_EST_initialized
        is_subject = no
        NOT = { has_country_flag = TFR_EST_occupied }
    }
    ''')
    write("common/on_actions/TFR_EST_systems.txt", '''
    on_actions = {
        on_startup = {
            effect = {
                EST = {
                    if = {
                        limit = { country_exists = EST NOT = { has_country_flag = TFR_EST_initialized } }
                        set_country_flag = TFR_EST_init_pending
                        country_event = { id = tfr_estonia_systems.1 days = 1 }
                    }
                }
            }
        }
        on_daily_EST = {
            effect = {
                if = {
                    limit = { has_country_flag = TFR_EST_initialized }
                    TFR_EST_reconcile_occupation = yes
                    TFR_EST_reconcile_campaign = yes
                    TFR_EST_initialize_country_modifiers = yes
                    TFR_EST_opening_tick = yes
                    TFR_EST_refresh_focus_visibility = yes
                }
            }
        }
        on_weekly_EST = {
            effect = {
                if = {
                    limit = { has_country_flag = TFR_EST_initialized }
                    TFR_EST_weekly_systems = yes
                }
            }
        }
    }
    ''')
    extra_ideas = '''
    TFR_EST_defense_commitment = {
        picture = generic_military_org
        allowed = { original_tag = EST }
        removal_cost = -1
        modifier = { mobilization_speed = 0.05 }
    }
    TFR_EST_reserve_training = {
        picture = generic_military_org
        allowed = { original_tag = EST }
        removal_cost = -1
        modifier = { training_time_army_factor = -0.10 }
    }
    '''
    loc("TFR_EST_defense_commitment", "A Credible Defense Commitment", "Estonia has replaced peacetime restraint with a funded defense program. Parent NATO production restrictions have been lifted for Estonia only.")
    loc("TFR_EST_reserve_training", "Reserve Assembly and Training", "A limited training program prepares Kaitseliit reserve brigades. Recruit them through the division designer and deployment screen; equipment and manpower are consumed normally.")
    write("common/ideas/TFR_EST_systems.txt", "ideas = { country = {\n" + "\n".join(idea_blocks) + extra_ideas + "\n} }")
    write("events/TFR_EST_systems.txt", '''
    add_namespace = tfr_estonia_systems
    country_event = {
        id = tfr_estonia_systems.1
        hidden = yes
        is_triggered_only = yes
        immediate = { TFR_EST_initialize_systems = yes }
    }
    country_event = {
        id = tfr_estonia_systems.2
        title = TFR_EST_welcome_title
        desc = TFR_EST_welcome_desc
        picture = GFX_report_event_generic_parliament
        is_triggered_only = yes
        option = { name = TFR_EST_welcome_option }
    }
    ''')
    loc("TFR_EST_welcome_title", "A Republic on the Baltic Frontier")
    loc("TFR_EST_welcome_desc", "Jüri Ratas enters 2020 at the head of a 57-seat Centre–EKRE–Isamaa coalition. President Kersti Kaljulaid remains the head of state. Beyond the cabinet, the Riigikogu, public confidence and the Defense Forces will determine how Estonia meets the crisis ahead.\n\nUse the Riigikogu decisions to manage your coalition and contest elections. National cohesion and defense readiness are shown in their own decision categories. These meters complement TFR's existing economy, NATO and EU systems.\n\nIf Estonia loses a supported European-war settlement, its campaign continues under an occupation administration retaining Northern Estonia. Government and election content returns after restoration.")
    loc("TFR_EST_welcome_option", "The republic must endure.")
    categories = []
    decisions = {}
    for name in ("cohesion", "readiness"):
        cat = f"TFR_EST_{name}_category"
        categories.append(f"{cat} = {{ icon = generic_political_actions priority = 95 allowed = {{ original_tag = EST }} visible = {{ has_country_flag = TFR_EST_initialized }} visible_when_empty = yes }}")
        decisions[cat] = []
    loc("TFR_EST_cohesion_category", "National Cohesion", "Cohesion: §Y[?TFR_EST_cohesion|1]/100§!\nNet weekly change: §Y[?TFR_EST_cohesion_weekly|2]§!\n\nTiers: fragile below 25; divided at 25; functional at 50; united at 75. Caretaker government reduces cohesion by 0.50 each week; war reduces it by 0.15. Community consultation adds 0.75 and emergency relief adds 0.50 while their programs run.\n\nOccupation changes which measures are permitted. Cohesion measures trust in institutions and civil resilience across the whole population.")
    loc("TFR_EST_readiness_category", "Defense Readiness", "Readiness: §Y[?TFR_EST_readiness|1]/100§!\nNet weekly change: §Y[?TFR_EST_readiness_weekly|2]§!\n\nTiers: unprepared below 25; developing at 25; prepared at 50; resilient at 75. War consumes 0.20 readiness weekly. Reserve exercises add 1.25 each week during their program.\n\nAt 50 readiness, or during war, independent Estonia can authorize reserve recruitment. Units still require ordinary equipment, manpower and training. Allied brigades are separate from this program.")
    specs = [
        ("cohesion", "community_consultation", "Community Consultation", "Hold regional meetings and commission practical service improvements. The four-week program adds 0.75 cohesion each week.", 35, 28, 56, "TFR_EST_consultation_active", 25, "", 10),
        ("cohesion", "emergency_relief", "Fund Emergency Relief", "Support displaced families and keep essential municipal services running. The four-week program adds 0.50 cohesion each week.", 40, 28, 90, "TFR_EST_relief_active", 40, "OR = { has_war = yes has_country_flag = TFR_EST_occupied }", 8),
        ("readiness", "reserve_drills", "Conduct Local Reserve Exercises", "Bring local commanders, reservists and municipal planners together. The four-week program adds 1.25 readiness each week.", 40, 28, 56, "TFR_EST_exercises_active", 30, "NOT = { has_country_flag = TFR_EST_occupied }", 12),
    ]
    for meter, suffix, title, desc, pp, days, cooldown, flag, budget, visible, weight in specs:
        id_ = "TFR_EST_" + suffix
        decisions[f"TFR_EST_{meter}_category"].append(f'''
        {id_} = {{
            icon = generic_political_discourse
            cost = {pp}
            days_remove = {days}
            days_re_enable = {cooldown}
            visible = {{ {visible} }}
            available = {{ NOT = {{ has_country_flag = {flag} }} }}
            complete_effect = {{
                TFR_EST_spend_budget = {{ AMOUNT = {budget} }}
                set_country_flag = {{ flag = {flag} days = {days} }}
            }}
            remove_effect = {{ clr_country_flag = {flag} }}
            ai_will_do = {{ factor = {weight} }}
        }}
        ''')
        loc(id_, title, desc + f"\n\nBudget: €{budget} million, financed through TFR's inflation-adjusted debt ledger.")
    decisions["TFR_EST_readiness_category"].append('''
    TFR_EST_authorize_reserves = {
        icon = generic_military
        cost = 60
        fire_only_once = yes
        visible = { NOT = { has_country_flag = TFR_EST_reserves_mobilized } NOT = { has_country_flag = TFR_EST_occupied } }
        available = { TFR_EST_can_mobilize = yes }
        complete_effect = { TFR_EST_spend_budget = { AMOUNT = 50 } TFR_EST_mobilize_reserves = yes }
        ai_will_do = { factor = 30 }
    }
    TFR_EST_defense_procurement = {
        icon = generic_military_support
        cost = 45
        days_re_enable = 180
        visible = { NOT = { has_country_flag = TFR_EST_occupied } }
        available = { 13 = { is_owned_by = EST is_controlled_by = EST } }
        complete_effect = {
            TFR_EST_spend_budget = { AMOUNT = 90 }
            TFR_EST_change_readiness = { AMOUNT = 3 }
            add_equipment_to_stockpile = { type = infantry_equipment amount = 500 producer = EST }
            add_equipment_to_stockpile = { type = support_equipment amount = 50 producer = EST }
        }
        ai_will_do = { factor = 12 modifier = { factor = 2 has_war = yes } }
    }
    TFR_EST_fortify_tallinn = {
        icon = generic_military
        cost = 50
        fire_only_once = yes
        visible = { NOT = { has_country_flag = TFR_EST_occupied } }
        available = { 13 = { is_owned_by = EST is_controlled_by = EST } }
        complete_effect = {
            TFR_EST_spend_budget = { AMOUNT = 75 }
            TFR_EST_change_readiness = { AMOUNT = 5 }
            13 = { add_building_construction = { type = bunker level = 1 province = 3152 instant_build = yes } }
        }
        ai_will_do = { factor = 15 }
    }
    ''')
    loc("TFR_EST_authorize_reserves", "Authorize Kaitseliit Reserve Recruitment", "Unlock a two-battalion reserve template and a 90-day training program. This does not create free divisions: recruit the brigades normally. Requires independent Estonia, control of Northern Estonia, and either 50 readiness or an active war.\n\nBudget: €50 million.")
    loc("TFR_EST_defense_procurement", "A Limited Defense Procurement Package", "Purchase 500 infantry equipment and 50 support equipment through a funded contract. Readiness increases by 3. Each contract costs €90 million; another can be approved after 180 days.")
    loc("TFR_EST_fortify_tallinn", "Prepare Tallinn's Defensive Belt", "Build one additional level of land fortifications at Tallinn and improve readiness by 5. The €75 million project can be authorized once.")
    loc("TFR_EST_budget_cost_tt", "The project is financed through TFR's inflation-adjusted public debt ledger; budget figures are in millions of euros.")
    loc("TFR_EST_nato_restrictions_tt", "Replace Estonia's inherited NATO peacetime military restrictions with its funded defense commitment. Other NATO countries are unaffected.")
    loc("TFR_EST_reserve_template_tt", "Unlock the Kaitseliidu reservbrigaad template and a temporary reserve-training bonus. Train units through normal recruitment; no soldiers or equipment are created by this authorization.")
    write("common/decisions/categories/TFR_EST_systems.txt", "\n\n".join(categories))
    write("common/decisions/TFR_EST_systems.txt", "\n".join(cat + " = {\n" + "\n".join(items) + "\n}" for cat, items in decisions.items()))
    path = ROOT / "localisation/english/TFR_EST_systems_l_english.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    def quote(s):
        return s.replace('"', "'").replace("\n", "\\n")
    path.write_text("l_english:\n" + "\n".join(f' {k}:0 "{quote(v)}"' for k, v in LOC.items()) + "\n", encoding="utf-8-sig")
    print("Generated shared Estonia systems, lifecycle, decisions and localization.")


if __name__ == "__main__":
    main()

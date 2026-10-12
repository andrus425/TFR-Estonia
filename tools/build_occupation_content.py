"""Generate deterministic, English-localized occupation content (no parent edits)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_occupation_"
LOC = {
    "TFR_EST_autonomy_occupation": "Protected occupation administration",
    "TFR_EST_autonomy_occupation_desc": "Estonia's civilian administration retains Northern Estonia throughout supported settlements. Ordinary autonomy changes cannot annex this country. Sovereignty returns through a liberation settlement or the restoration compact.",
    "TFR_EST_communist_council": "Estonian Reconstruction Council",
    "TFR_EST_military_council": "Estonian Security Directorate",
    "TFR_EST_eurasian_council": "Estonian Eurasian Council",
    "TFR_EST_baltic_council": "Estonian Baltic Administration",
    "TFR_EST_european_authority": "Estonian Occupation Authority",
    "TFR_EST_civil_administration": "Estonian Civil Administration",
    "TFR_EST_occupation_category": "Estonia under occupation",
    "TFR_EST_occupation_category_desc": "Normal parliamentary elections are suspended. Our administration remains playable in Northern Estonia.\n\nWeeks under the current settlement: [?TFR_EST_occupation_weeks|0]\nAdministrative cooperation: [?TFR_EST_occupation_cooperation|0]/100\nRestoration networks: [?TFR_EST_occupation_resistance|0]/100\n\nCollaboration or clandestine organization adds 0.5 points each week to its corresponding track. A liberal or supervised administration may negotiate independence after 52 weeks with 60 cooperation, 60 cohesion and 40 readiness. Other administrations require the patron's military collapse. Territorial recovery follows the wider peace settlement.",
    "TFR_EST_occupation_mandate": "Restricted Sovereignty",
    "TFR_EST_occupation_mandate_desc": "The occupying power controls foreign policy and national elections. A protected administration in Tallinn provides a continuous government, but public authority and military recruitment remain constrained.",
    "TFR_EST_occupation_local_services": "Municipal Continuity",
    "TFR_EST_occupation_local_services_desc": "Civil registries, schools and emergency services operate across our remaining territory even while constitutional politics are suspended.",
    "TFR_EST_occupation_recovery": "Reconstruction Directorate",
    "TFR_EST_occupation_recovery_desc": "Repair crews prioritize infrastructure and restart civilian production. The directorate survives a change of administration because the recovered expertise belongs to Estonia.",
    "TFR_EST_occupation_limited_forces": "Limited Territorial Forces",
    "TFR_EST_occupation_limited_forces_desc": "A negotiated mandate permits a small local security and defense force. Units still require Estonia's manpower, equipment and training.",
    "TFR_EST_occupation_collaboration": "Administrative Accommodation",
    "TFR_EST_occupation_collaboration_desc": "Officials cooperate with the patron to preserve services and obtain concessions. Cooperation rises by 0.5 each week; this arrangement does not itself restore elected government.",
    "TFR_EST_occupation_clandestine_network": "Restoration Networks",
    "TFR_EST_occupation_clandestine_network_desc": "Civil networks preserve independent institutions and records. Their strength rises by 0.5 each week, with a risk of searches and repression once organization reaches 40.",
    "TFR_EST_occupation_civilian_compact": "Civilian Administration Compact",
    "TFR_EST_occupation_civilian_compact_desc": "Local officials secure written limits on interference and maintain an Estonian administrative chain of command.",
    "TFR_EST_occupation_social_guarantees": "Social Guarantees",
    "TFR_EST_occupation_social_guarantees_desc": "The administration protects basic public services. The patron's economic framework remains in force, and these guarantees require continuing expenditure.",
    "TFR_EST_occupation_security_compact": "Security Mandate",
    "TFR_EST_occupation_security_compact_desc": "Local units gain a defined defensive role while their supervision remains a source of public tension.",
    "tfr_estonia_occupation.2.t": "Government after Defeat",
    "tfr_estonia_occupation.2.d": "Defeat has placed Estonia under an occupation administration. The Riigikogu's party ledger is preserved, but ordinary elections and independent foreign policy are suspended. Tallinn remains the seat of a playable Estonian government.\n\nOur immediate tasks are to preserve civilian services, negotiate the permissible role of local forces and decide how to pursue a future restoration. Cooperation can win concessions; underground organization carries the risk of repression. The administration's mandate depends on the political order of the occupying power.",
    "tfr_estonia_occupation.2.a": "Preserve the institutions that remain.",
    "tfr_estonia_occupation.3.t": "Searches and Detentions",
    "tfr_estonia_occupation.3.d": "Security officials have detected part of the restoration network. Municipal offices and veterans' associations face searches, and several organizers are in detention. The administration must decide whether to sacrifice exposed cells to protect the wider organization or risk an open confrontation over the detainees.",
    "tfr_estonia_occupation.3.a": "Protect the remaining network.",
    "tfr_estonia_occupation.3.b": "Defend the detainees in public.",
    "tfr_estonia_occupation.4.t": "The Sovereignty Petition",
    "tfr_estonia_occupation.4.d": "Our delegates have presented the restoration compact. Its practical success rests on the patron's condition and the institutions rebuilt at home. If the settlement still meets the requirements for independence, executive authority can return to an Estonian caretaker cabinet. Otherwise the delegation must return to negotiations without a constitutional breakthrough.",
    "tfr_estonia_occupation.4.a": "Ratify the restoration compact.",
    "tfr_estonia_occupation.4.b": "The mandate has not yet changed.",
    "tfr_estonia_occupation.5.t": "Constitutional Authority Restored",
    "tfr_estonia_occupation.5.d": "Independent constitutional government has resumed. A caretaker cabinet will maintain services until a national election within ninety days. Completed public reforms and reconstructed institutions remain in place. The final territorial settlement still depends on the wider conflict; independence does not automatically return every disputed region.",
    "tfr_estonia_occupation.5.a": "Prepare an accountable government.",
    "TFR_EST_occupation_can_restore_tt": "The patron has capitulated, or the restoration compact is complete and the patron is collapsing militarily. Liberal and supervised administrations may also qualify peacefully after 52 weeks with 60 cooperation, 60 cohesion and 40 readiness.",
}


def write(relative, text, bom=False):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    text = re.sub(r'add_to_variable = \{ var = TFR_EST_occupation_(cooperation|resistance) value = ([^ }]+) \}', r'TFR_EST_change_occupation_\1 = { AMOUNT = \2 }', text)
    path.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


def focus(name, title, desc, x, y, reward, prerequisites=(), available="", branch="", exclusive=(), icon="political_pressure", cost=4):
    key = PREFIX + name
    LOC[key], LOC[key + "_desc"] = title, desc
    lines = ["    focus = {", f"        id = {key}", f"        icon = GFX_goal_generic_{icon}", f"        x = {x}", f"        y = {y}", f"        cost = {cost}", "        cancel_if_invalid = yes", f"        bypass = {{ has_country_flag = {key}_done }}"]
    for group in prerequisites:
        if isinstance(group, str):
            group = (group,)
        lines.append("        prerequisite = { " + " ".join("focus = " + PREFIX + p for p in group) + " }")
    if exclusive:
        lines.append("        mutually_exclusive = { " + " ".join("focus = " + PREFIX + p for p in exclusive) + " }")
    lines.append("        available = { has_country_flag = TFR_EST_occupied " + available + " }")
    if branch:
        lines.append("        allow_branch = { " + branch + " }")
    lines += [f"        completion_reward = {{ if = {{ limit = {{ NOT = {{ has_country_flag = {key}_done }} }} {reward} set_country_flag = {key}_done }} }}", "        ai_will_do = { factor = 1 }", "    }"]
    return "\n".join(lines)


def main():
    nodes = [focus("transition", "An Administration in Tallinn", "The state has survived defeat, but its mandate is constrained by an occupying power. Keep the civil service working while preparing a durable political settlement.", 18, 0, "add_political_power = 50 TFR_EST_change_cohesion = { AMOUNT = 3 }")]
    shared = [
        ("municipal_services", "Keep the Municipalities Working", "Schools, hospitals and emergency response need a consistent civilian chain of command. Reestablish local service boards across the territory we still govern.", 12, 1, "add_ideas = TFR_EST_occupation_local_services TFR_EST_change_cohesion = { AMOUNT = 5 } TFR_EST_spend_budget = { AMOUNT = 100 }", ("transition",), "national_unity"),
        ("rebuild", "Repair the Lifelines", "A damaged economy cannot support either accommodation or resistance. Reopen transport links, restore utilities and employ local repair crews. This commits EUR 250 million to reconstruction.", 12, 2, "add_ideas = TFR_EST_occupation_recovery TFR_EST_spend_budget = { AMOUNT = 250 }", ("municipal_services",), "construction"),
        ("employment", "A Civilian Recovery Program", "Provide work in civilian production and use recovered industrial land in Northern Estonia. The EUR 350 million program adds one civilian factory if the state remains under our control.", 12, 3, "TFR_EST_spend_budget = { AMOUNT = 350 } 13 = { if = { limit = { is_owned_by = EST is_controlled_by = EST } add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } } TFR_EST_change_cohesion = { AMOUNT = 4 }", ("rebuild",), "construction2"),
        ("security", "Define the Security Mandate", "Negotiate rules for local officers, the protection of civilian buildings and the supervision of public order. Restoring predictability comes before expanding force strength.", 24, 1, "TFR_EST_change_readiness = { AMOUNT = 5 } add_ideas = TFR_EST_occupation_security_compact", ("transition",), "defence"),
        ("local_forces", "Permitted Territorial Forces", "Secure permission to recruit and train a limited territorial force. This improves organization; all units must still be equipped and staffed from our own resources.", 24, 2, "add_ideas = TFR_EST_occupation_limited_forces TFR_EST_change_readiness = { AMOUNT = 8 } TFR_EST_spend_budget = { AMOUNT = 150 }", ("security",), "army_doctrines"),
        ("returned_officers", "An Estonian Officer Cadre", "Recover service records and assign qualified officers to training and logistics. Preserve an institutional memory that can serve a future independent army.", 24, 3, "TFR_EST_change_readiness = { AMOUNT = 8 } TFR_EST_spend_budget = { AMOUNT = 100 }", ("local_forces",), "military_sphere"),
        ("assembly", "A Local Consultative Assembly", "Even without free national elections, local representatives can scrutinize services and make Estonian needs visible. The assembly is advisory and does not replace the suspended Riigikogu.", 18, 4, "TFR_EST_change_cohesion = { AMOUNT = 6 } add_political_power = 50", ("employment", "returned_officers"), "political_pressure"),
    ]
    for name, title, desc, x, y, reward, prereq, icon in shared:
        nodes.append(focus(name, title, desc, x, y, reward, prereq, icon=icon))
    variants = [
        (1, "communist", "A Socialist Reconstruction Mandate", "Labor Councils and Services", "Guarantees for Local Institutions", "The new socialist order demands political alignment. Negotiate an Estonian reconstruction mandate that protects civilian expertise while the parent administration determines the party leadership.", "Public services and workplace councils become the administration's organizing institutions. Commit resources to social provision without promising a return to parliamentary competition.", "Obtain written protections for schools, registries and local administration within the occupation framework.", "social_guarantees", 8, 4),
        (2, "civilian", "A Civilian Russian Administration", "Regional Investment Bargains", "An Administrative Autonomy Statute", "A civilian authoritarian patron offers stability on its own terms. Preserve an Estonian civil service while negotiating the limits of central oversight.", "Seek investment for utilities and regional employment in exchange for predictable administration. Public acceptance depends on tangible results.", "Record a limited autonomy statute. It improves the administration's position but neither removes the patron nor restores national elections.", "civilian_compact", 6, 6),
        (3, "military", "Under the Security Directorate", "A Territorial Security Compact", "Civil Authority beneath the Command", "A military or nationalist occupation places security before constitutional politics. Establish lines of responsibility that prevent local services from being absorbed into military command.", "Train local forces for clearly defined defensive tasks. Keep their equipment and manpower obligations separate from the patron's formations.", "Seek a protected civil sphere for schools, courts and municipalities. Every concession remains vulnerable to the commanding authority.", "security_compact", 3, 12),
        (4, "eurasian", "The Eurasian Administrative Order", "Protect the Local Cultural Sphere", "A Local Charter within the Empire", "The Eurasian order requires political and cultural alignment with the patron. The administration's first task is to preserve the institutions through which Estonian society can continue to function.", "Negotiate room for local education and public services within the patron's ideological program. These concessions cost resources and political capital.", "An administrative charter provides limited local continuity. It does not imply approval of the occupation or a democratic electoral mandate.", "social_guarantees", 6, 7),
        (5, "baltic", "Estonia beside the Baltic Federation", "A Baltic Reconstruction Agreement", "An Estonian Sovereignty Clause", "A liberal Russian victory may organize the wider region as a Baltic federation. Estonia retains its own administration alongside that structure rather than disappearing into it.", "Coordinate trade and infrastructure with neighboring administrations. The EUR 150 million agreement seeks access to reconstruction expertise without merging the Estonian state.", "Put the right to seek restored sovereignty into the administrative settlement. A peaceful exit still requires strong institutions and cooperation.", "civilian_compact", 9, 6),
        (6, "supervised", "A European Supervisory Mandate", "Civilian Oversight and Reconstruction", "A Schedule for Constitutional Return", "A European supervisory authority seeks a stable local administration. Preserve accountable records and a clear distinction between supervision and independent elected authority.", "Place reconstruction accounts and public procurement under civilian scrutiny. A credible administration can bargain for an eventual end to supervision.", "Agree a framework for constitutional return. Independence requires the restoration compact and measurable administrative readiness.", "civilian_compact", 10, 5),
        (7, "european_authoritarian", "An Authoritarian European Authority", "Local Services under Occupation", "A Defensive Administrative Charter", "An authoritarian European victory places Estonia alongside a regional occupation structure. Northern Estonia remains a separate administration directly answerable to the victorious power.", "Keep schools, utilities and public health working while negotiating the restrictions imposed by the occupying authority.", "Secure limits on the use of local forces and protect civilian administrative functions. A strong patron will still refuse an independent constitutional settlement.", "security_compact", 4, 10),
    ]
    last = []
    for i, slug, t1, t2, t3, d1, d2, d3, idea, cohesion, readiness in variants:
        gate = f"check_variable = {{ var = TFR_EST_occupation_type value = {i} compare = equals }}"
        x = (i - 1) * 6
        n1, n2, n3 = slug + "_mandate", slug + "_program", slug + "_charter"
        nodes.append(focus(n1, t1, d1, x, 5, "add_political_power = 40 TFR_EST_change_cohesion = { AMOUNT = 2 }", ("assembly",), gate, gate))
        nodes.append(focus(n2, t2, d2, x, 6, f"add_ideas = TFR_EST_occupation_{idea} TFR_EST_change_cohesion = {{ AMOUNT = {cohesion} }} TFR_EST_change_readiness = {{ AMOUNT = {readiness} }} TFR_EST_spend_budget = {{ AMOUNT = 150 }} country_event = {{ id = tfr_estonia_occupation.{10 + i} days = 7 }}", (n1,), gate, gate, icon="construction"))
        nodes.append(focus(n3, t3, d3, x, 7, "add_to_variable = { var = TFR_EST_occupation_cooperation value = 10 } TFR_EST_change_cohesion = { AMOUNT = 3 }", (n2,), gate, gate))
        last.append(n3)
    nodes += [
        focus("accommodation", "Administrative Accommodation", "Work within the imposed administration to secure services and political concessions. Cooperation grows gradually; it can support a peaceful sovereignty petition under liberal or supervised mandates.", 12, 8, "add_ideas = TFR_EST_occupation_collaboration add_to_variable = { var = TFR_EST_occupation_cooperation value = 10 } TFR_EST_change_cohesion = { AMOUNT = -3 }", (tuple(last),), exclusive=("clandestine",)),
        focus("clandestine", "Preserve a Restoration Network", "Build discreet civilian networks, retain constitutional records and protect the people who could rebuild independent institutions. Exposure can lead to searches and detentions.", 24, 8, "add_ideas = TFR_EST_occupation_clandestine_network add_to_variable = { var = TFR_EST_occupation_resistance value = 10 } TFR_EST_change_cohesion = { AMOUNT = 4 }", (tuple(last),), exclusive=("accommodation",), icon="secret_weapon"),
        focus("guarantees", "Negotiated Civilian Guarantees", "Convert administrative cooperation into written commitments on services, civil registries and local accountability. These guarantees improve public confidence while sovereignty remains restricted.", 12, 9, "add_to_variable = { var = TFR_EST_occupation_cooperation value = 15 } TFR_EST_change_cohesion = { AMOUNT = 8 }", ("accommodation",)),
        focus("exile_charter", "A Charter for Constitutional Restoration", "Agree a common charter with surviving democratic institutions and representatives abroad. No normal political party is treated as an automatic collaborator; the restored constitution will return competition to the electorate.", 24, 9, "add_to_variable = { var = TFR_EST_occupation_resistance value = 15 } TFR_EST_change_cohesion = { AMOUNT = 8 } TFR_EST_change_readiness = { AMOUNT = 5 }", ("clandestine",), icon="national_unity"),
        focus("restoration_compact", "The Restoration Compact", "Prepare the institutions, records and personnel for a return to constitutional government. A liberal or supervised patron may accept a petition after a year of credible administration. A coercive patron requires military collapse before the compact can take effect.", 18, 10, "TFR_EST_change_cohesion = { AMOUNT = 6 } TFR_EST_change_readiness = { AMOUNT = 5 } custom_effect_tooltip = TFR_EST_occupation_can_restore_tt", (("guarantees", "exile_charter"),), icon="national_unity", cost=6),
        focus("constitutional_return", "Restore Constitutional Authority", "End the occupation mandate when the compact is enforceable. A caretaker government will prepare a national election within ninety days. Borders follow the wider settlement and are not automatically restored by this focus.", 18, 11, "TFR_EST_restore_sovereignty = yes", ("restoration_compact",), "TFR_EST_can_restore_sovereignty = yes", icon="national_unity", cost=2),
    ]
    write("common/national_focus/TFR_EST_occupation.txt", "focus_tree = {\n    id = TFR_EST_occupation_tree\n    country = { factor = 0 modifier = { add = 100 original_tag = EST has_country_flag = TFR_EST_occupied } }\n    default = no\n    continuous_focus_position = { x = 1400 y = 1350 }\n" + "\n".join(nodes) + "\n}\n")
    decisions = []
    specs = [
        ("service_relief", "Emergency Service Grants", "Commit EUR 50 million to local healthcare and essential services. This raises cohesion by 3 and administrative cooperation by 5. Available every sixty days after municipal services are organized.", "has_completed_focus = TFR_EST_occupation_municipal_services", "TFR_EST_spend_budget = { AMOUNT = 50 } TFR_EST_change_cohesion = { AMOUNT = 3 } add_to_variable = { var = TFR_EST_occupation_cooperation value = 5 }", 35, 60),
        ("training", "Fund Permitted Local Training", "Commit EUR 60 million to training and logistics for the permitted territorial forces. Readiness rises by 4; the decision grants no units or equipment. Available every ninety days.", "has_completed_focus = TFR_EST_occupation_local_forces", "TFR_EST_spend_budget = { AMOUNT = 60 } TFR_EST_change_readiness = { AMOUNT = 4 }", 40, 90),
        ("cooperation", "Negotiate Administrative Concessions", "Use administrative cooperation to protect local authority. Cooperation rises by 8 at the cost of 2 cohesion. Available every sixty days under an accommodation program.", "has_idea = TFR_EST_occupation_collaboration", "add_to_variable = { var = TFR_EST_occupation_cooperation value = 8 } TFR_EST_change_cohesion = { AMOUNT = -2 }", 35, 60),
        ("network", "Protect Constitutional Records", "Commit EUR 20 million to safeguard service records and constitutional documents. Restoration networks gain 8 strength and cohesion rises by 2. Strong networks invite periodic security searches.", "has_idea = TFR_EST_occupation_clandestine_network", "TFR_EST_spend_budget = { AMOUNT = 20 } add_to_variable = { var = TFR_EST_occupation_resistance value = 8 } TFR_EST_change_cohesion = { AMOUNT = 2 }", 40, 60),
        ("petition", "Petition for Restored Sovereignty", "Present the completed restoration compact. Requirements are checked again when the delegation returns. Independence resumes constitutional politics and schedules an election within ninety days, while territory follows the wider settlement.", "TFR_EST_can_restore_sovereignty = yes NOT = { has_country_flag = TFR_EST_petition_pending }", "set_country_flag = TFR_EST_petition_pending country_event = { id = tfr_estonia_occupation.4 days = 7 }", 75, 90),
    ]
    for name, title, desc, available, effect, cost, cooldown in specs:
        key = PREFIX + name
        LOC[key], LOC[key + "_desc"] = title, desc
        decisions.append(f"    {key} = {{\n        icon = generic_political_discourse\n        visible = {{ has_country_flag = TFR_EST_occupied }}\n        available = {{ has_country_flag = TFR_EST_occupied {available} }}\n        cost = {cost}\n        days_re_enable = {cooldown}\n        complete_effect = {{ {effect} }}\n        ai_will_do = {{ factor = 1 }}\n    }}")
    write("common/decisions/TFR_EST_occupation.txt", "TFR_EST_occupation_category = {\n" + "\n".join(decisions) + "\n}\n")
    write("common/decisions/categories/TFR_EST_occupation.txt", "TFR_EST_occupation_category = {\n    icon = generic_political_actions\n    allowed = { original_tag = EST }\n    visible = { has_country_flag = TFR_EST_occupied }\n    priority = 250\n}\n")
    events = '''add_namespace = tfr_estonia_occupation

country_event = {
    id = tfr_estonia_occupation.1
    hidden = yes
    is_triggered_only = yes
    immediate = {
        clr_country_flag = TFR_EST_occupation_reconciliation_queued
        # Resolve the current patron here; queued targets may already be stale.
        TFR_EST_reconcile_occupation = yes
    }
}

country_event = {
    id = tfr_estonia_occupation.2
    title = tfr_estonia_occupation.2.t
    desc = tfr_estonia_occupation.2.d
    picture = GFX_report_event_generic_parliament
    is_triggered_only = yes
    trigger = { original_tag = EST has_country_flag = TFR_EST_occupied is_subject = yes }
    option = { name = tfr_estonia_occupation.2.a ai_chance = { factor = 1 } }
}

country_event = {
    id = tfr_estonia_occupation.3
    title = tfr_estonia_occupation.3.t
    desc = tfr_estonia_occupation.3.d
    picture = GFX_report_event_generic_riot
    is_triggered_only = yes
    trigger = { original_tag = EST has_country_flag = TFR_EST_occupied is_subject = yes has_idea = TFR_EST_occupation_clandestine_network }
    option = {
        name = tfr_estonia_occupation.3.a
        ai_chance = { factor = 3 }
        add_to_variable = { var = TFR_EST_occupation_resistance value = -8 }
        TFR_EST_change_cohesion = { AMOUNT = -2 }
    }
    option = {
        name = tfr_estonia_occupation.3.b
        ai_chance = { factor = 1 }
        add_political_power = -30
        TFR_EST_change_cohesion = { AMOUNT = -5 }
        add_to_variable = { var = TFR_EST_occupation_resistance value = 3 }
    }
}

country_event = {
    id = tfr_estonia_occupation.4
    title = tfr_estonia_occupation.4.t
    desc = tfr_estonia_occupation.4.d
    picture = GFX_report_event_generic_parliament
    is_triggered_only = yes
    immediate = { clr_country_flag = TFR_EST_petition_pending }
    option = {
        name = tfr_estonia_occupation.4.a
        trigger = { TFR_EST_can_restore_sovereignty = yes }
        ai_chance = { factor = 100 }
        TFR_EST_restore_sovereignty = yes
    }
    option = {
        name = tfr_estonia_occupation.4.b
        trigger = { NOT = { TFR_EST_can_restore_sovereignty = yes } }
        ai_chance = { factor = 1 }
        add_political_power = 25
    }
}

country_event = {
    id = tfr_estonia_occupation.5
    title = tfr_estonia_occupation.5.t
    desc = tfr_estonia_occupation.5.d
    picture = GFX_report_event_generic_parliament
    is_triggered_only = yes
    trigger = { original_tag = EST NOT = { has_country_flag = TFR_EST_occupied } is_subject = no }
    option = { name = tfr_estonia_occupation.5.a ai_chance = { factor = 1 } }
}
'''
    conflicts = [
        (1, "Who Appoints the Workplace Councils?", "Reconstruction has reopened several workplaces, but the patron's political representatives want control over appointments to the labor councils. Local organizers argue that qualified workers and municipal officials should choose the delegates. The dispute now threatens to delay public services.", "Retain local appointments.", "Accept the supervisory nominees."),
        (2, "The Regional Investment Conditions", "The promised investment package includes a requirement that key procurement and utility contracts pass through the patron's regional authority. Our civil servants can obtain a larger immediate grant by accepting those conditions, or defend a smaller program under local supervision.", "Keep the contracts under local scrutiny.", "Accept the regional authority's terms."),
        (3, "Civilian Services or Command Resources?", "The security command has requested vehicles and staff assigned to municipal emergency services. Local officers warn that surrendering them will weaken public health and winter response. Refusing the request could jeopardize the limited military training mandate.", "Protect municipal emergency capacity.", "Meet the command's requisitions."),
        (4, "The School Charter Dispute", "The Eurasian authority wants the new school charter to give its supervisory board control over teaching appointments. Administrators propose retaining an Estonian civilian appointment process while accepting the patron's mandatory framework. The decision will shape public confidence in the entire reconstruction program.", "Defend the civilian appointment process.", "Accept the supervisory board."),
        (5, "A Common Market, a Separate Administration", "The Baltic reconstruction agreement offers useful access to neighboring markets, but the regional authority proposes merging several registries and procurement boards. Our delegation must decide how much administrative control to share while Estonia's sovereignty clause is still being negotiated.", "Retain separate national registries.", "Share the boards for immediate access."),
        (6, "The Reconstruction Accounts", "A supervisory review has identified emergency contracts that bypassed normal procurement. Local representatives want an independent public inquiry. Supervisors offer to close the issue quietly if the administration accepts tighter external control over future spending.", "Authorize a public civilian inquiry.", "Accept external control to release the funds."),
        (7, "A Regional Authority's Security Demand", "The regional occupation authority has asked Estonia to surrender control of a local security office and its personnel records. Municipal officials fear the loss of the safeguards negotiated in the administrative charter. Compliance could secure additional resources for the permitted territorial forces.", "Keep the local office under its charter.", "Hand the office to the occupation authority."),
    ]
    for occupation_type, title, desc, local, patron in conflicts:
        event_id = f"tfr_estonia_occupation.{10 + occupation_type}"
        LOC[event_id + ".t"], LOC[event_id + ".d"] = title, desc
        LOC[event_id + ".a"], LOC[event_id + ".b"] = local, patron
        events += f'''\ncountry_event = {{
    id = {event_id}
    title = {event_id}.t
    desc = {event_id}.d
    picture = GFX_report_event_generic_parliament
    is_triggered_only = yes
    trigger = {{ has_country_flag = TFR_EST_occupied is_subject = yes check_variable = {{ var = TFR_EST_occupation_type value = {occupation_type} compare = equals }} }}
    option = {{
        name = {event_id}.a
        ai_chance = {{ factor = 2 }}
        TFR_EST_change_cohesion = {{ AMOUNT = 4 }}
        TFR_EST_change_occupation_cooperation = {{ AMOUNT = -6 }}
        TFR_EST_spend_budget = {{ AMOUNT = 25 }}
    }}
    option = {{
        name = {event_id}.b
        ai_chance = {{ factor = 1 }}
        TFR_EST_change_cohesion = {{ AMOUNT = -3 }}
        TFR_EST_change_readiness = {{ AMOUNT = 4 }}
        TFR_EST_change_occupation_cooperation = {{ AMOUNT = 10 }}
    }}
}}
'''
    write("events/TFR_EST_occupation.txt", events)
    localization = "l_english:\n" + "\n".join(' ' + key + ':0 "' + value.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"') + '"' for key, value in LOC.items()) + "\n"
    write("localisation/english/TFR_EST_occupation_l_english.yml", localization, bom=True)
    print(f"Generated {len(nodes)} occupation focuses, {len(specs)} decisions, 12 events, {len(LOC)} English keys.")


if __name__ == "__main__":
    main()

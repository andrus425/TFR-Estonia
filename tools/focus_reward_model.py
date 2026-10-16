"""Shared numerical rewards and native previews for the historical cabinets.

Keep numerical balancing separate from the historical focus descriptions. Each
preview is generated from the exact values written to the persistent modifier.
"""
from dataclasses import replace


OPENING_ECONOMIC = {
    "pension_reform": (("consumer_goods_factor", -.02), ("production_factory_max_efficiency_factor", .025)),
    "teacher_pay": (("research_speed_factor", .03),),
    "covid_emergency": (("consumer_goods_factor", -.01),),
    "pension_increase": (("consumer_goods_factor", -.01),),
    "wage_compensation": (("industrial_capacity_factory", .05), ("production_factory_max_efficiency_factor", .025)),
    "excise_relief": (("consumer_goods_factor", -.03),),
    "kose_voobu": (("production_speed_buildings_factor", .05),),
    "three_seas": (("production_factory_efficiency_gain_factor", .05),),
    "research_budget": (("research_speed_factor", .05),),
}
OPENING_MILITARY = {
    "eastern_border": (("army_defence_factor", .05), ("dig_in_speed_factor", .10)),
    "kose_voobu": (("supply_consumption_factor", -.04),),
}

ECONOMIC = {
    "ratas": {
        "family_home_guarantees": (("production_speed_buildings_factor", .04),),
        "child_tax_allowance": (("consumer_goods_factor", -.01),),
        "home_care": (("consumer_goods_factor", -.01), ("production_factory_max_efficiency_factor", .025)),
        "state_jobs_counties": (("production_speed_buildings_factor", .03), ("industrial_capacity_factory", .02)),
        "rural_broadband": (("research_speed_factor", .03), ("production_factory_efficiency_gain_factor", .03)),
        "industrial_parks": (("industrial_capacity_factory", .05), ("production_speed_buildings_factor", .05)),
        "worker_retraining": (("production_factory_efficiency_gain_factor", .05), ("production_factory_max_efficiency_factor", .05)),
        "hospital_covid": (("consumer_goods_factor", -.01),),
        "testing_tracing": (("research_speed_factor", .02),),
        "family_doctors": (("production_factory_max_efficiency_factor", .025),),
        "vaccinate_risk_groups": (("industrial_capacity_factory", .03),),
        "lng_connection": (("local_resources_factor", .05), ("industrial_capacity_factory", .02)),
        "grid_synchronisation": (("production_speed_buildings_factor", .04),),
        "renewable_chp": (("industrial_capacity_factory", .04),),
        "building_renovation": (("production_speed_buildings_factor", .05),),
        "network_charge_relief": (("consumer_goods_factor", -.01),),
    },
    "kallas": {
        "sick_pay": (("consumer_goods_factor", -.01),),
        "hospital_support": (("production_factory_max_efficiency_factor", .03),),
        "frontline_vaccination": (("industrial_capacity_factory", .03),),
        "covid_certificates": (("research_speed_factor", .03),),
        "pension_twenty": (("consumer_goods_factor", -.015),),
        "pension_tax_allowance": (("consumer_goods_factor", -.015),),
        "teacher_pay": (("research_speed_factor", .03),),
        "school_catch_up": (("research_speed_factor", .04),),
        "recovery_plan": (("production_speed_buildings_factor", .05),),
        "enterprise_digital": (("production_factory_efficiency_gain_factor", .05), ("production_factory_max_efficiency_factor", .05)),
        "rural_broadband": (("industrial_capacity_factory", .03), ("production_speed_buildings_factor", .03)),
        "mental_health": (("production_factory_max_efficiency_factor", .03),),
        "energy_households": (("consumer_goods_factor", -.01),),
        "energy_networks": (("consumer_goods_factor", -.01), ("industrial_capacity_factory", .03)),
        "gas_reserve": (("local_resources_factor", .05), ("production_factory_max_efficiency_factor", .03)),
        "lng_connection": (("production_speed_buildings_factor", .04), ("industrial_capacity_factory", .02)),
    },
}
MILITARY = {
    "ratas": {
        "police_reserve": (("army_org_factor", .04), ("mobilization_speed", .15)),
        "territorial_training": (("training_time_army_factor", -.08), ("army_defence_factor", .05)),
    },
    "kallas": {
        "defence_budget": (("training_time_army_factor", -.08), ("army_org_factor", .05)),
        "civil_protection": (("army_defence_factor", .05), ("dig_in_speed_factor", .10)),
    },
}


def rebalance_policies(policies, route):
    """Preserve names/descriptions/conditions while improving permanent rewards."""
    result = []
    for policy in policies:
        extra = policy.extra.replace("add_political_power = 25", "add_political_power = 40").replace("add_political_power = 50", "add_political_power = 75")
        result.append(replace(
            policy,
            economic=ECONOMIC[route].get(policy.suffix, policy.economic),
            military=MILITARY[route].get(policy.suffix, policy.military),
            cohesion=policy.cohesion + (1 if policy.cohesion else 0),
            readiness=policy.readiness + (2 if policy.readiness else 0),
            extra=extra,
        ))
    return tuple(result)


def modifier_reward(focus_id, group, changes):
    """TFR's native delta preview, followed by hidden persistent arithmetic."""
    if not changes:
        return ""
    writes = "\n        ".join(
        f"add_to_variable = {{ TFR_EST_{group}_{field}_var = {amount:g} }}"
        for field, amount in changes
    )
    return f"""effect_tooltip = {{
        swap_ideas = {{
            remove_idea = TFR_EST_tooltip_{group}_empty
            add_idea = {focus_id}_{group}_delta
        }}
    }}
    hidden_effect = {{
        {writes}
    }}"""


def energy_progress_tooltip(route, suffix):
    if route == "ratas" and suffix in {"lng_connection", "grid_synchronisation", "renewable_chp", "building_renovation", "network_charge_relief"}:
        return "custom_effect_tooltip = TFR_EST_energy_one_stage_tt"
    if route == "kallas" and suffix == "energy_networks":
        return "custom_effect_tooltip = TFR_EST_energy_two_stages_tt"
    if route == "kallas" and suffix in {"energy_households", "gas_reserve", "lng_connection"}:
        return "custom_effect_tooltip = TFR_EST_energy_one_stage_tt"
    return ""


def concise_trigger(name, content, tooltip=None):
    """Wrap one scripted trigger without changing its underlying conditions."""
    marker = name + " = {"
    start = content.index(marker) + len(marker)
    depth = 1
    end = start
    while depth:
        if content[end] == "{":
            depth += 1
        elif content[end] == "}":
            depth -= 1
        end += 1
    inner = content[start:end - 1].strip("\n")
    wrapped = "\n    custom_trigger_tooltip = {\n        tooltip = " + (tooltip or name + "_tt") + "\n"
    wrapped += "\n".join("    " + line for line in inner.splitlines())
    wrapped += "\n    }\n"
    return content[:start] + wrapped + content[end - 1:]

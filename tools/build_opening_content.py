"""Build the compact 2020 Ratas coalition programme and its English text.

These are shared-focus definitions. The main Estonia tree references their IDs;
country lifecycle and reward effects remain in their own scripted-effect files.
The 35-day periods represent policy implementation, not literal legislative dates.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TFR_EST_opening_"
FOCUS_PATH = ROOT / "common/national_focus/TFR_EST_opening.txt"
LOCALISATION_PATH = ROOT / "localisation/english/TFR_EST_opening_l_english.yml"


@dataclass(frozen=True)
class Policy:
    suffix: str
    title: str
    description: str
    icon: str


POLICIES = (
    Policy(
        "pension_reform",
        "Pass the Voluntary Second-Pillar Reform",
        "Isamaa's pension reform would make participation in the second pillar voluntary, "
        "giving savers a choice over contributions and the use of accumulated funds. "
        "The Centre–Isamaa–EKRE cabinet must carry the bill through parliament and the "
        "constitutional review process. Prepare the administration and public guidance; "
        "this does not mean that pension withdrawals already occur in January 2020. "
        "The governing coalition needs at least 51 seats to pursue its programme.",
        "political_pressure",
    ),
    Policy(
        "teacher_pay",
        "Teachers' Minimum Pay: €1,315",
        "The 2020 state budget raises the minimum monthly salary of a full-time general "
        "education teacher to €1,315. Fund the commitment and coordinate allocations "
        "with municipalities so the increase reaches schools across Estonia. The policy "
        "supports recruitment and retention while adding to the government's spending "
        "commitments. The coalition needs at least 51 seats to sustain its programme.",
        "consumer_goods",
    ),
    Policy(
        "covid_emergency",
        "Declare the COVID-19 Emergency",
        "The spread of COVID-19 requires the cabinet to coordinate the Health Board, "
        "hospitals, schools and border authorities. Estonia's emergency response in "
        "March 2020 includes restrictions on gatherings, remote learning and measures "
        "to reduce imported infections. Establish responsibility for those measures "
        "and keep essential government services working. COVID-19 must be present "
        "in Estonia before this response can begin. The coalition must command "
        "at least 51 parliamentary seats when it begins the response.",
        "consumer_goods",
    ),
    Policy(
        "pension_increase",
        "The €7 Extraordinary Pension Increase",
        "Alongside annual indexation, the government adds €7 to the pension base amount "
        "from April 2020. Put this concrete Centre Party commitment into operation and "
        "provide pensioners with clear information about their payments. The increase "
        "offers predictable support during the public-health emergency, with a lasting "
        "cost to the state budget. The governing coalition needs at least 51 seats.",
        "consumer_goods",
    ),
    Policy(
        "wage_compensation",
        "Töötukassa Wage Compensation",
        "Use the Unemployment Insurance Fund's temporary wage-compensation programme "
        "to help employers retain workers when the pandemic cuts turnover and work. "
        "The initial scheme supports employment during March–May 2020 and requires "
        "substantial emergency financing. Administer the claims and eligibility "
        "checks so support preserves jobs rather than rewarding ineligible firms. "
        "The coalition needs at least 51 seats.",
        "consumer_goods",
    ),
    Policy(
        "excise_relief",
        "Cut Diesel and Electricity Excise",
        "The emergency economic package lowers excise duties on diesel, electricity "
        "and several other energy products from May 2020. Implement the reductions "
        "to ease transport and energy costs for households and businesses, while "
        "accounting for the revenue the state forgoes. These are targeted changes to "
        "existing tax rates, not a promise of unlimited cheap energy. The governing "
        "coalition needs at least 51 seats.",
        "trade",
    ),
    Policy(
        "eastern_border",
        "Build the First 23.5 km of Eastern Border",
        "Begin the first 23.5-kilometre construction stage of Estonia's land border "
        "with Russia. The 2020 contract covers the initial section, patrol access "
        "and supporting infrastructure; it does not complete the entire eastern "
        "border. Coordinate the Police and Border Guard Board, contractors and local "
        "access arrangements so the project improves practical border security. "
        "The governing coalition needs at least 51 seats.",
        "defence",
    ),
    Policy(
        "kose_voobu",
        "Open the Kose–Võõbu Highway",
        "Bring the 23-kilometre Kose–Võõbu section of the Tallinn–Tartu road into "
        "service as a divided highway. This concrete 2020 transport project improves "
        "safety and travel between the capital and central Estonia. Complete the "
        "opening, connect the new route to the road network and plan its maintenance; "
        "the focus represents one section rather than a rebuilt national highway "
        "system. The governing coalition needs at least 51 seats.",
        "construct_infrastructure",
    ),
    Policy(
        "three_seas",
        "Host the Tallinn Three Seas Summit",
        "Estonia hosts the Three Seas Initiative summit in Tallinn in October 2020, "
        "with President Kersti Kaljulaid representing the country alongside the "
        "government's work on transport, energy and digital connections. Organise "
        "the summit and its investment discussions to advance specific regional "
        "projects. Participation opens cooperation opportunities; it does not "
        "automatically deliver every proposed investment. The coalition needs "
        "at least 51 seats to sustain its commitments.",
        "alliance",
    ),
    Policy(
        "research_budget",
        "Research Funding: 1% of GDP",
        "The 2021 state budget commits public research and development funding "
        "equivalent to one percent of GDP. Prepare the allocations and longer-term "
        "funding arrangements with universities and research institutions so the "
        "commitment becomes usable support. The additional spending strengthens "
        "Estonia's research base while competing with other budget priorities. "
        "The governing coalition needs at least 51 seats.",
        "scientific_exchange",
    ),
    Policy(
        "marriage_referendum",
        "The Marriage Referendum Bill",
        "The coalition brings forward the proposal for a spring 2021 referendum "
        "asking whether marriage should remain a union between a man and a woman. "
        "Complete the entire opening government programme before taking this final "
        "step. Once work on the bill begins, the focus cannot be cancelled, even "
        "if the cabinet loses its majority. The Porto Franco investigation will "
        "force Jüri Ratas to decide whether to remain prime minister or step back "
        "while the parliamentary process is under way. This focus concerns the "
        "bill and its political crisis; it does not mean that the referendum has "
        "already taken place.",
        "national_unity",
    ),
)


# Short branches preserve policy progression while allowing the cabinet to
# choose between several programmes. Separate prerequisite blocks are ANDs.
PREREQUISITES = {
    "pension_reform": (),
    "pension_increase": ("pension_reform",),
    "teacher_pay": (),
    "research_budget": ("teacher_pay",),
    "kose_voobu": (),
    "eastern_border": ("kose_voobu",),
    "three_seas": ("kose_voobu",),
    "covid_emergency": (),
    "wage_compensation": ("covid_emergency",),
    "excise_relief": ("covid_emergency",),
    "marriage_referendum": (
        "pension_increase", "research_budget", "eastern_border",
        "three_seas", "wage_compensation", "excise_relief",
    ),
}
POSITIONS = {
    "pension_reform": (0, 0),
    "pension_increase": (0, 2),
    "teacher_pay": (3, 0),
    "research_budget": (3, 2),
    "kose_voobu": (7, 0),
    "eastern_border": (6, 2),
    "three_seas": (9, 2),
    "covid_emergency": (13, 0),
    "wage_compensation": (12, 2),
    "excise_relief": (15, 2),
    "marriage_referendum": (7, 5),
}


def build_focuses() -> str:
    pieces = [
        "# The compact 2020 Centre-Isamaa-EKRE programme.\n"
        "# The main tree imports these shared IDs; no country tree is declared here.\n"
        "# Each five-point focus is a 35-day implementation period.\n"
    ]
    for row, policy in enumerate(POLICIES):
        ident = PREFIX + policy.suffix
        flag = "TFR_EST_done_opening_" + policy.suffix
        final = policy.suffix == "marriage_referendum"
        # The final focus joins all six branch ends; their ancestors cover all
        # ten policies. The central availability trigger also checks each one.
        prerequisites = "".join(
            f"    prerequisite = {{ focus = {PREFIX}{parent} }}\n"
            for parent in PREREQUISITES[policy.suffix]
        )
        available = "TFR_EST_can_start_referendum = yes" if final else "TFR_EST_opening_coalition_majority = yes"
        if policy.suffix == "covid_emergency":
            available += "\n        generic_has_corona = yes"
        x, y = POSITIONS[policy.suffix]
        cancellation = (
            "    cancelable = no\n    cancel_if_invalid = no\n    continue_if_invalid = yes\n"
            if final else "    cancel_if_invalid = yes\n    continue_if_invalid = no\n"
        )
        selection = ""
        if final:
            selection = "    select_effect = { TFR_EST_begin_referendum = yes }\n"
        elif policy.suffix == "covid_emergency":
            selection = "    select_effect = { TFR_EST_begin_covid_response = yes }\n"
        reward = "TFR_EST_finish_opening" if final else "TFR_EST_opening_reward_" + policy.suffix
        pieces.append(
            f"\nshared_focus = {{\n"
            f"    id = {ident}\n"
            f"    icon = GFX_goal_generic_{policy.icon}\n"
            f"    x = {x}\n"
            f"    y = {y}\n"
            f"    cost = 5\n"
            f"{prerequisites}"
            f"    available = {{\n        {available}\n    }}\n"
            f"    bypass = {{ has_country_flag = {flag} }}\n"
            f"{cancellation}"
            f"    ai_will_do = {{ factor = {100 - row} }}\n"
            f"{selection}"
            f"    completion_reward = {{\n"
            f"        if = {{\n"
            f"            limit = {{ NOT = {{ has_country_flag = {flag} }} }}\n"
            f"            set_country_flag = {flag}\n"
            f"            {reward} = yes\n"
            f"        }}\n"
            f"    }}\n"
            f"}}\n"
        )
    return "".join(pieces)


def build_localisation() -> str:
    lines = ["l_english:\n"]
    for policy in POLICIES:
        ident = PREFIX + policy.suffix
        lines.append(f" {ident}:0 {json.dumps(policy.title, ensure_ascii=False)}\n")
        lines.append(f" {ident}_desc:0 {json.dumps(policy.description, ensure_ascii=False)}\n")
    return "".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated files without changing them.")
    args = parser.parse_args()
    outputs = (
        (FOCUS_PATH, build_focuses().encode("utf-8")),
        (LOCALISATION_PATH, build_localisation().encode("utf-8-sig")),
    )
    for path, data in outputs:
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Generated file is stale: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f"{path.relative_to(ROOT).as_posix()}: {hashlib.sha256(data).hexdigest()}")
    verb = "Verified" if args.check else "Wrote"
    print(f"{verb} {len(POLICIES)} shared opening focuses and {2 * len(POLICIES)} English localisation keys.")


if __name__ == "__main__":
    main()

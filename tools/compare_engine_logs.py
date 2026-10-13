"""Compare captured startup errors with a parent-only baseline.

Normalize log timestamps and source line numbers, since exact-path compatibility
patches legitimately move parent code. This compares unique messages, not an
emulation of script behavior. Review new messages before accepting a build.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def messages(path):
    counts = Counter()
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = re.sub(r"^(?:\[[^\]]+\])+:?\s*", "", line)
        line = re.sub(r"(\.(?:txt|gui|gfx|yml|lua|cpp|h)):\d+", r"\1:<line>", line)
        line = re.sub(r"\bline\s*:?\s*\d+", "line <line>", line)
        line = re.sub(r"\bnear\s+line\s*:?\s*\d+", "near line <line>", line)
        if line.strip(): counts[line.strip()] += 1
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("baseline", type=Path, help="Parent-only captured error.log")
    ap.add_argument("submod", type=Path, help="Submod captured error.log")
    ap.add_argument("--output", type=Path, help="Save a JSON comparison report")
    ap.add_argument("--fail-on-new", action="store_true")
    args = ap.parse_args()
    before, after = messages(args.baseline), messages(args.submod)
    new = sorted(after.keys() - before.keys())
    resolved = sorted(before.keys() - after.keys())
    own = sorted(m for m in after if "TFR_EST_" in m or "tfr_estonia" in m)
    report = {
        "normalization": "timestamps and source line numbers",
        "baseline_unique_messages": len(before),
        "submod_unique_messages": len(after),
        "new_messages": new,
        "resolved_messages": resolved,
        "estonia_messages": own,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return bool(own or (args.fail_on_new and new))


if __name__ == "__main__":
    raise SystemExit(main())

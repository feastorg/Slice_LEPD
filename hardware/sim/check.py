#!/usr/bin/env python3
"""Simulate the LEPD LED driver and photodiode TIA bench and check it against expect.toml.

Exports the bench's SPICE netlist with kicad-cli, appends each analysis from the .wbk
workbook, measures in an ngspice .control block, and compares each measure with its
expected value, or with its `min` / `max` limits (a measure with neither is only printed). Also checks that every
ref listed in `mirrors` has the same value in the bench as in the real schematic. Exits 1 on any failure.

Usage: python3 hardware/sim/check.py   (needs kicad-cli and ngspice on PATH)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

SIM = Path(__file__).resolve().parent
REPO = SIM.parents[1]
BUILD = REPO / "build"
BENCH = SIM / "lepd_frontend.kicad_sch"
REAL = REPO / "hardware" / "BREAD_Slice.kicad_sch"

SUFFIX = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}


def export(sch: Path, fmt: str, out: Path) -> Path:
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", fmt, "-o", str(out), str(sch)], check=True)
    return out


def values(xml: Path) -> dict[str, str]:
    return {c.get("ref"): c.findtext("value") for c in ET.parse(xml).getroot().iter("comp")}


def number(text: str) -> float | None:
    m = re.match(r"([-+]?[0-9.]+(?:e[-+]?\d+)?)(meg|[tgkmunpf])?", text.strip(), re.IGNORECASE)
    if not m:
        return None
    # KiCad values use M for mega ("4.7M"); SPICE uses meg, and m for milli.
    suffix = "meg" if m.group(2) == "M" else (m.group(2) or "").lower()
    return float(m.group(1)) * SUFFIX.get(suffix, 1.0)


def check_mirrors(refs: list[str], cir: str) -> list[str]:
    bench = values(export(BENCH, "kicadxml", BUILD / "lepd_frontend.xml"))
    real = values(export(REAL, "kicadxml", BUILD / "real.xml"))
    # The value each R/C is simulated with, from its SPICE line: "R5 a b 36k".
    simulated = {f[0]: f[3] for f in (line.split() for line in cir.splitlines()) if len(f) >= 4 and f[0][:1] in "RC"}
    failures = []
    for entry in refs:
        b, _, r = entry.partition("=")
        r = r or b
        if b not in bench or r not in real:
            failures.append(f"mirror {entry}: missing from {'bench' if b not in bench else 'real schematic'}")
            continue
        ok = bench[b] == real[r]
        if ok and b in simulated:
            ok = number(simulated[b]) == number(real[r])
        print(f"mirror {entry}: bench {bench[b]!r} (simulated {simulated.get(b, '-')}) real {real[r]!r} {'ok' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"mirror {entry}: bench {bench[b]!r}/{simulated.get(b)} != real {real[r]!r}")
    return failures


def run(netlist: str, commands: list[str], control: list[str], name: str) -> str:
    deck = "\n".join([netlist, *commands, ".control", "run", *control, ".endc", ".end", ""])
    path = BUILD / f"{name}.cir"
    path.write_text(deck, encoding="utf-8")
    # KiCad's default LT_PSPICE compatibility mode, as the .kicad_pro sets it.
    proc = subprocess.run(["ngspice", "-D", "ngbehavior=ltpsa", "-b", str(path)], cwd=BUILD, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ngspice exited {proc.returncode}:\n{proc.stdout}{proc.stderr}")
    return proc.stdout


def main() -> int:
    missing = [t for t in ("kicad-cli", "ngspice") if shutil.which(t) is None]
    if missing:
        print(f"error: not found on PATH: {', '.join(missing)}", file=sys.stderr)
        return 1
    BUILD.mkdir(exist_ok=True)
    spec = tomllib.loads((SIM / "expect.toml").read_text(encoding="utf-8"))
    tabs = json.loads(BENCH.with_suffix(".wbk").read_text(encoding="utf-8"))["tabs"]

    cir = export(BENCH, "spice", BUILD / "lepd_frontend.cir").read_text(encoding="utf-8")
    netlist = "\n".join(line for line in cir.splitlines() if line.strip().lower() != ".end")
    failures = check_mirrors(spec.get("mirrors", []), cir)

    by_analysis: dict[str, list[dict]] = {}
    for m in spec["measure"]:
        by_analysis.setdefault(m["analysis"].lower(), []).append(m)
    for analysis, measures in by_analysis.items():
        (tab,) = [t for t in tabs if t["analysis"].lower() == analysis]
        commands = [c for c in tab["commands"] if not c.lower().startswith(".kicad")]
        # meas in the control block, after run: a .meas dot-line makes ngspice build
        # its save list from the expression.
        control = [f"meas {analysis} {m['name']} {m['meas']}" for m in measures]
        output = run(netlist, commands, control, f"lepd_frontend_{analysis}")
        for m in measures:
            found = re.search(rf"^\s*{re.escape(m['name'])}\s*=\s*([-+0-9.eE]+)", output, re.MULTILINE | re.IGNORECASE)
            if not found:
                failures.append(f"{m['name']}: ngspice printed no value")
                continue
            value = float(found.group(1))
            if "max" in m or "min" in m:
                lo, hi = m.get("min", float("-inf")), m.get("max", float("inf"))
                ok = lo <= value <= hi
                print(f"{m['name']} = {value:.4g} (limit {lo:.4g} .. {hi:.4g}) {'ok' if ok else 'FAIL'}")
                if not ok:
                    failures.append(f"{m['name']} = {value:.4g}, outside {lo:.4g} .. {hi:.4g}")
                continue
            if "expect" not in m:
                print(f"{m['name']} = {value:.4g} (informational)")
                continue
            expect, rtol = m["expect"], m["rtol"]
            ok = abs(value - expect) <= rtol * abs(expect)
            print(f"{m['name']} = {value:.4g} (expect {expect:.4g} ± {rtol * 100:g}%) {'ok' if ok else 'FAIL'}")
            if not ok:
                failures.append(f"{m['name']} = {value:.4g}, expected {expect:.4g} ± {rtol * 100:g}%")
    for f in failures:
        print(f"error: {f}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

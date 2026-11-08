# -*- coding: utf-8 -*-
"""Shared helpers for the manuscript builders: results, number formatting, block lists."""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "manuscript")
R = json.load(open(os.path.join(ROOT, "results", os.environ.get("LANTP_RESULTS", "results.json")), encoding="utf-8"))
DOIS = json.load(open(os.path.join(HERE, "dois.json"), encoding="utf-8"))
GITHUB = "https://github.com/sandlerleon/lantp-cislunar-mc"
VERSION = "1.2.1"
EMAIL = "sandler.leon@gmail.com"
TITLE = "Laser-Assisted Nuclear Thermal Propulsion for Cislunar Logistics: A Monte Carlo Power-Closure Assessment"


def jand(items):
    """Oxford-comma list: a, b, and c"""
    items = list(items)
    return items[0] if len(items) == 1 else (" and ".join(items) if len(items) == 2 else ", ".join(items[:-1]) + ", and " + items[-1])


def n(x, d=0):
    if x is None:
        return "n/a"
    s = "{:,.{d}f}".format(x, d=d)
    if set(s) <= set("-0.,"):
        return s.lstrip("-")
    return s.replace("-", "−")


def pc(x, d=0):
    return n(100.0 * x, d) + "%"


FIGNUM = {"arch": 1, "thermo": 2, "power": 3, "laser": 4, "beam": 5, "burn": 6, "opt": 7, "mc": 8, "trade": 9, "be": 10, "sens": 11, "conv": 12, "cont": 13, "thr": 14}
TABNUM = {"val": 1, "rng": 2, "chain": 3, "claims": 4, "infra": 5, "cont": 6, "mat": 7, "rt": 8}
_TOK = re.compile(r"@([FT]):(\w+)@")


def _sub(x):
    if isinstance(x, str):
        return _TOK.sub(lambda m: str({"F": FIGNUM, "T": TABNUM}[m.group(1)][m.group(2)]), x)
    if isinstance(x, tuple):
        return tuple(_sub(i) for i in x)
    if isinstance(x, list):
        return [_sub(i) for i in x]
    return x


B = []
BS = []


def add(b):
    B.append(_sub(b))


def adds(b):
    BS.append(_sub(b))


def fmt(_text, **kw):
    for k, v in kw.items():
        _text = _text.replace("<<%s>>" % k, str(v))
    assert "<<" not in _text, _text[_text.index("<<"):_text.index("<<") + 30]
    return _text


# ---------------------------------------------------------------------------------------------- derived quantities used in several places
import numpy as np                                                    # noqa: E402

TH, PW, LT, BM, NOM, MC, SENS, CONV = R["thermo"], R["power"], R["laser_thrust"], R["beam"], R["nominal"], R["mc"], R["sensitivity"], R["convergence"]
RR, RM, BE, CT, AST = R["ratio_rho"], R["ratio_mu"], R["breakeven"], R["contingency"], R["asteroid"]
OPT, SOB, THR, NOFF, IBURN = R["opt_mc"], R["sobol"], R["threshold"], R["node_offset"], R["independent_burn"]
SCAL = R.get("opt_scaling")
RATIO = np.array(MC["ratio"], float); FIN = np.isfinite(RATIO)
RQ = np.percentile(RATIO[FIN], [5, 25, 50, 75, 95])
ISPD = np.array(MC["isp_design"]); ISPE = np.array(MC["isp_eff_tli"], float)
SHARE_IN_BAND = float(((ISPD >= 1300) & (ISPD <= 1500)).mean())
SHARE_LT1 = float((RATIO[FIN] < 1).mean()); SHARE_CLAIM = float((RATIO[FIN] <= 0.6).mean())
RATIO_INF = np.array(MC["ratio_inf"], float)
PEMIT = np.array(MC["P_emit"]) / 1e9; PELEC = np.array(MC["P_elec"]) / 1e9; MINF = np.array(MC["M_inf"]) / 1e3
VAL = TH["validation"]
A_ERR = [a["mine"] / a["ref"] - 1 for a in VAL["alpha"]]
FRZ_ERR = [i["frozen_mine"] / i["frozen_ref"] - 1 for i in VAL["isp"]]; SHF_ERR = [i["shifting_mine"] / i["shifting_ref"] - 1 for i in VAL["isp"]]
FKN = np.array(LT["F_kN"])


def lt_at(target, F):
    """emitted laser power (MW): [5th, median, 95th] percentile at thrust F (kN) for the target specific impulse (interpolated on the thrust grid)"""
    rows = LT[str(int(target))]
    return [float(np.interp(F, FKN, [r["P_emit"][k] for r in rows])) for k in range(3)]


def r10(x):
    return n(round(x / 10.0) * 10)


def r100(x):
    return n(round(x / 100.0) * 100)


def cross(xs, ys, level=1.0):
    """x at which ys first reaches the level (linear interpolation); None if it never does"""
    xs = list(xs); ys = list(ys)
    for x0, y0, x1, y1 in zip(xs[:-1], ys[:-1], xs[1:], ys[1:]):
        if (y0 - level) * (y1 - level) <= 0 and y0 != y1:
            return x0 + (level - y0) / (y1 - y0) * (x1 - x0)
    return None


def sci(x):
    """x in scientific notation for the text, e.g. 2.1e-3 -> 2×10$^{-3}$"""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x)))); m = x / 10 ** e
    return "%s×10$^{%d}$" % (n(m, 0), e)

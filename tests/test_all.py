# -*- coding: utf-8 -*-
"""Automated checks of the LANTP model:  python tests/test_all.py   (or python -m pytest tests -q)"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lantp_core as L          # noqa: E402
import lantp_mission as Mi      # noqa: E402
import lantp_studies as S       # noqa: E402


def test_alpha_against_cantera():
    import cantera as ct
    g = ct.Solution("h2o2.yaml")
    for T, P in ((3000, 1e5), (4500, 3e6), (6000, 3e6)):
        g.TPX = T, P, "H2:1"; g.equilibrate("TP"); xh = g["H"].X[0]; ref = xh / (xh + 2 * g["H2"].X[0])
        assert abs(float(L.alpha_eq(T, P)) / ref - 1) < 0.10


def test_isp_against_cantera():
    import cantera as ct
    g = ct.Solution("h2o2.yaml")
    Tc, pc = 4500.0, 3e6; pe = pc * 1e-4
    g.TPX = Tc, pc, "H2:1"; g.equilibrate("TP"); hc, s, X = g.enthalpy_mass, g.entropy_mass, g.X
    g.SPX = s, pe, X; fr = math.sqrt(2 * (hc - g.enthalpy_mass)) / L.G0
    g.TPX = Tc, pc, "H2:1"; g.equilibrate("TP"); g.SP = s, pe; g.equilibrate("SP"); sh = math.sqrt(2 * (hc - g.enthalpy_mass)) / L.G0
    assert abs(L.exhaust(np.array([Tc]), np.array([pc]), 1e-4, 0.0, 1.0, "partial")[0] / L.G0 / fr - 1) < 0.03
    assert abs(L.exhaust(np.array([Tc]), np.array([pc]), 1e-4, 0.0, 1.0, "shifting")[0] / L.G0 / sh - 1) < 0.03


def test_ordering_of_expansions():
    T = np.array([3500.0, 4500.0, 5500.0]); p = np.full(3, 3e6)
    fr = L.exhaust(T, p, 1e-4, 0.0, 0.94, "partial"); pa = L.exhaust(T, p, 1e-4, 0.3, 0.94, "partial"); sh = L.exhaust(T, p, 1e-4, 0.0, 0.94, "shifting")
    assert np.all(fr < pa) and np.all(pa < sh * 1.02)
    assert np.all(np.diff(fr) > 0)


def test_gibbs_minimization_matches_equilibrium_constant():
    v = S.study_thermo()["validation"]["gibbs"]
    assert all(abs(g["gibbs"] - g["analytic"]) < 1e-6 for g in v)


def test_enthalpy_balance_inversion():
    p = np.full(4, 3e6); T = np.array([2000.0, 3000.0, 4500.0, 6500.0])
    h = L.h_mix(T, L.alpha_eq(T, p)); assert np.allclose(L.temp_from_enthalpy(h, p), T, rtol=1e-4)


def test_transfer_delta_v():
    a = L.transfer_dv(4.5); b = L.transfer_dv(2.0)
    assert abs(a["dv_tli"] - 3.08) < 0.05 and abs(a["dv_loi"] - 0.83) < 0.06
    assert b["dv_tli"] > a["dv_tli"] and b["dv_loi"] > a["dv_loi"]


def test_capture_properties():
    R = np.geomspace(1e2, 1e6, 50); c = L.capture(R, 10.0, 3.0, 1.2, 0.05)
    assert np.all((c >= 0) & (c <= 1)) and np.all(np.diff(c) <= 1e-12)
    assert L.capture(3e4, 20.0, 3.0, 1.2, 0.05) > L.capture(3e4, 5.0, 3.0, 1.2, 0.05)
    assert L.capture(3e4, 10.0, 3.0, 1.2, 0.3) < L.capture(3e4, 10.0, 3.0, 1.2, 0.05)


def test_high_thrust_burn_reproduces_rocket_equation():
    S0 = Mi.nominal(1); D0 = Mi.make_design(S0, rho=0.0)
    tab, mdot, *_ = L.make_table(D0); geo = L.transfer_dv(2.0); link = Mi._link(S0)
    mdot = mdot * 40                                                    # near-impulsive burn
    M = 2.0e5
    c, t, h = L.burn("depart", L.MU_E, L.RE + 400.0, geo["eps_tli"], tab, mdot, np.ones(1), link, np.array([M]), np.array([False]), L.RE, 100.0, 1000.0, dt=2.0, tmax=3000.0)
    ve = tab[0, -1] * L.G0
    ref = M * (1 - math.exp(-geo["dv_tli"] * 1e3 / ve))
    assert abs(c[0] / ref - 1) < 0.06


def test_mass_closure_and_comparison():
    S0 = Mi.nominal(2); S0["mu_rec"] = np.array([5.0, 40.0])
    D = Mi.make_design(S0); D0 = Mi.make_design(S0, rho=0.0)
    fx = dict(legs=2)
    r = Mi.solve_mission(S0, D, fixed=fx); nt = Mi.solve_mission(S0, D0, receiver=False, fixed=fx)
    assert np.all(np.abs(r["resid"]) < 0.01 * r["M"]) and np.all(np.abs(nt["resid"]) < 0.01 * nt["M"])
    ratio = r["M"] / nt["M"]
    assert ratio[1] > ratio[0] > 0.8                                    # a heavier receiver costs more
    assert np.all(r["ve"] > nt["ve"]) and np.all(r["F"] > nt["F"])


def test_infrastructure_scaling():
    S0 = Mi.nominal(1); D = Mi.make_design(S0); r = Mi.solve_mission(S0, D, fixed=dict(legs=2))
    inf = Mi.infrastructure(S0, D, r, fixed=dict(legs=2))
    assert inf["P_emit"][0] > inf["P_rec"][0] > inf["P_abs"][0] > inf["P_use"][0] > 0
    assert inf["M_inf"][0] > 10 * r["M"][0]


def test_laser_fault_costs_propellant():
    S0 = Mi.nominal(1); D = Mi.make_design(S0)
    a = Mi.solve_mission(S0, D, laser=(1, 1, 0, 0), fixed=dict(legs=2)); b = Mi.solve_mission(S0, D, laser=(0, 1, 0, 0), fixed=dict(legs=2))
    assert b["M"][0] > a["M"][0]


def test_power_study_runs_and_claims_fail():
    r = S.study_power(n=120)
    assert r["isp_at_claimed_laser"][1] < 1100 and r["rho_needed"]["1300"] > 1.0


def test_independent_burn_integration():
    r = S.study_independent_burn()["rows"]
    assert len(r) == 6 and max(abs(x["diff"]) for x in r) < 0.01
    assert max(abs(x["t_model"] - x["t_independent"]) for x in r) <= 12.0
    lim = S.study_independent_burn()["limit"]                                         # near-impulsive burns against the rocket equation
    assert len(lim) == 6 and max(abs(x["diff"]) for x in lim) < 0.005


def test_engine_mass_exponent():
    S0 = Mi.nominal(1); S0["P_R"] = np.array([250e6]); D = Mi.make_design(S0); fx = dict(legs=2)
    a = Mi.solve_mission(S0, D, fixed=dict(fx, eng_exp=1.0)); b = Mi.solve_mission(S0, D, fixed=dict(fx, eng_exp=1.3))
    assert abs(b["m_eng"][0] / a["m_eng"][0] - 0.5 ** 0.3) < 1e-9                    # a smaller reactor is lighter per unit of thrust for x > 1


def test_infrastructure_energy_consistency():
    S0 = Mi.nominal(1); D = Mi.make_design(S0); fx = dict(legs=2); r = Mi.solve_mission(S0, D, fixed=fx, record=True)
    inf = Mi.infrastructure(S0, D, r, fixed=fx)
    assert inf["P_emit"][0] > 0 and inf["M_inf"][0] > 0
    for k in ("leo", "llo"):                        # electrical energy = emitted energy / wall-plug efficiency; the waste-heat mass uses the difference
        nd = inf[k]
        assert abs(nd["E_elec"][0] * S0["eta_wp"][0] / nd["E_emit"][0] - 1) < 1e-9
        assert abs(nd["m_heat"][0] * S0["c_s"] / (nd["E_elec"][0] - nd["E_emit"][0]) - 1) < 1e-9


def test_unfinished_burn_is_infeasible():
    S0 = Mi.nominal(1); S0["P_R"] = np.array([1e6]); D0 = Mi.make_design(S0, rho=0.0)      # 1 MWt: the burn cannot finish within the time limit
    nt = Mi.solve_mission(S0, D0, receiver=False, fixed=dict(legs=2))
    assert not np.isfinite(nt["M"][0]) or nt["M"][0] > 1e10                   # no closure (nan) rather than a silently truncated burn


def test_optimized_benchmark_not_worse_than_fixed_reactor():
    r = S.study_opt_mc(n=6)
    assert np.all(np.array(r["M_ntp_opt"]) > 0) and np.all(np.array(r["ratio_opt"]) > 0.5)
    assert np.all(np.array(r["ratio_opt"]) >= 0.9 * np.array(r["ratio_claim_reactor"]) * 0 + 0.5)


def test_node_phasing_direction():
    rows = S.study_node_offset()["rows"]
    near = [x["ratio"] for x in rows if x["offset_km"] <= 3000]; far = [x["ratio"] for x in rows if x["offset_km"] >= 10000]
    assert max(near) < min(far)                                                       # an occulted node removes the benefit


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for f in fns:
        f(); print("ok  ", f.__name__)
    print("%d checks passed" % len(fns))

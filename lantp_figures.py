# -*- coding: utf-8 -*-
"""Figures of the LANTP assessment, drawn from results/results.json (python lantp_studies.py --figures)."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
C1, C2, C3, C4, GR = "#1f4e9c", "#d1495b", "#2a9d8f", "#e9a23b", "0.35"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "mathtext.fontset": "dejavusans"})


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_thermo(R):
    T = np.array(R["thermo"]["T"]); t = R["thermo"]
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.1))
    for k, ls, lab in (("alpha_2", "--", "2 MPa"), ("alpha_3", "-", "3 MPa"), ("alpha_7", ":", "7 MPa")):
        ax[0].plot(T, t[k], ls, color=C1, lw=1.4, label=lab)
    ax[0].axvspan(2600, 2900, color="0.88"); ax[0].text(2650, 0.9, "core\nlimit", fontsize=7); ax[0].axvline(4500, color=C2, lw=0.8)
    ax[0].set_xlabel("Chamber temperature $T_c$ (K)"); ax[0].set_ylabel("H$_2$ dissociation degree $\\alpha$"); ax[0].legend(frameon=False); ax[0].set_title("(a)", loc="left", fontsize=9)
    ax[1].axhspan(1300, 1500, color=C4, alpha=0.25); ax[1].text(2050, 1510, "claimed 1300-1500 s", fontsize=7)
    ax[1].plot(T, t["frozen"], color=C1, lw=1.4, label="frozen, $\\phi=0$"); ax[1].plot(T, t["partial"], color=C3, lw=1.4, label="partial, $\\phi=0.3$"); ax[1].plot(T, t["shifting"], "--", color=GR, lw=1.4, label="shifting equilibrium (bound)")
    ax[1].plot(T, t["eq1_14"], ":", color=C2, lw=1.6, label="ideal gas, $\\gamma=1.4$"); ax[1].plot(T, t["eq1_13"], "-.", color=C2, lw=1, label="ideal gas, $\\gamma=1.3$"); ax[1].axvline(4500, color=C2, lw=0.8)
    ax[1].set_ylim(600, 2300); ax[1].set_xlabel("Chamber temperature $T_c$ (K)"); ax[1].set_ylabel("Specific impulse (s)"); ax[1].legend(frameon=False, fontsize=6.5, loc="upper left"); ax[1].set_title("(b) $p_c$ = 3 MPa, $\\eta_n$ = 0.94", loc="left", fontsize=9)
    save(fig, "Fig2_thermochemistry.png")


def fig_power(R):
    p = R["power"]; rho = np.array(p["rho"])
    fig, ax = plt.subplots(figsize=(4.4, 3.3))
    ax.axvspan(0.001, p["rho_claim"][1], color=C2, alpha=0.15); ax.text(0.0014, 2200, "claimed 1-50 MW laser\non 100-500 MW$_t$ reactor", color=C2, fontsize=7, va="top")
    ax.axhspan(1300, 1500, color=C4, alpha=0.25)
    ax.fill_between(rho, p["q05"], p["q95"], color=C1, alpha=0.3, label="Monte Carlo 5-95%"); ax.plot(rho, p["q50"], color=C1, lw=1.6, label="median")
    ax.plot(rho, p["frozen"], ":", color=GR, lw=1.2, label="frozen (nominal)"); ax.plot(rho, p["shifting"], "--", color=GR, lw=1.2, label="shifting equilibrium (nominal)")
    ax.set_xscale("log"); ax.set_xlim(0.001, 6); ax.set_ylim(700, 2400); ax.set_xlabel("Useful laser power / reactor thermal power"); ax.set_ylabel("Specific impulse (s)"); ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    save(fig, "Fig3_power_closure.png")


def fig_laser(R):
    lt = R["laser_thrust"]; F = np.array(lt["F_kN"])
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    for key, col in (("1300", C3), ("1400", C1), ("1500", C2)):
        rows = lt[key]; ax.plot(F, [r["P_emit"][1] for r in rows], color=col, lw=1.6, label="target $I_{sp}$ %s s" % key)
        ax.fill_between(F, [r["P_emit"][0] for r in rows], [r["P_emit"][2] for r in rows], color=col, alpha=0.12)
    ax.axvspan(50, 120, color="0.9"); ax.text(52, 8e4, "claimed thrust\n50-120 kN", fontsize=7, va="top")
    ax.axhspan(1, 50, color=C2, alpha=0.15); ax.text(22, 1.6, "claimed 'multi-megawatt' (1-50 MW)", color=C2, fontsize=7)
    ax.set_yscale("log"); ax.set_ylim(1, 1e5); ax.set_xlabel("Thrust (kN)"); ax.set_ylabel("Emitted laser power (MW)"); ax.legend(frameon=False, fontsize=7, loc="lower right", bbox_to_anchor=(1, 0.2))
    save(fig, "Fig4_laser_power_thrust.png")


def fig_beam(R):
    b = R["beam"]; Rk = np.array(b["R_km"])
    fig, ax = plt.subplots(figsize=(4.4, 3.3))
    for key, col, ls, lab in (("D5", C2, "-", "$D_t$ = 5 m, 0.05 $\\mu$rad"), ("D10", C1, "-", "$D_t$ = 10 m, 0.05 $\\mu$rad"), ("D20", C3, "-", "$D_t$ = 20 m, 0.05 $\\mu$rad"), ("D10_j", C1, "--", "$D_t$ = 10 m, 0.3 $\\mu$rad")):
        ax.plot(Rk, b[key], ls, color=col, lw=1.5, label=lab)
    for x, lab in ((2e3, "LOI burn"), (4e4, "TLI burn"), (6e4, "L1-LLO"), (3.2e5, "LEO-L1")):
        ax.axvline(x, color="0.4", lw=0.7, ls=":"); ax.text(x * 1.05, 0.93, lab, rotation=90, fontsize=6.5, va="top")
    ax.set_xscale("log"); ax.set_xlabel("Range (km)"); ax.set_ylabel("Fraction of beam captured"); ax.text(110, 0.05, "$r_R$ = 3 m, $M^2$ = 1.2, $\\lambda$ = 1.07 $\\mu$m", fontsize=6.5); ax.legend(frameon=False, fontsize=6.5, loc="center left")
    save(fig, "Fig5_beam_link.png")


def fig_burn(R):
    n = R["nominal"]
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 4.6))
    for j, (key, ttl) in enumerate((("tli", "(a) TLI (LEO node)"), ("loi", "(b) LOI (LLO node)"))):
        h = n[key]; t = np.array(h["t"]); occ = np.array(h["occ"])
        ax[0, j].plot(t, h["R"], color=C1, lw=1.5); ax[0, j].set_ylabel("Node-ship range (km)"); ax[0, j].set_title(ttl, loc="left", fontsize=9)
        if occ.any():
            t0 = t[occ.argmax()]; ax[0, j].axvspan(t0, t[-1], color=C2, alpha=0.2); ax[1, j].axvspan(t0, t[-1], color=C2, alpha=0.2)
        ax[1, j].plot(t, h["isp"], color=C2, lw=1.5); ax[1, j].set_ylabel("Instantaneous $I_{sp}$ (s)"); ax[1, j].set_xlabel("Burn time (min)")
    save(fig, "Fig6_burn_timeline.png")


def fig_mc(R):
    m = R["mc"]; ratio = np.array(m["ratio"])
    fig, ax = plt.subplots(1, 3, figsize=(7.8, 2.9))
    ax[0].hist(m["isp_design"], bins=40, color=C1, alpha=0.8); ax[0].axvspan(1300, 1500, color=C4, alpha=0.25); ax[0].set_xlabel("$I_{sp}$ at $T_c$ = 4500 K design (s)"); ax[0].set_ylabel("Trials"); ax[0].set_title("(a)", loc="left", fontsize=9)
    ax[1].hist(m["isp_eff_tli"], bins=40, color=C1, alpha=0.8); ax[1].set_xlabel("Effective $I_{sp}$ of the TLI burn (s)\n(finite burn, link losses)"); ax[1].set_title("(b)", loc="left", fontsize=9)
    ax[2].hist(ratio[np.isfinite(ratio)], bins=np.linspace(0.5, 8, 60), color=C1, alpha=0.8); ax[2].axvline(1.0, color="0.3", lw=1); ax[2].axvline(0.6, color=C2, ls="--", lw=1.2); ax[2].text(0.65, ax[2].get_ylim()[1] * 0.9, "claimed\n$-$40%", color=C2, fontsize=7)
    ax[2].set_xlabel("IMLEO(LANTP) / IMLEO(NTP)"); ax[2].set_title("(c)", loc="left", fontsize=9)
    save(fig, "Fig7_mc_distributions.png")


def fig_tradeoffs(R):
    a, b = R["ratio_rho"], R["ratio_mu"]
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    rho = a["rho"]; ax[0].fill_between(rho, [r["q"][0] for r in a["rows"]], [r["q"][2] for r in a["rows"]], color=C1, alpha=0.3); ax[0].plot(rho, [r["q"][1] for r in a["rows"]], "o-", color=C1, ms=3)
    ax[0].axhline(1, color="0.3", lw=1); ax[0].axhline(0.6, color=C2, ls="--", lw=1.2); ax[0].text(0.05, 0.62, "claimed $-$40%", color=C2, fontsize=7); ax[0].set_xscale("log"); ax[0].set_xlabel("Useful laser power / reactor power"); ax[0].set_ylabel("IMLEO(LANTP) / IMLEO(NTP)"); ax[0].set_title("(a) 5-95% band, median", loc="left", fontsize=9); ax[0].set_ylim(0.5, 4.5)
    mu = b["mu"]
    for key, col, lab in (("design", C1, "$T_c$ = 4500 K design"), ("rho025", C3, "laser = 0.25 x reactor")):
        rows = b[key]; ax[1].fill_between(mu, [r["q"][0] for r in rows], [r["q"][2] for r in rows], color=col, alpha=0.2); ax[1].plot(mu, [r["q"][1] for r in rows], "o-", color=col, ms=3, label=lab)
    ax[1].axhline(1, color="0.3", lw=1); ax[1].set_xscale("log"); ax[1].set_xlabel("Receiver specific mass (kg per MW absorbed)"); ax[1].set_title("(b) median, interquartile band", loc="left", fontsize=9); ax[1].legend(frameon=False, fontsize=7)
    save(fig, "Fig8_imleo_trade.png")


def fig_breakeven(R):
    be = R["breakeven"]; mu = np.array(be["mu"]); rho = np.array(be["rho"]); Z = np.array(be["ratio_mu_rho"], float)
    fig, ax = plt.subplots(1, 3, figsize=(7.8, 2.9))
    cs = ax[0].contourf(rho, mu, Z, levels=[0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0], cmap="RdYlBu_r", extend="both"); ax[0].contour(rho, mu, Z, levels=[1.0], colors="k", linewidths=1.2)
    ax[0].set_xlabel("Useful laser power / reactor power"); ax[0].set_ylabel("Receiver specific mass (kg/MW)"); ax[0].set_title("(a) IMLEO ratio, 20 t payload", loc="left", fontsize=9); fig.colorbar(cs, ax=ax[0], fraction=0.05)
    pl = be["payload"]; ax[1].plot([p["m_pl"] / 1e3 for p in pl], [p["ratio"] for p in pl], "o-", color=C1, ms=3); ax[1].axhline(1, color="0.3", lw=1); ax[1].set_xscale("log"); ax[1].set_xlabel("Payload (t), $\\mu$ = 10 kg/MW"); ax[1].set_ylabel("IMLEO(LANTP) / IMLEO(NTP)"); ax[1].set_title("(b)", loc="left", fontsize=9)
    N = np.array(be["N_star"], float); N[~np.isfinite(N)] = np.nan
    for i, r_ in enumerate(rho[:4]):
        ax[2].plot(mu, N[:, i], "o-", ms=3, label="$\\rho$ = %g" % r_)
    ax[2].set_yscale("log"); ax[2].set_xscale("log"); ax[2].set_xlabel("Receiver specific mass (kg/MW)"); ax[2].set_ylabel("Missions to amortize the laser nodes"); ax[2].legend(frameon=False, fontsize=6.5); ax[2].set_title("(c)", loc="left", fontsize=9)
    save(fig, "Fig9_breakeven.png")


def fig_sens(R):
    s = sorted(R["sensitivity"], key=lambda r: abs(r["rho"])); so = R["sobol"]
    fig, ax = plt.subplots(1, 2, figsize=(7.8, 3.3))
    ax[0].barh(range(len(s)), [r["rho"] for r in s], color=[C2 if r["rho"] > 0 else C1 for r in s]); ax[0].set_yticks(range(len(s))); ax[0].set_yticklabels([r["name"] for r in s], fontsize=7); ax[0].axvline(0, color="k", lw=0.8)
    ax[0].set_xlabel("Spearman rank correlation with the IMLEO ratio"); ax[0].set_title("(a)", loc="left", fontsize=9)
    o = np.argsort(so["ST"]); y = np.arange(len(o))
    ax[1].barh(y + 0.2, [so["ST"][i] for i in o], 0.4, color=C2, label="total index $S_T$", xerr=[[so["ST"][i] - so["ST_lo"][i] for i in o], [so["ST_hi"][i] - so["ST"][i] for i in o]], error_kw=dict(lw=0.7))
    ax[1].barh(y - 0.2, [so["S1"][i] for i in o], 0.4, color=C1, label="first-order index $S_1$")
    ax[1].set_yticks(y); ax[1].set_yticklabels([so["names"][i] for i in o], fontsize=7); ax[1].axvline(0, color="k", lw=0.8); ax[1].set_xlabel("Sobol index of the IMLEO ratio"); ax[1].legend(frameon=False, fontsize=7, loc="lower right"); ax[1].set_title("(b)", loc="left", fontsize=9)
    save(fig, "Fig10_sensitivity.png")


def fig_threshold(R):
    t = R["threshold"]; Z = np.array(t["ratio"]); P = np.array(t["P_use_GW"]); mu = np.array(t["mu"]); Tc = np.array(t["Tc"])
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    cs = ax.contourf(P, mu, Z.T, levels=[0.5, 0.6, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0], cmap="RdYlBu_r", extend="both"); fig.colorbar(cs, ax=ax, label="IMLEO ratio")
    c1 = ax.contour(P, mu, Z.T, levels=[1.0], colors="k", linewidths=1.4); ax.clabel(c1, fmt="ratio 1", fontsize=7)
    c9 = ax.contour(P, mu, Z.T, levels=[0.9], colors="k", linewidths=0.9, linestyles="--"); ax.clabel(c9, fmt="0.9", fontsize=7)
    Tm = 4232.0
    if Tc.max() > Tm:
        Pm = float(np.interp(Tm, Tc, P)); ax.axvspan(Pm, P.max(), facecolor="none", hatch="//", edgecolor="0.3", lw=0); ax.axvline(Pm, color="0.2", lw=1.0)
        ax.text(Pm * 0.97, 12.0, "chamber above 4232 K (highest measured melting temperature) →", fontsize=6.3, rotation=90, ha="right", va="bottom")
    ax.text(P.min() * 1.1, 1.2, "mass-beneficial region\n(below the line)", fontsize=7)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Useful laser power (GW), reactor 500 MWt"); ax.set_ylabel("Receiver specific mass (kg per MW absorbed)")
    save(fig, "Fig13_threshold_map.png")


def fig_conv(R):
    c = R["convergence"]; fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax[0].plot(c["tof"], c["dv_tli"], color=C1, label="$\\Delta v_{TLI}$"); ax[0].plot(c["tof"], c["dv_loi"], color=C2, label="$\\Delta v_{LOI}$"); ax[0].plot(c["tof"], np.array(c["dv_tli"]) + np.array(c["dv_loi"]), "--", color=GR, label="sum (one way)")
    ax[0].axvspan(1.8, 2.2, color=C4, alpha=0.25); ax[0].set_xlabel("Time of flight (days)"); ax[0].set_ylabel("Impulsive $\\Delta v$ (km/s)"); ax[0].legend(frameon=False, fontsize=7); ax[0].set_title("(a)", loc="left", fontsize=9)
    ax[1].plot(c["N"], c["median"], "o-", color=C1, ms=3); ax[1].axhspan(*c["median_ci"], color=C1, alpha=0.15); ax[1].set_xscale("log"); ax[1].set_xlabel("Monte Carlo trials $N$"); ax[1].set_ylabel("Median IMLEO ratio"); ax[1].set_title("(b) band: 95% bootstrap interval at full $N$", loc="left", fontsize=8)
    save(fig, "Fig11_transfer_convergence.png")


def fig_conting(R):
    c = R["contingency"]; fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    names = list(c["policies"].keys()); lab = ["nominal", "reactor-only TLI\n(single fault)", "full fallback"]
    for i, nme in enumerate(names):
        qq = c["policies"][nme]["q"]; ax[0].bar(i, qq[2], color=[C3, C4, C2][i], alpha=0.85); ax[0].plot([i, i], [qq[0], qq[4]], "k-", lw=1); ax[0].plot([i, i], [qq[1], qq[3]], "k-", lw=4)
    ax[0].axhline(1, color="0.3", lw=1); ax[0].set_xticks(range(3)); ax[0].set_xticklabels(lab, fontsize=7); ax[0].set_ylabel("IMLEO(LANTP policy) / IMLEO(NTP)"); ax[0].set_title("(a) median, IQR, 5-95%", loc="left", fontsize=9)
    oc = c["outage_curve"]; ax[1].plot([r["t_out_frac"] for r in oc], [r["burned_t"] for r in oc], "o-", color=C1, ms=3); ax[1].axhline(c["tli_nominal_burned_t"], color=C3, ls="--", lw=1); ax[1].text(0.02, c["tli_nominal_burned_t"] + 0.3, "no outage", color=C3, fontsize=7)
    ax[1].set_xlabel("Laser lost at this fraction of the nominal TLI burn"); ax[1].set_ylabel("Propellant for the TLI burn (t)"); ax[1].set_title("(b) nominal vehicle", loc="left", fontsize=9)
    save(fig, "Fig12_contingency.png")


def fig_ast(R):
    a = R["asteroid"]; fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    D = np.array(a["main"]["D"]); ax[0].fill_between(D, a["main"]["q05"], a["main"]["q95"], color=C1, alpha=0.3); ax[0].plot(D, a["main"]["q50"], color=C1, lw=1.6); ax[0].axhline(1, color=C2, ls="--", lw=1); ax[0].text(2.5, 1.3, "required displacement (1 $R_\\oplus$)", color=C2, fontsize=7)
    ax[0].axvspan(40, 90, color="0.88"); ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_xlabel("Asteroid diameter (m)"); ax[0].set_ylabel("Achieved / required displacement"); ax[0].set_title("(a) 1.4 GW, 10 m aperture", loc="left", fontsize=9)
    P = np.array(a["P_gw"])
    for k, col in (("10", C1), ("30", C3), ("100", C2)):
        ax[1].plot(P, np.maximum(a["largest_diameter"][k], 0.5), "o-", ms=3, color=col, label="%s m aperture" % k)
    ax[1].axhspan(40, 90, color=C2, alpha=0.15); ax[1].text(0.35, 55, "2024 YR4 class", fontsize=7); ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlabel("Emitted laser power (GW)"); ax[1].set_ylabel("Largest deflectable diameter (m)"); ax[1].legend(frameon=False, fontsize=7); ax[1].set_title("(b) median over uncertainty", loc="left", fontsize=9)
    save(fig, "FigS1_asteroid.png")


def make_all(R):
    os.makedirs(FIG, exist_ok=True)
    for f in (fig_thermo, fig_power, fig_laser, fig_beam, fig_burn, fig_mc, fig_tradeoffs, fig_breakeven, fig_sens, fig_conv, fig_conting, fig_ast, fig_threshold):
        f(R)
    print("figures written")

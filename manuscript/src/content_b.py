# -*- coding: utf-8 -*-
"""Manuscript, part B: Results (Section 6)."""
from common import *

RHO = BE["rho"]; MU = BE["mu"]; Zg = np.array(BE["ratio_mu_rho"], float); Ns = np.array(BE["N_star"], float)
BEST = BM["best"]; INF = NOM["infra"]; CAP = BM["capture_at_segments"]
POL = CT["policies"]; PK = list(POL.keys())
QO = OPT["q_ratio_opt"]; QC = OPT["q_ratio_claim_reactor"]
SO = dict(zip(SOB["keys"], zip(SOB["S1"], SOB["ST"], SOB["ST_lo"], SOB["ST_hi"])))
GWH = 3.6e12

add(("h1", "6. Results"))
add(("p", "All results are conditional on the assumed ranges of Table @T:rng@. Probabilities and percentiles describe the assumed uncertainty, not field statistics. Unless stated, the mission is a one-way delivery of 20 t at a transfer time of 2 days."))

# ------------------------------------------------------------------------------------------- 6.1 thermochemistry
add(("h2", "6.1 Hydrogen thermochemistry and validation"))
add(("fig", "Fig2_thermochemistry.png", "Fig. @F:thermo@. (a) Equilibrium dissociation degree of hydrogen against chamber temperature at three pressures. (b) Specific impulse for frozen flow, partial recombination, the shifting-equilibrium bound and the ideal-gas formula without dissociation, for $η_n$ = 0.94 (vertical line: 4500 K; band: targeted 1300–1500 s).", 6.4))
i45 = next(i for i in VAL["isp"] if i["Tc"] == 4500.0 and i["p_c"] == 3e6)
add(("p", fmt("The dissociation degree at 3 MPa is <<a3>> at 4500 K and the core limit of 2600–2900 K lies below the onset of dissociation (Fig. @F:thermo@a). Table @T:val@ compares the model with Cantera at identical conditions: the same temperature, pressure, expansion ratio ($p_e=10^{-4}p_c$) and, for the specific impulse, the same nozzle efficiency, first 1 (the isentropic limit, which Cantera computes) and then 0.94 (the value used in Fig. @F:thermo@b and in the rest of the paper, obtained by multiplying the exhaust velocity). "
              "At 4500 K and 3 MPa the frozen specific impulse is <<f1c>> s for Cantera and <<f1m>> s for this model at an efficiency of 1, and <<f94c>> and <<f94m>> s at 0.94; the shifting-equilibrium bound is <<s1c>> and <<s1m>> s at 1, and <<s94c>> and <<s94m>> s at 0.94. The values of Fig. @F:thermo@b and of the text (<<f94m>> s frozen, <<s94m>> s shifting) are thus the efficiency-0.94 values of the same calculation. "
              "Recombination of 30% of the dissociation energy (Fig. @F:thermo@b) has no Cantera counterpart and gives <<pa>> s; the ideal-gas formula, which neglects dissociation, gives <<g14>> s (γ = 1.4) and <<g13>> s (γ = 1.3). "
              "Over the validation cases the dissociation degree of this model is higher than that of Cantera by <<ae1>> to <<ae2>>, the frozen specific impulse lower by <<fe1>> to <<fe2>> and the shifting-equilibrium bound within <<se1>> to <<se2>>; the difference in the dissociation degree is that of a rigid-rotor, harmonic-oscillator model without anharmonicity and is not corrected. "
              "The targeted 1300–1500 s at 4500 K is reached only if a substantial part of the dissociation energy is recovered in the nozzle, which depends on nozzle kinetics that this model does not resolve; at the core limit the specific impulse is <<ntp>> s. "
              "The minimization of the Gibbs energy agrees with the analytic equilibrium to <<gib>> in the dissociation degree, which verifies the equilibrium solver but not the thermodynamic data.",
              a3=n(float(np.interp(4500, TH["T"], TH["alpha_3"])), 2), f1c=n(i45["frozen_ref"], 0), f1m=n(i45["frozen_mine"], 0), f94c=n(i45["frozen_ref94"], 0), f94m=n(i45["frozen_mine94"], 0), s1c=n(i45["shifting_ref"], 0), s1m=n(i45["shifting_mine"], 0), s94c=n(i45["shifting_ref94"], 0), s94m=n(i45["shifting_mine94"], 0),
              pa=n(float(np.interp(4500, TH["T"], TH["partial"])), 0), g14=n(float(np.interp(4500, TH["T"], TH["eq1_14"])), 0), g13=n(float(np.interp(4500, TH["T"], TH["eq1_13"])), 0), ntp=n(PW["isp_ntp"][1], 0),
              ae1=pc(min(A_ERR), 0), ae2=pc(max(A_ERR), 0), fe1=pc(-max(FRZ_ERR), 1), fe2=pc(-min(FRZ_ERR), 1), se1=pc(min(SHF_ERR), 1), se2=pc(max(SHF_ERR), 1), gib="%.0e" % max(abs(g["gibbs"] - g["analytic"]) for g in VAL["gibbs"]))))
rows = [["α", "%g K, %g MPa" % (a["T"], a["p"] / 1e6), n(a["ref"], 4), n(a["mine"], 4), pc(a["mine"] / a["ref"] - 1, 1), "–"] for a in VAL["alpha"][:5]]
rows += [["Isp frozen (s)", "%g K, %g MPa" % (i["Tc"], i["p_c"] / 1e6), n(i["frozen_ref"], 0), n(i["frozen_mine"], 0), pc(i["frozen_mine"] / i["frozen_ref"] - 1, 1), n(i["frozen_mine94"], 0)] for i in VAL["isp"]]
rows += [["Isp shifting (s)", "%g K, %g MPa" % (i["Tc"], i["p_c"] / 1e6), n(i["shifting_ref"], 0), n(i["shifting_mine"], 0), pc(i["shifting_mine"] / i["shifting_ref"] - 1, 1), n(i["shifting_mine94"], 0)] for i in VAL["isp"]]
add(("table", "Table @T:val@. Validation of the hydrogen model against %s at identical conditions (equilibrium and isentropic expansion to $p_e=10^{-4}p_c$). The specific-impulse columns for $η_n$ = 1 compare the two solvers; the last column is the value of this model at the nozzle efficiency of 0.94 used in the paper (the Cantera value at 0.94 is 0.94 times the reference)." % VAL.get("tool", "Cantera"),
     ["Quantity", "Condition", "Reference", "This model", "Difference", "This model, $η_n$ = 0.94"], rows, [1.4, 1.5, 0.9, 0.9, 0.9, 1.3], 15))

# ------------------------------------------------------------------------------------------- 6.2 power closure
add(("h2", "6.2 Power closure: the laser fraction required"))
add(("fig", "Fig3_power_closure.png", "Fig. @F:power@. Specific impulse against the useful laser power as a fraction of the reactor power: Monte Carlo median and 5–95% band, the frozen and shifting-equilibrium bounds for the nominal parameters, the targeted laser class (shaded) and the targeted specific impulse (band).", 4.4))
add(("p", fmt("With the reactor alone the specific impulse is <<ntp>> s (5th–95th percentile <<n5>>–<<n95>> s). Reaching 1300, 1400 and 1500 s at the median of the parameters requires a useful laser power of <<r13>>, <<r14>> and <<r15>> times the reactor power (Fig. @F:power@); with 4500 K as the design point the fraction is <<rd>>. "
              "A laser of 1–50 MW on a reactor of 100–500 MWt corresponds to a fraction between <<c1>> and <<c2>>, and the specific impulse at those two ends is <<i1>> and <<i2>> s. The targeted performance is therefore inconsistent with the targeted laser power: the most favorable end of the combination (50 MW on 100 MWt) is short by a factor of <<f1>>, and the other end by a factor of more than <<f2>> (H1). "
              "The reason is the enthalpy balance: heating hydrogen from the core limit to 4500 K, including dissociation, needs about <<h>> times the enthalpy that the reactor delivers between the tank and the core outlet.",
              ntp=n(PW["isp_ntp"][1], 0), n5=n(PW["isp_ntp"][0], 0), n95=n(PW["isp_ntp"][2], 0), r13=n(PW["rho_needed"]["1300"], 1), r14=n(PW["rho_needed"]["1400"], 1), r15=n(PW["rho_needed"]["1500"], 1), rd=n(NOM["rho"], 1),
              c1=n(PW["rho_claim"][0], 3), c2=n(PW["rho_claim"][1], 2), f1=n(PW["rho_needed"]["1300"] / PW["rho_claim"][1], 0), f2=n(round(PW["rho_needed"]["1300"] / PW["rho_claim"][0], -2), 0),
              i1=n(PW["isp_at_claimed_laser"][0], 0), i2=n(PW["isp_at_claimed_laser"][1], 0), h=n(NOM["rho"], 1))))

# ------------------------------------------------------------------------------------------- 6.3 laser power at the targeted thrust
add(("h2", "6.3 Emitted laser power at the targeted thrust"))
add(("fig", "Fig4_laser_power_thrust.png", "Fig. @F:laser@. Emitted laser power required for a given thrust and specific impulse (median and 5–95% band over the parameters), against the targeted thrust (band) and the targeted laser class (shaded).", 4.4))
p50 = lt_at(1400, 50); p120 = lt_at(1400, 120)
add(("p", fmt("For a thrust of 50 kN at 1400 s the emitted laser power is <<a>> MW (5th–95th percentile <<a5>>–<<a95>> MW), and for 120 kN <<b>> MW (<<b5>>–<<b95>> MW) (Fig. @F:laser@), against the targeted 1–50 MW. These are emitted powers at the start of the burn, where the beam is captured almost completely; "
              "they include the receiver, optics and coupling efficiencies of Section 4 and need an electrical power of <<e1>>–<<e2>> GW at the median wall-plug efficiency. Table @T:chain@ gives the power chain for the nominal vehicle: a useful power of <<u>> GW on the propellant needs <<em>> GW of emitted power and <<el>> GW of electrical power, "
              "and rejects <<w1>> GW of waste heat at the node and <<w2>> GW at the receiver.",
              a=n(p50[1], 0), a5=n(p50[0], 0), a95=n(p50[2], 0), b=n(p120[1], 0), b5=n(p120[0], 0), b95=n(p120[2], 0), e1=n(p50[1] / 0.4 / 1e3, 1), e2=n(p120[1] / 0.4 / 1e3, 1),
              u=n(NOM["P_use"] / 1e9, 2), em=n(NOM["P_emit"] / 1e9, 2), el=n(NOM["P_elec"] / 1e9, 2), w1=n(NOM["P_waste_node"] / 1e9, 2), w2=n(NOM["P_waste_rec"] / 1e9, 2))))
rows = [["Reactor thermal power $P_R$", n(NOM["P_R"] / 1e6, 0) + " MW"], ["Useful thermal power on the propellant $P_{use}=ρP_R$ (ρ = %s)" % n(NOM["rho"], 2), n(NOM["P_use"] / 1e6, 0) + " MW"],
        ["Absorbed by the receiver $P_{abs}$ (coupling 0.90)", n(NOM["P_abs"] / 1e6, 0) + " MW"], ["Received at the aperture $P_{rec}$ (absorption 0.95)", n(NOM["P_rec"] / 1e6, 0) + " MW"],
        ["Emitted by the node $P_{emit}$ (optics 0.9, capture at 1000 km)", n(NOM["P_emit"] / 1e6, 0) + " MW"], ["Electrical power $P_{elec}$ (wall plug 0.4)", n(NOM["P_elec"] / 1e6, 0) + " MW"],
        ["Waste heat at the laser node", n(NOM["P_waste_node"] / 1e6, 0) + " MW"], ["Waste heat at the receiver", n(NOM["P_waste_rec"] / 1e6, 0) + " MW"],
        ["Thrust (reactor only: %s kN)" % n(NOM["F_ntp_kN"], 0), n(NOM["F_kN"], 0) + " kN"], ["Specific impulse (reactor only: %s s)" % n(NOM["isp_ntp"], 0), n(NOM["isp"], 0) + " s"]]
add(("table", "Table @T:chain@. Power chain of the nominal vehicle at a chamber temperature of 4500 K.", ["Quantity", "Value"], rows, [4.6, 1.4]))

# ------------------------------------------------------------------------------------------- 6.4 beam link
add(("h2", "6.4 Beam link"))
add(("fig", "Fig5_beam_link.png", "Fig. @F:beam@. Fraction of the emitted beam captured by a 3 m receiver against range, for three apertures at 0.05 µrad pointing jitter and one at 0.3 µrad (refocused beam, $M^2$ = 1.2, λ = 1.07 µm); vertical lines mark the ranges of the burns and of the relay links.", 4.4))
add(("p", fmt("With a 10 m aperture and 0.05 µrad of jitter the captured fraction is <<c1>> at 1000 km (the start of LOI), <<c2>> at 29,000 km, <<c3>> over the 60,000 km between the L1 relay and the lunar node and <<c4>> over the 320,000 km between the Earth node and L1 (Fig. @F:beam@). "
              "Even a 100 m aperture captures <<c5>> at 60,000 km and <<c6>> at 320,000 km, because the pointing jitter, not diffraction, then limits the spot; the receiver radius needed for half of the beam at 60,000 km is <<rr>> m with a 10 m aperture. "
              "Beaming across the relay legs is therefore excluded and the laser must act while the vehicle is within a few 10$^4$ km of its node, the ranges drawn in Fig. @F:arch@. Tolerating a jitter of 0.3 µrad shortens the range at which half of the beam is captured with the 10 m aperture to about <<rj>> km (Supplementary Information).",
              c1=n(CAP["LOI_start"], 2), c2=n(BEST["TLI_end"]["capture_10m"], 2), c3=n(CAP["L1_LLO"], 2), c4=n(CAP["LEO_L1"], 3), c5=n(BEST["L1_LLO"]["capture_100m"], 2), c6=n(BEST["LEO_L1"]["capture_100m"], 3), rr=n(BEST["L1_LLO"]["r_R_for_half_10m"], 1),
              rj=r100(next(t["r50"] for t in BM["range_table"] if t["Dt"] == 10.0 and t["jit"] == 0.3)))))

# ------------------------------------------------------------------------------------------- 6.5 finite burns and node geometry
add(("h2", "6.5 Finite burns, occultation, link losses and node phasing"))
add(("fig", "Fig6_burn_timeline.png", "Fig. @F:burn@. Burn timelines of the nominal vehicle: node–vehicle range and instantaneous specific impulse during (a) TLI and (b) LOI; shaded: line of sight blocked by the Earth or the Moon.", 6.0))
no = {int(r["offset_km"]): r for r in NOFF["rows"]}
add(("p", fmt("The nominal LANTP tug (initial mass <<M>> t, thrust <<F>> kN) burns for <<t1>> min during TLI and <<t2>> min during LOI, against <<n1>> and <<n2>> min for the reactor-only tug of <<Mn>> t (Fig. @F:burn@). "
              "In the nominal case the TLI burn ends within <<rmax>> km of the node, so that the beam is captured completely and the specific impulse stays at the design value; during LOI the Moon blocks the line of sight <<tocc>> min after the start of the burn, and the specific impulse falls to the reactor-only value for the rest of the burn. "
              "Over the Monte Carlo draws the lower power of the weaker links and the gravity losses of the longer burns lower the delivered impulse: the effective specific impulse of the TLI burn, defined by the impulsive $Δv$ and the propellant used and so including gravity losses, has a median of <<ie>> s (5th–95th percentile <<i5>>–<<i95>> s), well below the design value of <<id>> s (Fig. @F:mc@b). "
              "The result depends on the phasing of the node. With the node 500 km, 1000 km and 3000 km ahead of the vehicle at the start of the burn the IMLEO ratio at equal reactor power is <<o1>>, <<o2>> and <<o3>>; with the node 10,000 km ahead the vehicle is occulted by the Earth during the burn, the specific impulse falls to the reactor-only value and the ratio is <<o4>> (<<o5>> at 20,000 km). "
              "The benefit therefore requires a node that stays near the vehicle throughout the burn.",
              M=n(NOM["M"] / 1e3, 0), F=n(NOM["F_kN"], 0), t1=n(NOM["t_burn"][0] / 60, 0), t2=n(NOM["t_burn"][1] / 60, 0), n1=n(NOM["t_burn_ntp"][0] / 60, 0), n2=n(NOM["t_burn_ntp"][1] / 60, 0), Mn=n(NOM["M_ntp"] / 1e3, 0),
              rmax=r100(max(NOM["tli"]["R"])), tocc=n(next(t for t, o in zip(NOM["loi"]["t"], NOM["loi"]["occ"]) if o), 1), ie=n(np.nanmedian(ISPE), 0), i5=n(np.nanpercentile(ISPE, 5), 0), i95=n(np.nanpercentile(ISPE, 95), 0), id=n(np.median(ISPD), 0),
              o1=n(no[500]["ratio"], 2), o2=n(no[1000]["ratio"], 2), o3=n(no[3000]["ratio"], 2), o4=n(no[10000]["ratio"], 2), o5=n(no[20000]["ratio"], 2))))

# ------------------------------------------------------------------------------------------- 6.6 Monte Carlo
add(("h2", "6.6 Monte Carlo analysis of the initial mass"))
add(("p", fmt("Primary benchmark. With the reactor power of each tug chosen to minimize its own initial mass for the same payload (<<No>> draws; reactor power scanned over <<g>> MWt), the laser-assisted tug has an IMLEO ratio with a median of <<m>> (5th–95th percentile <<q5>>–<<q95>>); <<b1>> of the draws are below 1 and <<b6>> reach the targeted ratio of 0.6 (H2). "
              "The optimal reactor power of the conventional tug has a median of <<pn>> MWt (<<pnr>>), that of the laser-assisted tug <<pl>> MWt (5th–95th percentile <<pl5>>–<<pl95>>), because every megawatt of reactor power carries a receiver with it. "
              "Against the same best conventional tug, the laser-assisted tug at the reactor power of the draw (100–500 MWt) has a median ratio of <<c>> (<<c5>>–<<c95>>).",
              No=n(OPT["n"]), g=", ".join(n(x) for x in OPT["grid_MW"]), m=n(QO[2], 2), q5=n(QO[0], 2), q95=n(QO[4], 2), b1=pc(OPT["share_below_1"], 0), b6=pc(OPT["share_below_06"], 0),
              pnr=("the same in at least 90% of the draws" if np.percentile(OPT["best_P_ntp"], 5) == np.percentile(OPT["best_P_ntp"], 95) else "5th–95th percentile %s–%s" % (n(np.percentile(OPT["best_P_ntp"], 5), 0), n(np.percentile(OPT["best_P_ntp"], 95), 0))), pn=n(np.median(OPT["best_P_ntp"]), 0), pn5=n(np.percentile(OPT["best_P_ntp"], 5), 0), pn95=n(np.percentile(OPT["best_P_ntp"], 95), 0), pl=n(np.median(OPT["best_P_lantp"]), 0), pl5=n(np.percentile(OPT["best_P_lantp"], 5), 0), pl95=n(np.percentile(OPT["best_P_lantp"], 95), 0),
              c=n(QC[2], 2), c5=n(QC[0], 2), c95=n(QC[4], 2))))
add(("fig", "Fig7_mc_distributions.png", "Fig. @F:mc@. Monte Carlo distributions at equal reactor power (%s draws): (a) specific impulse at the 4500 K design point, with the targeted band; (b) effective specific impulse of the TLI burn including gravity losses and link losses; (c) IMLEO of the laser-assisted tug divided by that of conventional NTP, with the targeted 40%% reduction." % n(MC["n"]), 6.4))
add(("p", fmt("Secondary comparison at equal reactor power. The design-point specific impulse has a median of <<im>> s (5th–95th percentile <<i5>>–<<i95>> s), and <<ib>> of the draws lie in the targeted band of 1300–1500 s (Fig. @F:mc@a). The IMLEO ratio at equal reactor power has a median of <<m>> (5th–95th percentile <<q5>>–<<q95>>); <<l1>> of the draws are below 1 and <<l6>> reach 0.6 (Fig. @F:mc@c). "
              "The receiver is the main cause: the median receiver mass is <<mr>> t (5th–95th percentile <<mr5>>–<<mr95>> t) against a reactor-only tug of about <<mn>> t. The 95% bootstrap interval of the median ratio at <<N>> draws is <<ci>> (Fig. @F:conv@b).",
              im=n(np.median(ISPD), 0), i5=n(np.percentile(ISPD, 5), 0), i95=n(np.percentile(ISPD, 95), 0), ib=pc(SHARE_IN_BAND, 0), m=n(RQ[2], 2), q5=n(RQ[0], 2), q95=n(RQ[4], 2), l1=pc(SHARE_LT1, 1), l6=pc(SHARE_CLAIM, 1),
              mr=n(np.median(MC["m_rec"]) / 1e3, 1), mr5=n(np.percentile(MC["m_rec"], 5) / 1e3, 1), mr95=n(np.percentile(MC["m_rec"], 95) / 1e3, 1), mn=n(np.median(np.array(MC["M_ntp"])[FIN]) / 1e3, 0),
              ci="%s–%s" % (n(CONV["median_ci"][0], 2), n(CONV["median_ci"][1], 2)), N=n(CONV["N"][-1]))))
add(("fig", "Fig8_imleo_trade.png", "Fig. @F:trade@. IMLEO ratio of the laser-assisted tug to conventional NTP (reactor power of the draw) against (a) the useful laser power fraction (5–95% band and median) and (b) the receiver specific mass, for the 4500 K design point and for a fixed laser fraction of 0.25.", 6.2))
r0 = RR["rows"]
add(("p", fmt("The ratio rises with the laser fraction (Fig. @F:trade@a): its median is <<a1>> at a fraction of 0.1, <<a2>> at 0.5 and <<a3>> at 2, and the lower end of the 5–95% band is <<a4>> at a fraction of 0.25. At a fixed fraction of 0.25 the median ratio is <<b1>> for a receiver of 10 kg/MW and <<b2>> for 80 kg/MW; for the 4500 K design it is <<b3>> and <<b4>> (Fig. @F:trade@b).",
              a1=n(r0[1]["q"][1], 2), a2=n(r0[3]["q"][1], 2), a3=n(r0[5]["q"][1], 2), a4=n(r0[2]["q"][0], 2), b1=n(RM["rho025"][0]["q"][1], 2), b2=n(RM["rho025"][-1]["q"][1], 2), b3=n(RM["design"][0]["q"][1], 2), b4=n(RM["design"][-1]["q"][1], 2))))
add(("fig", "Fig11_transfer_convergence.png", "Fig. @F:conv@. (a) Impulsive $Δv$ of TLI and LOI against the time of flight (band: the 1.8–2.2 day transfer of the nominal case). (b) Convergence of the median IMLEO ratio at equal reactor power with the number of Monte Carlo draws; the band is the 95% bootstrap interval of the median at the full number of draws.", 6.2))

# ------------------------------------------------------------------------------------------- 6.7 global sensitivity
add(("h2", "6.7 Global sensitivity analysis"))
add(("fig", "Fig10_sensitivity.png", "Fig. @F:sens@. Sensitivity of the IMLEO ratio at equal reactor power: (a) Spearman rank correlation with the uncertain parameters (Monte Carlo draws); (b) Sobol first-order and total indices (Saltelli sampling, bars: 95% bootstrap interval of the total index).", 6.4))
S1sum = sum(SOB["S1"])
add(("p", fmt("The rank correlation of the IMLEO ratio with the receiver specific mass is <<s1>>, with the reactor power <<s2>>, with the chamber pressure <<s3>> and with the nozzle recombination fraction <<s4>> (Fig. @F:sens@a). The Sobol indices (<<ns>> evaluations, 14 parameters; Fig. @F:sens@b) show that the receiver specific mass has a total index of <<t1>> (first-order <<f1>>) and the reactor power <<t2>> (first-order <<f2>>); "
              "the sum of the first-order indices is <<ss>>, so that <<ix>> of the variance comes from interactions. The interaction between receiver mass and reactor power is expected: the receiver mass is the product of the specific mass and the absorbed power, which is proportional to the reactor power at the 4500 K design. "
              "All link parameters (jitter, beam quality, dropouts, re-acquisition time) have total indices of <<tl>> or less, and the efficiencies of the receiver (coupling, absorption) <<te>> at most. The conclusions are therefore about the receiver and the reactor, not about the link, once the beam is held (Section 6.5).",
              s1=n([r["rho"] for r in SENS if r["key"] == "mu_rec"][0], 2), s2=n([r["rho"] for r in SENS if r["key"] == "P_R"][0], 2), s3=n([r["rho"] for r in SENS if r["key"] == "p_c"][0], 2), s4=n([r["rho"] for r in SENS if r["key"] == "phi"][0], 2),
              ns=n(SOB["evaluations"]), t1=n(SO["mu_rec"][1], 2), f1=n(SO["mu_rec"][0], 2), t2=n(SO["P_R"][1], 2), f2=n(SO["P_R"][0], 2), ss=n(S1sum, 2), ix=pc(max(0.0, 1 - S1sum), 0),
              tl=n(max(0.01, round(max(SO[k][1] for k in ("jit", "M2", "drop", "t_reacq")) + 0.004, 2)), 2), te=n(max(SO[k][1] for k in ("eta_coup", "eta_abs")), 2))))

# ------------------------------------------------------------------------------------------- 6.8 break-even and threshold map
add(("h2", "6.8 Break-even surfaces and technology-threshold map"))
add(("fig", "Fig9_breakeven.png", "Fig. @F:be@. Break-even analysis for the nominal vehicle (reactor 500 MWt): (a) IMLEO ratio on a grid of receiver specific mass and useful laser power fraction (black line: ratio 1); (b) ratio against payload at a receiver of 10 kg/MW; (c) number of missions over which the laser nodes must be amortized for the spacecraft saving to equal the node mass (missing points: no saving).", 6.4))
mu_cross = cross(MU, Zg[:, 2].tolist(), 1.0); pl = BE["payload"]; pl_cross = cross([p["m_pl"] / 1e3 for p in pl], [p["ratio"] for p in pl], 1.0)
tofr = [t["ratio"] for t in BE["tof"]]
NT = [dict(best=min(x for x in r["M_ntp"] if x), ref=r["M_ntp"][1], lantp=r["M_lantp_10"]) for r in R["ntp_reactor"]["rows"]]
fin_N = Ns[np.isfinite(Ns)]
add(("p", fmt("On the grid of receiver specific mass and laser fraction (Fig. @F:be@a) the IMLEO ratio at the nominal 500 MWt is below 1 only in a small corner: its minimum is <<mn>>, at the smallest receiver (<<mu>> kg/MW) and a laser fraction of <<rho>>; at a fraction of 0.25 the ratio crosses 1 at a receiver of about <<mc>> kg/MW. "
              "The best case saves <<sv>> of the IMLEO, not 40%. The advantage grows with the payload because the fixed receiver is shared by more cargo: against the 500 MWt reference tug the ratio at 10 kg/MW falls below 1 at a payload of about <<plc>> t (Fig. @F:be@b); "
              "against the best conventional tug (reactor scan from 250 to 2000 MWt) the ratio is <<f40>> for 40 t of payload and <<f80>> for 80 t (the best conventional tug weighs <<b40>> t and <<b80>> t), not <<c40>> and <<c80>> against the 500 MWt reference. The transfer time changes the ratio by less than <<tofd>> between 1.8 and 4.5 days. "
              "The laser nodes of Section 6.9 weigh <<mi>> t for the nominal vehicle, so the smallest number of missions that amortizes them on the grid is <<ns>>, against an assumed lifetime of <<nl>> missions, and for most of the grid they are never amortized (Fig. @F:be@c).",
              mn=n(np.nanmin(Zg), 2), mu=n(MU[int(np.unravel_index(np.nanargmin(Zg), Zg.shape)[0])], 0), rho=n(RHO[int(np.unravel_index(np.nanargmin(Zg), Zg.shape)[1])], 2), mc=n(mu_cross, 0) if mu_cross else "n/a", sv=pc(1 - float(np.nanmin(Zg)), 0),
              plc=n(pl_cross, 0) if pl_cross else "more than %s" % n(pl[-1]["m_pl"] / 1e3, 0), f40=n(NT[1]["lantp"] / NT[1]["best"], 2), f80=n(NT[2]["lantp"] / NT[2]["best"], 2), b40=n(NT[1]["best"] / 1e3, 0), b80=n(NT[2]["best"] / 1e3, 0),
              c40=n(NT[1]["lantp"] / NT[1]["ref"], 2), c80=n(NT[2]["lantp"] / NT[2]["ref"], 2), tofd=pc(max(tofr) / min(tofr) - 1, 0), mi=n(NOM["M_inf"] / 1e3, 0), ns=n(float(np.min(fin_N)), 0) if fin_N.size else "n/a", nl=n(NOM["N_life"]))))
add(("fig", "Fig13_threshold_map.png", "Fig. @F:thr@. Technology-threshold map of the nominal vehicle: IMLEO ratio against the useful laser power and the receiver specific mass (reactor 500 MWt). A mass benefit exists below the solid line (ratio 1) and a 10% benefit below the dashed line; the hatched region has a chamber temperature above the highest measured melting temperature of any compound.", 4.8))
m1 = THR["mu_star_1"]; m9 = THR["mu_star_0.9"]; P_ = THR["P_use_GW"]; Tc_ = THR["Tc"]
PH = float(np.interp(4232.0, Tc_, P_)) if max(Tc_) > 4232 else None
add(("p", fmt("Fig. @F:thr@ condenses the result into a threshold: for a useful laser power of <<p1>> GW the receiver must weigh less than <<a1>> kg per MW absorbed for the mass benefit to exist at all, and less than <<a2>> kg/MW at <<p2>> GW; a 10% benefit needs less than <<b1>> kg/MW at <<p3>> GW and is not reached below <<p4>> GW within the range of receiver masses studied (down to 1 kg/MW). "
              "No point of the map reaches the targeted 0.6. The power at which the chamber temperature reaches the highest measured melting temperature of any compound, 4232 K [@Cedillos2016], is <<ph>> GW; the laser powers beyond it require a heating concept that does not rely on a solid wall (Section 4.2). The map is for the nominal reactor, laser-link and mass parameters and the 20 t payload.",
              p1=n(P_[0], 2), a1=n(m1[0], 0), a2=n(m1[-1], 0), p2=n(P_[-1], 1), b1=n(m9[-1], 1), p3=n(P_[-1], 1), p4=n(next(P_[i] for i in range(len(P_)) if m9[i]) if any(m9) else P_[-1], 2), ph=n(PH, 2) if PH else "above the range")))

# ------------------------------------------------------------------------------------------- 6.9 infrastructure and round trip
add(("h2", "6.9 Laser infrastructure and the round trip"))
Eem = INF["leo"]["E_emit"]; Eel = INF["leo"]["E_elec"]; Ew = Eel - Eem
rows = [["Emitted power $P_{emit}$", n(NOM["P_emit"] / 1e9, 2) + " GW"], ["Electrical power at the node $P_{elec}$", n(NOM["P_elec"] / 1e9, 2) + " GW"],
        ["Burn time with the laser on (TLI)", n(NOM["t_burn"][0] / 60, 0) + " min"],
        ["Optical energy emitted $E_{emit}$ (LEO node, TLI)", "%s GWh" % n(Eem / GWH, 2)], ["Electrical energy drawn from the buffer $E_{el}=E_{emit}/η_{wp}$", "%s GWh" % n(Eel / GWH, 2)],
        ["Waste heat to be absorbed $E_w=E_{el}-E_{emit}$", "%s GWh = %s TJ" % (n(Ew / GWH, 2), n(Ew / 1e12, 1))],
        ["Battery buffer $E_{el}/e_s$ (250 Wh/kg)", n(INF["leo"]["m_batt"] / 1e3, 0) + " t"], ["Waste-heat buffer $E_w/c_s$ (1.5 MJ/kg)", n(INF["leo"]["m_heat"] / 1e3, 0) + " t"],
        ["Laser and optics (300 kg/MW emitted)", n(INF["leo"]["m_las"] / 1e3, 0) + " t"], ["Aperture and recharge array", n((INF["leo"]["m_ap"] + INF["leo"]["m_arr"]) / 1e3, 1) + " t"], ["Node in low Earth orbit", n(INF["leo"]["m_node"] / 1e3, 0) + " t"],
        ["Both nodes and relay", n(NOM["M_inf"] / 1e3, 0) + " t"], ["Per mission over %s missions" % n(NOM["N_life"]), n(NOM["M_inf_per_mission"] / 1e3, 0) + " t"], ["Tug, LANTP / conventional NTP (same reactor)", "%s t / %s t" % (n(NOM["M"] / 1e3, 0), n(NOM["M_ntp"] / 1e3, 0))]]
add(("table", "Table @T:infra@. Laser infrastructure of the nominal vehicle: the quantities are the optical energy emitted, the electrical energy drawn from the buffer and the waste heat, each with its own mass (lower bound: energy buffered, not supplied at peak power).", ["Item", "Value"], rows, [4.4, 1.6]))
RT = R.get("roundtrip", {}).get("rows", [])
rt_txt = ""
if RT:
    rr_ = {(r["m_pl"], r["mu"]): r for r in RT}

    def rt(pl, mu):
        r = rr_[(pl, mu)]
        if r["M_lantp"] is None:
            return "no closure"
        if r["ratio"] is None:
            return "%s t, where the reactor-only tug does not close" % n(r["M_lantp"] / 1e3, 0)
        return "%s (%s t against %s t)" % (n(r["ratio"], 2), n(r["M_lantp"] / 1e3, 0), n(r["M_ntp"] / 1e3, 0))
    rt_txt = (" A round trip with propulsive return (four burns, the tug reused, same 500 MWt reactor) gives an IMLEO ratio of %s for a 10 t payload at 10 kg/MW and %s at 25 kg/MW. For 20 t and for 40 t the reactor-only tug does not close, because its thrust is too low for the multi-hour burns of a heavy vehicle, "
              "while the laser-assisted tug closes at an initial mass of %s for 20 t and of %s for 40 t at 10 kg/MW (25 kg/MW: %s and %s). The advantage at large payloads at a fixed reactor is a thrust advantage and not a specific-impulse advantage, and it is reduced when the conventional tug is allowed a larger reactor (Section 6.8)."
              % (rt(10e3, 10.0), rt(10e3, 25.0), rt(20e3, 10.0).split(",")[0], rt(40e3, 10.0).split(",")[0], rt(20e3, 25.0).split(",")[0], rt(40e3, 25.0)))
add(("p", fmt("The nominal laser node would emit <<pe>> GW for <<tb>> min, that is <<eo>> GWh of optical energy; at the wall-plug efficiency of 0.4 this is <<ee>> GWh of electrical energy to be stored and <<wh>> GWh (<<wt>> TJ) of waste heat to be buffered per burn (Table @T:infra@). The two nodes and the relay weigh <<mi>> t (median over the draws <<mm>> t, 5th–95th percentile <<m5>>–<<m95>> t), "
              "against a tug of <<tg>> t; per mission, over <<nl>> missions, the infrastructure adds <<pm>> t to the IMLEO, so that the infrastructure-inclusive IMLEO ratio at equal reactor power has a median of <<ri>> (5th–95th percentile <<r5>>–<<r95>>). "
              "Supplying the peak power from solar arrays or a reactor instead of buffering the energy would be far heavier. The comparison with conventional NTP is thus unfavorable even before the link is considered.<<rt>>",
              pe=n(NOM["P_emit"] / 1e9, 1), tb=n(NOM["t_burn"][0] / 60, 0), eo=n(Eem / GWH, 2), ee=n(Eel / GWH, 2), wh=n(Ew / GWH, 2), wt=n(Ew / 1e12, 1), mi=n(NOM["M_inf"] / 1e3, 0), mm=n(np.median(MINF), 0), m5=n(np.percentile(MINF, 5), 0), m95=n(np.percentile(MINF, 95), 0),
              tg=n(NOM["M"] / 1e3, 0), nl=n(NOM["N_life"]), pm=n(NOM["M_inf_per_mission"] / 1e3, 0), ri=n(np.nanmedian(RATIO_INF), 1), r5=n(np.nanpercentile(RATIO_INF, 5), 1), r95=n(np.nanpercentile(RATIO_INF, 95), 1), rt=rt_txt)))

# ------------------------------------------------------------------------------------------- 6.10 contingency
add(("h2", "6.10 Laser outage and contingency"))
add(("fig", "Fig12_contingency.png", "Fig. @F:cont@. (a) IMLEO ratio for three tank-loading policies (bar: median; thick line: interquartile range; thin line: 5–95%). (b) Propellant to complete TLI after a loss of the laser at a given fraction of the nominal burn, for the nominal vehicle.", 6.2))
rows = [[k, n(POL[k]["q"][2], 2), "%s–%s" % (n(POL[k]["q"][0], 2), n(POL[k]["q"][4], 2)), n(POL[k]["M_med"] / 1e3, 0)] for k in PK]
oc = CT["outage_curve"]
add(("p", fmt("A laser outage does not strand the vehicle, because the reactor continues the burn, but it costs propellant: the TLI burn of the nominal vehicle uses <<p0>> t with the laser throughout and <<p1>> t if the laser is lost at the start (Fig. @F:cont@b). "
              "Carrying the propellant to complete TLI on the reactor alone (single-fault tolerance) raises the median IMLEO ratio from <<a>> to <<b>>, and carrying the propellant for a reactor-only mission with the LANTP hardware gives <<c>> (Table @T:cont@); "
              "since the receiver mass stays, the full-fallback ratio is above 1 in <<f>> of the draws. A conventional NTP tug has no such fault. Whether the reserve is worth carrying depends on the probability of an outage, which no data support here; the reserve is the cost of the dependence on the beam.",
              p0=n(CT["tli_nominal_burned_t"], 1), p1=n(oc[0]["burned_t"], 1), a=n(POL[PK[0]]["q"][2], 2), b=n(POL[PK[1]]["q"][2], 2), c=n(POL[PK[2]]["q"][2], 2), f="more than 95%" if POL[PK[2]]["q"][0] > 1 else "most")))
add(("table", "Table @T:cont@. Tank-loading policies: median IMLEO ratio to conventional NTP (same reactor), 5–95%% range, and median initial mass (%s draws)." % n(CT["n"]), ["Policy", "Median ratio", "5–95%", "Median mass (t)"], rows, [3.6, 1.0, 1.1, 1.0]))

# ------------------------------------------------------------------------------------------- 6.11 independent verification
add(("h2", "6.11 Independent verification"))
dif = [abs(r["diff"]) for r in IBURN["rows"]]
add(("p", fmt("The finite burns of the mission model (fixed-step fourth-order integration) were compared with an independent adaptive eighth-order integration (DOP853, relative tolerance 10$^{-11}$) of the same equations for TLI and for the departure burn from low lunar orbit at initial masses of 40, 80 and 160 t, with constant specific impulse (Supplementary Information). "
              "The propellant used differs by at most <<dm>> and the burn times by at most <<dt>> s, which is the step of the fixed-step integrator, so the integrator is not a source of error at the level of the results. The mass equation closes with a residual below 1% of the initial mass in every draw, and the thermochemistry has been checked against Cantera (Section 6.1). "
              "A second, independent implementation of the whole mission and mass model was not made, and the conclusions about the receiver, the infrastructure and the contingency policies rest on one implementation of those parts.",
              dm=pc(max(dif), 2), dt=n(max(abs(r["t_independent"] - r["t_model"]) for r in IBURN["rows"]), 0))))

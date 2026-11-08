# Laser-assisted nuclear thermal propulsion for cislunar logistics: a Monte Carlo power-closure assessment

Leon Sandler, Independent Researcher — sandler.leon@gmail.com — ORCID 0009-0007-4584-808X

Code, data and manuscript for a coupled assessment of performance targets for laser-assisted nuclear thermal propulsion (LANTP) between low Earth orbit and low lunar orbit, prepared for the **CEAS Space Journal** (Springer). Version 1.1.0 (revision after a pre-submission review): the performance targets are treated as hypothetical design targets; the optimized-reactor conventional tug is the primary benchmark; Sobol sensitivity, a technology-threshold map, node-phasing and independent-integration checks were added; the asteroid-deflection extension moved to the Supplementary Information.
Manuscript: `manuscript/LANTP_CEAS_Manuscript.{docx,pdf}`, supplementary information `manuscript/LANTP_Supplementary_Information.{docx,pdf}`, cover letter `manuscript/LANTP_Cover_Letter.{docx,pdf}`.
Archived on Zenodo (all versions): paper 10.5281/zenodo.24048701, code 10.5281/zenodo.24048703 (version 1.0.0: paper 10.5281/zenodo.24048702, code 10.5281/zenodo.24048704; version 1.1.0 DOIs: see the Zenodo records).

**All design inputs (efficiencies, specific masses, link parameters, coupling coefficients) are assumed ranges, not measurements. The performance targets tested (Isp 1300-1500 s, 50-120 kN, 1-50 MW laser on 100-500 MWt, IMLEO 40% below conventional NTP) come from a concept description that is not cited; the manuscript treats them as hypothetical design targets.**

## What the study does

1. **Hydrogen thermochemistry (`lantp_core.py`).** Equilibrium H2 <-> 2H from partition functions; enthalpy and entropy; frozen, partially recombined and shifting-equilibrium nozzle expansion; validated against Cantera and an independent Gibbs minimization.
2. **Power chain and link.** Useful, absorbed, received, emitted and electrical power; waste heat; Gaussian-beam capture with refocusing and pointing jitter; occultation by the Earth and the Moon and link dropouts along finite burns.
3. **Mission and mass (`lantp_mission.py`).** Patched-conic transfer with finite burns; initial-mass closure of the laser-assisted tug and of the conventional reactor-only tug for the same payload; laser-node infrastructure (energy buffer, waste-heat buffer, laser, optics, array); contingency policies for a laser outage.
4. **Studies (`lantp_studies.py`, `lantp_figures.py`).** Power closure, emitted power against thrust, beam link, burn timelines, Monte Carlo of the initial mass (fixed reactor and optimized reactor), Spearman and Sobol sensitivity, convergence, break-even surfaces, technology-threshold map, node phasing, independent burn integration, amortization of the nodes, contingency, round trip, and (Supplementary Information) an asteroid-deflection extension.
5. **Main findings (assumed ranges).** A useful laser power of 2.2-3.6 times the reactor power is needed for 1300-1500 s; a 1-50 MW laser on a 100-500 MWt reactor gives at most about 1000 s; 50-120 kN needs gigawatts of emitted power; against a conventional tug with an optimized reactor the median IMLEO ratio is 1.44 (5th-95th percentile 1.13-1.94) with no draw below 1; the receiver specific mass carries 73% of the variance and a mass benefit needs a receiver below about 11 kg/MW; the laser nodes (about 18 kt) and a single laser fault remove the benefit.

## Reproduce

```
pip install -r requirements.txt
python lantp_studies.py --all      # all studies -> results/results.json and figures/ (about 15 min)
python tests/test_all.py           # automated checks
python manuscript/src/build_manuscript.py          # manuscript and supplementary information (.docx)
python manuscript/src/build_cover_letter.py        # cover letter (.docx)
python manuscript/src/build_submission_files.py    # title page (.docx)
```

Seeds are fixed (`SEED = 2027`); every number in the manuscript is read from `results/results.json`. `figures/Fig1_architecture.png` and `figures/Graphical_abstract.png` are schematics.

## License

MIT for the code, CC-BY-4.0 for the manuscript. See `LICENSE`.

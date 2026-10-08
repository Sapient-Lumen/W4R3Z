#!/usr/bin/env python3
"""Offline source-custody isolation checks for volatile frontier references.

The goal is not to add support. It prevents fresh/current source refs from
bleeding through generic multi-route rows and making unrelated routes look live.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/frontier-source-custody-isolation-audit.generated.md"
ROUTES_ALL = {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}

FRONTIER_SOURCE_REF_POLICY: dict[str, dict[str, Any]] = {
    "REF-0437": {"label": "MICROSCOPE WEP final-result denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 weak-equivalence-principle/composition-denominator only; not metric-theory proof or route support"},
    "REF-0624": {"label": "GWTC-5.0 official release-status anchor", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-LAB-GRAVITON-COUNTING"}, "policy": "gravitational-wave catalog custody only"},
    "REF-0625": {"label": "GWTC-5.0 catalog-analysis anchor", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-LAB-GRAVITON-COUNTING"}, "policy": "gravitational-wave catalog-analysis only"},
    "REF-0626": {"label": "DESI DR2 cosmology chains/data products", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "DESI late-time expansion / BAO custody only"},
    "REF-0627": {"label": "Euclid Q1 public-data watchlist", "allowed_routes": set(), "policy": "watchlist only; not route evidence in this release"},
    "REF-0628": {"label": "CERN accelerator schedule pressure", "allowed_routes": set(), "policy": "schedule/watchlist only; not route evidence in this release"},
    "REF-0629": {"label": "GWOSC O4b open-data release", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-LAB-GRAVITON-COUNTING"}, "policy": "gravitational-wave open-data custody only"},
    "REF-0630": {"label": "ESA LISA factsheet", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "future gravitational-wave runway only; not graviton-counting click evidence"},
    "REF-0631": {"label": "ESA LISA construction start", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "future gravitational-wave construction/runway only; not graviton-counting click evidence"},
    "REF-0632": {"label": "NASA LISA prototype hardware", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "future gravitational-wave hardware/runway only; not graviton-counting click evidence"},
    "REF-0633": {"label": "CMB-S4 shutdown/closeout status", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode closeout/forecast-realization custody only"},
    "REF-0634": {"label": "Simons Observatory B-mode forecast/runway", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode successor runway only"},
    "REF-0635": {"label": "Simons Observatory operations/start-of-hunt context", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode successor runway only"},
    "REF-0636": {"label": "LiteBIRD mission-status runway", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode successor runway only"},
    "REF-0637": {"label": "Euclid public release timeline", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "late-time expansion release-timing custody only"},
    "REF-0639": {"label": "scientific inverse-problem benchmark", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse benchmark/OOD pressure only"},
    "REF-0640": {"label": "SPT-3G two-year B-mode analysis", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode acquired-bandpower/foreground-likelihood pressure only"},
    "REF-0641": {"label": "SPT public B-mode likelihood/bandpower products", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode public-product replay only"},
    "REF-0642": {"label": "NASA LAMBDA SPT-3G data-product archive", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode public archive custody only"},
    "REF-0643": {"label": "GIE/BMV classical-gravity entanglement inference split", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE/BMV inference-status pressure only"},
    "REF-0644": {"label": "GIE/BMV semiclassical-model non-entanglement split", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE/BMV model-class split pressure only"},
    "REF-0645": {"label": "massive quantum systems review/status anchor", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE/BMV review/status pressure only"},
    "REF-0646": {"label": "quantum-information lab-QG review anchor", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE/BMV quantum-information framing pressure only"},
    "REF-0647": {"label": "single-graviton quantum-sensing proposal anchor", "allowed_routes": {"R-OQ0057-LAB-GRAVITON-COUNTING"}, "policy": "lab graviton-counting quantum-click proposal pressure only; not LISA mission runway"},
    "REF-0648": {"label": "graviton-detection quantization caution anchor", "allowed_routes": {"R-OQ0057-LAB-GRAVITON-COUNTING"}, "policy": "lab graviton-counting quantization-boundary caution only; not ToE identity support"},
    "REF-0649": {"label": "FamilyC gravitating-region state theory pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC subregion/gravitating-region state pressure only; not acquired evidence"},
    "REF-0650": {"label": "FamilyC subregion pure-state theory pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC subregion pure-state/frozen-region pressure only; not route promotion"},
    "REF-0651": {"label": "DESI DR2 extended dark-energy combination analysis", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "DESI dynamic-dark-energy model-combination pressure only; not ToE/new-physics identity"},
    "REF-0652": {"label": "crossing-symmetric gravitational S-matrix/bootstrap bounds", "allowed_routes": {"R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "amplitudes/bootstrap gravity-positivity consistency pressure only; not acquired evidence or candidate identity"},
    "REF-0653": {"label": "finite-resolution graviton-pole bootstrap/deprojection pressure", "allowed_routes": {"R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "amplitudes/bootstrap graviton-pole numerical and high-spin stability pressure only; not route promotion"},
    "REF-0654": {"label": "graviton-loop negativity and forward-singularity caveat", "allowed_routes": {"R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "amplitudes/bootstrap loop-corrected positivity caveat only; not acquired evidence or promotion"},
    "REF-0655": {"label": "string-loop/light-particle gravitational positivity IR sensitivity", "allowed_routes": {"R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "amplitudes/bootstrap light-spectrum and near-forward IR sensitivity pressure only; not candidate identity"},
    "REF-0656": {"label": "single-minus graviton kinematic-domain caveat", "allowed_routes": {"R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "amplitudes/bootstrap complex/Klein kinematic-domain caution only; not real-observable closure"},
    "REF-0729": {"label": "ACT DR6 official data-products custody", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "ACT DR6 CMB/cosmology denominator custody only; not dark-energy ontology, primordial tensor detection, or route promotion"},
    "REF-0730": {"label": "ACT DR6 power spectra/likelihood analysis", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "ACT DR6 CMB likelihood pressure only; no acquired evidence-unit credit in rev0357"},
    "REF-0731": {"label": "NASA LAMBDA ACT DR6 derived/lensing products", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "ACT DR6 derived/lensing product custody only; S0 denominator pressure"},
    "REF-0732": {"label": "NANOGrav 15-year GWB official summary", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "PTA nanohertz stochastic-background denominator pressure only; not ToE identity or graviton-counting support"},
    "REF-0733": {"label": "NANOGrav 15-year Hellings-Downs evidence paper", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "PTA correlation evidence pressure only; no single-graviton, strong-field-candidate, or route promotion credit"},
    "REF-0734": {"label": "NANOGrav 15-year public data products", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "PTA public-data custody only; exact payload replay still required before acquired credit"},
    "REF-0163": {"label": "FamilyB quantum-relative-entropy semiclassical-Einstein pressure", "allowed_routes": {"R-OQ0057-FAMILYB-THERMO-ENTROPIC"}, "policy": "FamilyB thermodynamic/relative-entropy local-law pressure only; not microscopic inverse support"},
    "REF-0166": {"label": "AS/amplitudes Lorentzian scattering-amplitude IR caveat", "allowed_routes": {"R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-AMPLITUDES-BOOTSTRAP"}, "policy": "asymptotic-safety and amplitudes/bootstrap Lorentzian scattering/IR pressure only; not acquired evidence or candidate identity"},
    "REF-0658": {"label": "AS matter form-factor momentum-dependence pressure", "allowed_routes": {"R-OQ0057-ASYMPTOTIC-SAFETY"}, "policy": "asymptotic-safety form-factor/momentum-dependence pressure only; not fixed-point promotion"},
    "REF-0659": {"label": "AS GLOB black-hole effective-action phase pressure", "allowed_routes": {"R-OQ0057-ASYMPTOTIC-SAFETY"}, "policy": "asymptotic-safety black-hole/GLOB phase pressure only; not black-hole-sector closure"},
    "REF-0131": {"label": "learned-inverse finite-window holographic reconstruction", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse finite-frequency/cutoff holographic-reconstruction pressure only; not full bulk ontology"},
    "REF-0143": {"label": "physics-informed holographic inverse learning", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse PIML/NeuralODE/PINN inverse-problem pressure only; not route promotion"},
    "REF-0670": {"label": "PINN propagation-failure analysis", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse solver/baseline and propagation-failure pressure only"},
    "REF-0671": {"label": "SciML multi-regime training failure analysis", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse seed/hyperparameter/multi-regime pressure only"},
    "REF-0672": {"label": "machine-learning uncertainty/coverage calibration", "allowed_routes": {"R-OQ0057-FAMILYC-LEARNED-INVERSE"}, "policy": "learned-inverse uncertainty/coverage calibration pressure only"},
    "REF-0673": {"label": "String/M Type IIB flux-landscape finite-region enumeration", "allowed_routes": {"R-OQ0057-STRINGM-ATLAS"}, "policy": "String/M finite-region flux-vacuum atlas pressure only; not observed-sector identity"},
    "REF-0674": {"label": "String/M Landau-Ginzburg interior-moduli vacua pressure", "allowed_routes": {"R-OQ0057-STRINGM-ATLAS"}, "policy": "String/M moduli-stabilization and exact-worldsheet pressure only; not acquired evidence"},
    "REF-0675": {"label": "String/M DESI/de Sitter swampland cosmology pressure", "allowed_routes": {"R-OQ0057-STRINGM-ATLAS", "R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "String/M and DESI/de Sitter swampland pressure only; not ToE or dark-energy identity"},
    "REF-0676": {"label": "String/M fully stabilized Minkowski Landau-Ginzburg vacua pressure", "allowed_routes": {"R-OQ0057-STRINGM-ATLAS"}, "policy": "String/M moduli-stabilization pressure only; not observed-sector closure"},
    "REF-0677": {"label": "GWTC-4 parameterized tests of GR", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "strong-field GW public GR-test constraint pressure only; not ToE identity or route promotion"},
    "REF-0678": {"label": "GW250114 black-hole spectroscopy and tests of GR", "allowed_routes": {"R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "loud-event strong-field spectroscopy pressure only; not generic S3 promotion"},
    "REF-0679": {"label": "QRF spacetime symmetries and large gauge transformations", "allowed_routes": {"R-OQ0057-FRAME-QRF-RELATIONAL"}, "policy": "QRF frame-transport, boundary/corner, and large-gauge pressure only; not acquired evidence or route promotion"},
    "REF-0680": {"label": "QRF crossed-product observer-dependent gravitational entropy", "allowed_routes": {"R-OQ0057-FRAME-QRF-RELATIONAL"}, "policy": "QRF crossed-product/observer-dependence pressure only; not observer-independent entropy closure"},
    "REF-0666": {"label": "FamilyB semiclassical spacetime thermodynamics/backreaction pressure", "allowed_routes": {"R-OQ0057-FAMILYB-THERMO-ENTROPIC"}, "policy": "FamilyB semiclassical thermodynamics/backreaction pressure only; not route promotion"},
    "REF-0667": {"label": "FamilyB non-Riemannian Jacobson-assumption sensitivity pressure", "allowed_routes": {"R-OQ0057-FAMILYB-THERMO-ENTROPIC"}, "policy": "FamilyB thermodynamic derivation scope/geometry-assumption caution only"},
    "REF-0683": {"label": "FamilyB non-extensive/topological horizon-entropy calibration pressure", "allowed_routes": {"R-OQ0057-FAMILYB-THERMO-ENTROPIC"}, "policy": "FamilyB horizon-entropy calibration pressure only; not microstate closure or route promotion"},
    "REF-0684": {"label": "FamilyB nonequilibrium entropy-production/stochastic-geometry pressure", "allowed_routes": {"R-OQ0057-FAMILYB-THERMO-ENTROPIC"}, "policy": "FamilyB nonequilibrium entropy-production pressure only; not microscopic noise-origin evidence or promotion"},
    "REF-0685": {"label": "Simons Observatory expanded-SAT primordial B-mode forecast", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode successor forecast/runway pressure only; not acquired tensor evidence"},
    "REF-0686": {"label": "LiteBIRD mission-design all-sky B-mode runway", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode future mission runway only; not acquired tensor evidence"},
    "REF-0687": {"label": "causal-source and multicomponent B-mode constraints", "allowed_routes": {"R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "primordial B-mode source-ambiguity pressure only; not inflationary or ToE identity"},
    "REF-0688": {"label": "DESI DR2 source-staged chain/posterior products", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "DESI chain/posterior product custody only; not underlying spectra/redshift custody or ToE support"},
    "REF-0689": {"label": "DESI DR2 Lambda-CDM exclusion interpretation caution", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "DESI dark-energy interpretation/pivot/parameterization caution only; not acquired evidence or route promotion"},
    "REF-0690": {"label": "DESI DR2 Lyman-alpha dynamic-dark-energy combination pressure", "allowed_routes": {"R-OQ0057-COSMO-DARK-ENERGY-BAO"}, "policy": "DESI Ly-alpha/gBAO/SNe/CMB combination pressure only; not decisive ontology or ToE identity"},
    "REF-0668": {"label": "causal-set non-manifoldlike continuum-emergence pressure", "allowed_routes": {"R-OQ0057-CAUSAL-SET"}, "policy": "causal-set continuum-emergence pressure only; not acquired dynamics evidence"},
    "REF-0669": {"label": "causal-set black-hole horizon/geodesic-focusing diagnostic pressure", "allowed_routes": {"R-OQ0057-CAUSAL-SET"}, "policy": "causal-set horizon-diagnostic pressure only; not black-hole-sector closure"},
    "REF-0681": {"label": "causal-set interacting-QFT correlator/scattering pressure", "allowed_routes": {"R-OQ0057-CAUSAL-SET"}, "policy": "causal-set matter-correlator/scattering pressure only; not matter-sector completion"},
    "REF-0682": {"label": "causal-set horizon-molecule black-hole entropy pressure", "allowed_routes": {"R-OQ0057-CAUSAL-SET"}, "policy": "causal-set horizon-molecule/entropy pressure only; not black-hole thermodynamics closure"},
    "REF-0691": {"label": "FamilyC dynamical-gravity black-hole-interior QEC", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC finite-N/interior-QEC backreaction pressure only; not acquired evidence or promotion"},
    "REF-0692": {"label": "FamilyC modular-Krylov island-area operator probe", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC modular/Krylov area-operator pressure only; not observed-sector closure"},
    "REF-0693": {"label": "FamilyC massless-graviton island / apologia pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC massless-island and gauge-invariant operator pressure only; not black-hole information closure"},
    "REF-0694": {"label": "FamilyC massless islands in wedge holography", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE"}, "policy": "FamilyC wedge-holography massless-island boundary-condition pressure only; not universal Page-curve support"},
    "REF-0695": {"label": "Lab GIE shielded-setup stability pressure", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE shielding/stability pressure only; not direct acquired evidence"},
    "REF-0696": {"label": "Lab GIE thermal-noise entanglement bound pressure", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE thermal-noise threshold pressure only; not direct acquired evidence"},
    "REF-0697": {"label": "Lab GIE collapse-model witness-comparator pressure", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE locality/collapse-model comparator pressure only; not direct acquired evidence"},
    "REF-0698": {"label": "Lab GIE gravitational quantum-channel proposal pressure", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV"}, "policy": "lab GIE quantum-channel proposal pressure only; not direct acquired evidence"},
    "REF-0392": {"label": "PDG 2026 current observed-particle denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route observed-matter denominator only; not acquired evidence or promotion"},
    "REF-0699": {"label": "Fermilab final Muon g-2 current precision benchmark", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route precision-coupling denominator only; not candidate-native BSM or ToE support"},
    "REF-0700": {"label": "KATRIN direct neutrino-mass current bound", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route neutrino-mass denominator only; not candidate-native mass-generation support"},
    "REF-0701": {"label": "CMS Higgs 2025 current Higgs/coupling searches", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route Higgs/coupling denominator only; not candidate-native Higgs-sector recovery"},
    "REF-0702": {"label": "EHT M87 persistent shadow model-comparison pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "classical-GR horizon/shadow denominator only; not black-hole microstate or ToE evidence"},
    "REF-0703": {"label": "EHT Sgr A* polarized horizon-scale magnetic-field pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "classical-GR horizon-scale polarization/source-model denominator only; not candidate-native support"},
    "REF-0704": {"label": "DESI full-shape/growth modified-gravity constraint pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "classical-GR cosmological-growth denominator only; not dark-energy or ToE closure"},
    "REF-0705": {"label": "GRAVITY S2 Schwarzschild-precession weak-field pressure", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-GW-STRONGFIELD-GR"}, "policy": "classical-GR weak-field/Galactic-center denominator only; not quantum-gravity evidence"},
    "REF-0706": {"label": "LZ low-mass WIMP / solar-neutrino dark-sector denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 dark-sector denominator only; not dark-matter identity or route support"},
    "REF-0707": {"label": "XENONnT ionization-only light-DM constraint denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 light-DM/hidden-sector denominator only; not route support"},
    "REF-0708": {"label": "KATRIN sterile-neutrino constraint denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 sterile-neutrino/neutrino-portal denominator only; not mass-generation or dark-sector solution"},
    "REF-0709": {"label": "ADMX axion dark-matter haloscope constraint denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 axion/hidden-sector denominator only; not axion detection or route support"},
    "REF-0710": {"label": "CODATA/NIST constants custody QM/QFT denominator", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-STRINGM-ATLAS"}, "policy": "QM/QFT/gauge constants and unit-convention denominator only; not candidate-native support"},
    "REF-0711": {"label": "precision electron magnetic-moment QED denominator", "allowed_routes": {"R-OQ0057-LAB-GIE-BMV", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-STRINGM-ATLAS"}, "policy": "precision-QED magnetic-moment replay denominator only; not route evidence or promotion"},
    "REF-0712": {"label": "FLAG lattice-QCD quark-mass/hadron-scale denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 QCD/hadronic denominator only; not Standard Model derivation or route support"},
    "REF-0713": {"label": "precision lattice alpha_s quark-gluon coupling denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 alpha_s/running and nonperturbative-QCD denominator only; not candidate-native support"},
    "REF-0714": {"label": "CMS inclusive-jet alpha_s/PDF running denominator", "allowed_routes": {"R-OQ0057-FAMILYC-EW-CODE", "R-OQ0057-FAMILYC-LEARNED-INVERSE", "R-OQ0057-FAMILYB-THERMO-ENTROPIC", "R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET", "R-OQ0057-AMPLITUDES-BOOTSTRAP", "R-OQ0057-LAB-GIE-BMV", "R-OQ0057-GW-STRONGFIELD-GR", "R-OQ0057-FRAME-QRF-RELATIONAL", "R-OQ0057-LAB-GRAVITON-COUNTING", "R-OQ0057-COSMO-DARK-ENERGY-BAO", "R-OQ0057-PRIMORDIAL-TENSOR-BMODES"}, "policy": "cross-route S0 jet/PDF/QCD-correlation denominator only; not BSM evidence or route promotion"},
    "REF-0509": {"label": "2026 SME Lorentz/CPT data tables denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 Lorentz/CPT/SME coefficient denominator only; not candidate-native support"},
    "REF-0715": {"label": "hydrogen/antihydrogen hyperfine Lorentz/CPT spectroscopy denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 precision-spectroscopy symmetry denominator only; not route support"},
    "REF-0716": {"label": "hydrogen molecular-ion Lorentz/CPT hyperfine-Zeeman denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 molecular-ion SME/spectroscopy denominator only; not acquired evidence"},
    "REF-0717": {"label": "LHAASO GRB photon-propagation LIV denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 photon-propagation/dispersion denominator only; not positive quantum-gravity signal"},
    "REF-0718": {"label": "charm-meson CPT/SME denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 neutral-meson flavour/CPT denominator only; not discrete-symmetry closure"},
    "REF-0719": {"label": "CMS W-boson mass electroweak denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 electroweak precision/input-scheme denominator only; not BSM evidence or route support"},
    "REF-0720": {"label": "CKMfitter CKM-unitarity flavor denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 CKM/flavor fit denominator only; not flavor-sector solution or route promotion"},
    "REF-0721": {"label": "HFLAV heavy-flavor average denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 heavy-flavor/CPV average denominator only; not candidate-native support"},
    "REF-0722": {"label": "NuFIT 6.0 neutrino-oscillation denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 neutrino-mixing/order/CP denominator only; not neutrino-mass-generation solution"},
    "REF-0723": {"label": "LHCb Z-boson mass electroweak denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 electroweak Z-mass/input-scheme denominator only; not route support"},
    "REF-0724": {"label": "JUNO first reactor-neutrino oscillation denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 reactor-neutrino oscillation denominator only; not neutrino-mass identity or route promotion"},
    "REF-0725": {"label": "short-range inverse-square/fifth-force weak-field denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 inverse-square/Yukawa/fifth-force denominator only; not route support or dark-sector identification"},
    "REF-0726": {"label": "in-orbit atom-interferometer quantum-WEP denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 quantum free-fall / atom-interferometer WEP denominator only; not quantum-gravity detection"},
    "REF-0727": {"label": "ACES/PHARAO clock-redshift operational denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 clock/local-position/redshift denominator and runway/status only; not acquired anomaly or route support"},
    "REF-0728": {"label": "torsion-balance solar/composition EP denominator", "allowed_routes": ROUTES_ALL, "policy": "cross-route S0 torsion-balance composition-dependent-force denominator only; not mediator identity or route promotion"},
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def row_identifier(row: dict[str, Any]) -> str:
    for key, val in row.items():
        if key.endswith("_id") and isinstance(val, str):
            return val
    if isinstance(row.get("route_id"), str):
        return row["route_id"]
    return "<unidentified-row>"


def route_ids_for_row(row: dict[str, Any]) -> list[str]:
    routes: list[str] = []
    for key, val in row.items():
        if "route" not in key:
            continue
        if isinstance(val, str) and val.startswith("R-"):
            routes.append(val)
        elif isinstance(val, list):
            routes.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
    out: list[str] = []
    for rid in routes:
        if rid and rid not in out:
            out.append(rid)
    return out


def iter_route_bearing_frontier_source_rows(root: Path):
    for path in sorted(root.glob("*LEDGER.json")):
        try:
            data = load_json(root, path.name)
        except json.JSONDecodeError:
            continue
        for rows_key, rows in data.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                route_ids = route_ids_for_row(row)
                if not route_ids:
                    continue
                refs = [ref for ref in row.get("source_refs", []) if ref in FRONTIER_SOURCE_REF_POLICY]
                if refs:
                    yield path.name, rows_key, row_identifier(row), route_ids, refs


def evaluate_frontier_source_isolation(root: Path) -> dict[str, Any]:
    placements: list[dict[str, Any]] = []
    failures: list[str] = []
    watchlist_route_placements: list[dict[str, Any]] = []
    for file_name, rows_key, rid, routes, refs in iter_route_bearing_frontier_source_rows(root):
        for ref in refs:
            policy = FRONTIER_SOURCE_REF_POLICY[ref]
            allowed = set(policy["allowed_routes"])
            disallowed = [route for route in routes if route not in allowed]
            passed = not disallowed
            item = {"ref": ref, "file": file_name, "rows_key": rows_key, "row_id": rid, "routes": routes, "policy": policy["policy"], "passed": passed}
            placements.append(item)
            if not allowed:
                watchlist_route_placements.append(item)
            if not passed:
                failures.append(f"{ref} appears on {file_name}:{rid} with disallowed routes {disallowed}")
    return {
        "audit_file": GENERATED_AUDIT,
        "policy_refs": len(FRONTIER_SOURCE_REF_POLICY),
        "placements": placements,
        "routes_touched": sorted({route for item in placements for route in item["routes"]}),
        "watchlist_route_placements": watchlist_route_placements,
        "failures": failures,
    }


def write_frontier_source_custody_isolation_audit(root: Path) -> None:
    result = evaluate_frontier_source_isolation(root)
    by_ref: dict[str, dict[str, Any]] = {}
    for item in result["placements"]:
        slot = by_ref.setdefault(item["ref"], {"placements": 0, "failures": 0, "routes": set(), "policy": item["policy"]})
        slot["placements"] += 1
        if not item["passed"]:
            slot["failures"] += 1
        for route in item["routes"]:
            slot["routes"].add(route)
    lines = [
        "# Frontier source-custody isolation audit (generated)",
        "",
        "Generated from route-bearing `*LEDGER.json` rows with volatile frontier `source_refs`. Do not edit directly; run `make index` after changing frontier source custody.",
        "",
        f"- Frontier refs under policy: `{result['policy_refs']}`",
        f"- Route-bearing frontier-ref placements: `{len(result['placements'])}`",
        f"- Routes touched by frontier refs: `{len(result['routes_touched'])}`",
        f"- Watchlist-only route-bearing placements: `{len(result['watchlist_route_placements'])}`",
        f"- Source-custody isolation failures: `{len(result['failures'])}`",
        "",
        "## Per-ref placement summary",
        "",
        "| Ref | Placements | Routes touched | Failures | Policy |",
        "|---|---:|---|---:|---|",
    ]
    for ref in sorted(FRONTIER_SOURCE_REF_POLICY):
        slot = by_ref.get(ref, {"placements": 0, "failures": 0, "routes": set(), "policy": FRONTIER_SOURCE_REF_POLICY[ref]["policy"]})
        routes = ", ".join(f"`{route}`" for route in sorted(slot["routes"])) or "—"
        lines.append(f"| `{ref}` | `{slot['placements']}` | {routes} | `{slot['failures']}` | {slot['policy']} |")
    lines += [
        "",
        "## Failure details",
        "",
    ]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Watchlist-only rule",
        "",
        "`REF-0627` and `REF-0628` are watchlist/schedule refs in this revision. They must have zero route-bearing placements unless a future revision converts them into a named route-local evidence row with an explicit non-promotion cap.",
        "",
        "## Non-promotion rule",
        "",
        "This compact audit prevents fresh frontier sources from leaking through generic custody rows. It creates no new support and promotes no route; the evaluator still checks every placement even though successful placements are summarized by ref instead of retained row-by-row.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_frontier_source_custody_isolation_audit(root)
    outcome = evaluate_frontier_source_isolation(root)
    if outcome["failures"]:
        print("FRONTIER SOURCE ISOLATION FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FRONTIER SOURCE ISOLATION OK")

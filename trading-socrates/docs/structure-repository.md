trading-socrates/
├── README.md                          # Vision du framework
├── docs/
│   ├── 101-prerequisites/
│   │   ├── complex-numbers.md         # Cours + liens externes
│   │   ├── shannon-entropy.md         # Théorie information
│   │   └── spectral-analysis.md       # Fourier, ondelettes
│   ├── modules/
│   │   ├── phase-coherence.md         # Doc module 1.1
│   │   ├── negative-value.md          # Module 1.2 (à venir)
│   │   └── spectral-signature.md      # Module 1.3 (à venir)
│   └── examples/
│       └── wif-btc-case-study.md      # Cas d'usage concret
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── phase_detector.py          # Module que nous venons de créer
│   │   ├── entropy_analyzer.py        # Valeur négative (prochaine étape)
│   │   └── spectral_engine.py         # Signature spectrale
│   ├── visualization/
│   │   ├── complex_plots.py           # Visualisation 4D
│   │   └── dashboard.py               # Interface interactive
│   └── protection/
│       ├── symbiotic_layer.py         # Protection algorithme
│       └── zk_encryption.py           # Zero-knowledge
├── examples/
│   ├── notebooks/
│   │   ├── 01-phase-coherence-demo.ipynb
│   │   ├── 02-negative-value-demo.ipynb
│   │   └── 03-full-pipeline-demo.ipynb
│   └── data/
│       └── sample_datasets/
└── tests/
    ├── test_phase_detector.py
    ├── test_entropy_analyzer.py
    └── integration_tests.py
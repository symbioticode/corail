# Structure du Repository CORAIL~

Ce document décrit l'organisation interne du repository CORAIL~ en tant que polype spécialisé au sein de l'écosystème [symbioticode](https://github.com/symbioticode).

## Vue d'ensemble

CORAIL~ se concentre sur la documentation collaborative et la co-création symbiotique entre humains et IA. Sa structure reflète cette spécialisation tout en maintenant des connexions avec d'autres polypes de l'écosystème.

```
symbioticode/corail/
├── .github/                        # Configuration GitHub
│   ├── workflows/                  # Actions automatisées
│   │   ├── ariane-connect.yml      # Connexion au système ARIANE
│   │   └── translation-sync.yml    # Synchronisation des traductions
│   └── ISSUE_TEMPLATE/
│       ├── nouvelle_idee.md        # Template pour nouvelles idées
│       └── evolution.md            # Template pour évolutions d'idées
├── CGVS.md                         # Code Génétique Vivant SYNERGIA (importé)
├── README.md                       # Présentation principale de CORAIL~
├── PROCESS.md                      # Cycle de vie des contributions
├── docs/                           # Documentation multilingue
│   ├── fr/                         # Documentation en français
│   ├── en/                         # Documentation en anglais
│   ├── es/                         # Documentation en espagnol
│   └── ar/                         # Documentation en arabe
├── bibliotheque/                   # Collections de connaissances co-créées
│   ├── humain-ia/                  # Explorations sur la collaboration symbiotique
│   ├── interconnexions/            # Liens vers d'autres polypes
│   └── meta-documentation/         # Documentation sur la documentation
├── interfaces/                     # Points de connexion
│   ├── web/                        # Interface web simple
│   ├── nostr/                      # Connecteurs vers Nostr
│   └── ipfs/                       # Scripts pour publication sur IPFS
└── utils/                          # Outils spécifiques à CORAIL~
    ├── traduction/                 # Outils de traduction collaborative
    ├── cycle-vie/                  # Suivi du cycle de vie des documents
    └── connexion/                  # Connecteurs vers d'autres polypes
```

## Éléments clés

### PROCESS.md
Ce fichier décrit le cycle de vie des contributions dans CORAIL~, incluant:
- Les phases organiques (Germination → Croissance → Floraison → Pollinisation → Régénération)
- Le processus de collaboration symbiotique humain-IA
- Les mécanismes de traduction et validation
- Le système de connexion avec d'autres polypes

### Bibliothèque
Le dossier `bibliotheque/` représente le cœur fonctionnel de CORAIL~, où sont stockées les connaissances co-créées:
- Structure modulaire permettant une organisation thématique
- Système de métadonnées indiquant le niveau de maturité
- Références vers d'autres polypes de l'écosystème symbioticode

### Interfaces
CORAIL~ propose plusieurs interfaces pour faciliter la contribution et la consultation:
- Interface web simple pour débutants
- Connecteurs Nostr pour niveau intermédiaire
- Scripts IPFS pour utilisateurs avancés

Ces interfaces sont spécifiquement conçues pour la documentation et la collaboration, contrairement à d'autres polypes qui peuvent avoir des interfaces plus spécialisées.

## Connexions avec d'autres polypes

CORAIL~ maintient des liens avec d'autres polypes de l'écosystème symbioticode sans les contenir ni les englober:

### Mécanismes de connexion
- **Références croisées**: Liens vers des connaissances dans d'autres polypes
- **Webhooks**: Notifications automatiques lors de mises à jour pertinentes
- **Compatibilité ARIANE**: Utilisation du système ARIANE pour détecter des résonances

### Exemples de connexions
- Lien vers GAIA pour documentation des concepts financiers
- Lien vers QAAF pour exemples d'implémentation algorithmique
- Lien vers SOPHIA pour documentation des systèmes d'optimisation

## Différences avec l'ancienne structure

Cette structure diffère de l'approche précédente où CORAIL~ était présenté comme contenant d'autres projets:

1. **Spécialisation**: CORAIL~ se concentre uniquement sur la documentation et la collaboration
2. **Autonomie**: Les autres projets (GAIA, SOPHIA, etc.) existent comme polypes autonomes
3. **Relation horizontale**: CORAIL~ est un polype parmi d'autres, sans hiérarchie implicite
4. **Connexions explicites**: Les liens entre polypes sont formalisés comme des connexions entre entités distinctes

## Évolution future

Cette structure est conçue pour évoluer organiquement:

1. **Expansion interne**: Ajout de nouvelles collections thématiques dans la bibliothèque
2. **Connexions accrues**: Développement de nouveaux mécanismes de connexion inter-polypes
3. **Spécialisation progressive**: Raffinement continu du rôle spécifique de CORAIL~ dans l'écosystème

---

*Ce document évoluera avec CORAIL~. Version actuelle: 1.0*

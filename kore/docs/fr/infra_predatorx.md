# Documentation du Projet PredatorX
# Serveur de Backtesting et Machine Learning pour le Trading Algorithmique

## Table des matières
1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
   - [Objectifs](#objectifs)
   - [Architecture globale](#architecture-globale)
   - [Matériel utilisé](#matériel-utilisé)
2. [Installation de Proxmox VE](#2-installation-de-proxmox-ve)
   - [Prérequis](#prérequis)
   - [Installation du système](#installation-du-système)
   - [Configuration post-installation](#configuration-post-installation)
3. [Configuration GPU Passthrough](#3-configuration-gpu-passthrough)
   - [Configuration spécifique à NVIDIA](#configuration-spécifique-à-nvidia)
   - [Vérification du fonctionnement](#vérification-du-fonctionnement)
   - [Résolution des problèmes courants](#résolution-des-problèmes-courants)
4. [Configuration des machines virtuelles](#4-configuration-des-machines-virtuelles)
   - [VM de Backtesting](#vm-de-backtesting)
   - [VM de Machine Learning](#vm-de-machine-learning)
5. [Configuration des environnements de trading](#5-configuration-des-environnements-de-trading)
   - [Environnement de backtesting](#environnement-de-backtesting)
   - [Environnement de machine learning](#environnement-de-machine-learning)
6. [Monitoring, maintenance et optimisation](#6-monitoring-maintenance-et-optimisation)
   - [Health Check](#health-check)
   - [Nettoyage d'espace disque](#nettoyage-despace-disque)
   - [Optimisation GPU](#optimisation-gpu)
   - [Stratégie de sauvegarde](#stratégie-de-sauvegarde)
7. [Annexes](#7-annexes)
   - [Liste des scripts](#liste-des-scripts)
   - [Références](#références)

## 1. Vue d'ensemble du projet

### Objectifs
Le projet PredatorX vise à repurposer une ancienne machine de minage de cryptomonnaies en un serveur de calcul dédié pour:
- Développer et tester des stratégies de trading algorithmique (backtesting)
- Appliquer des techniques de machine learning aux données financières
- Optimiser les stratégies de trading pour améliorer le ratio rendement/drawdown
- Centraliser stockage et analyse des données financières

### Architecture globale
L'architecture mise en place s'articule autour d'un système de virtualisation (Proxmox VE) qui permet de compartimenter les différentes charges de travail:

1. **Système hôte (Proxmox VE)**
   - Installé sur le disque SSD principal
   - Gère la virtualisation et le passthrough GPU

2. **Machines virtuelles**
   - VM de backtesting principal (avec 1-2 GPUs)
   - VM de machine learning (avec les GPUs restants)

3. **Stockage**
   - Disque SSD pour l'OS
   - Stockage secondaire monté pour les VMs et les données

### Matériel utilisé
- **Processeur**: Intel Celeron G4930 (2 cœurs)
- **Mémoire**: 32 GB RAM DDR4
- **Stockage**:
  - SSD Kingston A400 120GB (système)
  - Disque M.2 SATA3 de 512 GB (stockage principal)
  - Disque externe USB de 1 TB (sauvegardes, optionnel)
- **GPUs**: 8x NVIDIA GTX 1660 Super/Ti
- **Réseau**: Interface réseau Gigabit

## 2. Installation de Proxmox VE

### Prérequis
- ISO Proxmox VE 8.x
- Support d'installation USB
- Accès physique à la machine pour l'installation initiale
- Connexion réseau configurée

### Installation du système
1. Créer une clé USB bootable avec l'ISO Proxmox VE
2. Démarrer la machine depuis la clé USB
3. Suivre l'assistant d'installation avec les paramètres suivants:
   - Langue et clavier selon préférences
   - Disque d'installation: SSD Kingston A400
   - Allouer au moins 50 GB pour la partition racine
   - Configurer le nom d'hôte: predatorx
   - Configurer les paramètres réseau
   - Définir un mot de passe root sécurisé

Alternativement, vous pouvez utiliser le script `proxmox-installation.sh` pour automatiser l'installation sur une base Debian:

```bash
# Télécharger et exécuter le script d'installation
wget -O /tmp/proxmox-installation.sh https://raw.githubusercontent.com/dravitch/mlenv/simplified/proxmox-installation.sh
chmod +x /tmp/proxmox-installation.sh
sudo /tmp/proxmox-installation.sh
```

### Configuration post-installation
Après l'installation, exécuter le script de post-installation pour configurer l'environnement:

```bash
# Télécharger et exécuter le script de post-installation
wget -O /tmp/post-installation.sh https://raw.githubusercontent.com/dravitch/mlenv/simplified/post-installation.sh
chmod +x /tmp/post-installation.sh
sudo /tmp/post-installation.sh
```

Ce script effectue les actions suivantes:
- Configuration des dépôts Proxmox (désactivation des dépôts enterprise)
- Configuration du stockage
- Installation des templates LXC
- Configuration du pare-feu
- Configuration des sauvegardes automatiques
- Désactivation de la fenêtre contextuelle d'abonnement

### Configuration du stockage M.2
Si vous disposez d'un disque M.2 pour le stockage principal (comme dans notre configuration), configurez-le:

```bash
# Télécharger et exécuter le script de configuration du stockage M.2
wget -O /tmp/setup-m2-storage.sh https://raw.githubusercontent.com/dravitch/mlenv/simplified/storage/setup-m2-storage.sh
chmod +x /tmp/setup-m2-storage.sh
sudo /tmp/setup-m2-storage.sh
```

Ce script effectue:
1. Détection du disque M.2 SATA
2. Création de partitions et formatage
3. Montage du disque sur `/mnt/vmstorage`
4. Configuration des stockages dans Proxmox (vm-storage, ct-storage, backup, iso)
5. Configuration du montage automatique au démarrage

## 3. Configuration GPU Passthrough

### Configuration spécifique à NVIDIA

Pour que le passthrough GPU fonctionne correctement avec les cartes NVIDIA, il est crucial d'utiliser la configuration suivante:

1. **Format d'adressage PCI correct**:
   - Pour le premier GPU: `0000:01:00,x-vga=1` (bus complet avec option x-vga)
   - Pour les GPUs additionnels: `0000:XX:00.0,pcie=1` (périphérique spécifique)

2. **Options CPU spéciales** pour éviter l'erreur 43 NVIDIA:
   ```
   args: -cpu 'host,+kvm_pv_unhalt,+kvm_pv_eoi,hv_vendor_id=NV43FIX,kvm=off'
   ```

3. **Type de machine et BIOS**:
   - Machine: q35
   - BIOS: ovmf (UEFI)

Le script de création de VM `setup-backtesting-vm-updated.sh` intègre toutes ces configurations spécifiques et permet de créer des VMs avec passthrough GPU fonctionnel.

### Vérification du fonctionnement
Après redémarrage, vérifiez que le passthrough GPU fonctionne:

```bash
# Dans la VM, vérifier les GPUs détectés
nvidia-smi

# Lister les GPUs individuellement
nvidia-smi -L
```

Si les GPUs sont correctement détectés, vous devriez voir la liste de toutes les cartes NVIDIA passées à la VM.

### Résolution des problèmes courants
Les problèmes de passthrough GPU les plus courants avec les cartes NVIDIA sont:

1. **Redémarrage/plantage de l'hôte Proxmox** lors de l'ajout d'un GPU:
   - Cause: Mauvais format d'adressage PCI ou options manquantes
   - Solution: Utiliser la syntaxe exacte décrite ci-dessus

2. **Erreur 43 dans le gestionnaire de périphériques Windows**:
   - Cause: Détection de la virtualisation par le pilote NVIDIA
   - Solution: Utiliser les options CPU spéciales (hv_vendor_id=NV43FIX)

3. **Seul un GPU est détecté sur les 8 disponibles**:
   - Cause: Configuration incorrecte du premier GPU ou problème de module noyau
   - Solution: Utiliser l'option `x-vga=1` sur le premier GPU et exécuter le script d'optimisation GPU

## 4. Configuration des machines virtuelles

### VM de Backtesting
Pour créer et configurer la VM de backtesting avec la configuration qui fonctionne:

```bash
# Télécharger et exécuter le script mis à jour pour la création de VM
wget -O /tmp/setup-backtesting-vm-updated.sh https://raw.githubusercontent.com/dravitch/mlenv/main/setup-backtesting-vm-updated.sh
chmod +x /tmp/setup-backtesting-vm-updated.sh
sudo /tmp/setup-backtesting-vm-updated.sh

# Pour spécifier un ID VM et un nombre de GPUs différents:
sudo /tmp/setup-backtesting-vm-updated.sh 100 2  # VM ID 100 avec 2 GPUs
```

Ce script crée une VM avec:
- 8GB de RAM
- 2 cœurs CPU
- 60GB d'espace disque SSD
- Le nombre spécifié de GPUs en passthrough
- Ubuntu 22.04 comme système d'exploitation

Après la création, installez manuellement Ubuntu 22.04 Server via la console Proxmox.

### VM de Machine Learning
Pour la VM de Machine Learning, vous pouvez utiliser le même script en spécifiant un ID différent et plus de GPUs:

```bash
# Créer une VM de ML avec 6 GPUs
sudo /tmp/setup-backtesting-vm-updated.sh 101 6  # VM ID 101 avec 6 GPUs
```

## 5. Configuration des environnements de trading

### Environnement de backtesting
Après avoir installé Ubuntu dans la VM de backtesting, exécutez:

```bash
# Dans la VM de backtesting, télécharger et exécuter le script de configuration
wget -O /tmp/setup-backtesting.sh https://raw.githubusercontent.com/dravitch/mlenv/simplified/setup-backtesting.sh
chmod +x /tmp/setup-backtesting.sh
sudo /tmp/setup-backtesting.sh
```

Ce script installe:
- Pilotes NVIDIA et CUDA
- Python et bibliothèques pour le backtesting (pandas, numpy, backtrader, etc.)
- Jupyter Lab
- Service systemd pour Jupyter
- Structure de projet pour le backtesting

### Environnement de machine learning
Dans la VM de machine learning:

```bash
# Télécharger et exécuter le script de configuration ML
wget -O /tmp/setup-ml.sh https://raw.githubusercontent.com/dravitch/mlenv/simplified/setup-ml.sh
chmod +x /tmp/setup-ml.sh
sudo /tmp/setup-ml.sh
```

Ce script installe des composants similaires à la VM de backtesting, plus:
- Bibliothèques spécifiques pour le machine learning (TensorFlow, PyTorch, etc.)
- Outils d'optimisation et d'apprentissage par renforcement
- Structure de projet pour le ML

## 6. Monitoring, maintenance et optimisation

### Health Check
Pour vérifier l'état général de votre VM après installation:

```bash
# Télécharger et exécuter le script de vérification
wget -O health-check.sh https://raw.githubusercontent.com/dravitch/mlenv/main/health-check.sh
chmod +x health-check.sh
sudo bash health-check.sh

# Pour un rapport plus détaillé:
sudo bash health-check.sh --detailed
```

Ce script vérifie:
- L'état général du système (CPU, mémoire, disque)
- La configuration GRUB pour le passthrough GPU
- La détection des GPUs par le système et les pilotes NVIDIA
- L'environnement Python et les frameworks ML
- Les services comme Jupyter
- Les optimisations système pour ML

Le rapport complet est enregistré dans un fichier `vm_health_report_*.txt` et propose des recommandations spécifiques.

### Nettoyage d'espace disque
Pour libérer de l'espace disque après installation:

```bash
# Télécharger et exécuter le script de nettoyage
wget -O clean-disk-space.sh https://raw.githubusercontent.com/dravitch/mlenv/main/clean-disk-space.sh
chmod +x clean-disk-space.sh
sudo bash clean-disk-space.sh
```

Ce script effectue:
- Nettoyage des caches apt et packages inutilisés
- Suppression des fichiers temporaires et journaux
- Suppression des composants CUDA non essentiels (~3-4GB potentiels)
- Nettoyage des caches Python

### Optimisation GPU
Pour optimiser la configuration multi-GPU:

```bash
# Télécharger et exécuter le script d'optimisation
wget -O gpu-tuning.sh https://raw.githubusercontent.com/dravitch/mlenv/main/gpu-tuning.sh
chmod +x gpu-tuning.sh
sudo bash gpu-tuning.sh
```

Ce script effectue:
- Configuration des modules noyau NVIDIA pour multi-GPU
- Optimisation de GRUB pour le passthrough PCIe
- Création d'un script d'activation de tous les GPUs
- Configuration des paramètres système pour ML
- Mise en place d'un service d'activation automatique des GPUs

### Stratégie de sauvegarde
Les sauvegardes sont gérées automatiquement par le script post-installation avec:

- Sauvegarde quotidienne des VMs à 1h du matin
- Compression zstd pour économiser de l'espace
- Logs de sauvegarde dans /var/log/pve-backup/

Vous pouvez déclencher une sauvegarde manuelle:

```bash
# Sur l'hôte Proxmox, exécuter le script de sauvegarde
/usr/local/bin/pve-backup.sh
```

## 7. Annexes

### Liste des scripts
Voici la liste complète des scripts utilisés dans ce projet:

| Script | Description |
|--------|-------------|
| `post-installation.sh` | Configuration post-installation Proxmox |
| `setup-m2-storage.sh` | Configuration du stockage M.2 |
| `progressive-gpu-passthrough.sh` | Configuration du passthrough GPU |
| `setup-backtesting-vm-updated.sh` | Création de la VM de backtesting avec passthrough GPU correct |
| `setup-backtesting.sh` | Configuration de l'environnement de backtesting |
| `setup-ml.sh` | Configuration de l'environnement de machine learning |
| `health-check.sh` | Vérification de santé post-installation |
| `clean-disk-space.sh` | Nettoyage d'espace disque |
| `gpu-tuning.sh` | Optimisation des performances GPU |
| `pve-backup.sh` | Script de sauvegarde automatique |

### Références et enseignements clés

#### Spécificités du passthrough NVIDIA
Les cartes NVIDIA nécessitent une configuration très précise pour fonctionner en passthrough:
- Adressage du bus PCI complet (`0000:01:00`) plutôt que du dispositif seul (`01:00.0`)
- Option `x-vga=1` obligatoire pour le premier GPU
- Arguments CPU spécifiques pour contourner les restrictions NVIDIA

#### Optimisation des performances
Pour obtenir les meilleures performances:
- Désactivez le mode d'économie d'énergie des GPUs (`nvidia-smi -pm 1`)
- Configurez le swappiness à une valeur basse (`vm.swappiness=10`)
- Activez les huge pages transparentes (`echo always > /sys/kernel/mm/transparent_hugepage/enabled`)
- Utilisez un disque SSD pour les VMs

#### Maintenance régulière
Pour assurer la stabilité à long terme:
- Exécutez le script health-check mensuellement
- Nettoyez régulièrement l'espace disque
- Vérifiez les sauvegardes
- Mettez à jour les pilotes NVIDIA si nécessaire

#### Documentation recommandée
- [Documentation officielle Proxmox](https://pve.proxmox.com/wiki/Main_Page)
- [Guide NVIDIA GPU Passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough)
- [Guide d'installation CUDA](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- [Documentation Jupyter](https://jupyter.org/documentation)
- [Optimisation PyTorch pour multi-GPU](https://pytorch.org/tutorials/intermediate/model_parallel_tutorial.html)
- [Optimisation TensorFlow pour multi-GPU](https://www.tensorflow.org/guide/gpu)

Ce projet démontre qu'il est possible de repurposer efficacement du matériel de minage de cryptomonnaies pour des applications de backtesting et de machine learning, offrant ainsi une deuxième vie productive à ces composants tout en permettant l'exploitation de leur puissance de calcul.
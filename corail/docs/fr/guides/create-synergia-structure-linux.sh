# Script PowerShell pour créer l'arborescence SYNERGIA~
# À exécuter depuis le répertoire où vous souhaitez créer la structure

# Création des dossiers principaux
New-Item -Path ".\symbioticode" -ItemType Directory
Set-Location -Path ".\symbioticode"

# Création des fichiers README en différentes langues
"# SYNERGIA~" | Out-File -FilePath "README-fr.md" -Encoding utf8
"# SYNERGIA~" | Out-File -FilePath "README-en.md" -Encoding utf8
"# SYNERGIA~" | Out-File -FilePath "README-es.md" -Encoding utf8

# Création de la structure src
New-Item -Path ".\src" -ItemType Directory
"# SYNERGIA Compressed YAML" | Out-File -FilePath ".\src\synergia-compressed.yaml" -Encoding utf8
"// ARIANE Connector" | Out-File -FilePath ".\src\ariane-connector.js" -Encoding utf8
"// MIMIA Analyzer" | Out-File -FilePath ".\src\mimia-analyzer.js" -Encoding utf8
"// MELIA Harmonizer" | Out-File -FilePath ".\src\melia-harmonizer.js" -Encoding utf8
"// NEURIA Bridge" | Out-File -FilePath ".\src\neuria-bridge.js" -Encoding utf8

# Création de la structure docs
New-Item -Path ".\docs" -ItemType Directory
"# Code Génétique Vivant SYNERGIA~ (CGVS)" | Out-File -FilePath ".\docs\CGVS-COMPLET.md" -Encoding utf8
"# Métabolisme SYNERGIA~" | Out-File -FilePath ".\docs\METABOLISME.md" -Encoding utf8
"# Guide d'implémentation SYNERGIA~" | Out-File -FilePath ".\docs\IMPLEMENTATION.md" -Encoding utf8
"# Architecture des fichiers SYNERGIA~" | Out-File -FilePath ".\docs\ARBORESCENCE.md" -Encoding utf8

# Création des dossiers linguistiques
New-Item -Path ".\docs\fr" -ItemType Directory
New-Item -Path ".\docs\fr\principes" -ItemType Directory
New-Item -Path ".\docs\fr\guides" -ItemType Directory
"# Glossaire SYNERGIA~" | Out-File -FilePath ".\docs\fr\glossaire.md" -Encoding utf8

New-Item -Path ".\docs\en" -ItemType Directory
New-Item -Path ".\docs\es" -ItemType Directory

# Création des exemples
New-Item -Path ".\examples" -ItemType Directory
New-Item -Path ".\examples\minimal" -ItemType Directory
New-Item -Path ".\examples\intermediate" -ItemType Directory
New-Item -Path ".\examples\advanced" -ItemType Directory

# Création de la structure GitHub
New-Item -Path ".\.github" -ItemType Directory
New-Item -Path ".\.github\workflows" -ItemType Directory
"# GitHub Action - ARIANE Verification" | Out-File -FilePath ".\.github\workflows\ariane-verify.yml" -Encoding utf8
"# GitHub Action - MIMIA Analysis" | Out-File -FilePath ".\.github\workflows\mimia-analyze.yml" -Encoding utf8
"# GitHub Action - MELIA Harmonization" | Out-File -FilePath ".\.github\workflows\melia-harmonize.yml" -Encoding utf8

New-Item -Path ".\.github\ISSUE_TEMPLATE" -ItemType Directory
"# Template pour la phase de germination" | Out-File -FilePath ".\.github\ISSUE_TEMPLATE\germination.md" -Encoding utf8
"# Template pour la phase de croissance" | Out-File -FilePath ".\.github\ISSUE_TEMPLATE\growth.md" -Encoding utf8
"# Template pour la phase de régénération" | Out-File -FilePath ".\.github\ISSUE_TEMPLATE\regeneration.md" -Encoding utf8

# Retour à la racine
Set-Location -Path ".."

# Message de confirmation
Write-Host "L'arborescence SYNERGIA~ a été créée avec succès!" -ForegroundColor Green
Write-Host "Structure générée dans le dossier: symbioticode" -ForegroundColor Cyan
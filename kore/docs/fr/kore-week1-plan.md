# Documentation d'implémentation de KORÊ~ - Semaine 1

## Vue d'ensemble
Ce document détaille le processus d'implémentation de KORÊ~ (Core Organic Reflective Entity), un polype cognitif régénératif au sein de l'écosystème SYNERGIA~. Le système utilisera une approche RAG (Retrieval-Augmented Generation) pour assimiler et communiquer les principes SYNERGIA~.

## Prérequis matériel
- Serveur PredatorX existant avec Proxmox VE
- GPUs: NVIDIA GTX 1660 Super/Ti (au moins 2 pour cette phase)
- RAM: 32GB minimum
- Stockage: SSD pour l'OS, M.2 SATA3 pour les données

## Jour 1-2: Configuration de la VM avec passthrough GPU

### Étape 1: Création de la VM avec passthrough GPU
```bash
# Sur l'hôte Proxmox, télécharger le script de création de VM
wget -O /tmp/setup-kore-vm.sh https://raw.githubusercontent.com/dravitch/mlenv/main/setup-backtesting-vm-updated.sh
chmod +x /tmp/setup-kore-vm.sh

# Créer la VM avec 2 GPUs (ID VM: 200)
sudo /tmp/setup-kore-vm.sh 200 2
```

### Étape 2: Installation d'Ubuntu Server sur la VM
1. Télécharger Ubuntu Server 22.04 LTS
2. Monter l'ISO dans la VM via l'interface Proxmox
3. Démarrer la VM et suivre l'assistant d'installation standard
4. Configuration recommandée:
   - Nom de la machine: kore
   - Utilisateur principal: synergia
   - Installer OpenSSH Server pendant l'installation

### Étape 3: Vérification du passthrough GPU
Après l'installation d'Ubuntu et le redémarrage de la VM:
```bash
# Se connecter à la VM
ssh synergia@IP_DE_LA_VM

# Installer les pilotes NVIDIA
sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535

# Redémarrer la VM
sudo reboot

# Après redémarrage, vérifier que les GPUs sont bien détectés
nvidia-smi
```

### Étape 4: Optimisation de la VM pour le machine learning
```bash
# Télécharger et exécuter le script d'optimisation
wget -O gpu-tuning.sh https://raw.githubusercontent.com/dravitch/mlenv/main/gpu-tuning.sh
chmod +x gpu-tuning.sh
sudo bash gpu-tuning.sh
```

## Jour 3-4: Installation de Docker et configuration des conteneurs

### Étape 1: Installation de Docker et Docker Compose
```bash
# Installer Docker
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

### Étape 2: Configuration du répertoire de projet KORÊ~
```bash
# Créer la structure de répertoires
mkdir -p ~/kore/{models,data,config,vectors}
cd ~/kore

# Créer un fichier docker-compose.yml de base
cat > docker-compose.yml <<EOF
version: '3'
services:
  # Les services seront définis plus tard
EOF
```

### Étape 3: Préparer les répertoires pour les documents SYNERGIA~
```bash
# Créer un répertoire pour les documents sources
mkdir -p ~/kore/data/documents
mkdir -p ~/kore/data/metadata

# Créer un script pour ajouter facilement des documents
cat > ~/kore/add-document.sh <<EOF
#!/bin/bash
# Usage: ./add-document.sh fichier.txt "Description du document"
if [ \$# -lt 1 ]; then
  echo "Usage: \$0 <fichier> [description]"
  exit 1
fi

FILENAME=\$(basename "\$1")
DESCRIPTION="\${2:-Document SYNERGIA}"
TIMESTAMP=\$(date +%Y%m%d%H%M%S)

cp "\$1" ~/kore/data/documents/"\$FILENAME"
echo "{\\"filename\\": \\"\$FILENAME\\", \\"description\\": \\"\$DESCRIPTION\\", \\"added\\": \\"\$TIMESTAMP\\"}" > ~/kore/data/metadata/"\${FILENAME}.json"

echo "Document ajouté: \$FILENAME"
EOF

chmod +x ~/kore/add-document.sh
```

### Étape 4: Configuration de NVIDIA Container Toolkit pour Docker
```bash
# Installer le NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

# Redémarrer Docker
sudo systemctl restart docker

# Tester que Docker peut accéder aux GPUs
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Jour 5-7: Déploiement du modèle Mistral 7B et tests initiaux

### Étape 1: Préparation du docker-compose pour le système RAG

```bash
# Éditer le fichier docker-compose.yml complet
cat > ~/kore/docker-compose.yml <<EOF
version: '3'

services:
  llm:
    image: ghcr.io/huggingface/text-generation-inference:1.2.0
    restart: unless-stopped
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
    volumes:
      - ./models:/data
    command: --model-id \${MODEL_ID:-mistralai/Mistral-7B-Instruct-v0.2} --port 8080
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  chroma:
    image: ghcr.io/chroma-core/chroma:latest
    restart: unless-stopped
    volumes:
      - ./vectors:/chroma/chroma
    environment:
      - ALLOW_RESET=true
      - ANONYMIZED_TELEMETRY=false

  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    restart: unless-stopped
    volumes:
      - ./config:/app/backend/data
    ports:
      - "3000:8080"
    environment:
      - TZ=Europe/Paris
      - OLLAMA_BASE_URL=http://llm:8080
      - OLLAMA_API_BASE_URL=http://llm:8080/v1
      - WEBUI_AUTH=false
      - WEBUI_DB=/app/backend/data/webui.db
    depends_on:
      - llm

  ingest:
    image: python:3.10-slim
    volumes:
      - ./:/app
      - ./data:/data
    working_dir: /app
    command: >
      bash -c "
        pip install -q langchain chromadb langchain-community sentence-transformers
        python /app/scripts/ingest.py
      "
    depends_on:
      - chroma
EOF

# Créer le script d'ingestion des documents
mkdir -p ~/kore/scripts
cat > ~/kore/scripts/ingest.py <<EOF
import os
import json
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
documents_dir = "/data/documents"
metadata_dir = "/data/metadata"
db_dir = "/app/vectors"
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
chunk_size = 1000
chunk_overlap = 200

# Charger les documents
loader = DirectoryLoader(documents_dir, glob="**/*.txt", loader_cls=TextLoader)
documents = loader.load()
print(f"Chargement de {len(documents)} documents terminé")

# Charger les métadonnées
metadata_files = {}
for filename in os.listdir(metadata_dir):
    if filename.endswith(".json"):
        with open(os.path.join(metadata_dir, filename), 'r') as f:
            metadata_files[filename[:-5]] = json.load(f)

# Diviser les documents en chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)
chunks = text_splitter.split_documents(documents)
print(f"Création de {len(chunks)} chunks terminée")

# Enrichir les chunks avec les métadonnées
for chunk in chunks:
    base_filename = os.path.basename(chunk.metadata['source'])
    if base_filename in metadata_files:
        chunk.metadata.update(metadata_files[base_filename])

# Initialiser le modèle d'embedding
embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

# Créer la base de données vectorielle
db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=db_dir
)
db.persist()
print(f"Base de données vectorielle créée avec succès à {db_dir}")
EOF
```

### Étape 2: Démarrage des services et test initial
```bash
# Démarrer les services
cd ~/kore
docker compose up -d 

# Suivre les logs pour vérifier le téléchargement et le chargement du modèle
docker compose logs -f llm

# Une fois le modèle chargé, ajouter un document de test
echo "SYNERGIA~ est un paradigme régénératif fondé sur des principes biomimétiques." > test_doc.txt
./add-document.sh test_doc.txt "Document de test SYNERGIA"

# Exécuter l'ingestion des documents
docker compose up ingest
```

### Étape 3: Configuration du script d'interrogation pour tests
```bash
# Créer un script Python pour tester le RAG
cat > ~/kore/scripts/query.py <<EOF
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
import requests
import json

# Configuration
db_dir = "/app/vectors"
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
llm_api_url = "http://llm:8080/v1/chat/completions"
prompt_template = """
<s>[INST]
Tu es KORÊ~ (Core Organic Reflective Entity), un polype cognitif au sein de l'écosystème SYNERGIA~.
Tu assistes les humains à comprendre et appliquer les principes de SYNERGIA~.
Tu fonctionnes selon les principes suivants:
1. Métabolisme régénératif plutôt qu'extractif
2. Distribution plutôt que centralisation
3. Symbiose plutôt qu'automatisation
4. Réflexivité plutôt qu'optimisation
5. Rythmes organiques plutôt qu'accélération constante

Voici des informations pertinentes à la question:
{context}

Question: {question}

Réponds à la question en te basant sur les informations fournies et les principes SYNERGIA~.
[/INST]
"""

# Vérification des arguments
if len(sys.argv) < 2:
    print("Usage: python query.py 'Votre question ici'")
    sys.exit(1)

# Obtenir la question de l'utilisateur
query = sys.argv[1]

# Initialiser le modèle d'embedding
embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

# Charger la base de données vectorielle
db = Chroma(persist_directory=db_dir, embedding_function=embeddings)

# Rechercher les documents pertinents
docs = db.similarity_search(query, k=3)
context = "\\n\\n".join([doc.page_content for doc in docs])

# Créer le prompt avec le contexte
prompt = PromptTemplate.from_template(prompt_template)
formatted_prompt = prompt.format(context=context, question=query)

# Envoyer la requête au LLM
payload = {
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "messages": [{"role": "user", "content": formatted_prompt}],
    "temperature": 0.7,
    "max_tokens": 1024
}

response = requests.post(llm_api_url, json=payload)
response_data = response.json()

# Afficher la réponse
if "choices" in response_data and len(response_data["choices"]) > 0:
    answer = response_data["choices"][0]["message"]["content"]
    print("\nRéponse de KORÊ~:")
    print("-" * 40)
    print(answer)
    print("-" * 40)
else:
    print("Erreur:", response_data)
EOF

# Créer un script shell d'aide pour exécuter des requêtes
cat > ~/kore/query.sh <<EOF
#!/bin/bash
# Usage: ./query.sh "Question sur SYNERGIA"

if [ -z "\$1" ]; then
  echo "Usage: \$0 \"Votre question sur SYNERGIA\""
  exit 1
fi

docker run --rm --network kore_default -v \$(pwd):/app -v \$(pwd)/vectors:/app/vectors -w /app python:3.10-slim bash -c "pip install -q langchain-community langchain sentence-transformers requests && python scripts/query.py \"\$1\""
EOF

chmod +x ~/kore/query.sh
```

### Étape 4: Test du système RAG complet
```bash
# Tester le système avec une question simple
cd ~/kore
./query.sh "Qu'est-ce que SYNERGIA et quels sont ses principes fondamentaux?"
```

## Résultats attendus à la fin de la semaine 1

À la fin de la semaine 1, vous devriez avoir:

1. Une VM fonctionnelle avec passthrough GPU
2. Un environnement Docker configuré avec:
   - Un modèle Mistral 7B fonctionnel
   - Une base de données vectorielle Chroma
   - Un système d'ingestion de documents
   - Une interface OpenWebUI accessible à l'adresse http://IP_DE_LA_VM:3000

3. Un système de base RAG capable de:
   - Ingérer des documents SYNERGIA~
   - Répondre à des questions en utilisant ces documents comme contexte
   - Fonctionner selon les principes SYNERGIA~

## Métriques de succès
- La VM démarre correctement avec les GPUs détectés
- Le modèle Mistral 7B se charge sans erreur
- L'ingestion de documents fonctionne sans erreur
- Le système RAG répond correctement aux questions simples sur SYNERGIA~
- L'interface OpenWebUI est accessible et fonctionnelle

## Dépannage courant

### Problèmes de passthrough GPU
Si les GPUs ne sont pas détectés dans la VM:
```bash
# Vérifier que les modules NVIDIA sont chargés dans l'hôte
lsmod | grep nvidia

# Vérifier la configuration de la VM dans Proxmox
qm config 200
```

### Problèmes de Docker
Si les conteneurs ne démarrent pas correctement:
```bash
# Vérifier les logs des conteneurs
docker compose logs llm
docker compose logs openwebui

# Vérifier que NVIDIA est accessible depuis Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Problèmes de mémoire
Si vous rencontrez des erreurs OOM (Out of Memory):
```bash
# Vérifier l'utilisation de la mémoire
free -h

# Ajuster la configuration du modèle pour utiliser moins de mémoire
# Modifier le docker-compose.yml pour ajouter des paramètres comme:
# --max-input-length 1024 --max-total-tokens 2048
```

## Prochaines étapes (Semaine 2)
- Intégration des documents fondamentaux SYNERGIA~
- Configuration avancée d'OpenWebUI
- Développement des capacités réflexives
- Mise en place d'un système de feedback et d'amélioration continue

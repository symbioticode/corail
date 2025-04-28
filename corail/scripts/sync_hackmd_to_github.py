import requests
from github import Github
import os
from datetime import datetime

# Configuration
HACKMD_API_KEY = "5OIHMF02JK6NL0LQAC75B71K8OEABLG2CL35JLCD0I6EEPI2LA"  # Clé API HackMD
GITHUB_TOKEN = "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"  # Remplacer par ton token GitHub
GITHUB_REPO="symbioticode/corail"
HACKMD_FOLDER="hYAWxPn4NHtNFMuGN_Mjx"
LANGUAGES=["en","cn","ar","fr"]
FILES=["social_article","README"]

# Connexion à HackMD
headers={"Authorization":f"Bearer {HACKMD_API_KEY}"}


# Vérification de la clé API HackMD
def verify_hackmd_api ():
    """Vérifie si la clé API HackMD est valide."""
    url="https://api.hackmd.io/v1/me"
    response=requests.get (url,headers=headers)
    if response.status_code != 200:
        print (f"Erreur d'authentification HackMD : {response.status_code} - {response.text}")
        return False
    try:
        response.json ()
        print ("Clé API HackMD valide.")
        return True
    except requests.exceptions.JSONDecodeError as e:
        print (f"Erreur lors de la vérification de la clé API HackMD : {e}")
        return False


# Connexion à GitHub
g=Github (GITHUB_TOKEN)
repo=g.get_repo (GITHUB_REPO)


def get_hackmd_file (folder_path,file_name):
    """Récupère le contenu d'un fichier sur HackMD."""
    url="https://api.hackmd.io/v1/teams/symbioticode/notes"
    response=requests.get (url,headers=headers)
    if response.status_code != 200:
        print (f"Erreur lors de la récupération des notes HackMD : {response.status_code} - {response.text}")
        return None
    try:
        notes=response.json ()
    except requests.exceptions.JSONDecodeError as e:
        print (f"Erreur de parsing JSON pour les notes HackMD : {e} - Réponse : {response.text}")
        return None

    for note in notes:
        note_path=note.get ("folderPath","") + "/" + note.get ("title","")
        expected_path=f"/{folder_path}/{file_name}"
        if note_path.lower () == expected_path.lower ():
            note_url=f"https://api.hackmd.io/v1/notes/{note['id']}"
            note_response=requests.get (note_url,headers=headers)
            if note_response.status_code != 200:
                print (
                    f"Erreur lors de la récupération du contenu de la note {note['id']} : {note_response.status_code} - {note_response.text}")
                return None
            try:
                return note_response.json ()["content"]
            except requests.exceptions.JSONDecodeError as e:
                print (f"Erreur de parsing JSON pour la note {note['id']} : {e} - Réponse : {note_response.text}")
                return None
    print (f"Fichier non trouvé sur HackMD : {file_name} dans {folder_path}")
    return None


def get_github_file (path):
    """Récupère le contenu d'un fichier sur GitHub."""
    try:
        file=repo.get_contents (path)
        return file.decoded_content.decode ("utf-8")
    except Exception as e:
        print (f"Fichier non trouvé sur GitHub ou erreur : {path} - {e}")
        return None


def update_github_file (path,content,commit_message):
    """Met à jour ou crée un fichier sur GitHub."""
    try:
        # Vérifier si le fichier existe
        file=repo.get_contents (path)
        repo.update_file (
            path,
            commit_message,
            content,
            file.sha
        )
        print (f"Fichier mis à jour sur GitHub : {path}")
    except Exception as e:
        # Si le fichier n'existe pas, le créer
        try:
            repo.create_file (
                path,
                commit_message,
                content
            )
            print (f"Fichier créé sur GitHub : {path}")
        except Exception as e:
            print (f"Erreur lors de la mise à jour/création du fichier sur GitHub : {path} - {e}")


# Vérifier la clé API HackMD avant de continuer
if not verify_hackmd_api ():
    print ("Arrêt du script : clé API HackMD invalide.")
    exit (1)

# Synchronisation
for lang in LANGUAGES:
    for file in FILES:
        hackmd_path=f"{file}_{lang}.md"
        github_path=f"corail/docs/{lang}/{file}_{lang}.md"
        folder_path=f"{HACKMD_FOLDER}/docs/{lang}"

        # Récupérer le contenu de HackMD
        hackmd_content=get_hackmd_file (folder_path,hackmd_path)
        if hackmd_content is None:
            continue

        # Récupérer le contenu de GitHub
        github_content=get_github_file (github_path)

        # Comparer et mettre à jour si nécessaire
        if github_content != hackmd_content:
            commit_message=f"Sync HackMD to GitHub: Update {hackmd_path} ({datetime.now ().strftime ('%Y-%m-%d %H:%M:%S')})"
            update_github_file (github_path,hackmd_content,commit_message)
        else:
            print (f"Aucune mise à jour nécessaire : {github_path}")
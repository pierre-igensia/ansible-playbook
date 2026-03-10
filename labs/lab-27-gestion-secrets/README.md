# Lab 27 – Gestion des secrets

## 🎯 Objectifs

- Comprendre les limites d'Ansible Vault pour la gestion de secrets à grande échelle
- Intégrer HashiCorp Vault avec Ansible via les plugins lookup
- Utiliser AWS Secrets Manager et Azure Key Vault avec Ansible
- Comparer les différentes approches de gestion de secrets
- Mettre en place une architecture de secrets sécurisée

## 📋 Prérequis

- Labs 01–26 complétés (en particulier Lab 13 – Ansible Vault)
- Docker installé (pour HashiCorp Vault en mode dev)
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer les dépendances
uv pip install hvac boto3

# Se placer dans le répertoire du lab
cd labs/lab-27-gestion-secrets/
```

## 📚 Concepts expliqués

### Ansible Vault vs gestionnaires de secrets externes

| Critère | Ansible Vault | HashiCorp Vault | AWS Secrets Manager |
|---------|--------------|-----------------|---------------------|
| Stockage | Fichiers chiffrés | Serveur centralisé | Service cloud |
| Rotation | Manuelle | Automatique | Automatique |
| Audit | Limité | Complet | CloudTrail |
| Accès | Mot de passe/fichier | Tokens, policies | IAM |
| Échelle | Petit projet | Entreprise | Cloud AWS |

### HashiCorp Vault

Architecture client-serveur pour la gestion centralisée des secrets :

```
┌─────────────┐    API HTTPS    ┌─────────────────┐
│   Ansible   │ ──────────────→ │  HashiCorp      │
│  (lookup)   │                 │  Vault          │
│             │ ←────────────── │  (secrets)      │
└─────────────┘    Secret       └─────────────────┘
```

```yaml
# Lire un secret depuis HashiCorp Vault
- name: Récupérer le mot de passe DB
  ansible.builtin.debug:
    msg: "{{ lookup('community.hashi_vault.hashi_vault', 'secret/data/database password') }}"
```

### Plugins lookup pour les secrets

```yaml
# HashiCorp Vault
mot_de_passe: "{{ lookup('community.hashi_vault.hashi_vault',
  'secret/data/app password',
  url='http://localhost:8200',
  token='mon-token') }}"

# AWS Secrets Manager
cle_api: "{{ lookup('amazon.aws.aws_secret',
  'production/api-key',
  region='eu-west-1') }}"

# Azure Key Vault
certificat: "{{ lookup('azure.azcollection.azure_keyvault_secret',
  'mon-secret',
  vault_url='https://mon-vault.vault.azure.net') }}"
```

## 🛠️ Exercices

### Exercice 1 – HashiCorp Vault en mode dev

**But :** Déployer Vault localement et l'utiliser avec Ansible.

**Instructions :**

1. Lancer HashiCorp Vault en mode dev avec Docker :
```bash
docker run -d --name vault-dev \
  -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=formation-token \
  hashicorp/vault:latest
```

2. Écrire un secret dans Vault :
```bash
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='formation-token'

# Via l'API
curl -X POST \
  -H "X-Vault-Token: formation-token" \
  -d '{"data": {"password": "SuperSecret123", "username": "admin"}}' \
  http://localhost:8200/v1/secret/data/database
```

3. Examiner le playbook :
```bash
cat playbooks/vault_hashicorp.yml
```

4. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/vault_hashicorp.yml
```

**Résultat attendu :** Le secret est lu depuis Vault et utilisé dans le playbook.

---

### Exercice 2 – Comparer Ansible Vault et Vault externe

**But :** Comprendre quand utiliser chaque approche.

**Instructions :**

1. Examiner le playbook de comparaison :
```bash
cat playbooks/comparaison_vaults.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/comparaison_vaults.yml
```

**Résultat attendu :** Compréhension des avantages/inconvénients de chaque approche.

---

### Exercice 3 – Rotation automatique de secrets

**But :** Comprendre la rotation de secrets avec un gestionnaire externe.

**Instructions :**

1. Examiner le playbook de rotation :
```bash
cat playbooks/rotation_secrets.yml
```

2. Observer le workflow :
   - Générer un nouveau secret
   - Le stocker dans Vault
   - Mettre à jour l'application
   - Valider le nouveau secret

**Résultat attendu :** Compréhension du processus de rotation de secrets.

## ✅ Validation

```bash
# Lancer Vault en mode dev
docker run -d --name vault-dev -p 8200:8200 -e VAULT_DEV_ROOT_TOKEN_ID=formation-token hashicorp/vault:latest

# Écrire un secret
curl -X POST -H "X-Vault-Token: formation-token" \
  -d '{"data": {"password": "test123"}}' \
  http://localhost:8200/v1/secret/data/database

# Exécuter le playbook
ansible-playbook -i inventory/mononode.yml playbooks/vault_hashicorp.yml

# Nettoyer
docker stop vault-dev && docker rm vault-dev
```

## 🔍 Pour aller plus loin

- [HashiCorp Vault](https://www.vaultproject.io/)
- [Collection community.hashi_vault](https://docs.ansible.com/ansible/latest/collections/community/hashi_vault/index.html)
- [AWS Secrets Manager + Ansible](https://docs.ansible.com/ansible/latest/collections/amazon/aws/aws_secret_lookup.html)
- **Défi 1** : Configurez HashiCorp Vault avec une politique AppRole pour Ansible (au lieu du token root).
- **Défi 2** : Implémentez la rotation automatique des mots de passe de base de données avec Vault Database Secrets Engine.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : HashiCorp Vault</summary>

```bash
# Lancer Vault
docker run -d --name vault-dev -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=formation-token hashicorp/vault:latest

# Écrire des secrets
curl -X POST -H "X-Vault-Token: formation-token" \
  -d '{"data": {"password": "SuperSecret123", "username": "admin"}}' \
  http://localhost:8200/v1/secret/data/database

# Vérifier
curl -s -H "X-Vault-Token: formation-token" \
  http://localhost:8200/v1/secret/data/database | python3 -m json.tool
```

</details>

<details>
<summary>Solution – Exercice 3 : Rotation</summary>

```yaml
---
- name: Rotation de secrets
  hosts: local
  gather_facts: false
  vars:
    vault_addr: "http://localhost:8200"
    vault_token: "formation-token"
  tasks:
    - name: Générer un nouveau mot de passe
      ansible.builtin.set_fact:
        nouveau_mdp: "{{ lookup('password', '/dev/null length=24 chars=ascii_letters,digits') }}"
      no_log: true

    - name: Stocker dans Vault
      ansible.builtin.uri:
        url: "{{ vault_addr }}/v1/secret/data/database"
        method: POST
        headers:
          X-Vault-Token: "{{ vault_token }}"
        body_format: json
        body:
          data:
            password: "{{ nouveau_mdp }}"
      no_log: true

    - name: Confirmer la rotation
      ansible.builtin.debug:
        msg: "Secret roté avec succès"
```

</details>

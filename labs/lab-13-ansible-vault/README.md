# Lab 13 – Ansible Vault

## 🎯 Objectifs

- Chiffrer des fichiers de variables sensibles avec Ansible Vault
- Utiliser `ansible-vault encrypt_string` pour chiffrer des valeurs individuelles
- Gérer plusieurs mots de passe Vault avec les vault-id
- Intégrer Vault dans un workflow CI/CD

## 📋 Prérequis

- Labs 01–12 complétés
- Environnement virtuel Python activé
- Ansible installé dans l'environnement virtuel

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-13-ansible-vault/

# Vérifier qu'Ansible est disponible
ansible --version
```

## 📚 Concepts expliqués

### Pourquoi Ansible Vault ?

Ansible Vault permet de **chiffrer tout fichier ou valeur sensible** (mots de passe, clés API, certificats, tokens). Les fichiers chiffrés utilisent le chiffrement AES-256 et peuvent être stockés dans Git en toute sécurité, car ils ne sont lisibles qu'avec le mot de passe Vault.

Sans Vault, les secrets finissent souvent :
- en clair dans les fichiers de variables (`vars/secrets.yml`)
- dans des variables d'environnement non tracées
- dans des fichiers exclus par `.gitignore` (risque de perte)

Avec Vault, les secrets chiffrés font partie du dépôt Git et sont protégés.

### Commandes essentielles

| Commande | Description |
|----------|-------------|
| `ansible-vault create fichier.yml` | Créer un nouveau fichier chiffré |
| `ansible-vault edit fichier.yml` | Modifier un fichier chiffré |
| `ansible-vault encrypt fichier.yml` | Chiffrer un fichier existant |
| `ansible-vault decrypt fichier.yml` | Déchiffrer un fichier (en clair) |
| `ansible-vault view fichier.yml` | Afficher le contenu sans déchiffrer sur disque |
| `ansible-vault rekey fichier.yml` | Changer le mot de passe d'un fichier chiffré |
| `ansible-vault encrypt_string` | Chiffrer une valeur individuelle inline |

### Format d'un fichier chiffré

Après `ansible-vault encrypt vars/secrets.yml`, le fichier ressemble à :

```
$ANSIBLE_VAULT;1.1;AES256
66386439643631303666353937383163636163653
...
```

### Utilisation dans un playbook

**Via `vars_files` :**

```yaml
- name: Déploiement sécurisé
  hosts: production
  vars_files:
    - vars/app_vars.yml        # fichier non chiffré
    - vars/secrets.yml         # fichier chiffré avec Vault
  tasks:
    - name: Utiliser le secret
      ansible.builtin.debug:
        msg: "Connexion avec {{ bdd_utilisateur }}"
```

**Via des variables inline chiffrées (`encrypt_string`) :**

```yaml
vars:
  bdd_mot_de_passe: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    66386439643631...
```

**Exécution avec le mot de passe :**

```bash
# Demande interactive du mot de passe
ansible-playbook playbooks/vault_demo.yml --ask-vault-pass

# Via un fichier de mot de passe
ansible-playbook playbooks/vault_demo.yml --vault-password-file .vault_pass
```

### Variables ID de Vault (multi-vault)

Les **vault-id** permettent de gérer plusieurs mots de passe Vault simultanément, utile pour séparer les secrets par environnement :

```bash
# Créer des fichiers avec des vault-id distincts
ansible-vault create --vault-id dev@prompt vars/dev_secrets.yml
ansible-vault create --vault-id prod@prompt vars/prod_secrets.yml

# Exécuter en fournissant les deux mots de passe
ansible-playbook site.yml \
  --vault-id dev@prompt \
  --vault-id prod@/chemin/vers/fichier_prod_pass
```

### Bonne pratique : no_log

Pour éviter d'afficher les secrets dans les logs Ansible, utilisez `no_log: true` sur les tâches qui manipulent des données sensibles :

```yaml
- name: Configurer le mot de passe
  ansible.builtin.user:
    name: admin
    password: "{{ admin_mot_de_passe | password_hash('sha512') }}"
  no_log: true
```

### Intégration CI/CD

Dans une pipeline GitHub Actions ou GitLab CI, le mot de passe Vault est stocké en tant que secret de pipeline :

```yaml
# GitHub Actions
- name: Exécuter le playbook
  run: |
    echo "${{ secrets.VAULT_PASSWORD }}" > .vault_pass
    chmod 600 .vault_pass
    ansible-playbook site.yml --vault-password-file .vault_pass
    rm -f .vault_pass
```

## 🛠️ Exercices

### Exercice 1 – Créer un fichier vault

Créez un nouveau fichier vault chiffré contenant un mot de passe de base de données :

```bash
# 1. Créer un fichier vault interactif
ansible-vault create vars/mon_vault.yml
# Entrer le mot de passe vault : formation123
# Contenu du fichier (dans l'éditeur) :
# ---
# mon_secret: "valeur_confidentielle"

# 2. Vérifier que le fichier est bien chiffré
cat vars/mon_vault.yml

# 3. Voir le contenu déchiffré
ansible-vault view vars/mon_vault.yml
```

**Attendu** : Le fichier `vars/mon_vault.yml` commence par `$ANSIBLE_VAULT;1.1;AES256`.

---

### Exercice 2 – Chiffrer des valeurs individuelles avec encrypt_string

Chiffrez une valeur individuelle pour l'intégrer directement dans un fichier de variables :

```bash
# Chiffrer une valeur et afficher le résultat
ansible-vault encrypt_string 'MonSuperMotDePasse!' --name 'db_password'

# Résultat à copier dans un fichier vars :
# db_password: !vault |
#   $ANSIBLE_VAULT;1.1;AES256
#   ...
```

Créez un fichier `vars/inline_secrets.yml` contenant cette valeur chiffrée et vérifiez qu'elle est utilisable dans un playbook.

---

### Exercice 3 – Utiliser un vault dans un playbook

Exécutez le playbook de démonstration avec le fichier de secrets (en clair pour cet exercice) :

```bash
# Exécuter le playbook (secrets en clair pour la démo)
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml

# Vérifier le fichier de configuration créé
cat /tmp/vault_demo/app.conf
```

Ensuite, chiffrez le fichier de secrets et ré-exécutez avec `--ask-vault-pass` :

```bash
# Chiffrer le fichier de secrets
ansible-vault encrypt vars/secrets.yml

# Ré-exécuter avec le mot de passe vault
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml --ask-vault-pass

# Déchiffrer pour la suite des exercices
ansible-vault decrypt vars/secrets.yml
```

---

### Exercice 4 – Fichier de mot de passe (password file)

Configurez un fichier de mot de passe pour éviter la saisie interactive :

```bash
# 1. Créer le fichier de mot de passe
echo "formation123" > .vault_pass
chmod 600 .vault_pass

# 2. Chiffrer le fichier de secrets
ansible-vault encrypt --vault-password-file .vault_pass vars/secrets.yml

# 3. Exécuter le playbook sans saisie interactive
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml \
  --vault-password-file .vault_pass

# 4. Nettoyer
ansible-vault decrypt --vault-password-file .vault_pass vars/secrets.yml
rm -f .vault_pass
```

**Note** : Ne jamais versionner le fichier `.vault_pass`. Ajoutez-le à `.gitignore`.

## ✅ Validation

```bash
# Vérifier que le playbook s'exécute correctement (secrets en clair)
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml

# Vérifier le fichier de configuration créé
cat /tmp/vault_demo/app.conf

# Tester le chiffrement/déchiffrement
ansible-vault encrypt vars/secrets.yml
ansible-vault view vars/secrets.yml
ansible-vault decrypt vars/secrets.yml

# Tester encrypt_string
ansible-vault encrypt_string 'test123' --name 'variable_test'
```

## 🔍 Pour aller plus loin

- [Documentation officielle Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Guide de bonnes pratiques Vault](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html#keep-vaulted-variables-safely-visible)
- **Défi 1** : Configurez un vault-id pour chaque environnement (dev, staging, prod) avec des mots de passe différents. Créez un playbook qui utilise les trois fichiers de secrets simultanément.
- **Défi 2** : Intégrez le vault avec HashiCorp Vault en utilisant le lookup plugin `hashi_vault` de la collection `community.hashi_vault`.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Créer un fichier vault</summary>

```bash
# Créer le fichier vault
ansible-vault create vars/mon_vault.yml
# (saisir le mot de passe, puis dans l'éditeur) :
# ---
# mon_secret: "valeur_confidentielle"

# Vérifier
cat vars/mon_vault.yml
# Doit afficher : $ANSIBLE_VAULT;1.1;AES256 ...

ansible-vault view vars/mon_vault.yml
# Doit afficher : mon_secret: "valeur_confidentielle"
```

</details>

<details>
<summary>Solution – Exercice 2 : encrypt_string</summary>

```bash
ansible-vault encrypt_string 'MonSuperMotDePasse!' --name 'db_password'
```

Résultat à copier dans `vars/inline_secrets.yml` :

```yaml
---
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  66386439643631303666353937...
```

Playbook de test :

```yaml
---
- name: Test inline vault
  hosts: local
  gather_facts: false
  vars_files:
    - ../vars/inline_secrets.yml
  tasks:
    - name: Vérifier le secret
      ansible.builtin.debug:
        msg: "Secret chargé (masqué)"
      no_log: true
```

</details>

<details>
<summary>Solution – Exercice 3 : Playbook avec vault</summary>

```bash
# Exécution initiale (secrets en clair)
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml

# Chiffrer
ansible-vault encrypt vars/secrets.yml --ask-vault-pass

# Exécution avec vault
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml --ask-vault-pass

# Retour en clair pour la suite
ansible-vault decrypt vars/secrets.yml --ask-vault-pass
```

</details>

<details>
<summary>Solution – Exercice 4 : Fichier de mot de passe</summary>

```bash
# Créer le fichier de mot de passe
echo "formation123" > .vault_pass
chmod 600 .vault_pass

# Ajouter à .gitignore
echo ".vault_pass" >> .gitignore

# Chiffrer et exécuter
ansible-vault encrypt --vault-password-file .vault_pass vars/secrets.yml
ansible-playbook -i inventory/hosts.ini playbooks/vault_demo.yml \
  --vault-password-file .vault_pass

# Nettoyer
ansible-vault decrypt --vault-password-file .vault_pass vars/secrets.yml
rm .vault_pass
```

</details>

<details>
<summary>Solution – Défi 1 : Multi-vault par environnement</summary>

```bash
# Créer les fichiers vault par environnement
ansible-vault create --vault-id dev@prompt vars/dev_secrets.yml
ansible-vault create --vault-id staging@prompt vars/staging_secrets.yml
ansible-vault create --vault-id prod@prompt vars/prod_secrets.yml

# Exécuter avec les trois vault-id
ansible-playbook site.yml \
  --vault-id dev@prompt \
  --vault-id staging@prompt \
  --vault-id prod@prompt
```

Contenu de `vars/dev_secrets.yml` :

```yaml
---
bdd_mot_de_passe: "dev_password_simple"
api_cle: "dev-api-key-xxx"
```

</details>

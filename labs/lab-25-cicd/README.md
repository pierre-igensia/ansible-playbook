# Lab 25 – Intégration CI/CD

## 🎯 Objectifs

- Configurer un pipeline GitHub Actions pour Ansible
- Intégrer `ansible-lint` et `yamllint` dans le workflow CI
- Exécuter Molecule automatiquement dans la CI
- Mettre en place des pre-commit hooks pour la qualité du code
- Découvrir un pipeline GitLab CI équivalent

## 📋 Prérequis

- Labs 01–24 complétés (en particulier Lab 17 – Molecule)
- Compte GitHub avec un dépôt de test
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer les outils de linting
uv pip install ansible-lint yamllint pre-commit

# Se placer dans le répertoire du lab
cd labs/lab-25-cicd/
```

## 📚 Concepts expliqués

### Pourquoi la CI/CD pour Ansible ?

La CI/CD pour Ansible permet de :
- **Valider** la syntaxe et les bonnes pratiques à chaque commit
- **Tester** les rôles automatiquement avec Molecule
- **Déployer** de manière contrôlée et reproductible
- **Documenter** la qualité du code via des badges

### Pipeline typique

```
Commit → Lint → Syntax Check → Molecule Test → Deploy (staging) → Deploy (prod)
  │         │          │              │               │                │
  └─ Push   └─ ansible-lint  └─ --syntax-check  └─ molecule test  └─ Approbation
             yamllint                                                   manuelle
```

### ansible-lint

Analyse statique des playbooks et rôles :

```bash
# Vérifier un playbook
ansible-lint playbooks/site.yml

# Vérifier tout un répertoire
ansible-lint roles/

# Configuration via .ansible-lint
```

### Pre-commit hooks

Vérifient automatiquement le code avant chaque commit :

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.22.0
    hooks:
      - id: ansible-lint
```

## 🛠️ Exercices

### Exercice 1 – Configurer ansible-lint

**But :** Mettre en place le linting Ansible.

**Instructions :**

1. Examiner la configuration ansible-lint :
```bash
cat .ansible-lint
```

2. Exécuter ansible-lint sur un playbook :
```bash
ansible-lint playbooks/lint_et_test.yml
```

3. Corriger les éventuelles erreurs signalées.

**Résultat attendu :** Le playbook passe le linting sans erreur ou avec des avertissements compris.

---

### Exercice 2 – Créer un workflow GitHub Actions

**But :** Configurer un pipeline CI avec GitHub Actions.

**Instructions :**

1. Examiner le workflow GitHub Actions :
```bash
cat .github/workflows/ansible-ci.yml
```

2. Comprendre les étapes du workflow :
   - Checkout du code
   - Installation de Python et Ansible
   - Exécution d'ansible-lint
   - Vérification de la syntaxe
   - Exécution de Molecule (optionnel)

3. Pour tester : pousser le fichier dans un dépôt GitHub et observer l'exécution.

**Résultat attendu :** Le workflow s'exécute automatiquement à chaque push.

---

### Exercice 3 – Pre-commit hooks

**But :** Installer et configurer des hooks pre-commit.

**Instructions :**

1. Examiner la configuration :
```bash
cat .pre-commit-config.yaml
```

2. Installer les hooks :
```bash
pre-commit install
```

3. Tester manuellement :
```bash
pre-commit run --all-files
```

4. Les hooks s'exécuteront automatiquement à chaque `git commit`.

**Résultat attendu :** Les vérifications s'exécutent avant chaque commit.

---

### Exercice 4 – Pipeline GitLab CI

**But :** Comprendre l'équivalent en GitLab CI.

**Instructions :**

1. Examiner le fichier GitLab CI :
```bash
cat .gitlab-ci.yml
```

2. Comparer avec le workflow GitHub Actions :
   - Mêmes étapes, syntaxe différente
   - Stages vs jobs
   - Variables d'environnement

**Résultat attendu :** Compréhension des deux syntaxes CI/CD.

## ✅ Validation

```bash
# Lancer ansible-lint
ansible-lint playbooks/lint_et_test.yml

# Tester pre-commit
pre-commit run --all-files

# Vérifier la syntaxe
ansible-playbook playbooks/lint_et_test.yml --syntax-check
```

## 🔍 Pour aller plus loin

- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [GitHub Actions pour Ansible](https://github.com/marketplace/actions/run-ansible-lint)
- [Pre-commit](https://pre-commit.com/)
- **Défi 1** : Ajoutez un job de déploiement conditionnel (uniquement sur la branche `main`) dans le pipeline.
- **Défi 2** : Configurez des badges de statut CI dans le README du projet.

## 💡 Solutions

<details>
<summary>Solution – Exercice 2 : GitHub Actions</summary>

Le workflow `.github/workflows/ansible-ci.yml` contient :

```yaml
name: Ansible CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ansible ansible-lint yamllint
      - run: ansible-lint
      - run: yamllint .
```

</details>

<details>
<summary>Solution – Exercice 3 : Pre-commit</summary>

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks dans le repo
pre-commit install

# Tester
pre-commit run --all-files

# Lors du prochain git commit, les hooks s'exécuteront automatiquement
```

</details>

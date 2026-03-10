# Lab 17 – Tests avec Molecule

## 🎯 Objectifs

- Comprendre le rôle de Molecule dans le développement de rôles Ansible
- Installer et configurer Molecule avec le driver Docker
- Créer un scénario de test complet (`init`, `converge`, `verify`)
- Écrire des tests d'infrastructure avec Testinfra
- Intégrer Molecule dans un workflow de développement

## 📋 Prérequis

- Labs 01–16 complétés
- Maîtrise des rôles Ansible (Lab 09)
- Docker installé et fonctionnel
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer Molecule et ses dépendances
uv pip install molecule molecule-plugins[docker] pytest-testinfra

# Vérifier l'installation
molecule --version

# Vérifier que Docker fonctionne
docker ps

# Se placer dans le répertoire du lab
cd labs/lab-17-tests-molecule/
```

## 📚 Concepts expliqués

### Qu'est-ce que Molecule ?

Molecule est un framework de test pour les rôles Ansible. Il permet de :
- **Créer** des instances de test (conteneurs Docker, VMs, etc.)
- **Converger** : appliquer le rôle sur ces instances
- **Vérifier** : exécuter des tests d'infrastructure
- **Détruire** : nettoyer les ressources

### Cycle de vie Molecule

```
molecule create → molecule converge → molecule verify → molecule destroy
       │                  │                  │                  │
  Crée les          Applique le       Exécute les       Supprime les
  instances          rôle              tests             instances
```

La commande `molecule test` exécute tout le cycle automatiquement.

### Structure d'un scénario Molecule

```
roles/mon-role/
├── molecule/
│   └── default/           ← Scénario par défaut
│       ├── molecule.yml   ← Configuration du scénario
│       ├── converge.yml   ← Playbook appliqué aux instances
│       ├── verify.yml     ← Playbook de vérification (ou tests Python)
│       └── prepare.yml    ← (optionnel) Préparation avant converge
├── tasks/
│   └── main.yml
├── defaults/
│   └── main.yml
└── ...
```

### Configuration molecule.yml

```yaml
---
dependency:
  name: galaxy                    # Résolution des dépendances

driver:
  name: docker                    # Utilise Docker comme driver

platforms:
  - name: instance-debian         # Nom de l'instance
    image: debian:bullseye        # Image Docker
    pre_build_image: true         # Ne pas builder, utiliser telle quelle
    command: /bin/systemd          # Commande de démarrage (optionnel)

provisioner:
  name: ansible                   # Utilise Ansible pour provisionner
  inventory:
    host_vars:
      instance-debian:
        ma_variable: valeur

verifier:
  name: ansible                   # Vérification via playbook Ansible
  # ou
  # name: testinfra              # Vérification via Testinfra (Python)
```

### Testinfra : tests en Python

Testinfra permet d'écrire des tests d'infrastructure en Python :

```python
def test_nginx_installed(host):
    nginx = host.package("nginx")
    assert nginx.is_installed

def test_nginx_running(host):
    nginx = host.service("nginx")
    assert nginx.is_running
    assert nginx.is_enabled

def test_port_80(host):
    socket = host.socket("tcp://0.0.0.0:80")
    assert socket.is_listening
```

## 🛠️ Exercices

### Exercice 1 – Initialiser un scénario Molecule

**But :** Créer un rôle avec un scénario Molecule intégré.

**Instructions :**

1. Examiner le rôle `serveur-web-test` fourni :
```bash
tree roles/serveur-web-test/
```

2. Observer la configuration Molecule :
```bash
cat roles/serveur-web-test/molecule/default/molecule.yml
```

3. Créer les instances de test :
```bash
cd roles/serveur-web-test/
molecule create
```

4. Vérifier que les conteneurs sont créés :
```bash
molecule list
docker ps
```

**Résultat attendu :** Un conteneur Docker est créé et listé par `molecule list`.

---

### Exercice 2 – Converger et vérifier

**But :** Appliquer le rôle et vérifier son bon fonctionnement.

**Instructions :**

1. Appliquer le rôle sur l'instance :
```bash
molecule converge
```

2. Se connecter à l'instance pour inspecter :
```bash
molecule login
# Dans le conteneur :
ls /var/www/html/
cat /var/www/html/index.html
exit
```

3. Lancer la vérification :
```bash
molecule verify
```

4. Vérifier l'idempotence :
```bash
molecule idempotence
```

**Résultat attendu :** Le rôle s'applique sans erreur, les vérifications passent, et la deuxième exécution ne produit aucun changement.

---

### Exercice 3 – Cycle complet de test

**But :** Exécuter le cycle complet `molecule test`.

**Instructions :**

1. Détruire les instances existantes :
```bash
molecule destroy
```

2. Lancer le cycle complet :
```bash
molecule test
```

3. Observer les étapes exécutées :
   - dependency
   - cleanup
   - destroy
   - create
   - prepare
   - converge
   - idempotence
   - verify
   - cleanup
   - destroy

**Résultat attendu :** Toutes les étapes passent au vert.

---

### Exercice 4 – Ajouter des tests Testinfra

**But :** Écrire des tests d'infrastructure en Python.

**Instructions :**

1. Créer un fichier de tests :
```python
# molecule/default/tests/test_default.py
import pytest

def test_repertoire_web(host):
    """Vérifie que le répertoire web existe"""
    repertoire = host.file("/var/www/html")
    assert repertoire.exists
    assert repertoire.is_directory
    assert repertoire.mode == 0o755

def test_page_accueil(host):
    """Vérifie que la page d'accueil existe et contient le bon contenu"""
    page = host.file("/var/www/html/index.html")
    assert page.exists
    assert page.contains("Bienvenue")

def test_fichier_config(host):
    """Vérifie la configuration"""
    config = host.file("/etc/serveur-web/config.conf")
    assert config.exists
    assert config.contains("port=8080")
```

2. Modifier `molecule.yml` pour utiliser Testinfra comme vérificateur
3. Relancer les tests :
```bash
molecule verify
```

**Résultat attendu :** Les tests Python s'exécutent et valident l'état de l'instance.

## ✅ Validation

```bash
cd roles/serveur-web-test/

# Lancer le cycle complet
molecule test

# Vérifier que toutes les étapes passent
# Le résultat final doit être : PASSED
```

## 🔍 Pour aller plus loin

- [Documentation Molecule](https://molecule.readthedocs.io/)
- [Documentation Testinfra](https://testinfra.readthedocs.io/)
- [Molecule avec GitHub Actions](https://molecule.readthedocs.io/en/latest/ci.html)
- **Défi 1** : Créer un scénario Molecule multi-plateformes (Debian + CentOS) et vérifier que le rôle fonctionne sur les deux distributions.
- **Défi 2** : Ajouter un job GitHub Actions qui exécute `molecule test` automatiquement à chaque push.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Initialiser Molecule</summary>

```bash
cd roles/serveur-web-test/
molecule create
molecule list
# NAME              DRIVER    PROVISIONER   STATE     CREATED
# instance-debian   docker    ansible       created   true
```

</details>

<details>
<summary>Solution – Exercice 2 : Converge et verify</summary>

```bash
molecule converge
# PLAY [Converge] ...
# TASK [serveur-web-test : Créer le répertoire web] ... changed
# TASK [serveur-web-test : Déployer la page d'accueil] ... changed

molecule verify
# PLAY [Verify] ...
# TASK [Vérifier le répertoire web] ... ok
# TASK [Vérifier la page d'accueil] ... ok

molecule idempotence
# PLAY [Converge] ...
# TASK [serveur-web-test : Créer le répertoire web] ... ok
# TASK [serveur-web-test : Déployer la page d'accueil] ... ok
# Idempotence test passed.
```

</details>

<details>
<summary>Solution – Exercice 4 : Tests Testinfra</summary>

Modifier `molecule.yml` :
```yaml
verifier:
  name: testinfra
  directory: tests/
```

Créer `molecule/default/tests/test_default.py` :
```python
import pytest

def test_repertoire_web(host):
    repertoire = host.file("/var/www/html")
    assert repertoire.exists
    assert repertoire.is_directory
    assert repertoire.mode == 0o755

def test_page_accueil(host):
    page = host.file("/var/www/html/index.html")
    assert page.exists
    assert page.contains("Bienvenue")

def test_fichier_config(host):
    config = host.file("/etc/serveur-web/config.conf")
    assert config.exists
    assert config.contains("port=8080")
```

```bash
molecule verify
# ============================= test session starts =============================
# tests/test_default.py::test_repertoire_web PASSED
# tests/test_default.py::test_page_accueil PASSED
# tests/test_default.py::test_fichier_config PASSED
# ============================== 3 passed =======================================
```

</details>

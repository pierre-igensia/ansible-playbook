# Lab 15 – Modules Personnalisés

## 🎯 Objectifs

- Comprendre la structure d'un module Ansible en Python
- Utiliser `AnsibleModule` pour créer un module idempotent
- Documenter un module avec les standards Ansible (`DOCUMENTATION`, `EXAMPLES`, `RETURN`)
- Tester un module personnalisé dans un playbook

## 📋 Prérequis

- Labs 01–14 complétés
- Connaissances de base en Python
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-15-modules-personnalises/

# Les modules personnalisés sont dans le répertoire library/
ls library/
```

## 📚 Concepts expliqués

### Structure d'un module Ansible

Un module Ansible est un script Python autonome avec trois sections de documentation obligatoires et une fonction `main()` :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: mon_module
short_description: Description courte du module
description:
  - Description longue et détaillée du module.
options:
  parametre:
    description: Description du paramètre
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Utiliser mon module
  mon_module:
    parametre: valeur
'''

RETURN = r'''
resultat:
  description: Ce que retourne le module
  type: str
  returned: always
  sample: "valeur exemple"
'''

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            parametre=dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    resultat = dict(changed=False, message='')

    if module.check_mode:
        module.exit_json(**resultat)

    # Logique du module ici
    resultat['message'] = "Paramètre reçu : {}".format(module.params['parametre'])
    resultat['changed'] = True

    module.exit_json(**resultat)

if __name__ == '__main__':
    main()
```

### Emplacement des modules personnalisés

Ansible cherche les modules dans ces emplacements (par ordre de priorité) :

1. `./library/` – répertoire `library/` à côté du playbook ou du projet
2. `~/.ansible/plugins/modules/` – modules utilisateur
3. `/usr/share/ansible/plugins/modules/` – modules système
4. `ANSIBLE_LIBRARY` – variable d'environnement

### Idempotence

**Principe fondamental** : un module DOIT être idempotent. Si l'état désiré est déjà atteint, le module retourne `changed=False` sans modifier le système.

```python
# Vérifier avant de modifier
etat_actuel = lire_etat_systeme()
if etat_actuel == etat_desire:
    module.exit_json(changed=False, message="Déjà à l'état désiré")

# Sinon, effectuer la modification
modifier_systeme()
module.exit_json(changed=True, message="Modification effectuée")
```

### Mode check et diff

```python
# Supporter --check (simulation sans modification)
module = AnsibleModule(
    argument_spec=dict(...),
    supports_check_mode=True
)

if module.check_mode:
    # Simuler sans modifier
    module.exit_json(changed=True, message="check_mode : serait modifié")

# Mode diff pour afficher les différences
module.exit_json(
    changed=True,
    diff=dict(before="ancienne valeur\n", after="nouvelle valeur\n")
)
```

### Gestion des erreurs

```python
# Échec avec message d'erreur
if not os.path.exists(chemin):
    module.fail_json(msg="Le fichier '{}' est introuvable".format(chemin))

# Avertissement non bloquant
module.warn("Le paramètre 'ancien' est obsolète, utilisez 'nouveau'")
```

### Types de paramètres supportés

| Type | Description | Exemple |
|------|-------------|---------|
| `str` | Chaîne de caractères | `type: str` |
| `int` | Entier | `type: int` |
| `bool` | Booléen | `type: bool` |
| `list` | Liste | `type: list, elements: str` |
| `dict` | Dictionnaire | `type: dict` |
| `path` | Chemin de fichier | `type: path` |
| `raw` | Valeur brute | `type: raw` |

## 🛠️ Exercices

### Exercice 1 – Examiner le module gestion_ini

Lisez et comprenez le code du module `library/gestion_ini.py` :

```bash
# Afficher le module
cat library/gestion_ini.py

# Lire la documentation générée
ansible-doc -M library/ gestion_ini
```

Identifiez :
- Les paramètres acceptés par le module
- La logique d'idempotence
- La gestion du `check_mode`

---

### Exercice 2 – Tester le module dans un playbook

Exécutez le playbook de test :

```bash
ansible-playbook playbooks/test_modules.yml
```

Puis exécutez-le une deuxième fois pour vérifier l'idempotence :

```bash
ansible-playbook playbooks/test_modules.yml
```

**Attendu** : La deuxième exécution affiche `changed=0` pour les tâches déjà exécutées.

---

### Exercice 3 – Mode check

Testez le module en mode check (simulation sans modification) :

```bash
# Supprimer le fichier de test pour partir d'un état vide
rm -f /tmp/modules_demo/config.ini

# Simuler sans modifier
ansible-playbook playbooks/test_modules.yml --check

# Vérifier que le fichier n'a PAS été créé
ls /tmp/modules_demo/config.ini 2>/dev/null || echo "Fichier non créé (comportement attendu)"

# Exécuter réellement
ansible-playbook playbooks/test_modules.yml
```

---

### Exercice 4 – Créer un module simple

Créez un nouveau module `library/verifier_service.py` qui vérifie si un processus est en cours d'exécution :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: verifier_service
short_description: Vérifie si un processus est en cours d'exécution
options:
  nom:
    description: Nom du processus à vérifier
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Vérifier si sshd est en cours
  verifier_service:
    nom: sshd
'''

RETURN = r'''
en_cours:
  description: True si le processus est en cours d'exécution
  type: bool
  returned: always
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            nom=dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    nom = module.params['nom']

    # Vérifier si le processus est en cours
    resultat = subprocess.run(
        ['pgrep', '-x', nom],
        capture_output=True
    )
    en_cours = resultat.returncode == 0

    module.exit_json(
        changed=False,
        en_cours=en_cours,
        message="Processus '{}' {} en cours".format(
            nom, "est" if en_cours else "n'est pas"
        )
    )

if __name__ == '__main__':
    main()
```

Testez-le :

```bash
# Tester dans un playbook
cat > /tmp/test_service.yml << 'EOF'
---
- hosts: local
  gather_facts: false
  tasks:
    - verifier_service:
        nom: python3
      register: r
    - debug:
        msg: "{{ r.message }}"
EOF

ansible-playbook /tmp/test_service.yml
```

## ✅ Validation

```bash
# Vérifier la documentation du module
ansible-doc -M library/ gestion_ini

# Exécuter les tests (idempotence vérifiée automatiquement)
ansible-playbook playbooks/test_modules.yml

# Vérifier le fichier INI créé
cat /tmp/modules_demo/config.ini

# Tester le mode check
ansible-playbook playbooks/test_modules.yml --check
```

## 🔍 Pour aller plus loin

- [Guide de développement de modules Ansible](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- [Utilitaires de modules (module_utils)](https://docs.ansible.com/ansible/latest/dev_guide/developing_module_utilities.html)
- [Tester les modules avec unittest](https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html)
- **Défi 1** : Créez un module qui gère des entrées dans une base de données SQLite (`state: present/absent/query`).
- **Défi 2** : Ajoutez le support `diff` au module `gestion_ini` pour afficher les différences avant/après modification avec `--diff`.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Comprendre gestion_ini</summary>

**Paramètres acceptés :**
- `chemin` (path, requis) : chemin vers le fichier INI
- `section` (str, requis) : nom de la section
- `cle` (str, requis) : nom de la clé
- `valeur` (str, requis si etat=present) : valeur à définir
- `etat` (str, default=present) : `present` ou `absent`
- `creer` (bool, default=true) : créer le fichier si absent

**Logique d'idempotence :**
- Pour `etat=present` : compare la valeur actuelle avec la valeur désirée
- Pour `etat=absent` : vérifie si la clé existe avant de la supprimer
- Si aucun changement : retourne `changed=False`

**Gestion du check_mode :**
- `supports_check_mode=True` dans `AnsibleModule()`
- Les lectures de fichier se font normalement
- L'écriture est ignorée si `module.check_mode` est True

</details>

<details>
<summary>Solution – Exercice 3 : Mode check</summary>

```bash
rm -f /tmp/modules_demo/config.ini
ansible-playbook playbooks/test_modules.yml --check
# Résultat : changed=X (simulé), fichier non créé

ls /tmp/modules_demo/config.ini 2>/dev/null \
  && echo "ERREUR : fichier créé en mode check" \
  || echo "OK : fichier non créé en mode check"
```

</details>

<details>
<summary>Solution – Défi 2 : Support diff dans gestion_ini</summary>

Dans la fonction `main()`, modifiez le `module.exit_json` lors d'une modification :

```python
if modifie:
    contenu_apres = config_vers_chaine(config)
    if not module.check_mode:
        ecrire_fichier_ini(chemin, config)
    module.exit_json(
        changed=True,
        message=message,
        contenu_avant=contenu_avant,
        contenu_apres=contenu_apres,
        diff=dict(
            before=contenu_avant,
            after=contenu_apres
        )
    )
```

Puis testez avec `--diff` :

```bash
ansible-playbook playbooks/test_modules.yml --diff
```

</details>

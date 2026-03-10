# Lab 22 – Automatisation réseau

## 🎯 Objectifs

- Comprendre les particularités de l'automatisation réseau avec Ansible
- Configurer un inventaire réseau avec le type de connexion `network_cli`
- Utiliser les modules réseau (`cli_command`, `cli_config`, `ios_*`)
- Sauvegarder et restaurer des configurations réseau
- Découvrir la collection NAPALM pour le multi-constructeur

## 📋 Prérequis

- Labs 01–21 complétés
- Notions de base en réseau (TCP/IP, SSH, VLAN)
- Optionnel : accès à des équipements réseau ou simulateur (GNS3, EVE-NG)
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer les collections réseau
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon

# Optionnel : installer NAPALM
uv pip install napalm

# Se placer dans le répertoire du lab
cd labs/lab-22-automatisation-reseau/
```

## 📚 Concepts expliqués

### Différences avec l'automatisation serveur

| Aspect | Serveurs | Équipements réseau |
|--------|----------|-------------------|
| Connexion | SSH (shell standard) | SSH (CLI propriétaire) |
| Agent | Python sur la cible | Pas de Python |
| Modules | Exécutés sur la cible | Exécutés sur le contrôleur |
| Idempotence | Native | Dépend du module |
| Redémarrage | `reboot` | `reload` (plus risqué) |

### Types de connexion réseau

```yaml
# network_cli : CLI standard via SSH
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: cisco.ios.ios

# httpapi : API REST
ansible_connection: ansible.netcommon.httpapi

# netconf : Protocole NETCONF (XML)
ansible_connection: ansible.netcommon.netconf
```

### Inventaire réseau

```yaml
# inventory/reseau.yml
all:
  children:
    routeurs:
      hosts:
        R1:
          ansible_host: 192.168.1.1
        R2:
          ansible_host: 192.168.1.2
      vars:
        ansible_connection: ansible.netcommon.network_cli
        ansible_network_os: cisco.ios.ios
        ansible_user: admin
        ansible_password: "{{ vault_network_password }}"
        ansible_become: true
        ansible_become_method: enable
        ansible_become_password: "{{ vault_enable_password }}"

    switchs:
      hosts:
        SW1:
          ansible_host: 192.168.1.10
      vars:
        ansible_connection: ansible.netcommon.network_cli
        ansible_network_os: cisco.ios.ios
```

### Modules réseau courants

| Module | Description |
|--------|-------------|
| `cisco.ios.ios_command` | Exécuter des commandes show |
| `cisco.ios.ios_config` | Appliquer une configuration |
| `cisco.ios.ios_facts` | Collecter les faits réseau |
| `ansible.netcommon.cli_command` | Commande CLI générique |
| `ansible.netcommon.cli_config` | Configuration CLI générique |

### Sauvegarde de configuration

```yaml
- name: Sauvegarder la configuration
  cisco.ios.ios_config:
    backup: true
    backup_options:
      filename: "{{ inventory_hostname }}_backup.cfg"
      dir_path: ./backups/
```

## 🛠️ Exercices

### Exercice 1 – Inventaire réseau et connexion

**But :** Configurer un inventaire pour des équipements réseau.

**Instructions :**

1. Examiner l'inventaire réseau :
```bash
cat inventory/mononode.yml
```

2. Examiner le playbook de simulation :
```bash
cat playbooks/reseau_simulation.yml
```

3. Exécuter la simulation :
```bash
ansible-playbook playbooks/reseau_simulation.yml
```

**Résultat attendu :** Les concepts d'inventaire réseau sont affichés et compris.

---

### Exercice 2 – Commandes show et collecte de faits

**But :** Utiliser les modules pour collecter des informations réseau.

**Instructions :**

1. Examiner le playbook de collecte :
```bash
cat playbooks/collecte_faits.yml
```

2. Observer la syntaxe des modules réseau :
```yaml
- name: Exécuter show version
  cisco.ios.ios_command:
    commands:
      - show version
      - show ip interface brief
  register: sortie_show
```

3. Avec des équipements réels :
```bash
ansible-playbook -i inventory/reseau.yml playbooks/collecte_faits.yml
```

**Résultat attendu :** Les informations réseau sont collectées et affichées.

---

### Exercice 3 – Configuration et sauvegarde

**But :** Appliquer et sauvegarder des configurations réseau.

**Instructions :**

1. Examiner le playbook de configuration :
```bash
cat playbooks/configuration_reseau.yml
```

2. Observer les patterns de configuration :
```yaml
- name: Configurer une interface
  cisco.ios.ios_config:
    lines:
      - description Lien vers serveur web
      - ip address 10.0.1.1 255.255.255.0
      - no shutdown
    parents: interface GigabitEthernet0/1
    save_when: modified
```

**Résultat attendu :** Compréhension de la gestion de configuration réseau.

## ✅ Validation

```bash
# Exécuter la simulation
ansible-playbook playbooks/reseau_simulation.yml

# Vérifier les fichiers créés
ls /tmp/reseau_demo/
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Réseau](https://docs.ansible.com/ansible/latest/network/index.html)
- [Collection cisco.ios](https://docs.ansible.com/ansible/latest/collections/cisco/ios/index.html)
- [NAPALM](https://napalm.readthedocs.io/)
- **Défi 1** : Créez un playbook qui sauvegarde automatiquement la configuration de tous les équipements réseau et la versione dans Git.
- **Défi 2** : Utilisez NAPALM pour comparer la configuration running vs startup et générer un rapport de différences.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Inventaire réseau</summary>

```yaml
# inventory/reseau.yml
all:
  children:
    routeurs:
      hosts:
        R1:
          ansible_host: 192.168.1.1
        R2:
          ansible_host: 192.168.1.2
      vars:
        ansible_connection: ansible.netcommon.network_cli
        ansible_network_os: cisco.ios.ios
        ansible_user: admin
        ansible_password: "{{ vault_network_password }}"
```

```bash
# Test de connexion
ansible routeurs -i inventory/reseau.yml -m cisco.ios.ios_command -a "commands='show version'"
```

</details>

<details>
<summary>Solution – Exercice 3 : Configuration et sauvegarde</summary>

```yaml
---
- name: Configuration et sauvegarde réseau
  hosts: routeurs
  gather_facts: false
  tasks:
    - name: Sauvegarder la configuration actuelle
      cisco.ios.ios_config:
        backup: true
        backup_options:
          filename: "{{ inventory_hostname }}_{{ lookup('pipe', 'date +%Y%m%d') }}.cfg"
          dir_path: ./backups/

    - name: Appliquer la configuration
      cisco.ios.ios_config:
        lines:
          - description Configuré par Ansible
          - ip address 10.0.1.1 255.255.255.0
          - no shutdown
        parents: interface GigabitEthernet0/1
        save_when: modified

    - name: Vérifier la configuration
      cisco.ios.ios_command:
        commands:
          - show running-config interface GigabitEthernet0/1
      register: config_verif

    - name: Afficher la configuration
      ansible.builtin.debug:
        var: config_verif.stdout_lines
```

</details>

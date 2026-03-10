# Lab 03 – Commandes Ad-hoc

## 🎯 Objectifs
- Maîtriser la syntaxe des commandes ad-hoc Ansible
- Utiliser les modules courants : `shell`, `command`, `copy`, `file`, `package`, `service`, `user`
- Comprendre la différence entre les modules `command` et `shell`
- Récupérer des informations système sans écrire un playbook

## 📋 Prérequis
- Labs 01 et 02 complétés
- Ansible installé et fonctionnel
- Environnement virtuel activé

## ⏱️ Durée estimée
45 minutes

## 🏗️ Mise en place
1. Se placer dans le répertoire `labs/lab-03-commandes-adhoc/`
2. Activer l'environnement virtuel : `source .venv/bin/activate`
3. Vérifier l'inventaire : `cat inventory/mononode.yml`

## 📚 Concepts expliqués

### Qu'est-ce qu'une commande ad-hoc ?
Une commande ad-hoc est une commande Ansible exécutée directement depuis la ligne de commande, sans playbook. Elle est utile pour des opérations ponctuelles et rapides.

**Syntaxe générale :**
```bash
ansible <hôtes> -m <module> -a "<arguments>" -i <inventaire> [options]
```

### Comparaison : module `command` vs `shell`
| Critère | `command` | `shell` |
|---|---|---|
| Interpréteur shell | Non | Oui (`/bin/sh`) |
| Redirections (`>`, `|`) | Non supportées | Supportées |
| Variables d'environnement | Limitées | Complètes |
| Sécurité | Plus sûr | Moins sûr |
| Usage recommandé | Commandes simples | Commandes complexes |

### Modules courants pour les commandes ad-hoc

| Module | Usage | Exemple |
|---|---|---|
| `ping` | Tester la connectivité | `ansible all -m ping` |
| `command` | Exécuter une commande | `ansible all -m command -a "uptime"` |
| `shell` | Exécuter via le shell | `ansible all -m shell -a "echo $HOME"` |
| `copy` | Copier un fichier | `ansible all -m copy -a "src=f dest=/tmp/f"` |
| `file` | Gérer fichiers/répertoires | `ansible all -m file -a "path=/tmp/d state=directory"` |
| `fetch` | Rapatrier un fichier | `ansible all -m fetch -a "src=/etc/hosts dest=./hosts"` |
| `apt` | Gérer les paquets Debian | `ansible all -m apt -a "name=curl state=present"` |
| `service` | Gérer les services | `ansible all -m service -a "name=nginx state=started"` |
| `user` | Gérer les utilisateurs | `ansible all -m user -a "name=alice state=present"` |
| `setup` | Collecter les facts | `ansible all -m setup` |

### L'option `-b` / `--become`
Pour exécuter des commandes avec des privilèges élevés (sudo) :
```bash
ansible localhost -m apt -a "name=curl state=present" -b
```

### L'option `--check`
Le mode "dry-run" : simule l'exécution sans effectuer de changements réels :
```bash
ansible localhost -m file -a "path=/tmp/test state=directory" --check
```

## 🛠️ Exercices

### Exercice 1 – Collecte d'informations système
**But :** Utiliser les commandes ad-hoc pour obtenir des informations sur le système local.
**Instructions :**
1. Afficher le temps de fonctionnement (uptime) :
   ```bash
   ansible localhost -m command -a "uptime"
   ```
2. Afficher l'espace disque disponible :
   ```bash
   ansible localhost -m command -a "df -h"
   ```
3. Utiliser le module `setup` pour obtenir la distribution Linux :
   ```bash
   ansible localhost -m setup -a "filter=ansible_distribution"
   ```
4. Afficher l'utilisateur courant avec le module `shell` :
   ```bash
   ansible localhost -m shell -a "whoami && id"
   ```

**Questions :**
- Quelle est la différence entre la sortie de `command` et celle de `setup` ?
- Pourquoi utiliser `setup` plutôt que `command -a "uname -a"` ?

### Exercice 2 – Opérations sur les fichiers
**But :** Créer, modifier et supprimer des fichiers via des commandes ad-hoc.
**Instructions :**
1. Créer un répertoire temporaire :
   ```bash
   ansible localhost -m file -a "path=/tmp/ansible_lab state=directory mode=0755"
   ```
2. Créer un fichier avec du contenu :
   ```bash
   ansible localhost -m copy -a "content='Créé par Ansible\n' dest=/tmp/ansible_lab/test.txt mode=0644"
   ```
3. Vérifier que le fichier existe avec le module `stat` :
   ```bash
   ansible localhost -m stat -a "path=/tmp/ansible_lab/test.txt"
   ```
4. Récupérer le contenu du fichier :
   ```bash
   ansible localhost -m command -a "cat /tmp/ansible_lab/test.txt"
   ```
5. Supprimer le répertoire :
   ```bash
   ansible localhost -m file -a "path=/tmp/ansible_lab state=absent"
   ```

**Résultat attendu :** Le répertoire et son contenu sont créés puis supprimés correctement.

### Exercice 3 – Idempotence
**But :** Comprendre le concept d'idempotence en Ansible.
**Instructions :**
1. Exécuter deux fois la même commande de création de répertoire :
   ```bash
   ansible localhost -m file -a "path=/tmp/idem_test state=directory"
   ansible localhost -m file -a "path=/tmp/idem_test state=directory"
   ```
2. Observer la couleur et le statut (`changed` vs `ok`) lors des deux exécutions
3. Comparer avec un module non idempotent :
   ```bash
   ansible localhost -m shell -a "mkdir -p /tmp/idem_test2"
   ansible localhost -m shell -a "mkdir -p /tmp/idem_test2"
   ```
4. Nettoyer :
   ```bash
   ansible localhost -m file -a "path=/tmp/idem_test state=absent"
   ansible localhost -m file -a "path=/tmp/idem_test2 state=absent"
   ```

**Questions :**
- Quelle est la couleur de sortie lors de la première exécution ? Et la seconde ?
- Pourquoi le module `shell` est-il toujours marqué `changed` ?

## ✅ Validation
```bash
# Tester la connectivité
ansible localhost -m ping

# Vérifier l'uptime
ansible localhost -m command -a "uptime"

# Créer et vérifier un fichier
ansible localhost -m copy -a "content='test\n' dest=/tmp/validation_ansible.txt"
ansible localhost -m stat -a "path=/tmp/validation_ansible.txt"

# Nettoyer
ansible localhost -m file -a "path=/tmp/validation_ansible.txt state=absent"

```

## 🔍 Pour aller plus loin
- [Introduction aux commandes ad-hoc](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)
- [Module command](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html)
- [Module shell](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html)
- [Module copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html)
- **Défi 1** : Utiliser une commande ad-hoc pour afficher le contenu de `/etc/os-release`
- **Défi 2** : Utiliser `--check` et `--diff` ensemble sur une commande de copie de fichier pour voir ce qui changerait
- **Défi 3** : Utiliser `-o` (one-line output) pour afficher les résultats de plusieurs hôtes sur une seule ligne

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
# Uptime
ansible localhost -m command -a "uptime"

# Espace disque
ansible localhost -m command -a "df -h"

# Distribution via setup (retourne des facts structurés, plus fiables)
ansible localhost -m setup -a "filter=ansible_distribution"

# Utilisateur courant (nécessite le shell pour les pipes)
ansible localhost -m shell -a "whoami && id"

# La différence : setup retourne des données JSON structurées et fiables,
# tandis que command retourne du texte brut.
```

### Solution Exercice 2
```bash
# Créer le répertoire
ansible localhost -m file -a "path=/tmp/ansible_lab state=directory mode=0755"

# Créer un fichier
ansible localhost -m copy -a "content='Créé par Ansible\n' dest=/tmp/ansible_lab/test.txt mode=0644"

# Vérifier
ansible localhost -m stat -a "path=/tmp/ansible_lab/test.txt"

# Lire le contenu
ansible localhost -m command -a "cat /tmp/ansible_lab/test.txt"

# Supprimer
ansible localhost -m file -a "path=/tmp/ansible_lab state=absent"
```

### Solution Exercice 3
```bash
# Première exécution -> "changed" (jaune) : le répertoire est créé
ansible localhost -m file -a "path=/tmp/idem_test state=directory"

# Deuxième exécution -> "ok" (vert) : rien à faire, déjà idempotent
ansible localhost -m file -a "path=/tmp/idem_test state=directory"

# Le module shell est TOUJOURS "changed" car Ansible ne peut pas savoir
# si mkdir a réellement modifié quelque chose.
```
</details>

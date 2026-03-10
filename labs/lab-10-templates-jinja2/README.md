# Lab 10 – Templates Jinja2

## 🎯 Objectifs
- Maîtriser les filtres Jinja2 les plus utilisés dans Ansible
- Utiliser les tests Jinja2 (`is defined`, `is none`, `is match`)
- Créer des templates complexes avec boucles et conditions
- Comprendre les macros Jinja2

## 📋 Prérequis
- Labs 01–09 complétés
- Notions de base sur les templates (Lab 08)

## ⏱️ Durée estimée
75 minutes

## 🏗️ Mise en place
1. Activer l'environnement virtuel : `source .venv/bin/activate`
2. Se placer dans `labs/lab-10-templates-jinja2/`

## 📚 Concepts expliqués

### Filtres Jinja2 essentiels

| Filtre | Utilisation | Exemple |
|--------|-------------|---------|
| `default` | Valeur par défaut | `{{ port \| default(80) }}` |
| `upper` / `lower` | Casse | `{{ nom \| upper }}` |
| `join` | Joindre une liste | `{{ liste \| join(', ') }}` |
| `length` | Longueur | `{{ liste \| length }}` |
| `int` / `float` | Conversion | `{{ "42" \| int }}` |
| `replace` | Remplacer | `{{ texte \| replace('a','b') }}` |
| `regex_replace` | Regex | `{{ texte \| regex_replace('^www\.','') }}` |
| `select` | Filtrer liste | `{{ liste \| select('match', '^web') }}` |
| `map` | Transformer | `{{ liste \| map('upper') \| list }}` |
| `sort` | Trier | `{{ liste \| sort }}` |
| `unique` | Dédupliquer | `{{ liste \| unique }}` |
| `to_json` / `to_yaml` | Sérialiser | `{{ dict \| to_json }}` |
| `from_json` | Désérialiser | `{{ json_str \| from_json }}` |
| `combine` | Fusionner dicts | `{{ d1 \| combine(d2) }}` |

### Tests Jinja2

```jinja2
{% if variable is defined %}
{% if variable is none %}
{% if variable is string %}
{% if variable is number %}
{% if variable is iterable %}
{% if url is match("^https://") %}
```

### Macros Jinja2
Les macros sont des fonctions réutilisables dans les templates.

## 🛠️ Exercices

### Exercice 1 – Filtres essentiels
**But :** Utiliser les filtres Jinja2 courants dans un playbook.
**Instructions :**
1. Créer un playbook qui démontre une dizaine de filtres différents
2. Exécuter le playbook et observer les résultats

### Exercice 2 – Template de configuration nginx
**But :** Générer une configuration nginx réaliste.
**Instructions :**
1. Utiliser le template `templates/nginx.conf.j2`
2. Générer la configuration pour plusieurs vhosts

### Exercice 3 – Template avec macros
**But :** Créer et utiliser une macro Jinja2.
**Instructions :**
1. Définir une macro pour générer des blocs de configuration répétitifs
2. Appeler la macro plusieurs fois dans le template

### Exercice 4 – Filtres avancés
**But :** Utiliser `selectattr`, `map`, `combine` et autres filtres avancés.

## ✅ Validation
```bash
ansible-playbook playbooks/filtres_demo.yml
cat /tmp/jinja2_demo/nginx.conf
cat /tmp/jinja2_demo/rapport.html
```

## 🔍 Pour aller plus loin
- [Documentation Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [Filtres Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_filters.html)
- **Défi 1** : Créer un template qui génère un fichier `hosts` Linux complet depuis l'inventaire
- **Défi 2** : Créer un rapport HTML dynamique avec les facts de tous les hôtes

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```yaml
- name: Démonstration des filtres
  hosts: local
  vars:
    liste: [3, 1, 4, 1, 5, 9, 2, 6]
    texte: "Bonjour Monde"
  tasks:
    - name: Filtres sur listes
      debug:
        msg:
          - "Trié: {{ liste | sort }}"
          - "Unique: {{ liste | unique | sort }}"
          - "Longueur: {{ liste | length }}"
          - "Max: {{ liste | max }}, Min: {{ liste | min }}"
```

### Solution Exercice 2
```bash
ansible-playbook playbooks/nginx_config.yml
```
</details>

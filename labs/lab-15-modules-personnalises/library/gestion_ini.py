#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Ansible personnalisé : gestion_ini
Gère les entrées dans les fichiers de configuration au format INI.
"""

DOCUMENTATION = r'''
---
module: gestion_ini
short_description: Gère les entrées dans les fichiers INI
description:
  - Ce module permet d'ajouter, modifier ou supprimer des entrées
    dans des fichiers de configuration au format INI.
  - Il est idempotent : n'effectue des modifications que si nécessaire.
version_added: "1.0.0"
author:
  - Formation Ansible (@formation-ansible)
options:
  chemin:
    description:
      - Chemin vers le fichier INI à gérer.
    required: true
    type: path
  section:
    description:
      - Nom de la section INI (entre crochets).
    required: true
    type: str
  cle:
    description:
      - Nom de la clé dans la section.
    required: true
    type: str
  valeur:
    description:
      - Valeur à définir pour la clé.
      - Requis si etat=present.
    required: false
    type: str
  etat:
    description:
      - C(present) pour créer/modifier l'entrée.
      - C(absent) pour supprimer l'entrée.
    required: false
    default: present
    choices: ['present', 'absent']
    type: str
  creer:
    description:
      - Créer le fichier s'il n'existe pas.
    required: false
    default: true
    type: bool
notes:
  - Ce module est idempotent.
  - Supporte le mode check (--check).
'''

EXAMPLES = r'''
- name: Définir une valeur dans une section
  gestion_ini:
    chemin: /etc/mon-app/config.ini
    section: base_de_donnees
    cle: hote
    valeur: "localhost"
    etat: present

- name: Supprimer une entrée
  gestion_ini:
    chemin: /etc/mon-app/config.ini
    section: obsolete
    cle: ancienne_cle
    etat: absent
'''

RETURN = r'''
modifie:
  description: Indique si le fichier a été modifié.
  returned: always
  type: bool
  sample: true
message:
  description: Message décrivant l'action effectuée.
  returned: always
  type: str
  sample: "Entrée 'hote' dans [base_de_donnees] définie à 'localhost'"
contenu_avant:
  description: Contenu du fichier avant modification.
  returned: when changed
  type: str
contenu_apres:
  description: Contenu du fichier après modification.
  returned: when changed
  type: str
'''

import os
import configparser
import io

from ansible.module_utils.basic import AnsibleModule


def lire_fichier_ini(chemin):
    """Lit un fichier INI et retourne un objet ConfigParser."""
    config = configparser.RawConfigParser()
    config.optionxform = str  # Préserver la casse des clés
    if os.path.exists(chemin):
        config.read(chemin, encoding='utf-8')
    return config


def ecrire_fichier_ini(chemin, config):
    """Écrit un objet ConfigParser dans un fichier INI."""
    with open(chemin, 'w', encoding='utf-8') as f:
        config.write(f)


def config_vers_chaine(config):
    """Convertit un ConfigParser en chaîne de caractères."""
    output = io.StringIO()
    config.write(output)
    return output.getvalue()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            chemin=dict(type='path', required=True),
            section=dict(type='str', required=True),
            cle=dict(type='str', required=True),
            valeur=dict(type='str', required=False, default=None),
            etat=dict(type='str', default='present', choices=['present', 'absent']),
            creer=dict(type='bool', default=True),
        ),
        required_if=[
            ('etat', 'present', ['valeur']),
        ],
        supports_check_mode=True
    )

    chemin = module.params['chemin']
    section = module.params['section']
    cle = module.params['cle']
    valeur = module.params['valeur']
    etat = module.params['etat']
    creer = module.params['creer']

    # Vérifier si le fichier existe
    if not os.path.exists(chemin) and not creer:
        module.fail_json(
            msg="Le fichier '{}' n'existe pas et creer=false".format(chemin)
        )

    # Créer le répertoire parent si nécessaire
    repertoire_parent = os.path.dirname(chemin)
    if repertoire_parent and not os.path.exists(repertoire_parent):
        if not module.check_mode:
            os.makedirs(repertoire_parent, exist_ok=True)

    # Lire le fichier actuel
    config = lire_fichier_ini(chemin)
    contenu_avant = config_vers_chaine(config)

    modifie = False
    message = ""

    if etat == 'present':
        # Créer la section si elle n'existe pas
        if not config.has_section(section):
            config.add_section(section)
            modifie = True

        # Vérifier si la valeur doit être modifiée
        valeur_actuelle = config.get(section, cle, fallback=None)
        if valeur_actuelle != valeur:
            config.set(section, cle, valeur)
            modifie = True
            message = "Entrée '{}' dans [{}] définie à '{}'".format(cle, section, valeur)

    elif etat == 'absent':
        if config.has_section(section) and config.has_option(section, cle):
            config.remove_option(section, cle)
            modifie = True
            message = "Entrée '{}' supprimée de [{}]".format(cle, section)
            # Supprimer la section si elle est vide
            if not config.options(section):
                config.remove_section(section)
                message += " (section [{}] supprimée car vide)".format(section)

    if modifie:
        contenu_apres = config_vers_chaine(config)
        if not module.check_mode:
            ecrire_fichier_ini(chemin, config)
        module.exit_json(
            changed=True,
            message=message,
            contenu_avant=contenu_avant,
            contenu_apres=contenu_apres
        )
    else:
        if not message:
            message = "Aucune modification nécessaire pour '{}' dans [{}]".format(cle, section)
        module.exit_json(
            changed=False,
            message=message
        )


if __name__ == '__main__':
    main()

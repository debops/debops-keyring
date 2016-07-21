#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2016 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2016 DebOps Project http://debops.org/
#
# This Python module is part of DebOps.
#
# DebOps is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# DebOps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DebOps. If not, see http://www.gnu.org/licenses/.

__license__ = 'GPL-3.0'
__author__ = 'Robin Schneider <ypid@riseup.net>'
__version__ = '0.1.0'

"""
Generate debops-keyring rst documentation from files in the debian-keyring format .
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    raise Exception("debops.keyring requires Python3. Python2 is currently not supported.")

import os
import re
import logging
import pprint
from datetime import datetime
from subprocess import check_output
import time

import jinja2
from gnupg import GPG
import git


class Keyring:

    _EXCLUSIVE_ROLES = set([
        # Or primary roles. A entity can only be member of one exclusive role.
        #
        # Exclusive role model is the case for this implementation but must not always make sense.
        # For example. The permission management on GitHub of the DebOps roles
        # is handled differently in that DebOps Developers are also members of
        # the DebOps Contributors role in case Contributors get their own
        # permissions assigned to them.
        'developer',
        'contributor',
        'bot',
    ])
    _ADDITONAL_ROLES = [
        # Used for sorting.
        'leader',
        'admin',
    ]

    # https://keyring.debian.org/creating-key.html
    _OPENPGP_MIN_KEY_SIZE = 2048

    def __init__(
        self,
        strict=True,
        keyring_name='debops-keyring-gpg',
    ):

        self._entities = {}
        self._strict = strict
        self._keyring_name = keyring_name

    def read_keyids(self, keyids_file):
        with open(keyids_file, 'r') as keyids_fd:
            for keyid_line in keyids_fd:
                _re = re.search(
                    r'^(?P<keyid>[^ ]+) (?P<name>[^<]+) <(?P<nick>.*)>$',
                    keyid_line,
                )
                nick = _re.group('nick')
                self._entities.setdefault(nick, {
                    # Redundant because the dict gets translated to a sorted list later.
                    'nick': _re.group('nick'),
                    'keyids': [],  # Preserve order.
                    'name': _re.group('name'),
                    'roles': set([]),  # Sorted later.
                })
                self._entities[nick]['keyids'].append(_re.group('keyid'))

    def _role_sort(self, role):
        if role in self._ADDITONAL_ROLES:
            return self._ADDITONAL_ROLES.index(role)
        else:
            return -1

    def _sort_roles_lists(self):
        for nick in self._entities.keys():
            self._entities[nick]['roles'] = sorted(
                self._entities[nick]['roles'],
                key=self._role_sort,
            )

    def check_entity_consistency(self):
        def_roles = self._EXCLUSIVE_ROLES.union(set(self._ADDITONAL_ROLES))
        for nick, entity_data in self._entities.items():
            exclusive_role_member = self._EXCLUSIVE_ROLES.intersection(
                entity_data['roles']
            )
            if len(exclusive_role_member) != 1:
                raise Exception(
                    "Entity {} is member of `n` mutually exclusive roles"
                    " whereas `n` is {}."
                    " Member of the following set of roles: {}".format(
                        nick,
                        len(exclusive_role_member),
                        exclusive_role_member,
                    )
                )
            undef_roles = entity_data['roles'].difference(def_roles)
            if len(undef_roles) != 0:
                raise Exception(
                    "Entity {} is member of roles which are not defined: {}".format(
                        nick,
                        undef_roles,
                    )
                )
        return True

    def read_entity_role_file(self, entity_role_file, entity_role_name):
        with open(entity_role_file, 'r') as entity_role_fh:
            for entity_role_line in entity_role_fh:
                _re = re.search(
                    r'^(?P<name>[^<]+) <(?P<nick>.*)>$',
                    entity_role_line,
                )
                try:
                    nick = _re.group('nick')
                except AttributeError:
                    raise Exception("You probably made a mistake in the {} file.".format(
                        entity_role_file,
                    ))
                if nick not in self._entities:
                    raise Exception("Nickname {} not present in given keyid file.".format(
                        nick,
                    ))
                self._entities[nick]['roles'].add(entity_role_name)
                if self._strict and self._entities[nick]['name'] != _re.group('name'):
                    raise Exception(
                        "Name mismatch in {} file compared to the keyids file."
                        "\nExpected: {}"
                        "\nActual: {}".format(
                            entity_role_file,
                            _re.group('name'),
                            self._entities[nick]['name'],
                        )
                    )

    def entity_is_member_of(self, nick, role):
        return role in self._entities[nick]['roles']

    def _entity_sort(self, nick):
        if self.entity_is_member_of(nick, 'leader'):
            return -100
        else:
            return -10 * len(self._entities[nick]['roles'])

    def _get_sorted_nicks(self):
        return sorted(self._entities, key=self._entity_sort)


# https://help.riseup.net/en/security/message-security/openpgp/best-practices#openpgp-key-checks
# Tested version: 0.19.1 (as available in Debian Stretch)
# Don’t try to reimplement OpenPGP key linting when there is already a tool for it.
# hopenpgp is currently very alpha-ish and seems to completely lack any kind of documentation.
# At least it does have JSON output because also the exit codes are not
# reliable (at least I never got anything else then 0 even with an expired key
# and with way to small key sizes …)
# Evaluation of the JSON output is also not easy. There seems to be no overall
# result of the linting.
# E. g. when to pass and when to fail would need to be decided ourself.
# TODO: Recheck if hopenpgp-tools becomes usable (a proper exit code would be a start)
    def _check_openpgp_pubkey_from_file(self, pubkey_file, long_key_id):
        with TemporaryDirectory() as temp_gpg_home:
            gpg = GPG(gnupghome=temp_gpg_home)
            with open(pubkey_file, 'rb') as pubkey_fh:
                import_result = gpg.import_keys(pubkey_fh.read())
            if len(import_result.results) != 1:
                raise Exception(
                    "The OpenPGP file {} contains none or more than one OpenPGP key."
                    " Keys: {}".format(
                        pubkey_file,
                        import_result.results,
                    )
                )
            fingerprint = import_result.results[0]['fingerprint']
            actual_long_key_id = fingerprint[-16:]
            given_long_key_id = re.sub(r'^0x', '', long_key_id)
            if actual_long_key_id.lower() != given_long_key_id.lower():
                raise Exception(
                    "The OpenPGP file {given_long_key_id} contains a different key than what the file name suggests."
                    "\nKey ID from file name: {given_long_key_id},"
                    "\nKey ID from pubkey in file: {actual_long_key_id}".format(
                        given_long_key_id=given_long_key_id,
                        actual_long_key_id=actual_long_key_id,
                    )
                )

            list_key = gpg.list_keys()[0]
            epoch_time = int(time.time())
            expires_time = int(list_key['expires'])
            if self._strict and expires_time < epoch_time:
                raise Exception(
                    "The OpenPGP file {} contains a expired OpenPGP key."
                    "\nCurrent time: {}"
                    "\nExpires time: {}".format(
                        pubkey_file,
                        datetime.fromtimestamp(epoch_time),
                        datetime.fromtimestamp(expires_time),
                    )
                )
            # https://keyring.debian.org/creating-key.html
            if self._strict and int(list_key['length']) < self._OPENPGP_MIN_KEY_SIZE:
                raise Exception(
                    "The OpenPGP file {} contains a weak OpenPGP key."
                    "\nCurrent key length in bits: {}"
                    "\nExpected at least (inclusive): {}".format(
                        pubkey_file,
                        list_key['length'],
                        self._OPENPGP_MIN_KEY_SIZE,
                    )
                )

        return True

    def check_openpgp_consistency(self):
        for long_key_id in os.listdir(self._keyring_name):
            self._check_openpgp_pubkey_from_file(
                os.path.join(self._keyring_name, long_key_id),
                long_key_id,
            )
        return True

    def _get_gpg_output_for_pubkey_file(self, pubkey_file):
        with TemporaryDirectory() as temp_gpg_home:
            gpg = GPG(gnupghome=temp_gpg_home)
            with open(pubkey_file, 'rb') as pubkey_fh:
                gpg.import_keys(pubkey_fh.read())
            gpg_stdout = check_output([
                'gpg',
                '--homedir', temp_gpg_home,
                '--keyid-format', '0xlong',
                '--with-fingerprint',
                '--list-options', 'show-uid-validity',
                '--verify-options', 'show-uid-validity',
                # '--list-sigs',
                # Public keys for signatures over the UIDs might not be present.
                '--list-public-keys'
            ]).decode('utf-8')
            truncated_lines = []
            in_header = True
            for line in gpg_stdout.split('\n'):
                # OpenPGP subkeys might be subject to more frequent change
                # and are expected to not always be updated in the keyring.
                # You might need to update OpenPGP subkeys from keyservers.
                if not in_header and not re.match(r'sub\s', line):
                    truncated_lines.append(line)

                if re.match(r'^---------', line):
                    in_header = False
            return '\n'.join(truncated_lines)

    def read_gpg_output_for_pubkeys(self, keyring_name=None):
        if keyring_name is None:
            keyring_name = self._keyring_name
        for nick in self._entities.keys():
            for keyid in self._entities[nick]['keyids']:
                self._entities[nick].setdefault('key_gpg_output', {})
                self._entities[nick]['key_gpg_output'][keyid] = self._get_gpg_output_for_pubkey_file(
                    os.path.join(keyring_name, keyid)
                )

    def get_entity_docs(self, template_file=None):
        self._sort_roles_lists()

        if template_file is None:
            template_file = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'data',
                'debops-entities.rst.j2',
            )

        template_vars = {
            'entities': {
                'developers': [],
                'contributors': [],
                'bots': [],
            }
        }
        for nick in self._get_sorted_nicks():
            exclusive_role_member = self._EXCLUSIVE_ROLES.intersection(
                self._entities[nick]['roles']
            )
            template_vars['entities'][exclusive_role_member.pop()+'s'].append(
                self._entities[nick]
            )

        templateLoader = jinja2.FileSystemLoader(
            searchpath=os.path.dirname(template_file),
        )
        templateEnv = jinja2.Environment(
            loader=templateLoader,
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
        )
        template = templateEnv.get_template(os.path.basename(template_file))
        return template.render(template_vars)

    def write_entity_docs(self, output_file, template_file=None):
        with open(output_file, 'w') as output_fh:
            output_fh.write(self.get_entity_docs(template_file))

    def check_git_commits(self, repo_path='.'):
        with TemporaryDirectory() as temp_gpg_home:
            gpg = GPG(gnupghome=temp_gpg_home)

            for long_key_id in os.listdir(self._keyring_name):
                with open(os.path.join(
                    self._keyring_name,
                    long_key_id
                ), 'rb') as pubkey_fh:
                    gpg.import_keys(pubkey_fh.read())

            repo = git.Git(repo_path)
            repo.update_environment(GNUPGHOME=temp_gpg_home)
            # %G?: show "G" for a Good signature,
            #           "B" for a Bad signature,
            #           "U" for a good, untrusted signature and
            #           "N" for no signature
            for log_line in repo.log('--format=%H %G?').split('\n'):
                (commit_hash, signature_check) = log_line.split(' ')
                if signature_check not in ['U', 'G']:
                    raise Exception(
                        "OpenPGP signature of commit could not be verified."
                        "\nAffected commit:\n{}".format(
                            repo.log(commit_hash),
                        )
                    )

        return True


if __name__ == '__main__':
    from argparse import ArgumentParser

    args_parser = ArgumentParser(
        description=__doc__,
    )
    args_parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args_parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements.",
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    args_parser.add_argument(
        '-v', '--verbose',
        help="Be verbose.",
        action='store_const',
        dest='loglevel',
        const=logging.INFO,
    )
    args_parser.add_argument(
        '-n', '--no-strict',
        help="Do not exit immediately when there is a inconsistency.",
        dest='strict',
        action='store_false',
        default=True,
    )
    args_parser.add_argument(
        '-t', '--entity-template-file',
        help="Jinja2 template file to use for to generate the output file.",
    )
    args_parser.add_argument(
        '-o', '--output-file',
        help="Where to write the rendered template to.",
    )
    args_parser.add_argument(
        '-s', '--show-output',
        help="Write the rendered template to STDOUT for quick checking.",
        action='store_true',
        default=False,
    )
    args_parser.add_argument(
        '-c', '--consistency-check',
        help="Perform a full consistency check.",
        action='store_true',
        dest='consistency_check',
    )
    args_parser.add_argument(
        '--no-consistency-check',
        help="Do not run a full consistency check.",
        action='store_false',
        dest='consistency_check',
    )
    args_parser.add_argument(
        '--no-consistency-check-keyring',
        help="Do not run a keyring related consistency checks.",
        action='store_false',
        dest='consistency_check_keyring',
    )
    args_parser.add_argument(
        '--no-consistency-check-git',
        help="Do not run a git related consistency checks.",
        action='store_false',
        dest='consistency_check_git',
    )
    args_parser.set_defaults(consistency_check=None)
    args_parser.set_defaults(consistency_check_keyring=True)
    args_parser.set_defaults(consistency_check_git=True)
    args = args_parser.parse_args()

    if not args.output_file and not args.show_output and args.consistency_check is None:
        args_parser.error("At least one of the following parameters is required: {}".format(
            ', '.join([
                '--output-file',
                '--show-output',
                '--consistency-check',
            ])
        ))
    if args.consistency_check is None:
        args.consistency_check = True

    logger = logging.getLogger(__file__)
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=args.loglevel,
    )

    debops_keyring = Keyring(
        strict=args.strict,
    )
    debops_keyring.read_keyids('keyids')
    debops_keyring.read_entity_role_file('./leader', 'leader')
    debops_keyring.read_entity_role_file('./admins', 'admin')
    debops_keyring.read_entity_role_file('./developers', 'developer')
    debops_keyring.read_entity_role_file('./contributors', 'contributor')
    debops_keyring.read_entity_role_file('./bots', 'bot')

    if args.consistency_check:
        if args.consistency_check_keyring:
            if not debops_keyring.check_entity_consistency():
                raise Exception("check_entity_consistency failed.")
            if not debops_keyring.check_openpgp_consistency():
                raise Exception("check_openpgp_consistency failed.")
        if args.consistency_check_git:
            if not debops_keyring.check_git_commits():
                raise Exception("check_git_commits failed.")

    debops_keyring.read_gpg_output_for_pubkeys(debops_keyring._keyring_name)
    logger.info("debops_keyring._entities: {}".format(
        pprint.pformat(debops_keyring._entities),
    ))

    if args.show_output:
        print(debops_keyring.get_entity_docs(
            args.entity_template_file,
        ))

    if args.output_file:
        debops_keyring.write_entity_docs(
            args.output_file,
            args.entity_template_file,
        )

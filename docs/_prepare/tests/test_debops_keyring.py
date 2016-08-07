# -*- coding: utf-8 -*-

import os
from tempfile import TemporaryDirectory
import time
import shutil
import subprocess

from nose.tools import assert_equals, raises
from unittest import mock
import git
from gnupg import GPG

from debops.keyring import Keyring


debops_keyring_gpg_test_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'debops-keyring-gpg',
)
debops_keyring_fake_gnupg_home = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'fake_gnupg_home',
)


def test_entity_sorting():
    debops_keyring = Keyring()
    debops_keyring._entities = {
        'nick_a': {'roles': set(['developer'])},
        'nick_b': {'roles': set(['developer', 'leader'])},
        'nick_c': {'roles': set(['developer', 'admin'])},
    }
    assert_equals(
        ['nick_b', 'nick_c', 'nick_a'],
        debops_keyring._get_sorted_nicks()
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634371))
def test_check_openpgp_pubkey_from_file_valid():
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    assert debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, long_key_id),
        long_key_id,
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634371))
@raises(FileNotFoundError)
def test_check_openpgp_pubkey_from_file_with_not_existing_file():
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, 'not_existing_file'),
        long_key_id,
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634371))
def test_check_openpgp_pubkey_from_file_with_not_matching_file():
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, 'not_matching'),
        # Part of the filename. Is not compared.
        long_key_id,
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634371))
@raises(Exception)
def test_check_openpgp_pubkey_from_file_with_not_matching_key_id():
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, long_key_id),
        long_key_id + 'not_matching',
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634372))
@raises(Exception)
def test_check_openpgp_pubkey_expired():
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    assert debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, long_key_id),
        long_key_id,
    )


@mock.patch('time.time', mock.MagicMock(return_value=1506634371))
@raises(Exception)
def test_check_openpgp_pubkey_size():
    Keyring._OPENPGP_MIN_KEY_SIZE = 8192
    debops_keyring = Keyring()
    long_key_id = '0x2DCCF53E9BC74BEC'
    assert debops_keyring._check_openpgp_pubkey_from_file(
        os.path.join(debops_keyring_gpg_test_dir, long_key_id),
        long_key_id,
    )


def test_check_git_commits_unsigned():
    debops_keyring = Keyring(
        keyring_name='../../debops-keyring-gpg',
    )
    with TemporaryDirectory() as tmp_git_repo:
        git_cmd = git.Git(tmp_git_repo)
        git_cmd.init()
        git_cmd.config(['user.email', 'debops-keyring-test@debops.org'])
        git_cmd.config(['user.name', 'debops-keyring-test'])
        git_cmd.update_environment(
            GNUPGHOME=os.path.join(tmp_git_repo, 'gpg_tmp_home'),
        )
        tmp_git_file = os.path.join(tmp_git_repo, 'new-file')
        with open(tmp_git_file, 'w') as tmp_git_fh:
            tmp_git_fh.write(str(time.time()))
        git_cmd.add([tmp_git_file])
        git_cmd.commit(['--no-gpg-sign', '--message', 'Unsigned commit'])
        try:
            # Can raise different exceptions.
            debops_keyring.check_git_commits(tmp_git_repo)
            assert False
        except Exception as e:
            if 'OpenPGP signature of commit could not be verified' in str(e) and 'Unsigned commit' in str(e):
                assert True
            else:
                assert False


def test_check_git_commits_ok():
    with TemporaryDirectory() as tmp_git_repo:
        gpg_tmp_home = os.path.join(tmp_git_repo, 'gpg_tmp_home')
        # Included in the repository to avoid problems with low entropy in CI
        # environments.
        #  input_data = gpg.gen_key_input(
        #      key_type='RSA',
        #      subkey_type='RSA',
        #      key_length=1024,
        #      subkey_length=1024,
        #      name_comment='This is only a test key who’s private key is publicly know. Don’t use this key for anything!1!',
        #      name_email='debops-keyring-test-key@debops.org',
        #      # Has already expired at the time of creation to ensure no one will ever use the key.
        #      expire_date='2012-12-24',  # Needs to be set to the 24 for the key to expire on 23.
        #      # Hm, Ok, gpg does not do that by default. `--faked-system-time`
        #      # could be used to force it but that would require cmd access.
        #      # https://www.gnupg.org/documentation/manuals/gnupg/Unattended-GPG-key-generation.html
        #      # "gpg: Invalid option "--faked-system-time"" :(
        #      # Only: gpg2 --batch --gen-key --debug=0 --faked-system-time '2342-05-23'
        #      # has been confirmed to work from current Debian Stretch.
        #      # Faking it manually anyway …
        #  )
        #  print(input_data)
        #  print(gpg.gen_key(input_data))

        shutil.copytree(debops_keyring_fake_gnupg_home, gpg_tmp_home)
        gpg = GPG(gnupghome=gpg_tmp_home)

        os.chmod(gpg_tmp_home, 0o700)
        for r, d, f in os.walk(gpg_tmp_home):
            os.chmod(r, 0o700)
        gpg_key_fingerprint = gpg.list_keys()[0]['fingerprint']
        gpg_edit_key_cmd = subprocess.Popen(
            ['gpg', '--homedir', gpg_tmp_home, '--command-fd', '0', '--batch', '--edit-key', gpg_key_fingerprint],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        (gpg_edit_key_cmd_stdout, gpg_edit_key_cmd_stderr) = gpg_edit_key_cmd.communicate(
            input='expire\n0\nsave\n'.encode(),
            timeout=5,
        )
        #  print(gpg_edit_key_cmd_stderr.decode())
        #  print(subprocess.check_output(['gpg', '--homedir', gpg_tmp_home, '--list-public-keys']).decode())
        if 'expires: never' not in str(gpg_edit_key_cmd_stderr):
            raise Exception("Could not change expiration date.")
        tmp_keyring_dir = os.path.join(tmp_git_repo, 'tmp-keyring-gpg')
        tmp_pubkey_file = os.path.join(
            tmp_keyring_dir,
            '0x' + gpg_key_fingerprint[-16:].upper()
        )
        os.mkdir(tmp_keyring_dir)
        with open(tmp_pubkey_file, 'w') as tmp_pubkey_fh:
            tmp_pubkey_fh.write(gpg.export_keys(gpg_key_fingerprint))

        git_cmd = git.Git(tmp_git_repo)
        git_cmd.update_environment(
            GNUPGHOME=debops_keyring_fake_gnupg_home,
        )
        git_cmd.init()
        git_cmd.config(['user.signingkey', gpg_key_fingerprint])
        git_cmd.config(['user.email', 'debops-keyring-test@debops.org'])
        git_cmd.config(['user.name', 'debops-keyring-test'])
        git_cmd.update_environment(
            GNUPGHOME=os.path.join(tmp_git_repo, 'gpg_tmp_home'),
        )
        tmp_git_file = os.path.join(tmp_git_repo, 'new-file')
        with open(tmp_git_file, 'w') as tmp_git_fh:
            tmp_git_fh.write(str(time.time()))
        git_cmd.add([tmp_git_file])
        git_cmd.commit(['--gpg-sign', '--message', 'Signed commit'])
        debops_keyring = Keyring(
            keyring_name=tmp_keyring_dir,
        )
        debops_keyring.check_git_commits(tmp_git_repo)

        # Now make a unsigned commit to ensure that this raises an exception.
        with open(tmp_git_file, 'w') as tmp_git_fh:
            tmp_git_fh.write(str(time.time()))
        git_cmd.add([tmp_git_file])
        git_cmd.commit(['--no-gpg-sign', '--message', 'Unsigned commit'])
        try:
            debops_keyring.check_git_commits(tmp_git_repo)
            assert False
        except Exception as e:
            if 'OpenPGP signature of commit could not be verified' in str(e) and 'Unsigned commit' in str(e):
                assert True
            else:
                assert False

import os
from tempfile import TemporaryDirectory
import time

from nose.tools import assert_equals, raises
from unittest import mock
import git

from debops.keyring import Keyring


debops_keyring_gpg_test_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'debops-keyring-gpg',
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


@raises(Exception)
def test_check_git_commits_unsigned():
    debops_keyring = Keyring(
        keyring_name='../../debops-keyring-gpg',
    )
    with TemporaryDirectory() as temp_git_repo:
        r = git.Repo.init(temp_git_repo)
        temp_git_file = os.path.join(temp_git_repo, 'new-file')
        with open(temp_git_file, 'w') as temp_git_fh:
            temp_git_fh.write(str(time.time()))
        r.index.add([temp_git_file])
        r.index.commit("Unsigned commit.")
        debops_keyring.check_git_commits(temp_git_repo)


def test_check_git_commits_ok():
    """
    FIXME: This test does not create a isolated test environment but instead
    tests the current git repository!
    """
    debops_keyring = Keyring(
        keyring_name='../../debops-keyring-gpg',
    )
    assert debops_keyring.check_git_commits()

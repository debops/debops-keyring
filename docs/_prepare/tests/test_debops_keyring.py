from nose.tools import assert_equals, raises
from unittest import mock
from debops.keyring import Keyring
import os


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

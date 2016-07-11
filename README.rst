debops-keyring
==============

The repository contains OpenPGP / GnuPG keys used by the DebOps Developers.
These keys can be used to authenticate and verify the ``git`` commits and tags
in other DebOps repositories.

.. contents::
   :local:
   :depth: 1

Why GPG keys are used to sign code in the DebOps Project
--------------------------------------------------------

The DebOps Project is designed to be used in production environment, therefore
some kind of a verifiable trust path is required to ensure that the code used to
execute commands can be trusted. Because DebOps Project is developed in an
environment not exclusively controlled by its Developers (GitHub), additional
verification of authenticity provided by commits and tags signed by trusted GPG
keys is beneficial to the DebOps Project and its users, regardless of whether
signing each ``git`` commit is sensible or not.

See also
~~~~~~~~

- `DebOps Code Signing Policy <https://github.com/debops/debops-policy/blob/master/docs/code-signing.rst>`_
- `A Git Horror Story: Repository Integrity With Signed Commits <https://mikegerwitz.com/papers/git-horror-story>`_

Canonical source of the debops-keyring repository
-------------------------------------------------

The repository was initialized and signed by Maciej Delmanowski on his own
private computer and uploaded to the GitHub repository using the SSH protocol.
It can be found at the following URL:

    https://github.com/debops/debops-keyring

Repository contents
-------------------

The repository layout follows `debian-keyring <https://anonscm.debian.org/git/keyring/keyring.git/tree/>`_.

``debops-keyring-gpg/``
  This directory contains OpenPGP / GnuPG keys currently used by the DebOps
  Developers to sign their code and Pull/Merge Requests.

``keyids``
  This file contains a canonical mapping between GPG keys and the user names of
  their owners used within the DebOps Project.

``leader``
  This file defines who the current DebOps Project Leader is.

``admins``
  This file lists the DebOps Project Admins.

``developers``
  This file lists all DebOps Developers.

Commit and tag verification
---------------------------

Before the verification can be performed correctly, you need to import the GPG
keys to your GnuPG keyring. To do that, you should clone this repository to
a directory on your computer, for example with a command:

.. code-block:: console

   user@host:~$ git clone https://github.com/debops/debops-keyring ~/src/github.com/debops/debops-keyring

After that, you should import the provided keys to your GPG keyring:

.. code-block:: console

   user@host:~$ gpg --import ~/src/github.com/debops/debops-keyring/debops-keyring-gpg/0x*

To verify GPG signatures on commits in a ``git`` repository, you can use the
command:

.. code-block:: console

   user@host:~$ git log --show-signature

To verify GPG signature on a tag in a ``git`` repository, you can use the
command:

.. code-block:: console

   user@host:~$ git tag --verify <tag-id>

Adding your GPG publc key
-------------------------

When you feel associated with the DebOps Project and have made at least one
contribution to the Project you are free to add your GPG public key to this
repository.

To do so you should add your GPG public key(s) to ``debops-keyring-gpg/``
using:

.. code-block:: console

   user@host:~$ gpg --export <long_key_ID> > <long_key_ID>

And then specify key ID to person mapping in the ``keyids`` file.

Becoming a DebOps Developer
---------------------------

To become a DebOps Developer, you should have contribution to the DebOps
Project for a while (say 6 months) and know a thing or two how the Project
works.

To make this official, all you need to do is follow the `Adding your GPG publc
key`_ section and then add yourself to the ``developers`` file.

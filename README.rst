debops-keyring
==============

The debops-keyring_ contains OpenPGP/GnuPG keys used by the DebOps Developers and
DebOps Contributors.
These keys can be used to authenticate and verify the ``git`` commits and tags
in main repositories of the DebOps Project.

.. contents::
   :local:
   :depth: 1

Why OpenPGP keys are used to sign code in the DebOps Project
------------------------------------------------------------

The DebOps Project is designed to be used in production environment, therefore
some kind of a verifiable trust path is required to ensure that the code used to
execute commands can be trusted. Because DebOps Project is developed in an
environment not exclusively controlled by its Developers (GitHub), additional
verification of authenticity provided by commits and tags signed by trusted OpenPGP
keys is beneficial to the DebOps Project and its users, regardless of whether
signing each ``git`` commit is sensible or not.

See also
~~~~~~~~

- `DebOps Code Signing Policy`_
- `A Git Horror Story: Repository Integrity With Signed Commits <https://mikegerwitz.com/papers/git-horror-story>`_

Canonical source of the debops-keyring repository
-------------------------------------------------

The repository was initialized and signed by Maciej Delmanowski on his own
private computer and uploaded to the GitHub repository using the SSH protocol.
It can be found at the following URL:

    https://github.com/debops/debops-keyring

Repository contents
-------------------

The repository layout is modeled after the `debian-keyring <https://anonscm.debian.org/git/keyring/keyring.git/tree/>`_.

``debops-keyring-gpg/``
  This directory contains OpenPGP keys currently used by people working
  on DebOps.

``keyids``
  This file contains a canonical mapping between OpenPGP keys and the user names of
  their owners used within the DebOps Project.

``leader``
  This file defines who the current DebOps Project Leader is.

``admins``
  This file lists the DebOps Project Admins.

``developers``
  This file lists all DebOps Developers.

``contributors``
  This file lists all DebOps Contributors.

``bots``
  This file lists all DebOps Bots.

Commit and tag verification
---------------------------

Before the verification can be performed correctly, you need to import the OpenPGP
keys to your GnuPG keyring. To do that, you should clone this repository to
a directory on your computer, for example with a command:

.. code-block:: console

   user@host:~$ git clone https://github.com/debops/debops-keyring ~/src/github.com/debops/debops-keyring

After that, you should import the provided keys to your OpenPGP keyring:

.. code-block:: console

   user@host:~$ gpg --import ~/src/github.com/debops/debops-keyring/debops-keyring-gpg/0x*

To verify OpenPGP signatures on commits in a ``git`` repository, you can use the
command:

.. code-block:: console

   user@host:~$ git log --show-signature

To verify OpenPGP signature on a tag in a ``git`` repository, you can use the
command:

.. code-block:: console

   user@host:~$ git tag --verify <tag-id>

Adding your OpenPGP publc key
-----------------------------

When you feel associated with the DebOps Project and have made at least one
contribution to the Project you are free to add your OpenPGP public key to this
repository.

To do so you should add your OpenPGP public key(s) to ``debops-keyring-gpg/``
using:

.. code-block:: console

   user@host:~$ gpg --export <long_key_ID> > <long_key_ID>

And then specify the key ID to person mapping in the ``keyids`` file.

Note that you should be reasonably confident that "no
one has ever had a copy of your private key"[#opsec-snowden-quote]_.
Otherwise you could easily be impersonated.
Refer to `OpenPGP Best Practices <https://help.riseup.net/en/security/message-security/openpgp/best-practices>`_
for more details.

Then add yourself to the corresponding file, either ``contributors`` or
``developers`` (if the requirements from the `Becoming a DebOps Developer`_
section are met).

The commit that you make to add or change these files must be signed by your
most trusted  OpenPGP signing (sub)key (in case you have multiple which cross
sign each other) to prove that you have control over this identity (Root of
Trust).

.. [#opsec-snowden-quote] https://www.wired.com/2014/10/snowdens-first-emails-to-poitras/

Changing your OpenPGP publc key
-------------------------------

The policy for this procedure is not yet fixed. A starting point could be
`Rules for key replacement in the Debian keyring`_.

Becoming a DebOps Developer
---------------------------

To become a DebOps Developer, you should have contribution to the DebOps
Project for a while (say 6 months) and know a thing or two how the Project
works.

To make this official, all you need to do is follow the `Adding your OpenPGP publc
key`_ section and then add yourself to the ``developers`` file.

.. The file needs to be self contained e. g. no includes. Thus the needed
   entries from https://github.com/debops/docs/blob/master/docs/includes/global.rst
   are inlined here:
.. _debops-keyring: https://github.com/debops/debops-keyring
.. _DebOps Code Signing Policy: http://docs.debops.org/en/latest/debops-policy/docs/code-signing-policy.html
.. _Rules for key replacement in the Debian keyring: https://keyring.debian.org/replacing_keys.html

debops-keyring
==============

The debops-keyring_ contains OpenPGP/GnuPG keys used by the DebOps Developers and
DebOps Contributors.
These keys can be used to authenticate and verify the ``git`` commits and tags
in main repositories of the DebOps Project.

.. contents::
   :local:
   :depth: 1

Terminology
-----------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14, [`RFC2119`_].

Why OpenPGP keys are used to sign code in the DebOps Project
------------------------------------------------------------

The DebOps Project is designed to be used in production environment, therefore
some kind of a verifiable trust path is REQUIRED to ensure that the code used to
execute commands can be trusted. Because DebOps Project is developed in an
environment not exclusively controlled by its Developers (GitHub), additional
verification of authenticity provided by commits and tags signed by trusted OpenPGP
keys is beneficial to the DebOps Project and its users, regardless of whether
signing each ``git`` commit is sensible or not.

See also:

- `DebOps Code Signing Policy`_

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

``roles/leader``
  This file defines who the current DebOps Project Leader is.

``roles/admins``
  This file lists the DebOps Project Admins.

``roles/developers``
  This file lists all DebOps Developers.

``roles/contributors``
  This file lists all DebOps Contributors.

``roles/bots``
  This file lists all DebOps Bots.

Commit and tag verification
---------------------------

Before the verification can be performed correctly, you need to import the OpenPGP
keys to your GnuPG keyring. To do that, you should clone this repository to
a directory on your computer, for example with a command:

.. code-block:: console

   git clone https://github.com/debops/debops-keyring ~/src/github.com/debops/debops-keyring

After that, you should import the provided keys to your OpenPGP keyring:

.. code-block:: console

   gpg --import ~/src/github.com/debops/debops-keyring/debops-keyring-gpg/0x*

To verify OpenPGP signatures on commits in a ``git`` repository, you can use the
command:

.. code-block:: console

   git log --show-signature

To verify OpenPGP signature on a tag in a ``git`` repository, you can use the
command:

.. code-block:: console

   git tag --verify <tag-id>

Adding your OpenPGP public key
------------------------------

When you feel associated with the DebOps Project and have made at least one
contribution to the Project you are free to add your OpenPGP public key to this
repository.

Printing Long Key IDs:

.. code-block:: console

   gpg --keyid-format long --list-keys

To do so you should add your OpenPGP public key(s) to ``debops-keyring-gpg/``
using:

.. code-block:: console

   gpg --export <long_key_ID> > <long_key_ID>

Additionally, it is REQUIRED that you upload your public key(s) to
`sks-keyservers.net`_ or another OpenPGP keyserver pools which sync with
`sks-keyservers.net`_. This is also the place where changes (subkeys actively
used for signing or encryption, and key expiration) to your key(s) MUST be
uploaded to.  Key signatures SHOULD be uploaded there as well.

And then specify the key ID to person mapping in the ``keyids`` file.

Note that you SHOULD be reasonably confident that "no
one has ever had a copy of your private key"[#opsec-snowden-quote]_.
Otherwise you could easily be impersonated.
Refer to `OpenPGP Best Practices`_ for more details.


Then add yourself to the corresponding file, either ``roles/contributors`` or
``roles/developers`` (if the requirements from the `Becoming a DebOps Developer`_
section are met).

The commit that you make to add or change these files MUST be signed by your
most trusted OpenPGP signing (sub)key (Root of Trust – in case you have
multiple which (cross) sign each other) to prove that you have control over this
identity.

To prove that you have full control over your account on the source code
management platform used to work on the DebOps Project (currently GitHub) it is
RECOMMENDED for the DebOps Contributors and REQUIRED for the DebOps Developers
to provide a proof via the means of https://keybase.io/.

Additionally, it is RECOMMENDED to take part in the Web Of Trust to make it
harder for an adversary to fake signatures by pretending to be one of the
DebOps Contributors or Developers. In particular as the DebOps Project is
related to the Debian Project it is RECOMMENDED to get your key signed by at
least one Debian Developer.  A signature from another DebOps Developer is
sufficient as well.

RECOMMENDED, source https://bettercrypto.org/:

  For asymmetric public-key cryptography we consider any key length below 3248 bits to be
  deprecated at the time of this writing (for long term protection).

2048 bits is the absolut minimum key size which MUST be met (enforced by CI tests).

.. [#opsec-snowden-quote] https://www.wired.com/2014/10/snowdens-first-emails-to-poitras/

Changing your OpenPGP public key
--------------------------------

The policy for this procedure is not yet fixed. A starting point could be
`Rules for key replacement in the Debian keyring`_.

Becoming a DebOps Developer
---------------------------

To become a DebOps Developer, you SHOULD have contribution to the DebOps
Project for a while (say 6 months) and know a thing or two how the Project
works.

To make this official, all you need to do is follow the `Adding your OpenPGP public
key`_ section and then add yourself to the ``roles/developers`` file.

.. The file needs to be self contained e. g. no includes. Thus the needed
   entries from https://github.com/debops/docs/blob/master/docs/includes/global.rst
   are inlined here:
.. _debops-keyring: https://github.com/debops/debops-keyring
.. _DebOps Code Signing Policy: http://docs.debops.org/en/latest/debops-policy/docs/code-signing-policy.html
.. _Rules for key replacement in the Debian keyring: https://keyring.debian.org/replacing_keys.html
.. _sks-keyservers.net: https://sks-keyservers.net/status/
.. _OpenPGP Best Practices: https://help.riseup.net/en/security/message-security/openpgp/best-practices
.. _RFC2119: https://tools.ietf.org/html/rfc2119

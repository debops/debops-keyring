.PHONY: default docs docs-prepare docs-build entities-show
	docs-entities.rst-show check check-keyring check-implementation check-nose
	check-nose2 FORCE_MAKE install-pre-commit-hook run-pre-commit-hook

FORCE_MAKE:
SRC_DIR = docs/_prepare
PIP_OPTIONS =
NOSE_OPTIONS =
DEBOPS_KEYRING_VERBOSE = --verbose

default: check-keyring

install-dependencies:
	pip3 install $(PIP_OPTIONS) -r ./docs/_prepare/requirements.txt

install-pre-commit-hook: ./docs/_prepare/hooks/pre-commit
	ln -srf "$<" "$(shell git rev-parse --git-dir)/hooks"

run-pre-commit-hook: ./docs/_prepare/hooks/pre-commit
	"$<"

docs: docs-prepare docs-build

# Target will be made on docs build time when docs/_prepare/ is present.
docs-prepare: docs/entities.rst

docs-build:
	sphinx-debops-role-build

entities-show: docs-entities.rst-show

docs/entities.rst: $(SRC_DIR)/debops/keyring.py FORCE_MAKE
	"$<" --no-strict --output-file "$@"

docs-entities.rst-show: $(SRC_DIR)/debops/keyring.py
	"$<" --show-output

# Target will be made during CI of this repository.
check: check-implementation check-keyring

check-keyring: $(SRC_DIR)/debops/keyring.py
	"$<" --consistency-check $(DEBOPS_KEYRING_VERBOSE)
	"$<" --consistency-check --verbose

check-keyring-no-git: $(SRC_DIR)/debops/keyring.py
	"$<" --consistency-check --no-consistency-check-git $(DEBOPS_KEYRING_VERBOSE)

# check-keyring-additional:
#     hkt export-pubkeys $(long_keyid) | hokey lint

check-implementation: check-nose2

check-nose:
	cd "$(SRC_DIR)" && nosetests $(NOSE_OPTIONS)

check-nose2:
	cd "$(SRC_DIR)" && (nose2-3 --start-dir tests $(NOSE_OPTIONS) || nose2-3.4 $(NOSE_OPTIONS))

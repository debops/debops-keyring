FORCE_MAKE:
SRC_DIR = docs/_prepare
PIP_OPTIONS =
NOSE_OPTIONS =
DEBOPS_KEYRING_VERBOSE = --verbose

.PHONY: default
default: check-keyring

.PHONY: install-dependencies
install-dependencies:
	pip3 install $(PIP_OPTIONS) -r ./docs/_prepare/requirements.txt

## Git hooks {{{
.PHONY: install-pre-commit-hook
install-pre-commit-hook: ./docs/_prepare/hooks/pre-commit
	ln -srf "$<" "$(shell git rev-parse --git-dir)/hooks"

.PHONY: run-pre-commit-hook
run-pre-commit-hook: ./docs/_prepare/hooks/pre-commit
	"$<"

.PHONY: remove-pre-commit-hook
remove-pre-commit-hook:
	rm -f "$(shell git rev-parse --git-dir)/hooks/pre-commit"
## }}}

.PHONY: docs
docs: docs-prepare docs-build

# Target will be made on docs build time when docs/_prepare/ is present.
.PHONY: docs-prepare
docs-prepare: docs/entities.rst

.PHONY: docs-build
docs-build:
	sphinx-debops-role-build

.PHONY: entities-show
entities-show: docs-entities.rst-show

docs/entities.rst: $(SRC_DIR)/debops/keyring.py FORCE_MAKE
	"$<" --no-strict --output-file "$@"

.PHONY: docs-entities.rst-show
docs-entities.rst-show: $(SRC_DIR)/debops/keyring.py
	"$<" --show-output

# Target will be made during CI of this repository.
.PHONY: check
check: check-implementation check-keyring

.PHONY: check-keyring
check-keyring: $(SRC_DIR)/debops/keyring.py
	"$<" --consistency-check $(DEBOPS_KEYRING_VERBOSE)

.PHONY: check-keyring-no-git
check-keyring-no-git: $(SRC_DIR)/debops/keyring.py
	"$<" --consistency-check --no-consistency-check-git $(DEBOPS_KEYRING_VERBOSE)

# .PHONY: check-keyring-additional
# check-keyring-additional:
#     hkt export-pubkeys $(long_keyid) | hokey lint

.PHONY: check-implementation
check-implementation: check-nose2

# .PHONY: check-nose
# check-nose:
#     cd "$(SRC_DIR)" && nosetests3 $(NOSE_OPTIONS)

.PHONY: check-nose2
check-nose2:
	cd "$(SRC_DIR)" && (nose2-3 --start-dir tests $(NOSE_OPTIONS) || nose2-3.4 $(NOSE_OPTIONS))

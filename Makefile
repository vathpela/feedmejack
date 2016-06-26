PKGNAME=feedmejack
VERSION=$(shell python3 setup.py --version)
VERSION_TAG=$(PKGNAME)-$(VERSION)

PYTHON=python3
COVERAGE=coverage
PEP8=$(PYTHON)-pep8
ifeq ($(PYTHON),python3)
  COVERAGE=coverage3
endif

TEST_DEPENDENCIES += python3-mock
TEST_DEPENDENCIES += python3-coverage
TEST_DEPENDENCIES += python3-pocketlint
TEST_DEPENDENCIES += python3-pep8
TEST_DEPENDENCIES := $(shell echo $(sort $(TEST_DEPENDENCIES)) | uniq)

all:
	$(MAKE) -C po

check-requires:
	@echo "*** Checking if the dependencies required for testing and analysis are available ***"
	@status=0 ; \
	for pkg in $(TEST_DEPENDENCIES) ; do \
		test_output="$$(rpm -q --whatprovides "$$pkg")" ; \
		if [ $$? != 0 ]; then \
			echo "$$test_output" ; \
			status=1 ; \
		fi ; \
	done ; \
	exit $$status

install-requires:
	@echo "*** Installing the dependencies required for testing and analysis ***"
	dnf install -y $(TEST_DEPENDENCIES)

test: check-requires
	@echo "*** Running unittests with $(PYTHON) ***"
	PYTHONPATH=. $(PYTHON) -m unittest discover -v -s tests/ -p '*_test.py'

coverage: check-requires
	@echo "*** Running unittests with $(COVERAGE) for $(PYTHON) ***"
	PYTHONPATH=.:tests/ $(COVERAGE) run --branch -m unittest discover -v -s tests/ -p '*_test.py'
	$(COVERAGE) report --include="feedmejack/*" --show-missing
	$(COVERAGE) report --include="feedmejack/*" > coverage-report.log

pylint: check-requires
	@echo "*** Running pylint ***"
	PYTHONPATH=.:tests/:$(PYTHONPATH) tests/pylint/runpylint.py

pep8: check-requires
	@echo "*** Running pep8 compliance check ***"
	$(PEP8) --ignore=E501,E402,E731 feedmejack/ tests/ examples/

canary: check-requires po-fallback
	@echo "*** Running translation-canary tests ***"
	PYTHONPATH=translation-canary:$(PYTHONPATH) python3 -m translation_canary.translatable po/feedmejack.pot

check:
	@status=0; \
	$(MAKE) pylint || status=1; \
	$(MAKE) pep8 || status=1; \
	$(MAKE) canary || status=1; \
	exit $$status

clean:
	-rm *.tar.gz feedmejack/*.pyc feedmejack/*/*.pyc ChangeLog
	$(PYTHON) setup.py -q clean --all

install:
	$(PYTHON) setup.py install --root=$(DESTDIR)
	$(MAKE) -C po install

ChangeLog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

tag:
	@tags='$(VERSION_TAG)' ; \
	for tag in $$tags ; do \
	  git tag -a -s -m "Tag as $$tag" -f $$tag ; \
	  echo "Tagged as $$tag" ; \
	done

release: tag archive

archive:
	@make -B ChangeLog
	mkdir $(PKGNAME)-$(VERSION)
	git archive --format=tar --prefix=$(PKGNAME)-$(VERSION)/ $(VERSION_TAG) | tar -xf -
	cp -r po $(PKGNAME)-$(VERSION)
	cp ChangeLog $(PKGNAME)-$(VERSION)/
	( cd $(PKGNAME)-$(VERSION) && $(PYTHON) setup.py -q sdist --dist-dir .. )
	rm -rf $(PKGNAME)-$(VERSION)
	@echo "The archive is in $(PKGNAME)-$(VERSION).tar.gz"

local:
	@make -B ChangeLog
	$(PYTHON) setup.py -q sdist --dist-dir .
	@echo "The archive is in $(PKGNAME)-$(VERSION).tar.gz"

scratch:
	@rm -f ChangeLog
	@make ChangeLog
	@rm -rf $(PKGNAME)-$(VERSION).tar.gz
	@rm -rf /tmp/$(PKGNAME)-$(VERSION) /tmp/$(PKGNAME)
	@dir=$$PWD; cp -a $$dir /tmp/$(PKGNAME)-$(VERSION)
	@cd /tmp/$(PKGNAME)-$(VERSION) ; $(PYTHON) setup.py -q sdist
	@cp /tmp/$(PKGNAME)-$(VERSION)/dist/$(PKGNAME)-$(VERSION).tar.gz .
	@rm -rf /tmp/$(PKGNAME)-$(VERSION)
	@echo "The archive is in $(PKGNAME)-$(VERSION).tar.gz"

ci: check coverage

.PHONY: check clean pylint pep8 install tag archive local

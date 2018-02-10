MIN_COVER = 98

.PHONY: install install-dev install-test install-full run-tests \
	init-git-submodules

init-git-submodules:
	@git submodule init && \
	git submodule update

install:
	@pip install -e .

install-dev: init-git-submodules
	@pip install -e .[dev]

install-test:
	@pip install -e .[test]

install-full: init-git-submodules
	@pip install -e .[dev,test]

run-tests: install-test
	@nosetests --with-coverage --cover-inclusive --cover-erase \
	--cover-tests --cover-min-percentage=$(MIN_COVER)

release:
	@python setup.py sdist upload -r pypi
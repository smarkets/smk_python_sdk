.PHONY: docs dist

all: deps

build:
	python setup.py build

clean:
	python setup.py clean
	-rm -rf dist
	-rm -rf build
	-rm -rf smk.egg-info
	-rm -rf smarkets/streaming_api/eto.py
	-rm -rf smarkets/streaming_api/seto.py
	find . -name "*.pyc" -exec rm {} \;

dist: clean build
	python setup.py sdist
	python setup.py bdist_wheel

release: dist
	python setup.py sdist upload
	python setup.py bdist_wheel upload

test: build
	nosetests smarkets

check:
	mkdir -p build/pep8
	flake8 --exclude=eto.py,seto.py --max-line-length=110 smarkets *.py

docs:
	$(MAKE) -C docs html

github:
	git push github github-master:master
	git push github HEAD:refs/tags/v$(VSN)

delvsn:
	git push github :refs/tags/v$(VSN)

autopep8:
	find . -name \*.py |egrep -v "env|travis" | xargs autopep8 --max-line-length=115 --recursive --in-place -j 8

sync:
	git remote | while read remote; do \
		git pull $$remote master; \
		git push -u $$remote master; \
		git fetch $$remote --tags; \
		git push $$remote --tags; \
	done;

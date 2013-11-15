.PHONY: docs dist

all: deps

deps:
	python setup.py build

clean:
	python setup.py clean

distclean: clean
	-rm -rf dist
	-rm -rf build
	-rm -rf smk.egg-info
	-rm -rf smarkets/streaming_api/eto.py
	-rm -rf smarkets/streaming_api/seto.py
	-find . -name "*.pyc" | xargs rm

dist: distclean deps
	python setup.py sdist
	python setup.py bdist_wheel

release: dist
	python setup.py sdist upload
	python setup.py bdist_wheel upload

test: deps
	mkdir -p build/test
	nosetests --with-xunit --with-ignore-docstrings --verbose --all-modules \
		--xunit-file=build/test/nosetests.xml smarkets

check:
	mkdir -p build/pylint build/pep8
	pylint --rcfile=./.pylintrc --ignore=eto.py --ignore=seto.py -f parseable \
		-r n smarkets; test $$(( $$? & 3 )) -eq 0
	pep8 --exclude=eto.py,seto.py --ignore=E501,W292 smarkets

docs:
	$(MAKE) -C docs html

github:
	git push github github-master:master
	git push github HEAD:refs/tags/v$(VSN)

delvsn:
	git push github :refs/tags/v$(VSN)

autopep8:
	find . -name \*.py |egrep -v "env|travis" | xargs autopep8 --max-line-length=115 --recursive --in-place -j 8

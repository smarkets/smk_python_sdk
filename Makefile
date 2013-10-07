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
	-rm -rf smarkets/eto
	-rm -rf smarkets/seto
	-find . -name "*.pyc" | xargs rm

release: deps
	python setup.py sdist --format=gztar,zip

test: deps
	mkdir -p build/test
	nosetests --with-xunit --with-ignore-docstrings --verbose \
		--xunit-file=build/test/nosetests.xml tests/

check:
	mkdir -p build/pylint build/pep8
	pylint --rcfile=./.pylintrc --ignore=piqi_pb2.py -f parseable -r n smarkets; test $$(( $$? & 3 )) -eq 0
	pep8 --exclude=piqi_pb2.py --ignore=E501,W292 smarkets

docs:
	$(MAKE) -C docs html

github:
	git push github github-master:master
	git push github HEAD:refs/tags/v$(VSN)

delvsn:
	git push github :refs/tags/v$(VSN)

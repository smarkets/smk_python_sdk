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
	-rm README

release: deps
	python setup.py sdist --format=gztar,zip

test: deps
	mkdir -p build/test
	nosetests --with-xunit --quiet --xunit-file=build/test/nosetests.xml tests/unit_tests.py

check:
	mkdir -p build/pylint build/pep8
	-pylint --ignore=piqi_pb2.py -f parseable smarkets > build/pylint/pylint.out
	pep8 --exclude=piqi_pb2.py smarkets > build/pep8/pep8.out

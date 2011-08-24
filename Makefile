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
	./run_tests

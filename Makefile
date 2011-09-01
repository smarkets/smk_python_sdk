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
	-pylint --rcfile=./.pylintrc --ignore=piqi_pb2.py -f parseable -r n smarkets \
		| grep -v "Instance of 'Payload' has no 'events_request' member" \
		| grep -v "Instance of 'Payload' has no 'eto_payload' member" \
		| grep -v "Instance of 'Payload' has no 'Clear' member" \
		| grep -v "Instance of 'Uuid128' has no 'Clear' member" \
		| grep -v "Instance of 'Payload' has no 'CopyFrom' member" \
		| grep -v "Instance of 'Payload' has no 'ParseFromString' member" \
		| grep -v "Instance of 'Payload' has no 'SerializeToString' member" \
		| grep -v "Instance of 'Payload' has no 'login' member" \
		| grep -v "Instance of 'Events' has no 'ParseFromString' member" \
		> build/pylint/pylint.out
	pep8 --exclude=piqi_pb2.py smarkets > build/pep8/pep8.out

docs:
	$(MAKE) -C docs html

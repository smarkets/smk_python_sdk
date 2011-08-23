NAME = smk_python_sdk
VERSION = $(shell python setup.py --version)
DST = dist/$(NAME)-$(VERSION)

all:
	python setup.py build

clean:
	python setup.py clean

distclean: clean
	-rm -rf dist
	-rm -rf build
	-rm -rf smk.egg-info
	-rm -rf smk/eto
	-rm -rf smk/seto
	-find . -name "*.pyc" | xargs rm
	-rm README

release: all
	-find . -name "*.pyc" | xargs rm
	-find . -name "*.orig" | xargs rm
	-rm -rf smk/.cache
	-mkdir dist
	-rm -rf dist/$(NAME)-$(VERSION)
	-rm dist/$(NAME)-$(VERSION).tar.gz
	-rm dist/$(NAME)-$(VERSION).zip
	-mkdir dist/$(NAME)-$(VERSION)
	python setup.py sdist --formats=bztar,gztar,zip
	cp -r smk tests $(DST)
	cp setup.py README README.md MANIFEST.in CHANGELOG run_tests $(DST)
	cd dist && tar -czv -f $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	cd dist && zip $(NAME)-$(VERSION).zip -r $(NAME)-$(VERSION)

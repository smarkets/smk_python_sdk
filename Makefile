NAME = smk_python_sdk
VERSION = $(shell python setup.py --version)
DST = dist/$(NAME)-$(VERSION)

all: smk.seto.piqi.proto README

build/pb:
	mkdir -p build/pb
	(cd build/pb && \
		git clone git://git.corp.smarkets.com/smk_api_common.git && \
		cd smk_api_common && \
		./rebar get-deps)

eto.piqi: build/pb
	cp build/pb/smk_api_common/deps/eto_common/eto.piqi .

seto.piqi: build/pb
	cp build/pb/smk_api_common/seto.piqi .

smk.eto.piqi.proto: eto.piqi
	piqi to-proto eto.piqi -o smk.eto.piqi.proto

smk.seto.piqi.proto: smk.eto.piqi.proto seto.piqi
	piqi to-proto seto.piqi -o smk.seto.piqi.proto
	sed -i.bak 's/import "eto\.piqi\.proto"/import "smk.eto.piqi.proto"/g' \
		smk.seto.piqi.proto
	rm -f smk.seto.piqi.proto.bak

# seto/piqi_pb2.py: seto.piqi.proto
# 	mkdir -p smk/seto
# 	touch smk/seto/__init__.py
# 	protoc --python_out=. seto.piqi.proto

# eto/piqi_pb2.py: eto.piqi.proto
# 	mkdir -p smk/eto
# 	touch smk/eto/__init__.py
# 	protoc --python_out=. eto.piqi.proto

clean:
	rm -rf eto.piqi seto.piqi smk.seto.piqi.proto smk.eto.piqi.proto smk/eto smk/seto smk/*.pyc build

README: README.md
	pandoc -s README.md -w rst -o README

release: all
	-find . -name "*.pyc" | xargs rm
	-find . -name "*.orig" | xargs rm
	-rm -rf smk/.cache
	-mkdir dist
	-rm -rf dist/$(NAME)-$(VERSION)
	-rm dist/$(NAME)-$(VERSION).tar.gz
	-rm dist/$(NAME)-$(VERSION).zip
	-mkdir dist/$(NAME)-$(VERSION)
	python setup.py build
	cp -r smk seto eto tests $(DST)
	cp setup.py README README.md MANIFEST.in CHANGELOG run_tests $(DST)
	cd dist && tar -czv -f $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	cd dist && zip $(NAME)-$(VERSION).zip -r $(NAME)-$(VERSION)

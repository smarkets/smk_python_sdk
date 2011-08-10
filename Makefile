all: seto/piqi_pb2.py eto/piqi_pb2.py

build/pb:
	mkdir -p build/pb
	(cd build/pb && \
		git clone git://git.corp.smarkets.com/smk_api_common.git && \
		cd smk_api_common && \
		git checkout ticket-3228-new-types && \
		./rebar get-deps)

eto.piqi.proto: build/pb
	piqi to-proto build/pb/smk_api_common/deps/eto_common/eto.piqi \
		-o eto.piqi.proto

seto.piqi.proto: build/pb eto.piqi.proto
	piqi to-proto -I build/pb/smk_api_common/deps/eto_common/ \
		build/pb/smk_api_common/seto.piqi -o seto.piqi.proto

seto/piqi_pb2.py: seto.piqi.proto
	mkdir -p seto
	touch seto/__init__.py
	protoc --python_out=. seto.piqi.proto

eto/piqi_pb2.py: eto.piqi.proto
	mkdir -p eto
	touch eto/__init__.py
	protoc --python_out=. eto.piqi.proto

clean:
	rm -rf seto.piqi.proto eto.piqi.proto eto seto smk/*.pyc build

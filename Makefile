all: seto.proto smk/seto_pb2.py

seto.proto:
	mkdir -p build/pb
	(cd build/pb && \
		git clone git://git.corp.smarkets.com/smk_api_common.git && \
		cd smk_api_common && \
		./rebar get-deps)
	piqi to-proto -I build/pb/smk_api_common/deps/eto_common/ \
		build/pb/smk_api_common/seto.piqi -o seto.proto

smk/seto_pb2.py: seto.proto
	protoc --python_out=smk seto.proto

clean:
	rm -rf seto.proto smk/seto_pb2.py smk/*.pyc build

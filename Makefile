all: seto.proto seto_pb2.py

seto.proto:
	mkdir -p pb
	(cd pb && \
		git clone git://git.corp.smarkets.com/smk_api_common.git && \
		cd smk_api_common && \
		./rebar get-deps)
	piqi to-proto -I pb/smk_api_common/deps/eto_common/ \
		pb/smk_api_common/seto.piqi -o pb/seto.proto
	mv pb/seto.proto .
	rm -rf pb

seto_pb2.py: seto.proto
	protoc --python_out=. seto.proto

clean:
	rm -rf seto.proto seto_pb2.py *.pyc pb

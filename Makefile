



pb:
	mkdir pb
	(cd pb && \
		git clone ~/corp/smk_api_common && \
		cd smk_api_common && \
			./rebar get-deps)
	piqi to-proto -I pb/smk_api_common/deps/eto_common/ \
		pb/smk_api_common/seto.piqi -o pb/seto.proto
	protoc --python_out=. pb/seto.proto
	mv pb/seto_pb2.py .
	rm -rf pb

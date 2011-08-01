seto_pb2.py:
	protoc --python_out=. seto.proto

clean:
	rm -f seto_pb2.py *.pyc

all: seto_pb2.py

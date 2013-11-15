import os

if 'READTHEDOCS' in os.environ:
    from mock import Mock
    import sys

    mock = eto = seto = Mock()
    sys.modules['smarkets.streaming_api.eto'] = sys.modules['smarkets.streaming_api.seto'] = mock

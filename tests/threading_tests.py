import logging
import time
import threading
import unittest

from Queue import Queue, Empty

import smarkets.eto.piqi_pb2 as eto
import smarkets.seto.piqi_pb2 as seto
import smarkets as smk


class ThreadingTestCase(unittest.TestCase):

    "Test using separate reader and writer threads"
    host = None
    port = None
    passwords = None
    ssl = None

    def get_session(self, user_index, cls=None):
        if cls is None:
            cls = smk.Session
        username = 'none@domain.invalid'
        password = 'none'
        if self.passwords:
            username, password = self.passwords[user_index]
        settings = smk.SessionSettings(username, password)
        if self.host is not None:
            settings.host = self.host
        if self.port is not None:
            settings.port = self.port
        if self.ssl is not None:
            settings.ssl = self.ssl
        return cls(settings)

    def get_client(
            self, cls=None, session=None, session_cls=None, user_index=0):
        if cls is None:
            cls = smk.Smarkets
        if session is None:
            session = self.get_session(user_index, cls=session_cls)
        return cls(session)

    def setUp(self):
        time.sleep(1)
        self.client = self.get_client()
        self.sender = SendingThread(self.client)
        self.receiver = ReceivingThread(self.client)
        self.assertFalse(self.client.session.connected)
        self.assertTrue(self.client.session.session is None)
        # We must start with a clean seq #1
        self.assertEquals(self.client.session.outseq, 1)
        self.assertEquals(self.client.session.inseq, 1)
        # Start the sender thread first
        self.sender.login()
        self.sender.start()
        # Wait for 30 seconds (default socket timeout) until connected
        # and login is sent before starting receiver
        self.sender.login_complete.wait(30)
        self.assertTrue(self.sender.login_complete.isSet())
        self.receiver.start()
        name, response = self.receiver.get()
        self.assertEquals(name, 'eto.login_response')
        self.assertEquals(
            response.eto_payload.type,
            eto.PAYLOAD_LOGIN_RESPONSE)

    def tearDown(self):
        self.sender.send(self.client.logout)
        self.sender.stop()
        self.receiver.stop()
        self.sender.join()
        self.receiver.join()
        self.client = None
        self.receiver = None
        self.sender = None

    def test_ping(self):
        self.sender.send(self.client.ping)
        name, pong_msg = self.receiver.get()
        self.assertEquals('eto.pong', name)
        self.assertEquals(
            pong_msg.type,
            seto.PAYLOAD_ETO)
        self.assertEquals(
            pong_msg.eto_payload.type,
            eto.PAYLOAD_PONG)


class WorkItem(object):

    "Individual item of work for a sending thread"
    __slots__ = ('callable_obj', 'args', 'kwargs', 'login')

    def __init__(self, callable_obj, args=None, kwargs=None, login=False):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.callable_obj = callable_obj
        self.args = args
        self.kwargs = kwargs
        self.login = login

    def __call__(self):
        # Proxy the call to the callable and fail with additional
        # arguments
        self.callable_obj(*self.args, **self.kwargs)


class SendingThread(threading.Thread):

    "Thread used for all sending payloads"
    logger = logging.getLogger('smarkets.test.sender')

    def __init__(self, client):
        super(SendingThread, self).__init__()
        self.client = client
        self.running = True
        self.daemon = True
        self.queue = Queue()
        self.name = 'session sender'
        self.login_complete = threading.Event()

    def login(self):
        "Enqueue an initial connect-and-login work item"
        self.logger.debug('[%s] enqueueing a login work item', _cthrd())
        self.queue.put_nowait(WorkItem(self.client.login, [False], login=True))

    def send(self, callable_obj, *args, **kwargs):
        "Enqueue a callable with arguments"
        self.logger.debug('[%s] putting callable %r on queue', _cthrd(), callable_obj)
        self.queue.put_nowait(WorkItem(callable_obj, args, kwargs))

    def stop(self):
        "Stop the thread"
        self.logger.debug('[%s] stopping', _cthrd())
        self.running = False

    def run(self):
        "Repeated pull outgoing payloads off the queue and send them"
        while self.running:
            self.logger.debug('[%s] getting a WorkItem', _cthrd())
            try:
                item = self.queue.get(timeout=1)
            except Empty:
                self.logger.debug('[%s] nothing in queue')
                continue
            self.logger.debug('[%s] got a WorkItem, calling it', _cthrd())
            item()
            self.queue.task_done()
            if item.login:
                # Set the login for synchronization
                self.logger.debug('[%s] setting login_complete event', _cthrd())
                self.login_complete.set()
        self.logger.debug('[%s] leaving run()', _cthrd())


class ReceivingThread(threading.Thread):

    "Thread used for receiving payloads from the socket"
    logger = logging.getLogger('smarkets.test.receiver')
    queue_timeout = 1  # 1 second max wait

    def __init__(self, client):
        super(ReceivingThread, self).__init__()
        self.client = client
        self.daemon = True
        self.running = True
        self.queue = Queue()
        self.name = 'session receiver'

    def stop(self):
        "Stop the thread"
        self.running = False

    def on_message(self, name, message):
        "On receiving a message, put it in the queue"
        self.logger.debug('[%s] received message with name %s', _cthrd(), name)
        self.queue.put_nowait((name, self.client.copy_payload(message)))

    def run(self):
        "Repeatedly read new messages"
        self.client.add_global_handler(self.on_message)
        while self.running:
            try:
                self.client.read()
            except smk.SocketDisconnected:
                self.logger.info('[%s] caught SocketDisconnected exception, finishing...', _cthrd())
                self.running = False
        self.logger.debug('[%s] leaving run()', _cthrd())

    def get(self, timeout=None):
        "Get the next message"
        self.logger.debug('[%s] getting a message from the queue...', _cthrd())
        item = self.queue.get(timeout=timeout or self.queue_timeout)
        self.logger.debug('[%s] got a message', _cthrd())
        self.queue.task_done()
        return item


def _cthrd():
    "Shortcut for readable thread string"
    t = threading.current_thread()
    return '%s:%r' % (t.name, t.ident)

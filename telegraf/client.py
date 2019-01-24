import socket
from abc import abstractmethod
from functools import wraps
from time import time

from telegraf.protocol import Line
from telegraf.utils import is_higher_py35

if is_higher_py35():
    from telegraf.context import wrapped_coroutine
    from asyncio import iscoroutinefunction
else:
    def wrapped_coroutine(self, func):
        raise NotImplementedError(u"Async timer decorator requires Python 3.5 or higher.")

    def iscoroutinefunction(*args, **kwargs):
        return False


class ClientBase(object):

    def __init__(self, host='localhost', port=8094, tags=None):
        self.host = host
        self.port = port
        self.tags = tags or {}

    def metric(self, measurement_name, values, tags=None, timestamp=None):
        """
        Append global tags configured for the client to the tags given then
        converts the data into InfluxDB Line protocol and sends to to socket
        """
        if not measurement_name or values in (None, {}):
            # Don't try to send empty data
            return

        tags = tags or {}

        # Do a shallow merge of the metric tags and global tags
        all_tags = dict(self.tags, **tags)

        # Create a metric line from the input and then send it to socket
        line = Line(measurement_name, values, all_tags, timestamp)
        self.send(line.to_line_protocol())

    def timer(self, measurement_name, tags=None, use_ms=False):
        return TimerHelper(self, measurement_name=measurement_name, tags=tags, use_ms=use_ms)

    @abstractmethod
    def send(self, data):
        pass


class TelegrafClient(ClientBase):

    def __init__(self, host='localhost', port=8094, tags=None):
        super(TelegrafClient, self).__init__(host, port, tags)

        # Creating the socket immediately should be safe because it's UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        """
        Sends the given data to the socket via UDP
        """
        try:
            self.socket.sendto(data.encode('utf8') + b'\n', (self.host, self.port))
        except (socket.error, RuntimeError):
            # Socket errors should fail silently so they don't affect anything else
            pass


class HttpClient(ClientBase):

    def __init__(self, host='localhost', port=8094, tags=None):
        # only import HttpClient's dependencies if using HttpClient
        # if they're not found, inform the user how to install them
        try:
            from requests_futures.sessions import FuturesSession
        except ImportError:
            raise ImportError('pytelegraf[http] must be installed to use HTTP transport')

        super(HttpClient, self).__init__(host, port, tags)

        # the default url path for writing metrics to Telegraf is /write
        self.url = 'http://{host}:{port}/write'.format(host=self.host, port=self.port)

        # create a session to reuse the TCP socket when possible
        self.future_session = FuturesSession()

    def send(self, data):
        """
        Send the data in a separate thread via HTTP POST.
        HTTP introduces some overhead, so to avoid blocking the main thread,
        this issues the request in the background.
        """
        self.future_session.post(url=self.url, data=data)


class TimerHelper(object):
    def __init__(self, client, measurement_name=None, tags=None, use_ms=False):
        self.client = client
        self.measurement_name = measurement_name
        self.tags = tags or {}
        self.use_ms = use_ms

    def __call__(self, func):
        """Decorator helper for timing function calls."""
        if not self.measurement_name:
            self.measurement_name = '%s.%s' % (func.__module__, func.__name__)

        # Coroutines
        if iscoroutinefunction(func):
            return wrapped_coroutine(self, func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            start = time()
            try:
                return func(*args, **kwargs)
            finally:
                self._send(start)
        return wrapped

    def __enter__(self):
        if not self.measurement_name:
            raise TypeError("No metric name specified.")
        self.start_time = time()
        return self

    def __exit__(self, type, value, traceback):
        # Report the elapsed time of the context manager.
        self._send(self.start_time)

    def _send(self, start_time):
        elapsed = time() - start_time
        tags = self.tags.copy()
        if self.use_ms:
            elapsed = int(round(1000 * elapsed))
            tags['units'] = 'ms'
        else:
            tags['units'] = 's'
        line = Line(self.measurement_name, elapsed, tags, None)
        self.client.send(line.to_line_protocol())

#!/usr/bin/env python3
import logging
import socketserver
import threading

import backend

LISTEN_PORT = 8099
ENCODING = 'utf-8'


class SocketLineReader:
    """
    Convert bytes to lines.

    Stolen from https://stackoverflow.com/questions/41482989/socket-in-python3-listening-port
    """  # pylint:disable=line-too-long
    def __init__(self, socket_):
        self.socket = socket_
        self._buffer = b''

    def readline(self):
        pre, separator, post = self._buffer.partition(b'\n')
        if separator:
            self._buffer = post
            return pre + separator

        while True:
            data = self.socket.recv(1024)
            if not data:
                return None

            pre, separator, post = data.partition(b'\n')
            if not separator:
                self._buffer += data
            else:
                data = self._buffer + pre + separator
                self._buffer = post
                return data


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    Our handler to read lines from the recv call
    """

    def handle(self):
        logging.info("Connection opened")
        reader = SocketLineReader(self.request)
        try:
            while True:
                data = reader.readline()
                if not data:
                    break
                message = data.decode(ENCODING)
                status = backend.process_message(message)
                # Do not forget this \n.
                # The test server won't notice messages until you send a \n
                send_bytes = status.encode(ENCODING) + b'\n'
                self.request.sendall(send_bytes)
        except ConnectionResetError:
            logging.info("Connection closed")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """A Threaded TCPServer that can handle multiple requests."""
    allow_reuse_address = True


def start_server():
    # A fancy way of saying print()
    # TODO: Log to real files
    logging.basicConfig(level=logging.INFO,
                        handlers=[logging.StreamHandler()])

    # Docker servers need to run as 0.0.0.0
    server = ThreadedTCPServer(("0.0.0.0", LISTEN_PORT),
                               ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        logging.info("Starting server on %s:%s", ip, port)
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    start_server()

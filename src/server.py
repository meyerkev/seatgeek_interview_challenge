#!/usr/bin/env python3
import argparse
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
                message = data.decode(ENCODING).strip()
                logging.debug("Message recieved: %s", message)
                status = backend.process_message(message)
                logging.debug(
                    "Status to return in response to %s: %s", message, status)
                # Do not forget this \n.
                # The test server won't notice messages until you send a \n
                send_bytes = status.encode(ENCODING) + b'\n'
                self.request.sendall(send_bytes)
        except ConnectionResetError:
            logging.info("Connection closed")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """A Threaded TCPServer that can handle multiple requests."""
    allow_reuse_address = True


def parse_args():
    # This is a neat trick!
    # https://gist.github.com/ms5/9f6df9c42a5f5435be0e
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()

    # As of Python 3.9.12, Critical is 50 and every level below it is -10
    args.verbose = 60 - (10 * args.verbose)
    return args


def start_server():
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


def main():
    # Setup the logger
    # A fancy way of saying print()
    # TODO: Log to real files
    args = parse_args()
    logging.basicConfig(level=args.verbose,
                        handlers=[logging.StreamHandler()])

    start_server()


if __name__ == "__main__":
    main()

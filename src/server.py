#!/usr/bin/env python3
import logging
import socket
import threading

from time import sleep

import backend

LISTEN_PORT = 8099
ENCODING = 'utf-8'


class SocketLineReader:
    def __init__(self, socket):
        self.socket = socket
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


def start_server(socket):
    # A fancy way of saying print()
    # TODO: Log to real files

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 7200)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 60)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 30)
    # Sadly required to force-flush tiny messages like these
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.bind(('0.0.0.0', LISTEN_PORT))
    sock.listen(0)

    def handle(conn):
        logging.info('connected:', addr)

        reader = SocketLineReader(conn)
        while True:
            data = reader.readline()
            if not data:
                break
            message = data.decode(ENCODING)
            status = backend.process_message(message)
            # Do not forget this \n.
            # The test server won't notice messages until you send a \n
            send_bytes = status.encode(ENCODING) + b'\n'
            conn.send(send_bytes)

        conn.close()

    try:
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle, args=(conn,)).start()
    except KeyboardInterrupt:
        # clean shutdown w/o output
        pass


if __name__ == "__main__":
    start_server(socket=socket)

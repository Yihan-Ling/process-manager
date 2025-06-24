import logging
import socketserver
import pickle
import struct
from threading import Thread

class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            data = self.connection.recv(slen)
            while len(data) < slen:
                data += self.connection.recv(slen - len(data))
            record = pickle.loads(data)
            logger = logging.getLogger(record.name)
            logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, host='localhost', port=9020):
        super().__init__((host, port), LogRecordStreamHandler)

def start_log_server():
    server = LogRecordSocketReceiver()
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

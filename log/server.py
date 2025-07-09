import logging
import socketserver
import pickle
import struct
from threading import Thread
from process_manager.node import Watcher


def start_log_server(watcher: Watcher):
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

                # Deserialize the LogRecord
                record = pickle.loads(data)
                record = logging.makeLogRecord(record)
                # print(record)
                # print(f"Received log record: {record.name} - {record.getMessage()}")
                # Format the message
                msg = f"{record.name} {record.levelname}: {record.getMessage()}"

                # ✅ Add to global watcher log buffer
                watcher.logs.append(msg)
                if len(watcher.logs) > 1000:
                    watcher.logs.pop(0)

                # ✅ Add to matching node's logs
                flag = False
                for node in watcher.processes:
                    # if node.relaunched:
                    #     continue
                    if record.name in node.module_name or node.module_name in record.name:
                        node.logs.append(msg)
                        if len(node.logs) > 1000:
                            node.logs.pop(0)
                        node.update_severity(record.levelname)
                        flag = True
                        break
                if not flag:
                    watcher.main_logs.append(msg)
                # # Optional: Dispatch to main process's logger system (e.g., if you want colored console output too)
                # logger = logging.getLogger(record.name)
                # logger.handle(record)
                
                

    class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        def __init__(self, host='localhost', port=9020):
            super().__init__((host, port), LogRecordStreamHandler)

    server = LogRecordSocketReceiver()
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

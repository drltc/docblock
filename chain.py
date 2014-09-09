#!/usr/bin/env python3

"""
Connect to a chain server and parse the blockchain.
"""

import codecs
import contextlib
import functools
import struct

import tornado
import tornado.gen
import tornado.ioloop
import tornado.tcpclient

CMD_finish = 0
CMD_get_blocks_from_number = 1

class Logger(object):
    def __init__(self):
        self.level = 0
        return

    def log(self, *args, **kwargs):
        print(" "*self.level, end="")
        print(*args, **kwargs)
        return

    @contextlib.contextmanager
    def nlevel(self):
        self.level += 1
        yield
        self.level -= 1
        return

class Downloader(object):
    def __init__(self, conn):
        self.conn = conn
        return

    @tornado.gen.coroutine
    def read_uint8(self):
        b = yield self.conn.read_bytes(1)
        return struct.unpack("<B", b)[0]

    @tornado.gen.coroutine
    def read_uint32(self):
        b = yield self.conn.read_bytes(4)
        return struct.unpack("<I", b)[0]

    @tornado.gen.coroutine
    def read_uint64(self):
        b = yield self.conn.read_bytes(8)
        return struct.unpack("<Q", b)[0]

    @tornado.gen.coroutine
    def read_bool(self):
        b = yield self.conn.read_bytes(1)
        return struct.unpack("?", b)[0]

    @tornado.gen.coroutine
    def read_vuint(self):
        a = 0
        s = 0
        while True:
            b = yield self.conn.read_bytes(1)
            c = b[0]
            a |= ((c & 0x7F) << s)
            if ((c & 0x80) == 0):
                break
            s += 7
        return a

    @tornado.gen.coroutine
    def read_ripemd160(self):
        b = yield self.conn.read_bytes(20)
        return b

    @tornado.gen.coroutine
    def read_sha256(self):
        b = yield self.conn.read_bytes(32)
        return b

    read_block_id = read_ripemd160
    read_digest = read_sha256
    read_secret_hash = read_ripemd160
    read_time_point = read_uint32

    @tornado.gen.coroutine
    def read_signature(self):
        b = yield self.conn.read_bytes(65)
        return b

    @tornado.gen.coroutine
    def download_chain(self):
        server_protocol_version = yield self.read_uint32()
        print("protocol version:", repr(server_protocol_version))
        if server_protocol_version != 0:
            raise RuntimeError("unknown server_protocol_version")

        yield self.cmd_get_blocks_from_number(0)

        while True:
            count = yield self.read_uint32()
            if count == 0:
                break
            for i in range(count):
                yield self.read_block()

        return

    @tornado.gen.coroutine
    def read_block(self):
        previous = yield self.read_block_id()
        block_num = yield self.read_uint32()
        timestamp = yield self.read_time_point()
        digest_type = yield self.read_digest()
        secret_hash_type = yield self.read_secret_hash()
        previous_secret = yield self.read_secret_hash()
        delegate_signature = yield self.read_signature()

        tx_count = yield self.read_vuint()
        for i in range(tx_count):
            yield self.read_signed_transaction()

        return

    @tornado.gen.coroutine
    def read_optional_slate_id(self):
        valid = yield self.read_bool()
        if valid:
            data = yield self.read_uint64()
        return

    @tornado.gen.coroutine
    def read_operation(self):
        op_type = yield self.read_uint8()
        data_size = yield self.read_vuint()
        data = yield self.conn.read_bytes(data_size)
        return

    @tornado.gen.coroutine
    def read_signed_transaction(self):
        expiration = yield self.read_time_point()
        delegate_slate_id = yield self.read_optional_slate_id()

        op_count = yield self.read_vuint()
        for i in range(op_count):
            op = yield self.read_operation()

        sig_count = yield self.read_vuint()
        for i in range(sig_count):
            sig = yield self.read_signature()

        return

    @tornado.gen.coroutine
    def cmd_get_blocks_from_number(self, start_block=0):
        yield self.write_uint64(CMD_get_blocks_from_number)
        yield self.write_uint32(start_block)
        return

    @tornado.gen.coroutine
    def write_uint32(self, data):
        b = struct.pack("<I", data)
        yield self.conn.write(b)
        return data

    @tornado.gen.coroutine
    def write_uint64(self, data):
        b = struct.pack("<Q", data)
        yield self.conn.write(b)
        return data

class LoggingDownloader(Downloader):
    def __init__(self, conn):
        Downloader.__init__(self, conn)
        self.logger = Logger()
        for name in dir(self):
            if name.startswith("__"):
                continue
            target = getattr(self, name)
            if not callable(target):
                continue
            if not (name.startswith("write_") or name.startswith("read_") or name.startswith("download_")):
                continue
            setattr(self, name, functools.partial(self.wrap, name, target))
        return

    @tornado.gen.coroutine
    def wrap(self, name, target, *args, **kwargs):
        with self.logger.nlevel():
            self.logger.log(name)
            result = target(*args, **kwargs)
            result = yield result
            self.logger.log(name, "returned", self.format(result))
        return result

    def format(self, result):
        if isinstance(result, bytes):
            return codecs.encode(result, "hex_codec")
        return repr(result)

@tornado.gen.coroutine
def main():
    host = "127.0.0.1"
    port = "11235"

    client = tornado.tcpclient.TCPClient()
    connection = yield client.connect(host, port)
    print("connection:", connection)
    downloader = LoggingDownloader(connection)
    yield downloader.download_chain()

    return

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(main)


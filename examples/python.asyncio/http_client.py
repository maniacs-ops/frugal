import os
import logging
import sys
import uuid
import asyncio

from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
from frugal.context import FContext
from frugal.protocol import FProtocolFactory
from frugal.provider import FServiceProvider
from frugal.aio.transport import FHttpTransport

sys.path.append(os.path.join(os.path.dirname(__file__), "gen-py.asyncio"))
from v1.music.f_Store import Client as FStoreClient  # noqa
from v1.music.ttypes import Album  # noqa


root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


async def main():
    # Declare the protocol stack used for serialization.
    # Protocol stacks must match between clients and servers.
    prot_factory = FProtocolFactory(TBinaryProtocol.TBinaryProtocolFactory())

    # Create an HTTP to query the configured server URL
    transport = FHttpTransport("http://localhost:9090/frugal")

    # Using the configured transport and protocol, create a client
    # to talk to the music store service.
    store_client = FStoreClient(FServiceProvider(transport, prot_factory),
                                middleware=logging_middleware)

    album = await store_client.buyAlbum(FContext(),
                                        str(uuid.uuid4()),
                                        "ACT-12345")

    root.info("Bought an album %s\n", album.ASIN)

    await store_client.enterAlbumGiveaway(FContext(),
                                          "kevin@workiva.com",
                                          "Kevin")

    await transport.close()


def logging_middleware(next):
    def handler(method, args):
        root.info('==== CALLING %s ====', method.__name__)
        ret = next(method, args)
        root.info('==== CALLED  %s ====', method.__name__)
        return ret
    return handler


if __name__ == '__main__':
    io_loop = asyncio.get_event_loop()
    io_loop.run_until_complete(main())

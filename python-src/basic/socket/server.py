import asyncio
from basic.payload import builder  # Adjust the import path as necessary
import time

class BasicServer:
    def __init__(self, ipaddr, port=2000):
        self.ipaddr = ipaddr
        self.port = port
        if self.ipaddr is None:
            raise ValueError("IP address is missing or empty")
        elif self.port is None or self.port <= 1024:
            raise ValueError("Port number is missing or not valid (must be above 1024)")

    async def handle_client(self, reader, writer):
        bldr = builder.BasicBuilder()
        while True:
            data = await reader.read(2048)
            if not data:
                break  # Connection closed
            message = data.decode()
            # Log the time at which the message is received
            message_received_time = time.time()
            print(f"Message received time: {message_received_time}")
            _, _, text = bldr.decode(message)
            addr = writer.get_extra_info('peername')
            print(f"Received from {addr}: {text}")

            # Sending acknowledgment
            ack_msg = bldr.encode("Server", "ACK", "Message received")
            writer.write(ack_msg.encode("utf-8"))
            await writer.drain()

        writer.close()


    async def run(self):
        server = await asyncio.start_server(self.handle_client, self.ipaddr, self.port)
        addr = server.sockets[0].getsockname()
        print(f'Server running on {addr}')

        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    svr = BasicServer("127.0.0.1", 2000)
    asyncio.run(svr.run())

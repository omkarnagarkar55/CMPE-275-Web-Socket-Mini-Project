import asyncio
import sys
import time
import numpy as np
from basic.payload import builder  # Adjust this import as necessary

class BasicClient:
    def __init__(self, name, ipaddr="127.0.0.1", port=2000):
        self.name = name
        self.ipaddr = ipaddr
        self.port = port
        self.group = "public"

    async def sendMsg(self, message):
        start_time = time.time()
        reader, writer = await asyncio.open_connection(self.ipaddr, self.port)
        bldr = builder.BasicBuilder()
        encoded_message = bldr.encode(self.name, self.group, message)
        writer.write(encoded_message.encode('utf-8'))
        await writer.drain()

        data = await reader.read(2048)
        round_trip_time = time.time() - start_time
        print(f'Received: {data.decode()} in {round_trip_time:.4f} seconds')

        writer.close()
        await writer.wait_closed()
        return round_trip_time

    async def run(self, N):
        round_trip_times = []
        for i in range(1, N + 1):
            message = f"{self.name} message {i}"
            round_trip_time = await self.sendMsg(message)
            round_trip_times.append(round_trip_time)
            await asyncio.sleep(0.0001)  # Sleep for 0.1 ms
        return round_trip_times

async def main(clients_count, message_count):
    tasks = []
    for i in range(clients_count):
        client = BasicClient(f"Client_{i+1}", "127.0.0.1", 2000)
        tasks.append(client.run(message_count))
    results = await asyncio.gather(*tasks)
    # Optionally, aggregate and print/save results here

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python client.py <ClientsCount> <MessageCount>")
        sys.exit(1)
    clients_count = int(sys.argv[1])
    message_count = int(sys.argv[2])
    asyncio.run(main(clients_count, message_count))

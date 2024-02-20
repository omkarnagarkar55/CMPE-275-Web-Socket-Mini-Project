import asyncio
import sys
import time
import numpy as np
import os
import csv
from basic.payload.builder import BasicBuilder

project_base_path = "/Users/spartan/Documents/SJSU/Sem2/CMPE-275/Mini1/CMPE-275-Final/CMPE-275-Web-Socket-Mini-Project/python-src"


class BasicClient:
    def __init__(self, name, ipaddr="127.0.0.1", port=2000, scale=""):
        self.name = name
        self.ipaddr = ipaddr
        self.port = port
        self.group = "public"
        self.round_trip_times = []
        self.scale = scale
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.ipaddr, self.port)

    async def sendMsg(self, message):
        if self.writer is None:
            raise Exception("Connection not established. Call connect() first.")
            
        start_time = time.time()
        bldr = BasicBuilder()
        encoded_message = bldr.encode(self.name, self.group, message)
        self.writer.write(encoded_message.encode('utf-8'))
        await self.writer.drain()

        data = await self.reader.read(2048)
        round_trip_time = time.time() - start_time
        self.round_trip_times.append(round_trip_time)
        print(f'Received: {data.decode()} in {round_trip_time:.4f} seconds')

    async def run(self, N):
        messages_per_client = N
        await self.connect()  # Establish connection before sending messages
        start_time = time.time()
        for i in range(N):
            message = f"{self.name} message {i+1}"
            await self.sendMsg(message)
        total_time = time.time() - start_time
        self.save_round_trip_times(N)
        self.calculate_and_print_metrics()
        self.save_metrics(total_time, messages_per_client)

        self.writer.close()  # Close the connection after sending all messages
        await self.writer.wait_closed()

    def save_round_trip_times(self, messages_per_client):
        validate_dir = os.path.join(project_base_path, "validate")
        os.makedirs(validate_dir, exist_ok=True)
        filename = f'metrics_{self.scale}_{self.name}_{messages_per_client}_msgs.txt'  # Corrected filename pattern
        print(f'round trip time filename: {filename} ,messages_per_client:{messages_per_client}')
        print(f'txt_file_name: {filename}')
        filepath = os.path.join(validate_dir, filename)
        with open(filepath, 'w') as file:
            for rt_time in self.round_trip_times:
                file.write(f'{rt_time}\n')

    def calculate_and_print_metrics(self):
        avg_time = np.mean(self.round_trip_times)
        median_time = np.median(self.round_trip_times)
        percentile_75 = np.percentile(self.round_trip_times, 75)
        percentile_90 = np.percentile(self.round_trip_times, 90)
        print(f"Average Time: {avg_time:.4f} seconds")
        print(f"Median Time: {median_time:.4f} seconds")
        print(f"75th Percentile: {percentile_75:.4f} seconds")
        print(f"90th Percentile: {percentile_90:.4f} seconds")

    def save_metrics(self, total_time, message_count):
        metrics = {
            'total_time': total_time,
            'average_time': np.mean(self.round_trip_times),
            'median_time': np.median(self.round_trip_times),
            '70th_percentile': np.percentile(self.round_trip_times, 70),
            '90th_percentile': np.percentile(self.round_trip_times, 90),
        }
        metrics_dir = os.path.join(project_base_path, "metrics")
        os.makedirs(metrics_dir, exist_ok=True)
        filename = f'metrics_{self.scale}_{self.name}_{message_count}_msgs.csv'
        print(f'csv_file_name: {filename}')
        filepath = os.path.join(metrics_dir, filename)
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=metrics.keys())
            writer.writeheader()
            writer.writerow(metrics)   

async def main(clients_count, message_count, scale):
        messages_per_client = message_count // clients_count
        clients = [BasicClient(f"Client_{i+1}", scale=scale) for i in range(clients_count)]
        tasks = [client.run(messages_per_client) for client in clients]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python client.py <ClientsCount> <MessageCount> <Scale>")
        sys.exit(1)
    clients_count = int(sys.argv[1])
    message_count = int(sys.argv[2])
    scale = sys.argv[3]  # Scale is now passed as a command-line argument
    asyncio.run(main(clients_count, message_count, scale))

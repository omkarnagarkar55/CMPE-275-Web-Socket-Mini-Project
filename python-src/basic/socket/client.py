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
        self.round_trip_times = []  # To store round-trip times for each message
        self.scale = scale  # New attribute to keep track of the test scale

    async def sendMsg(self, message):
        start_time = time.time()
        reader, writer = await asyncio.open_connection(self.ipaddr, self.port)
        bldr = BasicBuilder()
        encoded_message = bldr.encode(self.name, self.group, message)
        writer.write(encoded_message.encode('utf-8'))
        await writer.drain()

        data = await reader.read(2048)
        round_trip_time = time.time() - start_time
        self.round_trip_times.append(round_trip_time)
        print(f'Received: {data.decode()} in {round_trip_time:.4f} seconds')

        writer.close()
        await writer.wait_closed()

    async def run(self, N):
        start_time = time.time()
        for i in range(N):
            message = f"{self.name} message {i+1}"
            await self.sendMsg(message)
        total_time = time.time() - start_time
        self.save_round_trip_times()
        self.calculate_and_print_metrics()
        self.save_metrics(total_time, N)  # Pass N (message_count) to save_metrics

    def save_round_trip_times(self):
        validate_dir = os.path.join(project_base_path, "validate")
        os.makedirs(validate_dir, exist_ok=True)
        filename = f'metrics_{self.scale}_{self.name}_round_trip_times.txt'  # Corrected filename pattern
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
        filepath = os.path.join(metrics_dir, filename)
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=metrics.keys())
            writer.writeheader()
            writer.writerow(metrics)   

async def main(clients_count, message_count, scale):
        clients = [BasicClient(f"Client_{i+1}", scale=scale) for i in range(clients_count)]
        tasks = [client.run(message_count) for client in clients]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python client.py <ClientsCount> <MessageCount> <Scale>")
        sys.exit(1)
    clients_count = int(sys.argv[1])
    message_count = int(sys.argv[2])
    scale = sys.argv[3]  # Scale is now passed as a command-line argument
    asyncio.run(main(clients_count, message_count, scale))

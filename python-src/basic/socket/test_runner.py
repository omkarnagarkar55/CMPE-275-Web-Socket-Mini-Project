import subprocess
import os
import asyncio
import numpy as np
import csv
import time

def start_server():
    # Terminate any existing server process
    subprocess.run(['pkill', '-f', 'server.py'])

    # Starting the server using the Python binary from the virtual environment
    cmd = ['/Users/spartan/Downloads/socket-3code/python-src/venv/bin/python', '/Users/spartan/Downloads/socket-3code/python-src/basic/socket/server.py']
    return subprocess.Popen(cmd)

def stop_server(server_process):
    server_process.terminate()
    server_process.wait()

async def run_clients(client_count, message_count):
    project_path = "/Users/spartan/Downloads/socket-3code/python-src"
    # Setting PYTHONPATH and running the client script
    cmd = (
        f"cd {project_path} && "  # Navigate to the script directory
        ". venv/bin/activate && "  # Activate the virtual environment
        f"export PYTHONPATH=\"{project_path}:$PYTHONPATH\" && "  # Set PYTHONPATH
        f"python basic/socket/client.py {client_count} {message_count}"
    )
    subprocess.run(cmd, shell=True)

def input_scale_values():
    small = int(input("Enter the number of messages for 'small' scale: "))
    medium = int(input("Enter the number of messages for 'medium' scale: "))
    large = int(input("Enter the number of messages for 'large' scale: "))
    return small, medium, large

def input_client_counts():
    counts = []
    for i in range(1, 4):  # Assuming 3 inputs for the number of clients
        count = int(input(f"Enter the number of clients for test {i}: "))
        counts.append(count)
    return counts

async def main():
    small, medium, large = input_scale_values()
    scales = {'small': small, 'medium': medium, 'large': large}
    
    client_counts = input_client_counts()
    
    server_process = start_server()
    print("Server started. Proceeding with client tests.")

    # Prepare data structure to store results
    results = []

    # Running tests
    for clients_count in client_counts:
        for scale_name, num_messages in scales.items():
            print(f"Launching {clients_count} clients for '{scale_name}' scale with {num_messages} messages each.")
            await run_clients(clients_count, num_messages)
            
            # Measure two-way connection time
            total_times = []
            for _ in range(clients_count):
                total_time = await measure_two_way_connection_time()
                total_times.append(total_time)
            
            # Calculate metrics
            avg_time = np.mean(total_times)
            median_time = np.median(total_times)
            percentile_70 = np.percentile(total_times, 70)
            percentile_90 = np.percentile(total_times, 90)
            
            # Add the metrics to the results list
            results.append({
                'Number of Clients': clients_count,
                'Scale': scale_name,
                'Total Time': sum(total_times),
                'Avg Time': avg_time,
                'Median Time': median_time,
                '70th Percentile': percentile_70,
                '90th Percentile': percentile_90
            })

    # Write results to a CSV file
    with open('test_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['Number of Clients', 'Scale', 'Total Time', 'Avg Time', 'Median Time', '70th Percentile', '90th Percentile']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Tests complete. Results saved to 'test_results.csv'.")
    input("Press Enter to stop the server...")
    stop_server(server_process)

async def measure_two_way_connection_time():
    # Measure two-way connection time
    start_time = time.time()
    project_path = "/Users/spartan/Downloads/socket-3code/python-src"
    cmd = (
        f"cd {project_path} && "  # Navigate to the script directory
        ". venv/bin/activate && "  # Activate the virtual environment
        f"export PYTHONPATH=\"{project_path}:$PYTHONPATH\" && "  # Set PYTHONPATH
        f"python basic/socket/client.py 1 1"
    )
    subprocess.run(cmd, shell=True)
    total_time = time.time() - start_time
    return total_time

if __name__ == '__main__':
    asyncio.run(main())

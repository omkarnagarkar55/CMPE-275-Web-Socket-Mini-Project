import subprocess
import asyncio
import csv
import os
import time

# Define the base path of the project and the path to the Python executable in the virtual environment
project_base_path = "/Users/spartan/Documents/SJSU/Sem2/CMPE-275/Mini1/CMPE-275-Final/CMPE-275-Web-Socket-Mini-Project/python-src"
python_exec_path = os.path.join(project_base_path, "myenv/bin/python")

# Paths to the server and client script within the project
server_script_path = os.path.join(project_base_path, "basic/socket/server.py")
client_script_path = os.path.join(project_base_path, "basic/socket/client.py")

def start_server():
    try:
        subprocess.run(['pkill', '-f', 'server.py'], check=True)
    except subprocess.CalledProcessError:
        print("No server process found. Starting a new server.")
    cmd = [python_exec_path, server_script_path]
    return subprocess.Popen(cmd)

def stop_server(server_process):
    server_process.terminate()
    server_process.wait()

async def run_clients_and_collect_metrics(client_count, message_count, scale):
    cmd = f"{python_exec_path} {client_script_path} {client_count} {message_count} {scale}"
    start_time = time.time()
    subprocess.run(cmd, shell=True, check=True)
    total_time = time.time() - start_time

    # Make sure this path matches exactly where client.py saves the file
    metrics_dir = os.path.join(project_base_path, "metrics")
    metrics_filename = f"metrics_{scale}_Client_{client_count}_{message_count}_msgs.csv"
    metrics_filepath = os.path.join(metrics_dir, metrics_filename)

    print(metrics_filepath)
    # Open the CSV file and read the metrics
    with open(metrics_filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Assuming each file contains only one row of metrics
            return {
                'scale': scale,
                'client_count': client_count,
                'message_count': message_count,
                'total_time': float(row['total_time']),
                'avg_time': float(row['average_time']),
                'median_time': float(row['median_time']),
                '70th_percentile': float(row['70th_percentile']),
                '90th_percentile': float(row['90th_percentile']),
            }

def get_user_input():
    test_params = {}
    for scale in ['small', 'medium', 'large']:
        test_params[scale] = {
            'message_count': int(input(f"Enter the number of messages for '{scale}' scale: ")),
            'clients': [int(input(f"Enter the number of clients for test {i+1} on '{scale}' scale: ")) for i in range(3)]
        }
    return test_params

async def main():
    server_process = start_server()
    test_params = get_user_input()
    results = []

    for scale, params in test_params.items():
        for client_count in params['clients']:
            metrics = await run_clients_and_collect_metrics(client_count, params['message_count'], scale)
            results.append(metrics)
            print(f"Test completed for {scale} scale with {client_count} client(s): {metrics}")

    write_results_to_csv(results)
    stop_server(server_process)

def write_results_to_csv(results, filename='test_results.csv'):
    fields = ['scale', 'client_count', 'message_count', 'total_time', 'avg_time', 'median_time', '70th_percentile', '90th_percentile']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for data in results:
            # Ensure only the correct fields are written to the CSV
            row = {field: data[field] for field in fields}
            writer.writerow(row)

if __name__ == '__main__':
    asyncio.run(main())
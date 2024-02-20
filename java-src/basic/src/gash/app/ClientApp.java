package gash.app;

import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import gash.socket.BasicClient;

public class ClientApp implements Runnable {
	// Lock object for synchronization
	private static final Object lock = new Object();
	// Thread-safe list to store message round-trip times
	private static List<Long> messageTimes = Collections.synchronizedList(new ArrayList<>());
	// Track the earliest and latest message times across all clients
	private static long combinedStartTime = Long.MAX_VALUE;
	private static long combinedEndTime = 0;

	private final String clientName;
	private final int messageCount;

	public ClientApp(String clientName, int messageCount) {
		this.clientName = clientName;
		this.messageCount = messageCount;
	}

	@Override
	public void run() {
		try {
			// Initialize the client and connect to the server
			BasicClient myClient = new BasicClient(clientName, "127.0.0.1", 2000);
			myClient.connect();
			myClient.join("pets/dogs");

			// Warm-up phase to stabilize performance
			for (int i = 0; i < 5; i++) {
				myClient.sendMessage("Warm-up message " + (i + 1));
				myClient.receiveMessage();
			}

			// Main message sending and receiving loop
			for (int i = 0; i < messageCount; i++) {
				long startTime = System.nanoTime();

				myClient.sendMessage("Message " + (i + 1));
				myClient.receiveMessage();

				long endTime = System.nanoTime();
				long duration = endTime - startTime;

				// Synchronize access to shared resources
				synchronized (lock) {
					messageTimes.add(duration);
					combinedStartTime = Math.min(combinedStartTime, startTime);
					combinedEndTime = Math.max(combinedEndTime, endTime);
				}

				// Short sleep to mimic realistic messaging intervals
				if (i < messageCount - 1) {
					Thread.sleep(0, 100000); // Sleep for 0.1 ms
				}
			}

			// Disconnect the client
			myClient.stop();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) throws Exception {
		// Prepare for collecting test results
		List<String> csvLines = new ArrayList<>();
		csvLines.add(
				"Number of Clients,Number of Messages,Total Time,Avg Time,Median Time,70th Percentile,90th Percentile");

		// Define different test configurations
		var messageSizes = new int[] { 6, 12, 18 };
		var clientTests = new int[] { 1, 2, 3 };

		// Execute tests for each configuration
		for (int size : messageSizes) {
			for (int test : clientTests) {
				String csvLine = runTest(size, test);
				csvLines.add(csvLine);
				// Reset shared resources for the next test
				messageTimes.clear();
				combinedStartTime = Long.MAX_VALUE;
				combinedEndTime = 0;
			}
		}

		// Write test results to a CSV file
		writeResultsToCsv("C:\\Users\\PC\\Documents\\testResults.csv", csvLines);
	}

	private static String runTest(int totalMessages, int numberOfClients) throws InterruptedException {
		// Calculate messages per client and prepare threads
		int messagesPerClient = totalMessages / numberOfClients;
		Thread[] threads = new Thread[numberOfClients];

		// Start client threads
		for (int i = 0; i < numberOfClients; i++) {
			threads[i] = new Thread(new ClientApp("Client" + (i + 1), messagesPerClient));
			threads[i].start();
		}

		// Wait for all threads to finish
		for (Thread t : threads) {
			t.join();
		}

		// Synchronize to safely calculate and return performance metrics
		synchronized (lock) {
			Collections.sort(messageTimes);
			double median = calculatePercentile(50.0);
			double percentile70 = calculatePercentile(70.0);
			double percentile90 = calculatePercentile(90.0);
			double averageTime = messageTimes.stream().mapToLong(Long::longValue).average().orElse(Double.NaN);

			long combinedTotalTime = combinedEndTime - combinedStartTime;
			return String.format("%d,%d,%.4f,%.4f,%.4f,%.4f,%.4f",
					numberOfClients, totalMessages, combinedTotalTime / 1_000_000.0, averageTime / 1_000_000.0,
					median / 1_000_000.0, percentile70 / 1_000_000.0, percentile90 / 1_000_000.0);
		}
	}

	private static void writeResultsToCsv(String filePath, List<String> lines) throws IOException {
		// Write lines to the specified CSV file
		try (PrintWriter pw = new PrintWriter(new FileWriter(filePath))) {
			for (String line : lines) {
				pw.println(line);
			}
		}
	}

	private static double calculatePercentile(double percentile) {
		// Calculate the specified percentile from the sorted message times
		int index = (int) Math.ceil(percentile / 100.0 * messageTimes.size()) - 1;
		return messageTimes.get(index);
	}
}

package gash.app;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import gash.socket.BasicClient;

public class ClientApp {
	public static void main(String[] args) throws Exception {
		var myClient = new BasicClient("app", "127.0.0.1", 2000);
		myClient.connect();
		myClient.join("pets/dogs");

		// Optimal Solution - Warm-up phase
		int warmUpCount = 5; // Number of warm-up messages
		for (int i = 0; i < warmUpCount; i++) {
			myClient.sendMessage("Warm-up message " + (i + 1));
			myClient.receiveMessage(); // Receive acknowledgment but don't measure time
		}

		System.out.print("Enter the number of messages to send: ");
		var br = new BufferedReader(new InputStreamReader(System.in));
		int n = Integer.parseInt(br.readLine());

		long totalStartTime = 0; // Initialize totalStartTime
		long sumOfIndividualTimes = 0;

		for (int i = 0; i < n; i++) {
			if (i == 0) {
				// Set totalStartTime just before sending the first message
				totalStartTime = System.nanoTime();
			}

			long startTime = System.nanoTime();

			myClient.sendMessage("Message " + (i + 1));
			String response = myClient.receiveMessage();

			long endTime = System.nanoTime();
			long duration = endTime - startTime;
			sumOfIndividualTimes += duration;

			System.out.println("Received from server: " + response);
			System.out.printf("Time for message %d: %.4f ms\n", i + 1, duration / 1_000_000.0);

			if (i < n - 1) {
				Thread.sleep(0, 100000); // Sleep for 0.1 ms (100 microseconds)
			}
		}

		// Set totalEndTime immediately after receiving the last message
		long totalEndTime = System.nanoTime();

		long totalTime = totalEndTime - totalStartTime;
		double averageTime = (double) sumOfIndividualTimes / n;

		System.out.printf("Total time for %d messages: %.4f ms\n", n, totalTime / 1_000_000.0);
		System.out.printf("Average time per message: %.4f ms\n", averageTime / 1_000_000.0);

		myClient.stop();
	}
}

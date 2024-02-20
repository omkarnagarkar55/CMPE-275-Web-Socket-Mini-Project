// Utilized chatGPT to implement Thread related logic

package gash.app;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import gash.socket.BasicClient;

public class ClientApp implements Runnable {
	private static final Object lock = new Object();
	private static List<Long> messageTimes = Collections.synchronizedList(new ArrayList<>());
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
			BasicClient myClient = new BasicClient(clientName, "127.0.0.1", 2000);
			myClient.connect();
			myClient.join("pets/dogs");
			// Round Trip Message Logic
			for (int i = 0; i < messageCount; i++) {
				long startTime = System.nanoTime();

				myClient.sendMessage("Message " + (i + 1));
				myClient.receiveMessage();

				long endTime = System.nanoTime();
				long duration = endTime - startTime;

				// Synchronization Block
				synchronized (lock) {
					messageTimes.add(duration);
					combinedStartTime = Math.min(combinedStartTime, startTime);
					combinedEndTime = Math.max(combinedEndTime, endTime);
				}

				if (i < messageCount - 1) {
					Thread.sleep(0, 100000); // Sleep for 0.1 ms
				}
			}

			myClient.stop();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) throws Exception {
		System.out.println(
				"Number of Clients,Number of Messages,Total Time,Avg Time,Median Time,70th Percentile,90th Percentile");

		int[] messageSizes = { 6, 12, 18 };
		int[] clientTests = { 1, 2, 3 };

		for (int size : messageSizes) {
			for (int test : clientTests) {
				String result = runTest(size, test);
				System.out.println(result);
				messageTimes.clear();
				combinedStartTime = Long.MAX_VALUE;
				combinedEndTime = 0;
			}
		}
	}

	private static String runTest(int totalMessages, int numberOfClients) throws InterruptedException {
		int messagesPerClient = totalMessages / numberOfClients;
		// Thread Implementation
		Thread[] threads = new Thread[numberOfClients];

		for (int i = 0; i < numberOfClients; i++) {
			threads[i] = new Thread(new ClientApp("Client" + (i + 1), messagesPerClient));
			threads[i].start();
		}

		for (Thread t : threads) {
			t.join();
		}

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

	// Percentile Calculation
	private static double calculatePercentile(double percentile) {
		int index = (int) Math.ceil(percentile / 100.0 * messageTimes.size()) - 1;
		return messageTimes.get(index);
	}
}

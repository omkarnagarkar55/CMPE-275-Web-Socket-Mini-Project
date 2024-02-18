package gash.socket;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.InterruptedIOException;
import java.net.Socket;

import gash.payload.BasicBuilder;
import gash.payload.Message;

class SessionHandler extends Thread {
	private Socket connection;
	private boolean forever = true;

	public SessionHandler(Socket connection) {
		this.connection = connection;
		this.setDaemon(true);
	}

	public void run() {
		System.out.println("Session " + this.getId() + " started");

		try {
			var in = new BufferedInputStream(connection.getInputStream());
			var out = new BufferedOutputStream(connection.getOutputStream());

			byte[] raw = new byte[2048];
			BasicBuilder builder = new BasicBuilder();
			while (forever) {
				int len = in.read(raw);
				if (len <= 0)
					continue;

				String msg = new String(raw, 0, len);
				System.out.println(msg);

				// Ensure the acknowledgment message ends with a newline character
				String ackMessage = "Ack: " + msg + "\n";
				out.write(ackMessage.getBytes());
				out.flush();
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			System.out.println("Session " + this.getId() + " ending");
			stopSession();
		}
	}

	public void stopSession() {
		forever = false;
		try {
			if (connection != null) {
				connection.close();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
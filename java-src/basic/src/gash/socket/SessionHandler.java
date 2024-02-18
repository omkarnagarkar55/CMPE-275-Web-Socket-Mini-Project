package gash.socket;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.Socket;

/**
 * Handles sessions with clients without handling socket timeouts.
 */
class SessionHandler extends Thread {
    private Socket connection;
    private boolean forever = true;

    public SessionHandler(Socket connection) {
        this.connection = connection;
        // Ensure the server can exit even if this thread is running
        this.setDaemon(true);
    }

    public void stopSession() {
        forever = false;
        if (connection != null) {
            try {
                connection.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        connection = null;
    }

    @Override
    public void run() {
        System.out.println("Session " + this.getId() + " started");
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));

            String line;
            while (forever) {
                // Block here until a line is read or the connection is closed
                line = reader.readLine();
                if (line != null) {
                    System.out.println("Received from client: " + line);
                } else {
                    // End of stream reached, stop the session
                    break;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            System.out.println("Session " + this.getId() + " ending");
            stopSession();
        }
    }
}

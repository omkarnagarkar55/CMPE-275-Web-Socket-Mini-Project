package gash.socket;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

public class BasicClient {
    private String name;
    private String ipaddr;
    private int port;
    private String group = "public";

    private Socket clt;
    private PrintWriter out;

    public BasicClient(String name, String ipaddr, int port) {
        this.name = name;
        this.ipaddr = ipaddr;
        this.port = port;
    }

    public void stop() {
        if (this.clt != null) {
            try {
                this.clt.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        this.clt = null;
    }

    public void join(String group) {
        this.group = group;
    }

    public void connect() {
        if (this.clt != null) {
            return;
        }

        try {
            this.clt = new Socket(this.ipaddr, this.port);
            this.out = new PrintWriter(clt.getOutputStream(), true);
            System.out.println("Connected to " + clt.getInetAddress().getHostAddress());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void sendMessage(String message) {
        if (this.clt == null) {
            System.out.println("no connection, text not sent");
            return;
        }

        try {
            String fullMessage = name + ":" + group + ":" + message;
            this.out.println(fullMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

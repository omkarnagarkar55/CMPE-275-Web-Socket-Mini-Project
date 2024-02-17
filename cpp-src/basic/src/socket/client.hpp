#ifndef BASICCLIENT_HPP
#define BASICCLIENT_HPP

#include <string>

namespace basic {

/**
 * @brief server class setup
 * 
 * ref: https://www.geeksforgeeks.org/socket-programming-cc/
 */
class BasicClient {
   private:
      std::string name;
      std::string group;  
      std::string ipaddr;
      unsigned int portN;
      bool good;
      int clt;

   public: 
      BasicClient() : name("anonymous"), group("public"), ipaddr("127.0.0.1"), 
                      portN(2000), good(false), clt(-1) {}
      BasicClient(std::string name, std::string ipaddr, unsigned int port);

      virtual ~BasicClient() {}

      int port() const {return (int)this->portN;}
      std::string ipaddress() const {return this->ipaddr;}

      void stop();
      void sendMessage(std::string m) noexcept(false);
      void join(std::string group);

      void connect() noexcept(false);

      // New method for handling dynamic message sending
      void run() {
        // Attempt to connect to the server
        this->connect();

        // Check if connection was successful
        if (!this->good) {
            std::cerr << "Connection failed, unable to send messages." << std::endl;
            return;
        }

        std::string message;
        
        // Loop to get messages from user
        while (true) {
            std::cout << "Enter messages to send (type 'exit' to quit):" << std::endl;
            std::getline(std::cin, message); // Read a line from standard input

            // Check for exit condition
            if (message == "exit") {
                break;
            }

            // Send the message
            try {
                this->sendMessage(message);
            } catch (const std::exception& e) {
                std::cerr << "Error sending message: " << e.what() << std::endl;
                break; // Exit on send error
            }
        }

        // Stop the client and close the connection when done
        this->stop();
    }
};

} // basic

#endif

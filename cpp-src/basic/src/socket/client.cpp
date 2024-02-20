
#include <thread>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <sstream>
#include <iostream>

#include "socket/client.hpp"
#include "payload/basicbuilder.hpp"
#include <chrono>

basic::BasicClient::BasicClient(std::string name, std::string ipaddr, unsigned int port)
{
   this->name = name;
   this->group = "public";
   this->ipaddr = ipaddr;
   this->portN = port;
   this->good = false;
   this->clt = -1;

   if (this->portN <= 1024)
      throw std::out_of_range("port must be greater than 1024");
}

void basic::BasicClient::stop()
{
   std::cerr << "--> closing client connection" << std::endl;
   this->good = false;

   if (this->clt > -1)
   {
      ::close(this->clt);
      this->clt = -1;
   }
}

void basic::BasicClient::join(std::string group)
{
   this->group = group;
}

void basic::BasicClient::sendMessage(std::string m)
{
   if (!this->good)
      return;

   // basic::Message msg(this->name, this->group, m);
   // basic::BasicBuilder bldr;
   auto payload = this->name + "," + this->group + "," + m;
   auto plen = payload.length();

   // Start timing
   auto start = std::chrono::high_resolution_clock::now();

   ssize_t n = ::write(this->clt, payload.c_str(), plen);
   if (n < 0)
   {
      std::cerr << "--> send() error for " << m << ", errno = " << strerror(errno) << std::endl;
      return; // Exit if there was an error sending the message
   }
   std::cerr << "Message sent: " << payload << ", size: " << plen << std::endl;

   // Wait for acknowledgment
   char buffer[1024] = {0};
   n = ::recv(this->clt, buffer, sizeof(buffer), 0);
   if (n < 0)
   {
      std::cerr << "--> recv() error, errno = " << strerror(errno) << std::endl;
      return; // Exit if there was an error receiving the acknowledgment
   }

   // Stop timing
   auto end = std::chrono::high_resolution_clock::now();
   std::chrono::duration<double, std::milli> rtt = end - start;

   std::cerr << "Acknowledgment received: " << std::string(buffer, n) << std::endl;
   std::cerr << "RTT: " << rtt.count() << " ms" << std::endl;
}

void basic::BasicClient::connect()
{
   if (this->good)
      return;

   std::cerr << "connecting..." << std::endl;

   this->clt = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
   if (this->clt < 0)
   {
      std::stringstream err;
      err << "failed to create socket, err = " << errno << std::endl;
      throw std::runtime_error(err.str());
   }

   struct sockaddr_in serv_addr;
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_addr.s_addr = inet_addr(this->ipaddr.c_str());
   serv_addr.sin_port = htons(this->portN);

   auto stat = inet_pton(AF_INET, this->ipaddr.c_str(), &serv_addr.sin_addr);
   if (stat < 0)
   {
      throw std::runtime_error("invalid IP address");
   }

   stat = ::connect(this->clt, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
   if (stat < 0)
   {
      std::stringstream err;
      err << "failed to connect() to server, err = " << errno << std::endl;
      throw std::runtime_error(err.str());
   }

   this->good = true;
}


// Took help from https://www.geeksforgeeks.org/socket-programming-cc/
void basic::BasicClient::run()
{
   // Attempt to connect to the server
   this->connect();

   // Check if connection was successful
   if (!this->good)
   {
      std::cerr << "Connection failed, unable to send messages." << std::endl;
      return;
   }

   std::string message;

   // Loop to get messages from user
   while (true)
   {
      std::cout << "Enter messages to send (type 'exit' to quit):" << std::endl;
      std::getline(std::cin, message); // Read a line from standard input

      // Check for exit condition
      if (message == "exit")
      {
         break;
      }

      // Send the message
      try
      {
         this->sendMessage(message);
      }
      catch (const std::exception &e)
      {
         std::cerr << "Error sending message: " << e.what() << std::endl;
         break; // Exit on send error
      }
   }

   // Stop the client and close the connection when done
   this->stop();
}

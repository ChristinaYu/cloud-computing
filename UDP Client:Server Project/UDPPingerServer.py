import random
from socket import *
import atexit
from datetime import datetime

class clientInfo:

    def __init__(self, address):

        # The address of the connected client
        self.address = address

        # The last message received from the client
        self.last_message = None

        # The last request number received from the client
        self.request_num = 0

class pingServer:

    def __init__(self, port):

        # Attribute to hold a clientInfo object, initially empty
        self.client = None

        # Create a new socket object
        self.socket = socket(AF_INET, SOCK_DGRAM)

        # Bind it to the port specified in the supplied parameter
        self.socket.bind(('', port))

        # Register a function to handle clean up of pingServers objects at program exit
        # (Closes the socket's port and alerts the user)
        atexit.register(self.exitServer)

        # Begin listening for incoming messages on the UDP port
        self.pingListen()

    def pingListen(self):

        # Loop continuously until the server receives a message from a client
        while True:

            try:
                # Get the message sent by the client, and that client's address
                message, address = self.socket.recvfrom(1024)

                # Simulate packet loss by drawing a rand int between 0 and 10, and skipping this iteration of the
                # loop if it is below 4 (simulates 30% packet loss)
                rand = random.randint(0, 10)
                if rand < 4:
                    continue

                # If the packet is not determined to be 'lost', then if a message has been received.
                elif message:

                    # Record the time that the message is receieved
                    t = datetime.now()

                    # Split the incoming message into tokens separated by spaces
                    message = message.upper().split()

                    # If the first argument of the message is not "PING", then also check the client's heartbeat
                    if message[0] != "PING":
                        self.checkHeartbeat(message, t, address)

                    # Send a message back to the client to notify receipt
                    self.socket.sendto('Message Received By Server!', address)

            # If there is an exception due to the client timing out...
            except timeout:

                # Print a notification that the client connection has timed out
                print("Client Connection Timed Out!\n")

                # Unregister the current client being tracked by the pingServer
                self.removeClient()

            # If there is some other exception that occurs, handle the exception.
            except error as exc:

                # If the exception number is 10054, the client closed the connection before a message could be sent
                if exc == 10054:
                    print("Client Closed Connection!\n")

    def checkHeartbeat(self, message, t, address, timeout=10.0):

        # If the pingServer is not currently tracking the heartbeat of any client...
        if self.client is None:

            # Print a notification that a new client's heartbeat is being tracked, and that client's address
            print("\nTracking Heartbeat of New Client at {}:{}\n".format(address[0], address[1]))

            # Create a new clientInfo object to store data about the client
            self.client = clientInfo(address)

            # Set a timeout duration for the socket to detect when a client is assumed disconnected
            self.socket.settimeout(timeout)

        # If the pingServer is already tracking a client's heartbeat...
        else:

            # Retrieve the last message that was received from that client
            last_message = self.client.last_message

            # Retrieve the new message's sequence number
            this_number = int(message[0])

            # Extract the timestamp from the last message
            last_timestamp = ' '.join(last_message[1:])

            # Use the current time and the last timestamp to calculate the difference in times between when the last
            # received message was sent, and when this message was sent
            t_delta = (t-datetime.strptime(last_timestamp, "%Y %m %d %H %M %S %f")).total_seconds()

            # Print a notification that a message has been received from the client, the messages sequence number,
            # and the time since the server has last received a message from the client.
            print("Client message received!\n\tSequence Number: {}\n\tTime Since Last Packet Receieved: {}\n".format(this_number,t_delta))

            # If a the current message's sequence number is not 1 greater than the sequence number of the last message...
            if this_number - self.client.request_num != 1:

                # Then at least one packet has been lost, and a notification is printed
                print("Detected Lost Packets!")

                # Print a notification that each packet between the last sequence number and this sequence number
                # was lost in transmission
                for i in range(self.client.request_num + 1, this_number):
                    print("\t Packet #: {}".format(i))
                print("\n")

            # Update the last recorded request number from the client
            self.client.request_num = this_number

        # Update the last recorded message from the client
        self.client.last_message = message

    def removeClient(self):

        # Remove the currently registered client
        self.client = None

        # Reset the socket timeout so that the server continues listening for messages
        self.socket.settimeout(None)

    def exitServer(self):

        # Print a notification that the server is closing its UDP connection
        print("Closing server connection...")

        # Close the UDP connection to the socket
        self.socket.close()

if __name__ == '__main__':

    # If the file is executed as a python script, then create a new pingServer on an arbitrary port
    # (Can be any number, as long as it is not the same number as the pingClient, or a currently bound port)
    S = pingServer(13000)


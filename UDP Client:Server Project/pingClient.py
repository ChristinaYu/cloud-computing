from socket import *
from datetime import datetime
import time
import atexit

class pingClient:

    def __init__(self, port):

        # Create a new socket object
        self.socket = socket(AF_INET, SOCK_DGRAM)

        # Bind it to the port specified in the supplied parameter
        self.socket.bind(('', port))

        # Set the socket timeout length to a default value of one second
        self.socket.settimeout(1.0)

        # Register a function to handle clean up of pingClient objects at program exit
        # (Closes the socket's port and alerts the user)
        atexit.register(self.exitClient)


    def pingServer(self, message_num, serverIP, serverPort):

        # Record the time at the beginning of the ping request
        start = datetime.now()

        # Convert that time into a formatted timestamp string
        timestamp = datetime.strftime(start, "%Y %m %d %H %M %S %f")

        # Form the message that will be sent to the server
        # In this case, the format is 'PING MessageNumber Timestamp'
        message = "PING {} {}".format(message_num, timestamp)

        # Send the formatted message to the specified server IP and Port
        self.socket.sendto(message, (serverIP, serverPort))

        # Print a notification that the ping has been sent to the server
        print("\nPing {} sent!".format(message_num))

        # Loop continuously until the server responds, or the client times out the request
        while True:

            try:

                # Get the response returned from the server, and that server's address
                response, address = self.socket.recvfrom(1024)

                # If the server sends a response...
                if response:

                    # Get the total round trip time as the difference between the current time
                    # and the time at which the ping was sent
                    t = (datetime.now() - start).total_seconds()

                    # Print a notification that includes the server's response message,
                    # and the elapsed round trip time
                    print("\tServer Response: {}\n\tRound Trip Time: {}".format(response, t))

                    # Break the loop and stop waiting for a response
                    break

            # If the server doesn't respond before the timeout occurs...
            except timeout:

                # Handle the raised exception, print a notification that the request timed out, and end the loop
                print("\tRequest {} timed out..".format(message_num))
                break


    def pingTest(self, serverIP, serverPort, nPings):

        # Send the server the specified number ping messages
        for n in range(1, nPings + 1):
            self.pingServer(n, serverIP, serverPort)


    def heartBeat(self, message, serverIP, serverPort):

        # Create a formatted timestamp string with the current time
        timestamp = datetime.strftime(datetime.now(),"%Y %m %d %H %M %S %f")

        # Send the server a formatted message that does not begin with "PING", and will be tracked as a heartbeat
        self.socket.sendto("{} {}".format(message, timestamp), (serverIP, serverPort))

    def testHeartBeat(self, serverIP, serverPort, nHeartbeats):

        # When testing the heartbeat application, don't time out the client if a message isn't received
        self.socket.settimeout(None)

        # Send the specified number of heartbeat messages
        [self.heartBeat(i, serverIP, serverPort) for i in range(1, nHeartbeats)]

    def exitClient(self):

        # When the program terminates, print a notification that the connection is being close
        print("\nClosing client connection...")

        # Close the socket
        self.socket.close()


if __name__ == '__main__':

    # Set the address and port to use for the host server
    host_ip = "127.0.0.1"
    host_port = 13000

    # Create a new pingClient object on the specified port
    # (Can be any number, as long as it is not the same number used by the pingServer, or an already bound port)
    C = pingClient(13001)

    # Run the ping test routine for 10 iterations
    C.pingTest(host_ip, host_port, 10)

    # Run the heartbeat test for 10 iterations
    C.testHeartBeat(host_ip, host_port, 10)

    # Sleep for 10 seconds before terminating the program.
    time.sleep(10)

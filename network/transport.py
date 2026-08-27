import socket
import json

class UDPTransport:
    def __init__(self, local_port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #AF_INET opens the port IPv4 address, SOCK_DGRAM is for UDP style instead of TCP 
        self.sock.bind(("localhost", local_port)) # Claims a local port to listen to
        self.sock.setblocking(False) # Raises an error instead of freezing

    def send(self, data: dict, dest_port: int): # By accepting a dict, the user doesn't have to worry about bytes or json logic, they only put in a dict and a dict is received. All encoding done internally.
  
        # Sending side
        
        # Convert data (dict) to JSON string
        json_string = json.dumps(data)

        # Encode string to bytes
        byte_data = json_string.encode('utf-8')

        self.sock.sendto(byte_data, ("localhost", dest_port)) # Sendto takes the bytes and a destination tuple, right now its all done locally (localhost)

    def receive(self):
        try:
            byte_data, addr = self.sock.recvfrom(4096) # Try to get bytes from the socket if they are there, to decode
        except BlockingIOError: # Catch the error and treat it as 'no package right now' instead of crashing
            return None

        # Decode bytes back to a string
        received_string = byte_data.decode('utf-8')

        # Convert JSON string back to python dict
        received_dict = json.loads(received_string)
        return received_dict # Add back to python dict

if __name__ == "__main__":
    import time

    a = UDPTransport(local_port=9998)
    b = UDPTransport(local_port=9999)

    a.send({"msg": "hello"}, dest_port=9999)
    time.sleep(0.1)  # Tiny pause to let the packet arrive
    print(b.receive()) 
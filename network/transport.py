import socket

class UDPTransport:
    def __init__(self, local_port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #AF_INET opens the port IPv4 address, SOCK_DGRAM is for UDP style instead of TCP 
        self.sock.bind(("localhost", local_port)) # Claims a local port to listen to
        self.sock.setblocking(False) # Raises an error instead of freezing

    def send(self, data: bytes, dest_port: int):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError
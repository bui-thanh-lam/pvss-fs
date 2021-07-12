from socket import AF_INET, SOCK_STREAM, socket, gethostname, create_connection


class ServerCommunicator:
    """Establish a server socket and communicate with clients.
    
    Parameters:
        server_ip (str): Server's name or IP. Default: socket.gethostname()
        server_port (int): Server's port to listen. Recommended to use an unusual port. Default: 1334
        
    Methods:
        send(message): Send a message to a connected client
    """
    
    def __init__(self, server_ip=gethostname(), server_port=1334, **kwargs) -> None:
        self.address = (server_ip, server_port)
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(0)
        
    def send(self, message=None):
        """Send a message to a connected client

        Args:
            message (str): The desired message to send. Defaults: None.
        """
        while True:
            to_client, addr = self.socket.accept()
            print(f"Connected by {addr}")
            to_client.send(bytes(message, "utf-8"))
    

class ClientCommunicator:
    """Communicate with a server.
    
    Parameters:
        server_ip (str): Server's name or IP.
        server_port (int): Server's port to connect. Default: 1334
        
    Methods:
        receive(): Receive a message from a connected server
    """
    
    
    def __init__(self, server_ip, server_port=1334, **kwargs) -> None:
        self.BUFFER_SIZE = 1024
        self.server_address = (server_ip, server_port)
        self.socket = create_connection(self.server_address)
        
    def receive(self):
        msg = self.socket.recv(self.BUFFER_SIZE)
        msg = msg.decode("utf-8")
        return msg
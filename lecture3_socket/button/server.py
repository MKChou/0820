from datetime import datetime
from aiy.board import Board #type:ignore
import socket
## >> PARAMETERS
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1275
## << PARAMETERS
board = Board()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(2.0)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print("Server started...")
try:
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print("Incoming connection from {}:{}".format(client_address[0], client_address[1]))
            board.button.wait_for_press()
            client_socket.sendall("Received data at {}".format(datetime.now().strftime("%Y/%m/%d_%H:%M:%S")).encode("utf-8"))
            print("Message sent...")
            client_socket.close()
        except KeyboardInterrupt:
            raise
        except IOError:
            pass
except KeyboardInterrupt:
    pass
server_socket.close()
board.close()
print("Server stopped...")
from utils import send_confirmation, wait_confirmation, receive_data, transfer_data, string2bytes
import socket
import json
import os
## >> PARAMETERS
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1277
## << PARAMETERS
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(2.0)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
def receive_arguments(client_socket : socket.socket) -> dict:
    received_data = b""
    while True:
        temp = client_socket.recv(4096)
        if not temp:
            break
        received_data += temp
        if (received_data[-1:] == b"@"):
            received_data = received_data[:-1]
            break
    return json.loads(string2bytes(received_data.decode("utf-8")).decode("utf-8"))
print("Server running...\n")
try:
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print("Incoming connection from {}:{}".format(client_address[0], client_address[1]))
            arguments = receive_arguments(client_socket)
            print("Method: {}\n".format(arguments["method"]))
            send_confirmation(client_socket)
            if (arguments["method"] == "send"):
                dst_path = os.path.join(os.path.dirname(__file__), os.path.basename(arguments["path"]))
                receive_data(client_socket, dst_path)
                client_socket.close()
                continue
            if not os.path.exists(os.path.dirname(arguments["path"])):
                send_confirmation(client_socket, b"$$$")
                client_socket.close()
                continue 
            if not os.path.isfile(arguments["path"]):
                send_confirmation(client_socket, b"$$$")
                client_socket.close()
                continue 
            send_confirmation(client_socket)
            wait_confirmation(client_socket) #
            transfer_data(client_socket, arguments["path"])
            client_socket.close()
        except KeyboardInterrupt:
            raise
        except IOError:
            pass
except KeyboardInterrupt:
    pass
server_socket.close()
print("Server stopped...")
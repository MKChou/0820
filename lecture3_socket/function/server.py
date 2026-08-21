import socket
import json
## >> PARAMETERS 
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1127
END_OF_DATA = "@@@@@@"
## << PARAMETERS
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()
print("Server running...\n")
while True:
    client_socket, client_address = server_socket.accept()
    print("Connection from {}:{}\n".format(client_address[0], client_address[1]))
    data = b""
    while True:
        _data = client_socket.recv(1024)
        if not _data:
            break
        data += _data
        if (data[-len(END_OF_DATA):] == END_OF_DATA.encode()):
            data = data[:-len(END_OF_DATA)]
            break
    arguments = json.loads(data.decode("utf-8"))
    if ("stop" in arguments):
        client_socket.close()
        break
    num_1 = arguments["num_1"]
    num_2 = arguments["num_2"]
    num_3 = num_1 + num_2
    response = json.dumps({ "num_3" : num_3 }).encode()
    client_socket.sendall(response)
    client_socket.close()
server_socket.close()
print("Server stopped...")
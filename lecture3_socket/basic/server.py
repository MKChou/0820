import socket
import time
## >> PARAMETERS 
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1278
## << PARAMETERS
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()
server_socket.settimeout(2.0)
received_data = []
print("Server Running...\n")
try:
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            __start_time = time.time()
            print("Connection from {}".format(f"{client_address[0]}:{client_address[1]}"))
            data = b""
            while True:
                _data = client_socket.recv(1024)
                if not _data:
                    break
                data += _data
            __elapse_time = time.time() - __start_time
            print("Received Data: {} ({}s)\n".format(data, round(__elapse_time, 1)))
            received_data.append(data)
            client_socket.close()
        except KeyboardInterrupt:
            raise
        except IOError:
            pass
except KeyboardInterrupt:
    print("Server Stopped...\n")
server_socket.close()
print("All Data: {}".format(received_data))
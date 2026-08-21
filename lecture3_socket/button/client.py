import socket
## >> PARAMETERS
CONNECT_HOST = "127.0.0.1"
CONNECT_PORT = 1275
## << PARAMETERS
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((CONNECT_HOST, CONNECT_PORT))
received_data = b""
while True:
    data = client_socket.recv(1024)
    if not data:
        break
    received_data += data
client_socket.close()
print(received_data.decode("utf-8"))
import socket
import json
## >> PARAMETERS 
CONNECT_HOST = "127.0.0.1"
CONNECT_PORT = 1127
END_OF_DATA  = "@@@@@@"
## << PARAMETERS
while True:
    NUM_1 = input("num_1> ").strip()
    if (NUM_1.isnumeric()):
        NUM_1 = int(NUM_1)
        break
while True:
    NUM_2 = input("num_2> ").strip()
    if (NUM_2.isnumeric()):
        NUM_2 = int(NUM_2)
        break
# ===================================================================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((CONNECT_HOST, CONNECT_PORT))
arguments = json.dumps({ "num_1" : NUM_1, "num_2" : NUM_2 }).encode() + END_OF_DATA.encode()
client_socket.sendall(arguments)
data = b""
while True:
    _data = client_socket.recv(1024)
    if not (_data):
        break
    data += _data
response = json.loads(data)
client_socket.close()
# ===================================================================
print("Test: {} + {} = {}".format(NUM_1, NUM_2, response["num_3"]))
# ===================================================================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((CONNECT_HOST, CONNECT_PORT))
arguments = json.dumps({ "stop" : True }).encode() + END_OF_DATA.encode()
client_socket.sendall(arguments)
client_socket.close()
# ===================================================================
print("Remote server stopped...")
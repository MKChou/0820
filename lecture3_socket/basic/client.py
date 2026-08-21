import socket
import time
## >> PARAMETERS 
CONNECT_HOST = "127.0.0.1"
CONNECT_PORT = 1278
SEND_MESSAGE = b"hello world everyone"
## << PARAMETERS
# ===================================================================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((CONNECT_HOST, CONNECT_PORT))
client_socket.sendall(SEND_MESSAGE)
time.sleep(10) # observe the effect on server's end
client_socket.close()
# ===================================================================
print("First message was successfully sent")
# ===================================================================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((CONNECT_HOST, CONNECT_PORT))
client_socket.sendall(SEND_MESSAGE)
client_socket.close()
# ===================================================================
print("Second message was successfully sent")
import base64
import socket
import typing
def string2bytes(string : str) -> bytes:
    return base64.b64decode(string)
def bytes2string(data : bytes) -> str:
    return base64.b64encode(data).decode("utf-8")
def send_confirmation(client_socket : socket.socket, token : typing.Optional[ bytes ] = b"@@@") -> None:
    client_socket.sendall(token)
def wait_confirmation(client_socket : socket.socket, token : typing.Optional[ typing.List[ bytes ] ] = [ b"@@@", b"$$$" ]) -> int:
    received_data = b""
    while True:
        temp = client_socket.recv(32)
        if not temp:
            break
        received_data += temp
        if any(received_data.__contains__(__token) for __token in token):
            break
    return token.index(received_data[-3:])
def receive_data(client_socket : socket.socket, filepath : str) -> None:
    received_data = b""
    while True:
        temp = client_socket.recv(4096)
        if not temp:
            break
        received_data += temp
        if (received_data[-1] == b"@"):
            received_data = received_data[:-1]
            break
    with open(filepath, "wb") as wf:
        wf.write(string2bytes(received_data.decode("utf-8")))
def transfer_data(client_socket : socket.socket, filepath : str) -> None:
    with open(filepath, "rb") as rf:
        client_socket.sendall(bytes2string(rf.read()).encode("utf-8") + b"@")
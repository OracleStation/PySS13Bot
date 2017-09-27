import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
sock.connect(("localhost", 3665))
sock.settimeout(1)

topic = "adminwho&key=default_pwd"

packet = bytearray([0, 0x83, 0, 0, 0, 0, 0, 0]) + ('?' + topic).encode('ascii') + bytearray([0])
length = (len(packet) - 4).to_bytes(2, byteorder='little', signed=False)

packet[2] = length[1]
packet[3] = length[0]

sent = sock.send(packet)

if sent != len(packet):
    print("Error sending packet")

receive = sock.recv(512)

if len(receive) <= 5:
    print("No response")
else:
    response = receive[5:-1].decode('ascii')
    print(response)

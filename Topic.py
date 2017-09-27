import socket

class Topic:

    def __init__(self, host="localhost", port=3665, key="default_pwd"):
        self.host = host
        self.port = port
        self.key = key

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect((self.host, self.port))
        sock.settimeout(5)

        self.sock = sock

    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close()

    def send_topic(self, query):
        query = "?" + query + "&key=" + self.key

        packet = bytearray([0, 0x83, 0, 0, 0, 0, 0, 0]) + query.encode('ascii') + bytearray([0])
        length = (len(packet) - 4).to_bytes(2, byteorder='little', signed=False)

        packet[2] = length[1]
        packet[3] = length[0]

        sent = self.sock.send(packet)

        if sent != len(packet):
            raise Exception("Could not send data!")

        receive = self.sock.recv(512)

        if len(receive) > 5:
            response = receive[5:-1].decode('ascii')
            return response

        return ""

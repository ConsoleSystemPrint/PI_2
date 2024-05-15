import socket
import struct
import time
import json
import ntplib
from datetime import datetime


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


config = load_config()
time_offset = config.get("time_offset", 0)


def get_accurate_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('time.windows.com', version=3)
        return response.tx_time + time_offset
    except:
        print("Не удалось получить время с NTP-сервера, из-за чего вернулось системное время.")
        return time.time() + time_offset


def sntp_server():
    address = ('', 123)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                recv_time = datetime.now().timestamp()
                unpacked = struct.unpack('!12I', data[0:48])
                transmit_time = get_accurate_time() + (recv_time - unpacked[10])
                packed = struct.pack('!3B B 10I',
                                     28, 0, 0, unpacked[3],
                                     unpacked[4], unpacked[5], unpacked[6], unpacked[7],
                                     unpacked[8], unpacked[9], int(recv_time), int((recv_time % 1) * 2 ** 32),
                                     int(transmit_time), int((transmit_time % 1) * 2 ** 32))
                sock.sendto(packed, addr)
        except (OSError, struct.error) as e:
            print(f"Запрос на обработку ошибки: {e}")
        except KeyboardInterrupt:
            print("Сервер выключается...")
            break


if __name__ == "__main__":
    sntp_server()
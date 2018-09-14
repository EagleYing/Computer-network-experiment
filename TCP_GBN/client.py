# -*- coding:utf-8 -*-
import socket
import server
from GBN import *


def new_client_socket(client_port, protocol):
    # 设置网络连接为ipv4， 传输层协议为tcp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 任意ip均可以访问
    s.bind(('', client_port))

    p = protocol(s)
    p.handshake_scond(client_port)
    p.sender()
    s.close()


if __name__ == '__main__':
    server.new_server_socket(CLIENT_PORT, 'data/senddata.txt', Gbn)


# -*- coding:utf-8 -*-
import socket
import client
from GBN import *


def new_server_socket(client_port, path, protocol):
    # 设置网络连接为ipv4， 传输层协议为udp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 任意ip均可以访问
    # s.bind(('', server_port))

    p = protocol(s)
    p.handshake_first(client_port)
    p.handshake_third(client_port)
    p.receiver(path, client_port)
    s.close()




if __name__ == '__main__':

    client.new_client_socket(CLIENT_PORT, Gbn)


# -*- coding:utf-8 -*-
import sys
import select
import random
import Tkinter as tk

#初始化界面
top = tk.Tk()
top.title("GBN")

#界面使用说明
imfor = tk.Label(top,text='INSTRUCTION : Press \"server\" button to start server first and then press \"client\" button to start client')
#左模块
frame1 = tk.Frame(top,width=50,height=40)
#右模块
frame2 = tk.Frame(top,width=50,height=40)
#上模块
frame3 = tk.Frame(top,width=110,height=10)
#左右边输出栏
text_l = tk.Text(frame1,width=50,height=40)
text_r = tk.Text(frame2,width=50,height=40)

#多线程实现
import server as s
import client as c
import threading

def Run_server():
    c.new_client_socket(CLIENT_PORT, Gbn)

def Run_client():
    s.new_server_socket(CLIENT_PORT, 'data/client_push.txt', Gbn)

def thread1():
    t1 = threading.Thread(target=Run_server)
    t1.start()

def thread2():
    t2 = threading.Thread(target=Run_client)
    t2.start()

#校验和
def do_checksum(source_string):
    sum = 0
    max_count = (len(source_string) / 2) * 2
    count = 0
    while count < max_count:
        val = ord(source_string[count + 1]) + ord(source_string[count])
        sum = sum + val
        count = count + 2

    if max_count < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
    answer = sum % 256
    return answer

# 设置在localhost进行测试
HOST = '127.0.0.1'

# 设置服务器端与客户端的端口号
SERVER_PORT = 81
CLIENT_PORT = 8080

# 单次读取的最大字节数
BUFFER_SIZE = 2048

# 窗口与包序号长度
WINDOWS_LENGTH = 5
SEQ_LENGTH = 10

# 最大延迟时间
MAX_TIME = 3

#校验和接收数据
source = []
sum = []

#校验和结果
global check1
global check2

file_data = []

#调试时需要
global flag

#读取文件
def get_data(path):
    with open(path, 'r') as f:
        for line in f.readlines():
            file_data.append(line)
    f.close()
    print file_data

#数据
class Data(object):

    def __init__(self, msg, seq=0, state=0):
        self.msg = msg
        self.state = state
        self.seq = str(seq % SEQ_LENGTH)

    def __str__(self):
        return self.seq + ' ' + self.msg


class Gbn(object):

    def __init__(self, s):
        self.s = s

    #三次握手
    def handshake_first(self, port):
        #产生随机数
        seq1 = random.randint(0,100)
        # string = 'First handshake:SYN = 1'
        text_l.insert(tk.END, 'First handshake:SYN = 1' + 'seq = ' + str(seq1) + '\n' )
        self.s.sendto(str(seq1), (HOST, port))

    def handshake_scond(self, port):
        #产生随机数
        seq2 = random.randint(0,100)
        second, addr = self.s.recvfrom(BUFFER_SIZE)
        text_r.insert(tk.END, 'Second handshake:SYN = 1,ACK = 1, seq = ' + str(second) + ',ack = ' + str(seq2) + '\n')
        second = int(second) + 1
        secondstr = str(seq2)
        #报文用‘，’隔开
        secondstr = secondstr + ',' + str(second)
        self.s.sendto(secondstr, addr)


    def handshake_third(self, port):
        third, addr = self.s.recvfrom(BUFFER_SIZE)
        #分解接收到的报文
        ack3 = third.split(',')[0]
        seq3 = third.split(',')[1]
        ack3 = int(ack3) + 1
        text_l.insert(tk.END, 'Third handshake: ack = ' + str(ack3) + 'seq = ' + str(seq3) + '\n')
        text_l.insert(tk.END, 'ACK begin...\n')


    def receiver(self, path, port):
        time = 0
        # 计时和包序号初始化
        seq = 0
        data_windows = []
        global flag,check1,check2
        flag = 0
        with open(path, 'r') as f:

            while True:

                # 当超时后，将窗口内的数据更改为未发送状态
                if time > MAX_TIME:
                    text_r.insert(tk.END, 'timeout\n')
                    # print "timeout"
                    for data in data_windows:
                        data.state = 0

                # 窗口中数据少于最大容量时，尝试添加新数据
                while len(data_windows) < WINDOWS_LENGTH:
                    line = f.readline().strip()

                    if not line:
                        break

                    data = Data(line, seq=seq)
                    data_windows.append(data)
                    seq += 1

                # 窗口内无数据则退出总循环
                if not data_windows:
                    break

                # 遍历窗口内数据，如果存在未成功发送的则发送
                for data in data_windows:
                    if not data.state:
                        self.s.sendto(str(data), (HOST, port))
                        data.state = 1
                    # else:
                    #     print(data)

                # 无阻塞socket连接监控
                readable, writeable, errors = select.select([self.s, ], [], [], 1)

                if len(readable) > 0:

                    # 收到数据则重新计时
                    time = 0

                    message, address = self.s.recvfrom(BUFFER_SIZE)
                    # sys.stdout.write('ACK ' + message + '\n')
                    text_r.insert(tk.END, 'ACK' + message + '\n')

                    for i in range(len(data_windows)):
                        if message == data_windows[i].seq:
                            source.append(str(data_windows[i])[2])
                            data_windows = data_windows[i+1:]
                            break
                else:
                    # 未收到数据则计时器加一
                    time += 1
            flag = 1
            if len(source) == 13:
                print('check1')
                check2 = do_checksum(sum)
                check1 = do_checksum(source)
                if check1 == check2:
                    text_r.insert(tk.END, 'checksum successfully, accept' + '\n')
        self.s.close()

    def sender(self):
        global flag,check2
        time = 0
        # 记录上一个回执的ack的值

        last_ack = SEQ_LENGTH - 1
        seq = 0
        data_windows = []
        get_data('data/client_push.txt')
        while True:

            readable, writeable, errors = select.select([self.s, ], [], [], 1)

            if len(readable) > 0:

                message, address = self.s.recvfrom(BUFFER_SIZE)

                ack = int(message.split()[0])
                letter = str(message.split()[1])

                if time > MAX_TIME:
                    text_l.insert(tk.END, 'timeout\n')
                    # print "timeout"
                    time = 0

                # 连续接收数据则反馈当前ack
                if last_ack == (ack - 1) % SEQ_LENGTH:
                    time = 0

                    # v.设置随机数,0代表正常，1代表帧丢失，2代表帧出错，3代表应答帧丢失（即不发生应答帧）
                    v = random.randint(0,10)
                    #print(v)

                    if v == 1:
                        text_l.insert(tk.END, 'loss\n')
                        if time < MAX_TIME:
                            ran = random.randint(ack, SEQ_LENGTH)
                            if ack == 0:
                                for i in range(ack, ack + 5):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                            else:
                                for i in range(ack - 1, ack + 4):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                                # print (str(i) + " " + file_data[i]),
                        continue
                    if v == 2:
                        text_l.insert(tk.END, 'wrong\n')
                        if time < MAX_TIME:
                            ran = random.randint(ack, SEQ_LENGTH)
                            if ack == 0:
                                for i in range(ack, ack + 5):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                            else:
                                for i in range(ack - 1, ack + 4):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                        continue
                    if v == 3:
                        text_l.insert(tk.END, 'ack loss\n')
                        if time < MAX_TIME:
                            ran = random.randint(ack, SEQ_LENGTH)
                            if ack == 0:
                                for i in range(ack, ack + 5):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                            else:
                                for i in range(ack - 1, ack + 4):
                                    text_l.insert(tk.END, str(i) + " " + file_data[i])
                        continue

                    # self.s.sendto(str(ack), address)
                    last_ack = ack

                    # 判断数据是否重复
                    if ack not in data_windows:
                        data_windows.append(ack)
                        sum.append(letter)
                        text_l.insert(tk.END, message + '\n')

                    # 返回成功接收的包序号
                    self.s.sendto(str(ack), address)
                    data_windows[ack] = message.split()[1]


                    # 滑动窗口delete
                    seq = ack%WINDOWS_LENGTH
                    print(seq)
                    if seq == 4:
                        # print("slide windows here")
                        # text_l.insert(tk.END, str(seq) + ' ' + data_windows[str(seq)] + '\n')
                        # sys.stdout.write(str(seq) + ' ' + data_windows[str(seq)] + '\n')
                        # data_windows.pop(str(seq))
                        # seq = (seq + 1) % SEQ_LENGTH
                        # text_l.insert(tk.END, 'sliding windows' + '\n')
                        seq = 0
                    # while len(data_windows) > WINDOWS_LENGTH:
                    #     data_windows.pop(0)
                else:
                    #重传
                    self.s.sendto(str(last_ack), address)
                    time += 1
            if flag == 1:
                exit(0)
            if len(sum) == 13:
                print('check2')
                check2 = do_checksum(sum)
        self.s.close()




if __name__ == '__main__':
    s1 = tk.Scrollbar(frame1)
    s2 = tk.Scrollbar(frame2)
    b1 = tk.Button(frame3, text='server(sender)', command=thread1)
    b2 = tk.Button(frame3, text='client(reseiver)', command=thread2)

    text_l.pack(side=tk.LEFT,padx=10,pady=10)
    b1.pack(side=tk.LEFT,fill=tk.X,padx=10,pady=10)
    s1.pack(side=tk.RIGHT,fill=tk.Y)

    text_r.pack(side=tk.LEFT,padx=10,pady=10)
    b2.pack(side=tk.RIGHT,fill=tk.X,padx=10,pady=10)
    s2.pack(side=tk.RIGHT,fill=tk.Y)

    imfor.pack()
    frame3.pack(side=tk.TOP)
    frame1.pack(side=tk.LEFT)
    frame2.pack(side=tk.LEFT)
    s1.config(command=text_l.yview)
    text_l.config(yscrollcommand=s1.set)
    s2.config(command=text_r.yview)
    text_r.config(yscrollcommand=s2.set)
    top.mainloop()



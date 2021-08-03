#!/usr/bin/env python
import socket
import sys
import threading
import time
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(BASE_DIR + "/Server")

from Game.GameElements import Card


def CreateRandomCards():
    colors = ["R", "G", "B", "W", "Y"]
    counts = [3, 2, 2, 2, 1]
    cards = []

    for color in colors:
        for i in range(5):
            for j in range(counts[i]):
                cards.append(Card(color, i + 1))

    random.shuffle(cards)
    return cards


MAX_PLAYER_NUMBER = 4    # 실제로 만들어서 플레이 할 때는 이걸 4로 바꾸면 댐
SYMBOL_ACTION = '//'
SYMBOL_CHAT = '#C'
SYMBOL_PLAYER_NUMBER = '#P'
SYMBOL_WHOS_TURN = '#T'
SYMBOL_GAME_START = '#S'


playerNumber = 0
clients = []


class Client(threading.Thread):
    global clients

    def __init__(self, ip, port, connection):
        '''
        :param ip: 접속할 ip주소, 보통 서버의 주소를 의미함
        :param port: 서버에서 지정해준 포트번호와 일치해야함 일단은 기본적으로 6666을 이용하고있음
        :param connection: socket의 accept() 함수로 가져온 소켓
        '''
        global playerNumber
        threading.Thread.__init__(self)
        self.connection = connection
        self.ip = ip
        self.port = port

        # 플레이어 넘버를 통신을 통해 지정해줌으로써 관리를 편하게 하고 보기도 편하게함
        # 들어오는 순서대로 1, 2, 3, 4임ㅎ
        # 누구만대로냐고? 내맘ㅎ
        self.connection.sendall((SYMBOL_PLAYER_NUMBER+str(playerNumber)).encode())
        self.playerNumber = playerNumber
        playerNumber += 1
        self.turn = 0

    def receive(self):
        while True:
            print("Waiting msg from the client...")
            data = self.connection.recv(1024)
            self.sendToAllClients(data)

    def sendToAllClients(self, msg):    # 채팅 커맨드와 누구로부터 왔는지 메세지 순서대로 데이터 전송
        for client in clients:
            # send msg without self
            if client == self:
                # print("pass me") # DEBUG
                continue
            print(msg.decode(), self.playerNumber, 'sending message to ', client.port) # 누구한테 보내는지 확인용
            client.connection.send(msg)
            print(client)

    def run(self):
        receiver = threading.Thread(target=self.receive)
        receiver.start()


class Server:
    global clients

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None

    def fullPlayer(self):
        print('Game start : //game\nSelect player : //turn + playernumber')
        data = input('> ')

        if data == "//game":    # menu 1
            self.gameStart()
            while True:  # 추후에 게임변수 넣어서 끊고 하고 그럴거임
                pass

        else:
            print("please enter right commend")

    def gameStart(self):
        startData = SYMBOL_GAME_START
        startData += str(0)  # first player number

        cards = CreateRandomCards()
        for card in cards:
            startData += str(card) + ','
        startData = startData[:-1]

        self.sendToAllClients(startData)
        time.sleep(0.5)

    def sendToAllClientsBytes(self, byteMsg: bytes):
        """
        :param byteMsg: 모든 Clients에게 보낼 메세지
        """
        for client in clients :
            print('sending message to ', client.port, str(byteMsg))  # DEBUG
            client.connection.send(byteMsg)

    def sendToAllClients(self, strMsg: str):
        self.sendToAllClientsBytes(strMsg.encode())

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
        except socket.error as e:
            if self.server:
                self.server.close()
            sys.exit(1)

    def run(self):
        self.open_socket()
        self.server.listen(MAX_PLAYER_NUMBER)

        while len(clients)!=MAX_PLAYER_NUMBER:
            # 접속 대기단계
            connection, (ip, port) = self.server.accept()

            c = Client(ip, port, connection)
            c.start()

            clients.append(c)
            print(clients)

        print('All clients are connected!')

        while True:
            # 접속 완료 후 단계
            self.fullPlayer()

        self.server.close()


if __name__ == '__main__':
    s = Server('0.0.0.0', 7777)
    s.run()

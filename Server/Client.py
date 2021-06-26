import socket
import threading
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(BASE_DIR + "/Server")

from Game.GameElements import Action

# MESSAGE SYMBOL
SYMBOL_ACTION = '//'
SYMBOL_CHAT = '#C'
SYMBOL_PLAYER_NUMBER = '#P'
SYMBOL_WHOS_TURN = '#T'
SYMBOL_GAME_START = '#S'


class Client():
    def __init__(self, IP, port):
        self.IP = IP
        self.port = port
        self.size = 1024
        self.s = None
        self.messageQueue = list()

    def connectWithServer(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.IP, self.port))
            print('connected with Server')
            recevePN = self.s.recv(self.size)
            if recevePN.decode()[0:2] == SYMBOL_PLAYER_NUMBER:
                self.playerNumber = recevePN.decode()[2]
                print('Your player number is ', self.playerNumber)
            else:
                print('Errer in receiving PN')

        except socket.error:
            if self.s:
                self.s.close()
            print("Could not open socket: ")
            return False

        return True

    def sendingMsg(self, s):
        while True:
            data = input()
            if data[0:2] not in [SYMBOL_PLAYER_NUMBER, SYMBOL_WHOS_TURN, SYMBOL_ACTION]:  # 커맨드가 없으면 채팅 커맨드 붙임
                data = SYMBOL_CHAT + str(self.playerNumber) + data
            s.send(data.encode())
            return
        s.close()

    def gettingMsg(self, s):
        while True:
            data = s.recv(1024)
            self.messageQueue.append(data)
            # TODO: GUI의 별도 스레드에서 메시지 queue를 처리

        s.close()

    def sendToGame(self, data):
        '''
        서버로부터 받은 데이터를 게임으로 보낼 함수
        :param data: 내가 판별해야하는 메세지(커맨드 포함)
        :return: 어떤 명령어인지 커맨드일경우 커맨드 자체를 채팅이나 다른거일경우 해당 커맨드 키값만
        '''
        if data.decode()[0:2] == SYMBOL_ACTION:  # 서버로 부터 받은게 커맨드라면
            return data.decode()

        elif data.decode()[0:2] == SYMBOL_CHAT:  # 채팅이라면
            if data.decode()[2] != self.playerNumber:  # 채팅이 내꺼면 출력 x
                print('Player ', data.decode()[2], ' : ', data.decode()[3:])
            return SYMBOL_CHAT

        elif data.decode()[0:2] == SYMBOL_WHOS_TURN:  # 턴을 알려주는 커맨드라면
            if data.decode()[2] == self.playerNumber:
                print('It\'s your turn!')
            else:
                print('Player', data.decode()[2], 'is playing')
            return SYMBOL_WHOS_TURN

    def sendAction(self, action: Action):
        time.sleep(1)
        type_ = action.getActionType()
        actionString = str(type_) + "/"

        if type_ == 3:
            actionString += str(action.getTargetIndex()) + "/"
            actionString += str(action.getHint().info)
        else:
            actionString += str(action.getCardIndex())
        self.s.sendall(actionString.encode())

    def myPlayerNumberis(self):
        return self.playerNumber

    def run(self):
        get = threading.Thread(target=self.gettingMsg, args=(self.s,))
        get.start()


if __name__ == "__main__":
    c = Client('192.168.0.4', 7777)
    c.connectWithServer()
    c.run()

import socket
import threading
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(BASE_DIR + "/Server")

from Game.GameElements import Action
from Game.GameElements import Card
# MESSAGE SYMBOL
SYMBOL_ACTION = '//'
SYMBOL_CHAT = '#C'
SYMBOL_PLAYER_NUMBER = '#P'
SYMBOL_WHOS_TURN = '#T'
SYMBOL_GAME_START = '#S'


class Client():
    def __init__(self, startHandler, chatHandler, actionHandler, IP, port):
        self.IP = IP
        self.port = port
        self.size = 1024
        self.s = None
        self.messageQueue = list()
        self.startHandler = startHandler
        self.actionHandler = actionHandler
        self.chatHandler = chatHandler
        self.playerNumber = -1;

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

    def getEventHandler(self, symbol):
        if symbol == SYMBOL_ACTION:
            return self.actionHandler

        elif symbol == SYMBOL_GAME_START:
            return self.startHandler

        elif symbol == SYMBOL_CHAT:
            return self.chatHandler

        return None

    def gettingMsg(self, s):
        while True:
            data_ = s.recv(1024)
            data_ = data_.decode('utf-8')
            symbol = data_[0:2]
            data = data_[2:]
            handler = self.getEventHandler(symbol)
            if handler is not None:
                handler(data)
        s.close()
        
    def sendAction(self, action: Action):
        time.sleep(1)
        type_ = action.getActionType()
        actionString = SYMBOL_ACTION + str(type_) + "/"

        if type_ == 3:
            actionString += str(action.getTargetIndex()) + "/"
            actionString += str(action.getHint().info)
        else:
            actionString += str(action.getCardIndex())
        self.s.sendall(actionString.encode())

    def getMyPlayerNumber(self):
        return self.playerNumber

    def run(self):
        get = threading.Thread(target=self.gettingMsg, args=(self.s,))
        get.start()


if __name__ == "__main__":
    c = Client('3.14.133.163', 7777)
    c.connectWithServer()
    c.run()

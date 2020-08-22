import socket
import threading
import sys

ITISACTION = '//'
ITISCHAT = '#C'
ITISPLAYERNUMBER = '#P'
ITISWHOSTURN = '#T'


# 깃 사용벙 연습중

class Client():
    def __init__(self, IP, port):
        self.IP = IP
        self.port = port
        self.size = 1024
        self.s = None

    def connectWithServer(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.IP, self.port))
            print('connected with Server')
            recevePN = self.s.recv(self.size)
            if recevePN.decode()[0:2] == ITISPLAYERNUMBER:
                self.playerNumber = recevePN.decode()[2]
                print('Your player number is ', self.playerNumber)
            else:
                print('Errer in receiving PN')


        except socket.error:
            if self.s:
                self.s.close()
            print("Could not open socket: ")
            sys.exit(1)

    def sendingMsg(self, s):

        while True:
            data = input()
            if data[0:2] not in [ITISPLAYERNUMBER, ITISWHOSTURN, ITISACTION]:  #  커맨드가 없으면 채팅 커맨드 붙임
                data = ITISCHAT + str(self.playerNumber) + data
            s.send(data.encode())
        s.close()

    def gettingMsg(self, s):

        while True:
            data = s.recv(1024)
            self.sendToGame(data)
        s.close()

    def sendToGame(self, data):
        '''
        서버로부터 받은 데이터를 게임으로 보낼 함수
        :param data: 내가 판별해야하는 메세지(커맨드 포함)
        :return: 어떤 명령어인지 커맨드일경우 커맨드 자체를 채팅이나 다른거일경우 해당 커맨드 키값만
        '''
        if data.decode()[0:2] == ITISACTION:  # 서버로 부터 받은게 커맨드라면
            return data.decode()

        elif data.decode()[0:2] == ITISCHAT:  # 채팅이라면
            if data.decode()[2] != self.playerNumber:  # 채팅이 내꺼면 출력 x
                print('Player ', data.decode()[2], ' : ', data.decode()[3:])
            return ITISCHAT

        elif data.decode()[0:2] == ITISWHOSTURN:  # 턴을 알려주는 커맨드라면
            if data.decode()[2] == self.playerNumber:
                print('It\'s your turn!')
            else:
                print('Player', data.decode()[2], 'is playing')
            return ITISWHOSTURN



    def myPlayerNumberis(self):
        return self.playerNumber

    def run(self):

        get = threading.Thread(target=self.gettingMsg, args=(self.s,))
        get.start()

        send = threading.Thread(target=self.sendingMsg, args=(self.s,))
        send.start()


'''
c = Client('localhost', 7777)
c.connectWithServer()
c.run()
'''
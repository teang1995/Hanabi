#!/usr/bin/env python
import socket
import sys
import threading

GAMESTART = 1
GAMEEND = 0
GAME = 0
MAXPLAYERNUMBER = 2 # 실제로 만들어서 플레이 할 때는 이걸 4로 바꾸면 됨.

playerNumber = 0


class Client(threading.Thread):

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
        self.connection.sendall(('//PN'+str(playerNumber)).encode())
        playerNumber += 1

    def getMsg(self): #Client로 부터 입력을 받아오라고하는 메소드. 입력 받을때까지 서버는 스탑
        print("Waiting msg from the client...")
        data = self.connection.recv(1024)
        return data


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None
        self.clients = []

    def gamestart(self):
        '''

        :return:
        '''
        global GAME, GAMESTART, GAMEEND
        # 게임이 끝날을 때 서버 통신을 끝내고 다음 게임을 준비하기 위해 집어넣은 변수들
        GAME = GAMESTART
        print('Game start : //game\nSelect player : //turn + playernumber')
        data = input('> ')

        if data == "//game":#menu 1
            while GAME == GAMESTART:
                for number, client in enumerate(self.clients):
                    self.send_to_all_clients('//turn'+str(number))
                    self.requestMsgToClient(self.clients[number].ip, self.clients[number].port)
                    if GAME == GAMEEND:
                        break

        elif data[:6] == '//turn':
            self.send_to_all_clients(data)
            clientNumber = int(data[6]) - 1
            self.requestMsgToClient(self.clients[clientNumber].ip,self.clients[clientNumber].port)

    def send_to_all_clients(self, msg):
        # 제에에발 문자열 그대로 넣으세요 아님 바꾸던가
        '''
        :param msg: 모든 Clients에게 보낼 메세지
        '''
        for client in self.clients :
            print('sanding message to ',client.port,msg)
            client.connection.send(msg.encode())

    def send_to_client(self, ip, port, msg):
        '''
        :param ip: 메세지를 보내려는 Client의 IP
        :param port: 메세지를 보냐려는 Client의 port
        :param msg: Client에게 보내려는 메세지
        '''
        for client in self.clients :
            if client.ip == ip and client.port == port :
                client.connection.send(msg.encode())

    def requestMsgToClient(self, ip, port):#살짝 수정해서 채팅기능 구현가능할듯
        '''
        :param ip : 메세지를 받고싶은Client의 IP
        :param port : 메세지를 받고싶은Client의 port
        '''
        global GAME,GAMESTART, GAMEEND
        print("Running requestMsgToClient...")
        for client in self.clients :
            if client.ip == ip and client.port == port :
                print('Found selected client...', ip, port)

                msg = client.getMsg()
                #print(msg.decode())
                '''
                if msg.decode() == '//endgame':
                    GAME = GAMEEND
                    break
                elif msg.decode() == '//endturn':
                    break
                '''
                self.send_to_all_clients(msg.decode())
        #self.send_to_all_clients('players Turn is ended')

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
        except socket.error as e:
            if self.server:
                self.server.close()
            sys.exit(1)

    def run(self):
        global MAXPLAYERNUMBER
        self.open_socket()
        self.server.listen(MAXPLAYERNUMBER)
        #b = threading.Thread(target= self.broadCast())
        #b.start()

        while len(self.clients)!=MAXPLAYERNUMBER :

            connection, (ip, port) = self.server.accept()

            c = Client(ip, port, connection)
            c.start()

            self.clients.append(c)
            print(self.clients)

        print('All clients are connected!')

        while True:

            self.gamestart()

        self.server.close()


if __name__ == '__main__':
    s = Server('', 6666) # '' 이렇게 IP부분에 빈칸으로 두면 모든 IP의 접속을 허용해준다고하는데 사실 정확하게는 모르겠어요ㅎ
    s.run()
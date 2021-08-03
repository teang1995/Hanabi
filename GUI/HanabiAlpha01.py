import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
# __file__Get the relative path of the execution file, and the whole line is taken from the upper-level directory
sys.path.append(BASE_DIR)
sys.path.append(BASE_DIR + "/GUI")
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon
from PyQt5.QtCore import Qt, QRect

from Game.GameManager import GameManager
from Game.GameManagerTest import initCards
from Game.GameElements import Action
from Game.GameElements import Hint
from Game.GameElements import Card
from Server.Client import Client
import time

FONTSIZE = 10
SERVER_IP_ADDRESS = "192.168.0.4"
PORT = 7777
# 파일명만 바꿔서
MainAlpha = uic.loadUiType("HanabiAlpha.ui")[0]
GiveHintAlpha = uic.loadUiType("testUI02.ui")[0]
# MainBoard
# giveHint
# etc..

SIDE_MARGIN = 1


class HanabiGui(QMainWindow, MainAlpha):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        '''
                initCards : 랜덤으로 줘야 해 - 서버에서 해서 뿌려야 할 것 같음. 진영 용택 논의 필요
                clientIndex : 서버에서 받아야 함
                beginnerIndex : 서버에서 받아야 함
        '''
        self.beginnerIndex = 0
        self.clientIndex = 0
        self.isTurn = 1
        self.isConnected = False
        self.client = Client(self.onReceiveGameStartSymbol, self.OnReceiveChat, self.onReceiveAction, IP=SERVER_IP_ADDRESS, port=PORT)
        self.gm = None
        self.btnGiveHint.clicked.connect(self.clickedGiveHint)

        # 배경 사진 넣기
        background = QImage("background.jpeg")
        palette = QPalette()
        palette.setBrush(10, QBrush(background))
        self.setPalette(palette)
        self.notice.setText(" ")
        self.remainDeck.setText("남은 카드 \n0")

        # 들고 있는 카드의 list
        self.deckList = [[self.player0Deck0, self.player0Deck1, self.player0Deck2, self.player0Deck3],
                         [self.player1Deck0, self.player1Deck1, self.player1Deck2, self.player1Deck3],
                         [self.player2Deck0, self.player2Deck1, self.player2Deck2, self.player2Deck3],
                         [self.player3Deck0, self.player3Deck1, self.player3Deck2, self.player3Deck3]]

        # 낸 카드의 list
        self.droppedCardList = [self.playedRed, self.playedGreen, self.playedBlue, self.playedWhite, self.playedYellow]

        # 버린 카드의 list
        self.thrownCardList = [[self.throwR1, self.throwR2, self.throwR3, self.throwR4, self.throwR5],
                               [self.throwG1, self.throwG2, self.throwG3, self.throwG4, self.throwG5],
                               [self.throwB1, self.throwB2, self.throwB3, self.throwB4, self.throwB5],
                               [self.throwW1, self.throwW2, self.throwW3, self.throwW4, self.throwW5],
                               [self.throwY1, self.throwY2, self.throwY3, self.throwY4, self.throwY5]]

        # 힌트 토큰의 list
        self.hintTokenList = [self.hintToken0, self.hintToken1, self.hintToken2, self.hintToken3,
                              self.hintToken4, self.hintToken5, self.hintToken6, self.hintToken7]

        # 목숨 토큰의 list
        self.lifeTokenList = [self.lifeToken0, self.lifeToken1, self.lifeToken2]

        for card in self.droppedCardList:
            card.setText("0")

        # for i, deck in enumerate(self.deckList):
        #     # clinet 위치를 어떻게 잡느냐가 관건..
        #     # 아래 주석은 자신의 카드를 가리기 위한 코드. test 시에는 무시하고 진행한다.
        #     '''
        #     if i == self.clientIndex:
        #         for j in range(4):
        #             SetCardDesign("mine", deck[j])
        #     '''
        #     for j in range(4):
        #         SetCardDesign(self.gm.playerDecks[i].getCardOrNone(j).getColor(), deck[j])
        #         deck[j].setText(str(self.gm.playerDecks[i].getCardOrNone(j)))

        self.updateMainWindow()

        self.btnThrow.clicked.connect(self.showThrowDeck)
        self.btnDrop.clicked.connect(self.showDropDeck)
        self.btnGiveHint.clicked.connect(self.showGiveHint)
        # 다음 내용은 불변.
        # 창 아이콘
        self.setWindowIcon(QIcon('Hanabi.PNG'))
        # 창크기 조절, 출력
        self.setFixedSize(1910, 990)
        self.setWindowTitle('Hanabi')
        self.show()

    def showEvent(self, event):
        while not self.isConnected:
            print("trying Connect to Server")
            self.isConnected = self.client.connectWithServer()
        event.accept()

    # 부모 창 업데이트 해주는 함수
    def updateMainWindow(self):
        # 덱 갱신
        # TODO: show no card info of my card
        if self.gm != None:
            for i in range(4):
                playerDeck = self.gm.getPlayerDeck(i)

                for k in range(4):
                    card = playerDeck.getCardOrNone(k)

                    if card != None:
                        setCardDesign(card.getColor(), self.deckList[i][k])
                        self.deckList[i][k].setText(str(card))
                    else:
                        setCardDesign("None", self.deckList[i][k])
                        self.deckList[i][k].setText("@@")

            # 남은 카드 더미 갱신
            self.remainDeck.setText("남은 카드 \n%d" % len(self.gm.cards))

            # 낸 카드 갱신
            color_list = ["R", "G", "B", "W", "Y"]
            for i, color in enumerate(color_list):
                self.droppedCardList[i].setText(str(len(self.gm.getPlayedCards(color))))

            # 버린 카드 갱신
            for i, color in enumerate(color_list):
                for j in range(5):
                    count = self.gm.getDiscardedCardCounter(color)[j + 1]
                    self.thrownCardList[i][j].setText(str(count))

            # 목숨 토큰 갱신
            numLifeToken = self.gm.getLifeToken()
            for i, lifeToken in enumerate(self.lifeTokenList):
                if i < numLifeToken:
                    lifeToken.setText("O")
                else:
                    lifeToken.setText("X")

            # 힌트 토큰 갱신
            numHintToken = self.gm.getHintToken()
            for i, hintToken in enumerate(self.hintTokenList):
                if i < numHintToken:
                    hintToken.setText("O")
                else:
                    hintToken.setText("X")

    # 카드 버리기 창
    def showThrowDeck(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            print("Opening a Throw window...")
            self.w = AppThrowDeck(self)
            self.w.setGeometry(QRect(700, 400, 300, 200))
            self.w.show()

    # 카드 내기 창
    def showDropDeck(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            print("Opening a Drop window...")
            self.w = AppDropDeck(self)
            self.w.setGeometry(QRect(700, 400, 300, 200))
            self.w.show()

    # 힌트 주기 창
    def showGiveHint(self):
        # 내 차례라면 창을 연다.
        if self.isTurn and self.gm.getHintToken() != 0:
            print("Opening a GiveHint window...")
            # 플레이어 덱 정보를 넘겨야 하므로 gm.playerDecks 를 매개변수로 넣는다 .
            self.w = AppGiveHint(self)
            self.w.setGeometry(QRect(700, 400, 300, 200))
            self.w.show()

    def clickedGiveHint(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            winGiveHint = GiveHint()
            winGiveHint.show()

    def onReceiveGameStartSymbol(self, data: str):
        beginPlayerIndex = int(data[0])
        cardStrings = data[1:].split()

        cards = []
        for cardStr in cardStrings:
            cards.append(Card(cardStr[0], int(cardStr[1])))

        self.gm = GameManager(cards, self.clientIndex, beginPlayerIndex)
        self.gm.distributeCards()
        self.updateMainWindow()
        
        # TODO: 시작 전엔 모든 버튼 잠그고, 시작 플레이어만 풀어주기

    def onReceiveAction(self, data: str):
        assert self.gm is not None

        actionStrings = data.split('/')
        type = int(actionStrings[0])

        if type == 3:    # type is hint
            targetIndex = int(actionStrings[1])
            if str.isdigit(actionStrings[2]):
                hint = Hint(int(actionStrings[2]))
            else:
                hint = Hint(actionStrings[2])
            self.onCurrentPlayerGiveHint(hint, targetIndex)
        else:
            element = int(actionStrings[1]) # card index

            if type == 1:
                self.onCurrentPlayerPlay(element, bUiInput=False)

            elif type == 2:
                self.onCurrentPlayerDiscard(element, bUiInput=False)

        # TODO: 각 자식 윈도우에서 처리하는 부분을 main 윈도우 멤버 메소드로 옮겨 하드코딩 없이 이 부분에서 동일한 처리하기 => 진행중

        self.updateMainWindow()

    def onReceiveChat(self, data: str):
        # 아직 채팅 UI가 없음
        pass

    def onCurrentPlayerPlay(self, cardIndex: int, bUiInput: bool):
        # TODO : notice 만들 때 한 번에 만들지 말고 append 하는 방식으로 작성하여 코드 중복 방지.
        action = Action(1, cardIndex)

        if bUiInput:
            self.client.sendAction(action)

        playedCard = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(cardIndex)

        flag = self.gm.doActionPlay(action)

        # 카드 내는 데에 성공했다면
        if flag:
            # 남은 덱이 있다면
            if not self.gm.isCardsEmpty():
                notice = "Play 성공!\n" \
                         "%d번째 플레이어가 %s 카드를 냈습니다.\n" \
                         "%d번 플레이어가 새로운 카드를 받았습니다." % (self.gm.currentPlayerIndex, str(playedCard),
                                                       self.gm.currentPlayerIndex)

            # 남은 덱이 없다면
            else:
                notice = "Play 성공!\n" \
                         "%d번째 플레이어가 %s 카드를 냈습니다.\n" \
                         "%d번 플레이어가 새로운 카드를 받았습니다\n" \
                         "카드가 전부 떨어졌습니다. \n" \
                         "다음 %d번째 플레이어의 차례를 마치면 게임을 끝냅니다." \
                         % (self.gm.currentPlayerIndex, str(playedCard), self.gm.currentPlayerIndex,
                            (self.gm.currentPlayerIndex + 3) % 4)

            # 카드 내는 데에 실패했다면
        else:
            if not self.gm.isCardsEmpty():
                notice = "Play 실패!\n" \
                         "라이프 토큰이 하나 감소합니다.\n" \
                         "%d번 플레이어가 새로운 카드를 받았습니다.\n" % (self.gm.currentPlayerIndex)

            # 남은 덱이 없으면
            else:
                notice = "Play 실패!\n" \
                         "라이프 토큰이 하나 감소합니다.\n" \
                         "%d번 플레이어가 새로운 카드를 받았습니다.\n" \
                         "카드가 전부 떨어졌습니다.\n" \
                         "다음 %d번째 플레이어의 차례를 마치면 게임을 끝냅니다." % (self.gm.currentPlayerIndex,
                                                              (self.gm.currentPlayerIndex + 3) % 4)

        endFlag = self.gm.nextTurn()
        if not endFlag:
            pass

        if endFlag or self.gm.getLifeToken() == 0:
            print("카드 내기로 게임 끝")  # DEBUG
            notice = "게임 종료!\n" \
                     "최종 점수: %d점" % (self.gm.calculateScore())

            # 게임이 끝나면 행동 버튼 눌리지 않게 처리함. 추후 변경 필요
            self.isTurn = 0
        # 카드 내기 후 notice 갱신
        self.notice.setText(notice)
        self.updateMainWindow()

    def onCurrentPlayerDiscard(self, cardIndex: int, bUiInput: bool):
        discardedCard = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(cardIndex)

        # 게임 진행
        action = Action(2, cardIndex)

        if bUiInput:    # UI를 통해 입력되었다면 서버로 전달되어야함
            # TODO: 클라이언트가 초기화되지 않았을 때도 클라이언트를 테스트하기 위해 clinet.isConnectValid() 함수가 있으면 좋을듯
            # 자꾸 크래시나서 불필요한 테스트 전처리를 많이 해야함 ㅠㅠ
            self.client.sendAction(action)

        self.gm.doActionDiscard(action)

        # Notice update
        notice = "%d번 플레이어가 %s 카드를 버렸습니다.\n 힌트 토큰이 하나 증가합니다. (8 이상이면 증가하지 않음)\n" % \
                 (self.gm.currentPlayerIndex, str(discardedCard))
        if self.gm.isCardsEmpty():
            notice += "카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다.\n" % self.gm.lastPlayerIndex

        # 게임 진행
        bEnd = self.gm.nextTurn()

        if bEnd:
            notice += "게임 종료!\n최종 점수: %d점\n" % self.gm.calculateScore()

        # notice 갱신
        self.notice.setText(notice)

        self.updateMainWindow()

    def onCurrentPlayerGiveHint(self, hint: Hint, targetIndex: int, bUiInput: bool):
        # 게임 진행
        action = Action(3, hint, targetIndex)

        if bUiInput:  # UI를 통해 입력되었다면 서버로 전달되어야함
            self.client.sendAction(action)

        result = self.gm.doActionHint(action)
        correspondedIndexes = result[1]

        hintString = hint.getHintString()
        notice = ""

        if not correspondedIndexes:    # 힌트와 일치하는 카드가 없는 경우 해당 카드가 없다 힌트를 준 것
            notice = "%d번 플레이어가 %d번 플레이어에게\n%s 카드가 없음을 알려주었습니다.\n" \
                     % (self.gm.currentPlayerIndex, targetIndex, hintString)
        else:
            notice = "%d번 플레이어가 %d번 플레이의\n" % (self.gm.getCurrentPlayerIndex(), targetIndex)
            for cardIndex in correspondedIndexes:
                notice += "%d번 " % cardIndex
            notice += "카드가\n"
            notice += "%s 카드임을 알려주었습니다.\n" % hintString

        notice += "힌트 토큰이 하나 감소합니다.\n"

        # 힌트 토큰 수가 0이라면 힌트 버튼 잠그기
        if self.gm.getHintToken() == 0:
            self.btnGiveHint.setEnabled(False)

        # 게임 진행
        bEnd = self.gm.nextTurn()
        if bEnd:
            notice += "게임 종료!\n최종 점수: %d점\n" % self.gm.calculateScore()

        # notice 갱신
        self.notice.setText(notice)

        self.updateMainWindow()


class GiveHint(QDialog):
    def __init__(self):
        super().__init__()
        # self.setupUi(GiveHintAlpha)
        # self.setFixedSize(900, 500)
        self.setWindowTitle('Give Hint')
        label = QLabel('나는 라벨', self)
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(10)
        font.setFamily('Times New Roman')
        font.setBold(True)
        label.setFont(font)

    def clickedGiveHint(self):
        winGiveHint = GiveHint()
        winGiveHint.show()

    def showModal(self):
        return super().exec_()


def setCardDesign(color, cardLabel):
    if color == "R":
        cardLabel.setStyleSheet("background-color : rgb(255, 79, 79);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "G":
        cardLabel.setStyleSheet("background-color : " + "rgb(11, 222, 0);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "B":
        cardLabel.setStyleSheet("background-color : rgb(49, 190, 255);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "Y":
        cardLabel.setStyleSheet("background-color : rgb(243, 243, 0);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "W":
        cardLabel.setStyleSheet("background-color :  rgb(255, 255, 255);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "mine":
        cardLabel.setStyleSheet("background-color :  rgb(12, 0, 186);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )
    elif color == "None":
        # TODO: to be decided with proper color, design
        cardLabel.setStyleSheet("background-color :  rgb(0, 0, 0);"
                                "border-width: 2px;"
                                "border-style : solid;"
                                "border-radius: 20px;"
                                "border-color : rgb(0, 0, 0)"
                                )


# 카드 버리기 창
class AppThrowDeck(QWidget):
    def __init__(self, mainUi: HanabiGui):
        QWidget.__init__(self)
        self.buttonGroup = QButtonGroup()
        self.mainUi = mainUi
        self.initUI()

    def initUI(self):
        self.setWindowTitle('버리기')
        deck0 = QPushButton("??")
        deck1 = QPushButton("??")
        deck2 = QPushButton("??")
        deck3 = QPushButton("??")

        self.buttonGroup.buttonClicked[int].connect(self.onButtonClicked)
        self.buttonGroup.addButton(deck0, 0)
        self.buttonGroup.addButton(deck1, 1)
        self.buttonGroup.addButton(deck2, 2)
        self.buttonGroup.addButton(deck3, 3)

        for button in self.buttonGroup.buttons():
            setCardDesign("mine", button)
        layout1 = QHBoxLayout()
        layout1.addWidget(deck0)
        layout1.addWidget(deck1)
        layout1.addWidget(deck2)
        layout1.addWidget(deck3)
        deck0.setMaximumHeight(400)
        deck1.setMaximumHeight(400)
        deck2.setMaximumHeight(400)
        deck3.setMaximumHeight(400)
        self.setLayout(layout1)

    def onButtonClicked(self, _id: int):
        '''
        :param _id: 몇 번째 카드를 버릴 건지
        :return: 버릴 카드 정보 반환
        '''
        if len(self.buttonGroup.buttons()) <= _id:
            return

        # 버려진 카드
        self.mainUi.onCurrentPlayerDiscard(_id, bUiInput=True)
        self.close()


# 카드 내기 창
class AppDropDeck(QWidget):
    def __init__(self, mainUi: HanabiGui):
        QWidget.__init__(self)
        self.buttonGroup = QButtonGroup()
        self.mainUi = mainUi
        self.initUI()

    def initUI(self):
        self.setWindowTitle("카드 내기")
        self.deck0 = QPushButton()
        self.deck1 = QPushButton()
        self.deck2 = QPushButton()
        self.deck3 = QPushButton()

        self.buttonGroup.buttonClicked[int].connect(self.onButtonClicked)
        self.buttonGroup.addButton(self.deck0, 0)
        self.buttonGroup.addButton(self.deck1, 1)
        self.buttonGroup.addButton(self.deck2, 2)
        self.buttonGroup.addButton(self.deck3, 3)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.deck0)
        layout1.addWidget(self.deck1)
        layout1.addWidget(self.deck2)
        layout1.addWidget(self.deck3)

        self.deck0.setMaximumHeight(400)
        self.deck1.setMaximumHeight(400)
        self.deck2.setMaximumHeight(400)
        self.deck3.setMaximumHeight(400)
        self.setLayout(layout1)

        self.cardList = [self.deck0, self.deck1, self.deck2, self.deck3]

        for i, deck in enumerate(self.cardList):
            card = self.mainUi.gm.playerDecks[self.mainUi.gm.currentPlayerIndex].getCardOrNone(i)
            if card is None:
                deck.setText("None")
            else:
                deck.setText("??")
            setCardDesign("mine", deck)
        self.setLayout(layout1)

    def onButtonClicked(self, _id: int):
        if len(self.buttonGroup.buttons()) <= _id:
            return

        # 카드 플레이
        self.mainUi.onCurrentPlayerPlay(_id, bUiInput=True)
        self.close()


# 힌트주기 창
class AppGiveHint(QWidget):
    def __init__(self, mainUi: HanabiGui):
        '''
        :param gm: gameManager
        :param notice: 게임진행 상황 출력하는 QLabel.
        '''
        QWidget.__init__(self)
        self.mainUi = mainUi
        self.gm = mainUi.gm
        self.selectorIndex = self.gm.getCurrentPlayerIndex()
        # 첫 창에 뜨는 카드가 자신이 0번유저면 1, 아니면 0이 나오게 함.
        self.targetPlayerIndex = 1 if self.gm.currentPlayerIndex == 0 else 0
        self.buttonGroup = QButtonGroup()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('힌트 주기')
        cob = QComboBox(self)

        # 아이디를 서버에서 받아야겠다
        player1 = "0번의 아이디"
        player2 = "1번의 아이디"
        player3 = "2번의 아이디"
        player4 = "3번의 아이디"
        self.deck0 = QLabel()
        self.deck1 = QLabel()
        self.deck2 = QLabel()
        self.deck3 = QLabel()

        # QComboBox 현재 플레이 중인 유저 아이디 제외하고 출력
        playerList = [player1, player2, player3, player4]
        for i, player in enumerate(playerList):
            if i == self.gm.currentPlayerIndex:
                continue
            cob.addItem(player)

        self.buttonGroup.buttonClicked[int].connect(self.onButtonClicked)
        cob.currentIndexChanged[int].connect(self.onComboBoxIndexChanged)

        deckList = [self.deck0, self.deck1, self.deck2, self.deck3]
        layout2 = QHBoxLayout()
        for i, deck in enumerate(deckList):
            if self.gm.playerDecks[self.targetPlayerIndex].getCardOrNone(i) is None:
                deck.setText("None")
                setCardDesign("mine", self.deck0)
            else:
                deck.setText(str(self.gm.playerDecks[self.targetPlayerIndex].getCardOrNone(i)))
                setCardDesign(self.gm.playerDecks[self.targetPlayerIndex].getCardOrNone(i).getColor(), deck)

        layout2.addWidget(self.deck0)
        layout2.addWidget(self.deck1)
        layout2.addWidget(self.deck2)
        layout2.addWidget(self.deck3)

        self.deck0.setMinimumHeight(160)
        self.deck1.setMinimumHeight(160)
        self.deck2.setMinimumHeight(160)
        self.deck3.setMinimumHeight(160)

        self.deck0.setMaximumWidth(140)
        self.deck1.setMaximumWidth(140)
        self.deck2.setMaximumWidth(140)
        self.deck3.setMaximumWidth(140)

        self.deck0.setAlignment(Qt.AlignCenter)
        self.deck1.setAlignment(Qt.AlignCenter)
        self.deck2.setAlignment(Qt.AlignCenter)
        self.deck3.setAlignment(Qt.AlignCenter)

        btnNumber1 = QPushButton("1")
        btnNumber2 = QPushButton("2")
        btnNumber3 = QPushButton("3")
        btnNumber4 = QPushButton("4")
        btnNumber5 = QPushButton("5")

        self.buttonGroup.addButton(btnNumber1, 0)
        self.buttonGroup.addButton(btnNumber2, 1)
        self.buttonGroup.addButton(btnNumber3, 2)
        self.buttonGroup.addButton(btnNumber4, 3)
        self.buttonGroup.addButton(btnNumber5, 4)

        layout3 = QHBoxLayout()
        layout3.addWidget(btnNumber1)
        layout3.addWidget(btnNumber2)
        layout3.addWidget(btnNumber3)
        layout3.addWidget(btnNumber4)
        layout3.addWidget(btnNumber5)

        btnColorR = QPushButton("R")
        btnColorG = QPushButton("G")
        btnColorB = QPushButton("B")
        btnColorY = QPushButton("W")
        btnColorW = QPushButton("Y")

        self.buttonGroup.addButton(btnColorR, 5)
        self.buttonGroup.addButton(btnColorG, 6)
        self.buttonGroup.addButton(btnColorB, 7)
        self.buttonGroup.addButton(btnColorY, 8)
        self.buttonGroup.addButton(btnColorW, 9)
        layout4 = QHBoxLayout()
        layout4.addWidget(btnColorR)
        layout4.addWidget(btnColorG)
        layout4.addWidget(btnColorB)
        layout4.addWidget(btnColorY)
        layout4.addWidget(btnColorW)

        layout5 = QVBoxLayout()
        layout5.addWidget(cob)
        layout5.addLayout(layout2)
        layout5.addLayout(layout3)
        layout5.addLayout(layout4)
        cob.setMaximumSize(300, 30)
        cob.setMinimumSize(300, 30)
        self.setLayout(layout5)

    def onComboBoxIndexChanged(self, index: int):
        # 현재 힌트를 주는 플레이어의 인덱스보다 작다면 +1 해주어야함
        self.targetPlayerIndex = index
        if self.selectorIndex <= index:
            self.targetPlayerIndex += 1

        deckList = [self.deck0, self.deck1, self.deck2, self.deck3]
        for i, cardLabel in enumerate(deckList):
            card = self.gm.playerDecks[self.targetPlayerIndex].getCardOrNone(i)
            if card is None:
                cardLabel.setText("None")
                setCardDesign("mine", cardLabel)
            else:
                cardLabel.setText(str(card))
                setCardDesign(self.gm.playerDecks[self.targetPlayerIndex].getCardOrNone(i).getColor(), cardLabel)

    def onButtonClicked(self, index: int):
        hint = Hint(Hint.HINT_INFO[index])
        self.hanabiGui.onCurrentPlayerGiveHint(hint, self.targetPlayerIndex, bUiInput=True)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = HanabiGui()
    myWindow.show()
    app.exec_()

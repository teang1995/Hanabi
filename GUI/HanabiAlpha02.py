import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon
from PyQt5.QtCore import Qt, QRect
from Game.GameManager import GameManager as GM
from Game.GameManagerTest import initCards
from Game.GameElements import Action as Action
from Game.GameElements import Hint as Hint

import time

FONTSIZE = 10

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

        self.gm = GM(initCards(5), self.clientIndex, self.beginnerIndex)
        self.gm.distributeCards()
        self.btnGiveHint.clicked.connect(self.clickedGiveHint)
        # 배경 사진 넣기
        background = QImage("background.jpeg")
        palette = QPalette()
        palette.setBrush(10, QBrush(background))
        self.setPalette(palette)
        self.notice.setText(" ")
        self.remainDeck.setText("남은 카드 \n%d" % len(self.gm.cards))
        # 임의 부여함.




        # 들고 있는 카드의 list
        self.deckList = [[self.player0Deck0, self.player0Deck1, self.player0Deck2, self.player0Deck3],
                         [self.player1Deck0, self.player1Deck1, self.player1Deck2, self.player1Deck3],
                         [self.player2Deck0, self.player2Deck1, self.player2Deck2, self.player2Deck3],
                         [self.player3Deck0, self.player3Deck1, self.player3Deck2, self.player3Deck3]]




        # 낸 카드의 list
        self.drpoedCardList = [self.playedRed, self.playedGreen, self.playedBlue, self.playedWhite, self.playedYellow]

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

        for card in self.drpoedCardList:
            card.setText("0")
        print(type(self.player3Deck2))
        for deck in self.gm.playerDecks:
            print(deck)
        for i, deck in enumerate(self.deckList):
            # clinet 위치를 어떻게 잡느냐가 관건..
            # 아래 주석은 자신의 카드를 가리기 위한 코드. test 시에는 무시하고 진행한다.
            '''
            if i == self.clientIndex:
                for j in range(4):
                    SetCardDesign("mine", deck[j])
            '''
            for j in range(4):
                SetCardDesign(self.gm.playerDecks[i].getCardOrNone(j).getColor(), deck[j])
                deck[j].setText(str(self.gm.playerDecks[i].getCardOrNone(j)))

        self.btnThrow.clicked.connect(self.ShowThrowDeck)
        self.btnDrop.clicked.connect(self.ShowDropDeck)
        self.btnGiveHint.clicked.connect(self.ShowGiveHint)
        # 다음 내용은 불변.
        # 창 아이콘
        self.setWindowIcon(QIcon('Hanabi.PNG'))
        # 창크기 조절, 출력
        self.setFixedSize(1910, 990)
        self.setWindowTitle('Hanabi')
        self.show()

    # 카드 버리기 창
    def ShowThrowDeck(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            print("Opening a Throw window...")
            self.w = AppThrowDeck(self, self.gm, self.deckList, self.notice, self.btnGiveHint, self.remainDeck,
                                  self.thrownCardList, self.hintTokenList)
            self.w.setGeometry(QRect(700, 400, 300, 200))
            self.w.show()

    # 카드 내기 창
    def ShowDropDeck(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            print("Opening a Drop window...")
            self.w = AppDropDeck(self, self.gm, self.deckList, self.drpoedCardList,
                                 self.thrownCardList, self.notice, self.lifeTokenList, self.remainDeck)
            self.w.setGeometry(QRect(700, 400, 300, 200))
            self.w.show()

    # 힌트 주기 창
    def ShowGiveHint(self):
        # 내 차례라면 창을 연다.
            if self.isTurn and self.gm.getHintToken() != 0:
                print("Opening a GiveHint window...")
                # 플레이어 덱 정보를 넘겨야 하므로 gm.playerDecks 를 매개변수로 넣는다 .
                self.w = AppGiveHint(self, self.gm, self.notice, self.btnGiveHint, self.hintTokenList)
                self.w.setGeometry(QRect(700, 400, 300, 200))
                self.w.show()

    def clickedGiveHint(self):
        # 내 차례라면 창을 연다.
        if self.isTurn:
            winGiveHint = GiveHint()
            winGiveHint.show()


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


def SetCardDesign(color, deck):
    if color == "R":
        deck.setStyleSheet("background-color : rgb(255, 79, 79);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )
    elif color == "G":
        deck.setStyleSheet("background-color : " + "rgb(11, 222, 0);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )
    elif color == "B":
        deck.setStyleSheet("background-color : rgb(49, 190, 255);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )
    elif color == "Y":
        deck.setStyleSheet("background-color : rgb(243, 243, 0);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )
    elif color == "W":
        deck.setStyleSheet("background-color :  rgb(255, 255, 255);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )
    elif color == "mine":
        deck.setStyleSheet("background-color :  rgb(12, 0, 186);"
                           "border-width: 2px;"
                           "border-style : solid;"
                           "border-radius: 20px;"
                           "border-color : rgb(0, 0, 0)"
                           )


#카드 버리기 창
class AppThrowDeck(QWidget):
    def __init__(self, hanabiGUI: HanabiGui, gm: GM, deckList: list, notice: QLabel, btnGiveHint: QPushButton, remainDeck: QLabel
                 , thrownCardList: list, hintTokenList: list):
        QWidget.__init__(self)
        self.gm = gm
        self.playerDeck = self.gm.playerDecks[self.gm.currentPlayerIndex]
        self.buttonGroup = QButtonGroup()
        self.deckList = deckList
        self.btnGiveHint = btnGiveHint
        self.notice = notice
        self.remainDeck = remainDeck
        self.thrownCardList = thrownCardList
        self.hintTokenList = hintTokenList
        self.colorDict = {"R": 0, "G": 1, "B": 2, "W": 3, "Y": 4}
        self.hanabiGUI = hanabiGUI
        self.initUI()

    def initUI(self):
        self.setWindowTitle('버리기')
        deck0 = QPushButton("??")
        deck1 = QPushButton("??")
        deck2 = QPushButton("??")
        deck3 = QPushButton("??")

        self.buttonGroup.buttonClicked[int].connect(self.discardCard)
        self.buttonGroup.addButton(deck0, 0)
        self.buttonGroup.addButton(deck1, 1)
        self.buttonGroup.addButton(deck2, 2)
        self.buttonGroup.addButton(deck3, 3)

        for button in self.buttonGroup.buttons():
            SetCardDesign("mine", button)
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

    def discardCard(self, id):
        '''
        :param id: 몇 번째 카드를 버릴 건지
        :return: 버릴 카드 정보 반환
        '''
        for button in self.buttonGroup.buttons():
            if button is self.buttonGroup.button(id):
                # print("{}번 플레이어가 {}번째 카드를 버렸습니다.".format(self.gm.currentPlayerIndex, id + 1)) # DEBUG

                # 버려진 카드
                cardDiscarded = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(id)

                # 게임 진행
                self.gm.doActionDiscard(Action(2, id))

                # 새로 표시할 카드
                card = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(id)

                if card == None:
                    self.deckList[self.gm.currentPlayerIndex][id].setText("None")
                    SetCardDesign("mine", self.deckList[self.gm.currentPlayerIndex][id])
                else:
                    # 현재 하나의 gui 에서 플레이할 때 확이하기 위해 남겨둠. 추후 서버 통합시 유저의 카드 확인 불가.
                    self.deckList[self.gm.currentPlayerIndex][id].setText(str(card))
                    SetCardDesign(card.getColor(), self.deckList[self.gm.currentPlayerIndex][id])

                # 덱이 비지 않았다면
                if not self.gm.isCardsEmpty():
                    notice = ("%d번 플레이어가 %s 카드를 버렸습니다.\n 힌트 토큰이 하나 증가합니다. (8 이상이면 증가하지 않음)" %
                               (self.gm.currentPlayerIndex, str(cardDiscarded)))
                # 덱이 비었다면
                else:
                    notice = ("%d번 플레이어가 %s 카드를 버렸습니다.\n 힌트 토큰이 하나 증가합니다. (8 이상이면 증가하지 않음)\n "
                               "카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다." %
                               (self.gm.currentPlayerIndex, str(cardDiscarded), self.gm.lastPlayerIndex))



                # 힌트 주기 버튼 갱신
                self.btnGiveHint.setEnabled(True)

                # 힌트 토큰 갱신
                self.hintTokenList[self.gm.getHintToken() - 1].setText("O")

                # 남은 카드 장수 갱신
                self.remainDeck.setText("남은 카드 \n%d" % len(self.gm.cards))

                # thrownCard 갱신
                self.thrownCardList[self.colorDict[cardDiscarded.getColor()]][cardDiscarded.getNumber() - 1].\
                    setText(str(self.gm.getDiscardedCardCounter(cardDiscarded.getColor())[cardDiscarded.getNumber()]))

                # 게임 진행
                endFlag = self.gm.nextTurn()

                if endFlag == None:
                    pass
                if endFlag == 1 or self.gm.getLifeToken() == 0 or self.gm.currentPlayerIndex == self.gm.lastPlayerIndex:
                    print("카드 버리기로 게임 끝")  # DEBUG
                    notice = "게임 종료!\n" \
                             "최종 점수: %d점" % (self.gm.calculateScore())
                    time.sleep(3)
                    self.hanabiGui.close()

                # notice 갱신
                self.notice.setText(notice)
                self.close()


# 카드 내기 창
class AppDropDeck(QWidget):
    def __init__(self, hanabiGui: HanabiGui, gm: GM, deckList: list, droppedCardList: list , thrownCardList: list,
                 notice: QLabel, lifeTokenList: list, remainDeck: QLabel):
        QWidget.__init__(self)
        self.hanabiGui = hanabiGui
        self.gm = gm
        self.droppedCardList = droppedCardList
        self.deckList = deckList
        self.thrownCardList = thrownCardList
        self.notice = notice
        self.lifeTokenList = lifeTokenList
        self.remainDeck = remainDeck
        self.colorDict = {"R" : 0, "G" : 1, "B" : 2, "W" : 3, "Y" : 4}
        self.deckGroup = QButtonGroup()
        self.buttonGroup = QButtonGroup()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("카드 내기")
        self.deck0 = QPushButton()
        self.deck1 = QPushButton()
        self.deck2 = QPushButton()
        self.deck3 = QPushButton()

        self.buttonGroup.buttonClicked[int].connect(self.playCard)
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
            card = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(i)
            if card is None:
                deck.setText("None")
            else:
                deck.setText("??")
            SetCardDesign("mine", deck)
        self.setLayout(layout1)

    def playCard(self, id):
        '''
                :param id: 몇 번째 카드를 낼 건지
                '''
        for button in self.buttonGroup.buttons():
            if button is self.buttonGroup.button(id):

                # 카드의 색 및 숫자
                playedCard = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(id)
                color = playedCard.getColor()
                number = playedCard.getNumber()
                # print("{}번 플레이어가 {}번째 카드를 냈습니다.".format(self.gm.currentPlayerIndex, id + 1)) # DEBUG
                '''
                카드 배치 성공 여부에 따라 행동이 달라짐. 
                성공했다면 playedCardList를, 실패했다면 discardedCardList 를 조작해주어야 함.
                우선 doAction 함수의 카드를 내는 부분에만 early return 을 넣어주어 성공 여부를 구분했음.
                1) 이를 개선할 방법이 있는지 알아봐야 함.
                2) 버려진 카드와 배치된 카드를 받아올 가장 효율적인 방법을 알아야 함.
                2-1) 현재까지 파악한 바로는 카드 색으로만 list 를 다루는 걸로 확인되는데, 숫자까지 구분해 digit 개념으로 리스트를 
                    따로 만들거나 ui 표시를 위한 리스트를 따로 만드는 것이 좋아보임.
                '''
                '''
                2020.08.17 updated
                기존의 doAction함수가 변경되면서 doActionPlay를 사용함. 
                입력값은 기존과 동일하고, 반환값으로 올바르게 냈는지 여부를 반환함.
                '''
                # 게임 진행 및 flag 설정
                flag = self.gm.doActionPlay(Action(1, id))

                # 카드 놓는 데에 성공했으면
                if flag:
                    # 낸 카드 ui 갱신
                    self.droppedCardList[self.colorDict[color]].setText(str(len(self.gm.getPlayedCards(color))))
                    # 남은 덱이 있으면
                    if not self.gm.isCardsEmpty():
                        notice = "Play 성공!\n" \
                                 "%d번째 플레이어가 %s 카드를 냈습니다.\n" \
                                 "%d번 플레이어가 새로운 카드를 받았습니다." % (self.gm.currentPlayerIndex, str(playedCard),
                                                               self.gm.currentPlayerIndex)
                    # 남은 덱이 없으면
                    else:
                        notice = "Play 성공!\n" \
                                 "%d번째 플레이어가 %s 카드를 냈습니다.\n" \
                                 "%d번 플레이어가 새로운 카드를 받았습니다\n" \
                                 "카드가 전부 떨어졌습니다. \n" \
                                 "다음 %d번째 플레이어의 차례를 마치면 게임을 끝냅니다." \
                                 % (self.gm.currentPlayerIndex, str(playedCard), self.gm.currentPlayerIndex,
                                   (self.gm.currentPlayerIndex + 3) % 4)


                # 카드 놓는 데에 실패했으면
                else:
                    # 버려진 카드 갱신
                    self.thrownCardList[self.colorDict[color]][number - 1].\
                        setText(str(self.gm.getDiscardedCardCounter(color)[number]))
                    self.lifeTokenList[self.gm.getLifeToken()].setText("X")
                    # 남은 덱이 있으면
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

                # 카드 낸 후 남은 카드 갱신
                self.remainDeck.setText("남은 카드 \n%d" % len(self.gm.cards))

                # 새로 표시할 카드
                card = self.gm.playerDecks[self.gm.currentPlayerIndex].getCardOrNone(id)
                if card == None:
                    self.deckList[self.gm.currentPlayerIndex][id].setText("None")
                    SetCardDesign("mine", self.deckList[self.gm.currentPlayerIndex][id])
                else:
                    # 현재 하나의 gui 에서 플레이할 때 확이하기 위해 남겨둠. 추후 서버 통합시 유저의 카드 확인 불가.
                    self.deckList[self.gm.currentPlayerIndex][id].setText(str(card))
                    SetCardDesign(card.getColor(), self.deckList[self.gm.currentPlayerIndex][id])

                endFlag = self.gm.nextTurn()

                if endFlag == None:
                    pass
                if endFlag == 1 or self.gm.getLifeToken() == 0 or self.gm.currentPlayerIndex == self.gm.lastPlayerIndex:
                    print("카드 내기로 게임 끝")  # DEBUG
                    notice = "게임 종료!\n" \
                             "최종 점수: %d점" % (self.gm.calculateScore())
                    self.notice.setText(notice)
                    self.close()

                    # 게임이 끝나면 행동 버튼 눌리지 않게 처리함. 추후 변경 필요
                    self.hanabiGui.isTurn = 0
                # 카드 내기 후 notice 갱신
                self.notice.setText(notice)

                self.close()


# 힌트주기 창
class AppGiveHint(QWidget):
    def __init__(self, hanabiGui: HanabiGui, gm: GM, notice: QLabel, btnGiveHint: QPushButton, hintTokenList: list):
        '''
        :param gm: gameManager
        :param notice: 게임진행 상황 출력하는 QLabel.
        '''
        QWidget.__init__(self)
        self.HanabiGui = hanabiGui
        self.gm = gm
        # 첫 창에 뜨는 카드가 자신이 0번유저면 1, 아니면 0이 나오게 함.
        self.playerNum = 1 if self.gm.currentPlayerIndex == 0 else 0
        self.notice = notice
        self.btnGiveHint = btnGiveHint
        self.hintTokenList = hintTokenList
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

        self.buttonGroup.buttonClicked[int].connect(self.giveHint)
        cob.activated[str].connect(self.onActivated)

        deckList = [self.deck0, self.deck1, self.deck2, self.deck3]
        layout2 = QHBoxLayout()
        for i, deck in enumerate(deckList):
            if self.gm.playerDecks[self.playerNum].getCardOrNone(i) is None:
                deck.setText("None")
                SetCardDesign("mine", self.deck0)
            else:
                deck.setText(str(self.gm.playerDecks[self.playerNum].getCardOrNone(i)))
                SetCardDesign(self.gm.playerDecks[self.playerNum].getCardOrNone(i).getColor(), deck)

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

    def onActivated(self, text):
        # 현재는 "n번의 아이디"에서 n을 가져오는 최악의 방식으로 playerNum 갱신 중. 수정 필요.
        self.playerNum = int(text[0])
        deckList = [self.deck0, self.deck1, self.deck2, self.deck3]
        for i, deck in enumerate(deckList):
            card = self.gm.playerDecks[self.playerNum].getCardOrNone(i)
            if card == None:
                deck.setText("None")
                SetCardDesign("mine", deck)
            else:
                deck.setText(str(card))
                SetCardDesign(self.gm.playerDecks[self.playerNum].getCardOrNone(i).getColor(), deck)

    def giveHint(self, id):
        '''
        :return: 힌트에 대한 정보를 줄 것. 플레이어 번호 + 힌트를 str로 넘긴다.
        '''
        colorDict = {5: "R", 6: "G", 7: "B", 8: "W", 9: "Y"}
        for button in self.buttonGroup.buttons():
            if button is self.buttonGroup.button(id):
                # print("{}번째 플레이어에게 {}로 힌트를 주었습니다.".format(self.playerNum, button.text())) # DEBUG
                # 숫자 버튼이면?
                if 0 <= id <= 4:
                    hint, correspondedIndexes = self.gm.doAction(Action(3, Hint(id + 1), self.playerNum))
                    endFlag = self.gm.nextTurn()
                    self.close()
                if 5 <= id <= 9:
                    hint, correspondedIndexes = self.gm.doAction(Action(3, Hint(colorDict[id]), self.playerNum))
                    endFlag = self.gm.nextTurn()
                    self.close()
                # ~가 없다는 힌트 줄 때
                if len(correspondedIndexes) != 0:
                    notice = "%d번 플레이어가 %d번 플레이어에게 \n %s번째 카드가 %s임을 알려주었습니다.\n" \
                             "힌트 토큰이 하나 감소합니다." % (self.gm.currentPlayerIndex - 1, self.playerNum, correspondedIndexes, hint)
                # ~가 있다는 힌트 줄 때
                else:
                    notice = "%d번 플레이어가 %d번 플레이어에게 \n %s 카드가 없음을 알려주었습니다.\n" \
                             "힌트 토큰이 하나 감소합니다." % (self.gm.currentPlayerIndex - 1, self.playerNum, hint)
                if endFlag or self.gm.currentPlayerIndex == self.gm.lastPlayerIndex:
                    print("힌트 주기로 게임 끝") # DEBUG
                    notice = "게임 종료!\n" \
                             "최종 점수: %d점" % (self.gm.calculateScore())
                    time.sleep(5)
                    self.hanabiGui.close()
                self.notice.setText(notice)

                self.hintTokenList[self.gm.getHintToken()].setText("X")
                if self.gm.getHintToken():
                    pass
                else:
                    self.btnGiveHint.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = HanabiGui()
    myWindow.show()
    app.exec_()
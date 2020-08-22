from Game.GameElements import Hint as Hint
from Game.GameElements import Card as Card
from Game.GameElements import Action as Action
from Game.GameElements import PlayerDeck as PlayerDeck
from Server.Client import Client

SERVERIP = 'localhost' #문자열 형식으로 ex) '127.0.0.1'
SERVERPORT = 6666
from GUI import HanabiAlpha01 as gameboard

# 시작버튼을 누르면 서버에서 게임 시작시 정보를 받아 게임매니저를 생성하고 게임이 시작된다.
class GameManager:

    def __init__(self, cards: list, clientIndex: int, beginnerIndex: int):
        global SERVERIP, SERVERPORT
        self.playerDecks = [PlayerDeck() for i in range(4)]
        self.clientIndex = clientIndex
        self.currentPlayerIndex = beginnerIndex
        self.lastPlayerIndex = -1

        self.__hintToken = 8
        self.__lifeToken = 3

        self.cards = cards

        self.__redPlayedCards = []
        self.__greenPlayedCards = []
        self.__bluePlayedCards = []
        self.__whitePlayedCards = []
        self.__yellowPlayedCards = []

        # self.discardedCards = []
        self.__redDiscardedCards = []
        self.__greenDiscardedCards = []
        self.__blueDiscardedCards = []
        self.__whiteDiscardedCards = []
        self.__yellowDiscardedCards = []

        #Client
        self.client = Client(SERVERIP, SERVERPORT)
        '''
        일단은 localhost를 IP로 지정해두어서 테스트하기에는 편하게 해두었음
        추후 포팅을 이용하여 외부 네트워트에서 접속된 디바이스와도 통신이 가능하게 업데이트 예정
        지금은 같은 공유기에서 접속하였을 때 연결 가능
        아직은 수동으로 IP주소를 수정해주어야함
        '''


    def isCardsEmpty(self):
        # 카드더미가 비었는지 확인하는 함수
        return len(self.cards) == 0

    def isGameEnd(self):
        return self.__lifeToken is 0

    def giveOneCard(self, playerIndex: int):
        """
        카드더미 맨 위에서 카드를 뽑아 플레이어에게 주는 함수. isCardEmpty로 카드를 줄 수 있는지 검증하고 호출할 것
        :param playerIndex: 카드르 받을 플레이어의 색인
        """
        assert not self.isCardsEmpty(), "cannot give card when have no cards"
        card = self.cards[0]
        del self.cards[0]       # pop()을 쓰면 한줄로 줄일 수도 있다.
        self.playerDecks[playerIndex].addCard(card)

    def distributeCards(self):
        for i in range(4):
            for j in range(4):
                self.giveOneCard(j)

    def decreaseHintToken(self):
        assert self.__hintToken != 0, "can't decrease hint token"
        self.__hintToken -= 1

    def increaseHintToken(self):
        if self.__hintToken < 8:
            self.__hintToken += 1

    def decreaseLifeToken(self):
        assert self.__lifeToken > 0, "life can't be negative value"
        self.__lifeToken -= 1

        # 라이프 토큰이 다 달아버리면 바로 게임 종료
        if self.__lifeToken == 0:
            self.onGameEnd()

    def nextTurn(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % 4
        if self.lastPlayerIndex == self.currentPlayerIndex:
            self.onGameEnd()

    def getPlayerCount(self):
        return len(self.playerDecks)

    def getPlayerDeck(self, playerIndex: int):
        return self.playerDecks[playerIndex]

    def getCurrentPlayerIndex(self):
        return self.currentPlayerIndex

    def getHintToken(self):
        return self.__hintToken

    def getLifeToken(self):
        return self.__lifeToken

    def getPlayedCards(self, color: str):
        assert color == "R" or color == "G" or color == "B" or color == "W" or color == "Y", "invalid card color"

        if color == "R":
            return self.__redPlayedCards
        elif color == "G":
            return self.__greenPlayedCards
        elif color == "B":
            return self.__bluePlayedCards
        elif color == "W":
            return self.__whitePlayedCards
        return self.__yellowPlayedCards

    def getDiscardedCards(self, color: str):
        assert color == "R" or color == "G" or color == "B" or color == "W" or color == "Y", "invalid card color"

        if color == "R":
            return self.__redDiscardedCards
        elif color == "G":
            return self.__greenDiscardedCards
        elif color == "B":
            return self.__blueDiscardedCards
        elif color == "W":
            return self.__whiteDiscardedCards
        return self.__yellowDiscardedCards

    def doAction(self, action: Action):
        """
        Action을 수행하는 함수
        :param action: 수행할 동작
        """

        if action.getActionType() == 1:         # 카드내기 (Play)
            playerDeck = self.playerDecks[self.currentPlayerIndex]
            cardIndex = action.getCardIndex()

            card = playerDeck.getCardOrNone(cardIndex)
            playedCards = self.getPlayedCards(card.getColor())

            print("%d번 플레이어가 %s 카드를 냈습니다." % (self.currentPlayerIndex, card))       # DEBUG
            if card.getNumber() - 1 == len(playedCards):        # 해당색의 카드를 카드를 줄지어 낼 수 있는 경우
                playedCards.append(card)
                print("Play 성공!")       # DEBUG
            else:
                discardedCards = self.getDiscardedCards(card.getColor())
                discardedCards.append(card)
                print("Play 실패! 라이프 토큰이 하나 감소합니다.")  # DEBUG
                self.decreaseLifeToken()

            playerDeck.useCard(cardIndex)

            if self.isGameEnd():
                return

            if not self.isCardsEmpty():
                self.giveOneCard(self.currentPlayerIndex)
                print("%d번 플레이어가 새로운 카드를 받았습니다." % self.currentPlayerIndex)       # DEBUG
            else:
                if self.lastPlayerIndex < 0:
                    self.lastPlayerIndex = self.currentPlayerIndex
                    print("카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다." % (self.currentPlayerIndex - 1))      # DEBUG

        elif action.getActionType() == 2:         # 버리기   (Discard)
            playerDeck = self.playerDecks[self.currentPlayerIndex]
            cardIndex = action.getCardIndex()


    def doActionDiscard(self, action: Action):
        """
        카드 버리기 Action 을 수행하는 함수
        :param action: 수행할 action. type 은 무조건 2이어야 한다.
        """
        assert action.getActionType() == 2, "<discard> must be action type 2"

        playerDeck = self.playerDecks[self.currentPlayerIndex]
        cardIndex = action.getCardIndex()


        card = playerDeck.getCardOrNone(cardIndex)
        discardedCardCounter = self.getDiscardedCardCounter(card.getColor())
        discardedCardCounter[card.getNumber()] += 1
        self.increaseHintToken()

        print("%d번 플레이어가 %s 카드를 버렸습니다." % (self.currentPlayerIndex, card))  # DEBUG
        print("힌트 토큰이 하나 증가합니다.(8 이상이면 증가하지 않음)")  # DEBUG
        playerDeck.useCard(cardIndex)
        if not self.isCardsEmpty():
            self.giveOneCard(self.currentPlayerIndex)
            # print("%d번 플레이어가 새로운 카드를 받았습니다." % self.currentPlayerIndex)  # DEBUG
            if self.isCardsEmpty():
                if self.lastPlayerIndex < 0:
                    self.lastPlayerIndex = self.currentPlayerIndex
                    print("카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다." % (self.currentPlayerIndex - 1))      # DEBUG

        elif action.getActionType() == 3:         # 힌트주기
            targetIndex = action.getTargetIndex()
            assert targetIndex is not self.currentPlayerIndex
            correspondedIndexes = []

            for i in range(4):
                card = self.playerDecks[targetIndex].getCardOrNone(i)
                if card is not None:
                    if card.isCorrespondedHint(action.getHint()):
                        correspondedIndexes.append(i)

            self.decreaseHintToken()
            self.deliverHintToUI(action.getHint(), targetIndex, correspondedIndexes)

    def deliverHintToUI(self, hint: Hint, targetIndex: int, cardIndexes: list):
        # 힌트를 받은 내용을 UI에게 넘겨주는 함수
        # 구체적인 구현 내용은 아직 미정.

        assert len(cardIndexes) is not 0, "invalid hint"
        if hint.isNumber():
            hintString = "숫자 %d" % hint.info
        else:
            if hint.info is "R":
                hintString = "빨간색"
            elif hint.info is "G":
                hintString = "초록색"
            elif hint.info is "B":
                hintString = "파란색"
            elif hint.info is "W":
                hintString = "하얀색"
            else:
                hintString = "노란색"

        if len(cardIndexes) == 0:
            print("%d번 플레이어의 힌트: %d번 플레이어의 %s 카드는 없습니다."
                  % (self.currentPlayerIndex, targetIndex, hintString))

        else:
            print("%d번 플레이어의 힌트: %d번 플레이어의 %s번째 카드는 %s 입니다."
                  % (self.currentPlayerIndex, targetIndex, str(cardIndexes), hintString))

        print("힌트 토큰이 하나 감소합니다.")

    def calculateScore(self):
        # 점수 계산
        score = len(self.__redPlayedCards) + len(self.__greenPlayedCards) + len(self.__bluePlayedCards) + len(self.__whitePlayedCards) + len(self.__yellowPlayedCards)
        return score

    def canHint(self):
        # 힌트를 사용 가능한지
        return self.__hintToken is not 0

    def onGameEnd(self):
        # 실제론 이 함수에서 UI랑 서버쪽에 게임이 끝났다 알려야 할듯?
        print()
        print("***** 게임 종료! 최종점수: %d점 ******" % self.calculateScore())

    def checkCommend(self,data):
        while True:
            if data[0:2] == '//':
                return

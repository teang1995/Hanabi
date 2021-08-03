from Game.GameElements import Action as Action
from Game.GameElements import PlayerDeck as PlayerDeck


# 시작버튼을 누르면 서버에서 게임 시작시 정보를 받아 게임매니저를 생성하고 게임이 시작된다.
class GameManager:

    def __init__(self, cards: list, clientIndex: int, beginnerIndex: int):
        self.playerDecks = [PlayerDeck() for i in range(4)]
        self.clientIndex = clientIndex
        self.currentPlayerIndex = beginnerIndex
        self.lastPlayerIndex = -1
        self.id = "teang1995"
        self.__hintToken = 8
        self.__lifeToken = 3
        self.__bTurnOver = False

        self.cards = cards

        self.__redPlayedCards = []
        self.__greenPlayedCards = []
        self.__bluePlayedCards = []
        self.__whitePlayedCards = []
        self.__yellowPlayedCards = []
        self.__playedCardDict = {
            'R': self.__redPlayedCards,
            'G': self.__greenPlayedCards,
            'B': self.__bluePlayedCards,
            'W': self.__whitePlayedCards,
            'Y': self.__yellowPlayedCards
        }

        # self.<COLOR>discardedCardCounter = [COLOR, 1_cnt, 2_cnt, 3_cnt, 4_cnt, 5_cnt]
        self.__redDiscardedCardCounter = ['R', 0, 0, 0, 0, 0]
        self.__greenDiscardedCardCounter = ['G', 0, 0, 0, 0, 0]
        self.__blueDiscardedCardCounter = ['B', 0, 0, 0, 0, 0]
        self.__whiteDiscardedCardCounter = ['W', 0, 0, 0, 0, 0]
        self.__yellowDiscardedCardCounter = ['Y', 0, 0, 0, 0, 0]
        self.__discardedCardCounterDict = {
            'R': self.__redDiscardedCardCounter,
            'G': self.__greenDiscardedCardCounter,
            'B': self.__blueDiscardedCardCounter,
            'W': self.__whiteDiscardedCardCounter,
            'Y': self.__yellowDiscardedCardCounter
        }

    def isCardsEmpty(self):
        # 카드더미가 비었는지 확인하는 함수
        return len(self.cards) == 0

    def isGameEnd(self):
        return self.__bTurnOver or self.__lifeToken is 0

    def giveOneCard(self, playerIndex: int):
        """
        카드더미 맨 위에서 카드를 뽑아 플레이어에게 주는 함수. isCardEmpty로 카드를 줄 수 있는지 검증하고 호출할 것
        :param playerIndex: 카드르 받을 플레이어의 색인
        """
        assert not self.isCardsEmpty(), "cannot give card when have no cards"
        card = self.cards[0]
        del self.cards[0]  # pop()을 쓰면 한줄로 줄일 수도 있다.
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

    def nextTurn(self):
        """
        do Action 호출 후 다음 턴을 진행하는 함수
        :return: 게임이 끝났으면 True, 아니면 False를 반환.
        """
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % 4
        if self.lastPlayerIndex == self.currentPlayerIndex:
            self.__bTurnOver = True
        return self.isGameEnd()

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
        return self.__playedCardDict[color]

    def getDiscardedCardCounter(self, color: str):
        assert color == "R" or color == "G" or color == "B" or color == "W" or color == "Y", "invalid card color"
        return self.__discardedCardCounterDict[color]

    def getDiscardedCardCounterDict(self):
        return self.__discardedCardCounterDict

    def doAction(self, action: Action):
        """
        (구) Action 을 수행하는 함수
        기존 CUI 테스트 코드를 유지하기 위해 남겨둔 상태. 현재는 각 Action 별로 함수가 작성되어 있다.
        :param action: 수행할 동작
        :return: 각 Action 을 처리하는 함수의 return 값을 반환한다. 즉 actionType을 점검하지 않으면 어떤 return 값을 가지는지
                 확신할 수 없으니 주의할 것. 반환 값이 있을 수도 있고 없을 수도 있다.
        """

        if action.getActionType() == 1:  # 카드내기 (Play)
            return self.doActionPlay(action)
        elif action.getActionType() == 2:  # 버리기   (Discard)
            self.doActionDiscard(action)
        elif action.getActionType() == 3:  # 힌트주기
            return self.doActionHint(action)

    def doActionPlay(self, action: Action):
        """
        카드내기 Action 을 수행하는 함수
        :param action: 수행할 action. type 은 무조건 1이어야 한다.
        :return: play 에 성공했는지 여부를 반환한다. 카드를 내는데 성공하면 True, 실패하면 False
        """
        assert action.getActionType() == 1, "<play> must be action type 1"

        playerDeck = self.playerDecks[self.currentPlayerIndex]
        cardIndex = action.getCardIndex()

        card = playerDeck.getCardOrNone(cardIndex)
        playedCards = self.getPlayedCards(card.getColor())

        print("%d번 플레이어가 %s 카드를 냈습니다." % (self.currentPlayerIndex, card))  # DEBUG
        if card.getNumber() - 1 == len(playedCards):  # 해당색의 카드를 카드를 줄지어 낼 수 있는 경우
            playedCards.append(card)
            didPlay = True
            print("Play 성공!")  # DEBUG
        else:
            discardedCardCounter = self.getDiscardedCardCounter(card.getColor())
            discardedCardCounter[card.getNumber()] += 1
            print("Play 실패! 라이프 토큰이 하나 감소합니다.")  # DEBUG
            self.decreaseLifeToken()
            didPlay = False

        playerDeck.useCard(cardIndex)
        if self.isGameEnd():
            return

        if not self.isCardsEmpty():
            self.giveOneCard(self.currentPlayerIndex)
            # print("%d번 플레이어가 새로운 카드를 받았습니다." % self.currentPlayerIndex)  # DEBUG
            if self.isCardsEmpty():
                if self.lastPlayerIndex < 0:
                    self.lastPlayerIndex = self.currentPlayerIndex
                    # print("카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다." % (self.currentPlayerIndex - 1))  # DEBUG

        return didPlay

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
                    # print("카드가 전부 떨어졌습니다. 다음 %d번 플레이어의 차례를 마치면 게임이 끝납니다." % (self.currentPlayerIndex - 1))  # DEBUG

    def doActionHint(self, action: Action):
        """
        힌트주기 Action 을 수행하는 함수
        :param action: 수행할 action. type 은 무조건 3이어야 한다.
        :return: 힌트: Hint, 힌트 대상 인덱스: int, 힌트에 해당하는 카드 인덱스 리스트: List
        """
        assert action.getActionType() == 3, "<hint> must be action type 3"

        targetIndex = action.getTargetIndex()
        assert targetIndex is not self.currentPlayerIndex
        correspondedIndexes = []

        for i in range(4):
            card = self.playerDecks[targetIndex].getCardOrNone(i)
            if card is not None:
                if card.isCorrespondedHint(action.getHint()):
                    correspondedIndexes.append(i)

        self.decreaseHintToken()
        return action.getHint(), correspondedIndexes

    def calculateScore(self):
        # 점수 계산
        score = len(self.__redPlayedCards) + len(self.__greenPlayedCards) + len(self.__bluePlayedCards) + len(
            self.__whitePlayedCards) + len(self.__yellowPlayedCards)
        return score

    def canHint(self):
        # 힌트를 사용 가능한지
        return self.__hintToken is not 0

class Hint:
    HINT_INFO = [1, 2, 3, 4, 5, 'R', 'G', 'B', 'W', 'Y']
    HINT_STRING_DICT = {
        1: '1번',
        2: '2번',
        3: '3번',
        4: '4번',
        5: '5번',
        'R': '빨강색',
        'G': '초록색',
        'B': '파랑색',
        'W': '하양색',
        'Y': '노랑색'
    }

    def __init__(self, info):
        """
        :param info: 색과                                                            힌트. 문자열 혹은 숫자를 받을 수 있도록 자료형을 명시하지 않았음
        """
        assert info == "R" or info == "G" or info == "B" or info == "W" or info == "Y" \
            or info == 1 or info == 2 or info == 3 or info == 4 or info == 5, "invalid card information"

        self.info = info

    def isNumber(self):
        return type(self.info) == int

    def isColor(self):
        return type(self.info) == str
    
    def __str__(self):
        return "%s" % str(self.info)

    def getHintString(self):
        return Hint.HINT_STRING_DICT[self.info]


class Card:

    def __init__(self, color: str, number: int):
        """
        :param color: 카드의 색
        :param number: 카드의 숫자
        """
        assert color == "R" or color == "G" or color == "B" or color == "W" or color == "Y", "invalid card color"
        assert 1 <= number <= 5, "invalid card number"
        self.__color = color
        self.__number = number

    def getColor(self):
        return self.__color

    def getNumber(self):
        return self.__number

    def isCorrespondedHint(self, hint: Hint):
        return self.__color == hint.info or self.__number == hint.info
    
    def __str__(self):
        return "%s%d" % (self.__color, self.__number)

    def __repr__(self):
        return self.__str__()
        # return "Card(\"%s\", %d)" % (self.__color, self.__number)


class Action:
    # 플레이어의 선택에 따른 행동의 정보를 표현하는 클래스.
    def __init__(self, actionType: int, element, targetIndex: int = -1):
        """
        :param actionType: Action의 타입을 의미 1-내려놓기 / 2-버리기 / 3-힌트주기
        :param element: 내고자 하는 카드의 색인(1,2 cardIndex: int), 힌트 객체(3 hint: Hint)
        :param targetIndex: 힌트를 받을 플레이어의 색인(3)
        """
        assert 1 <= actionType <= 3, "invalid action type"

        self.__actionType = actionType

        if actionType == 3:
            assert type(element) == Hint, "invalid element. Element should be Hint class when actionType is 3"
            self.__hint = element
            self.__targetIndex = targetIndex
        else:
            assert type(element) == int, "invalid element.Element should be integer when actionType is 1 or 2"
            assert 0 <= element <= 3, "invalid card index."
            self.__cardIndex = element

    def getActionType(self):
        return self.__actionType

    def getCardIndex(self):
        # getActionType()을 통해 메소드를 호출 할 수 있는지 확인하고 호출 할 것
        assert self.__actionType != 3
        return self.__cardIndex

    def getTargetIndex(self):
        # getActionType()을 통해 메소드를 호출 할 수 있는지 확인하고 호출 할 것
        assert self.__actionType == 3
        return self.__targetIndex

    def getHint(self):
        # getActionType()을 통해 메소드를 호출 할 수 있는지 확인하고 호출 할 것
        assert self.__actionType == 3
        return self.__hint


class PlayerDeck:
    """
    플레이어의 카드 덱을 관리하는 클래스이다.
    직접 게임 진행에 관여하지 않고 덱의 상태만을 주관한다.
    """

    def __init__(self):
        self.__cards = [0, 0, 0, 0]

    def getCardOrNone(self, index: int):
        """
        :param index: 카드 위치. 범위는 0~3
        :return: 지정된 위치의 Card를 반환. 해당 위치에 카드가 없는 경우(0인 경우) None을 반환함
        """
        assert 0 <= index <= 3, "invalid card index"

        if self.__cards[index] == 0:
            return None
        return self.__cards[index]

    def useCard(self, index: int):
        """
        카드 내기, 버리기 Action을 수행할 때 카드를 사용하는 함수
        :param index:카드 위치. 범위는 0~3
        :return: 카드를 사용하는데 성공하면 True, 실패했다면 False
        """
        assert 0 <= index <= 3, "invalid card index"

        if self.__cards[index] == 0:
            return False

        self.__cards[index] = 0
        return True

    def addCard(self, card: Card):
        """
        덱의 빈 자리에 카드를 추가하는 함수. 이 함수를 호출하기 전 isDeckFull()을 호출하여 덱에 여유가 있는지 미리 검증되어야 한다.
        :param card: 추가할 카드
        """
        assert not self.isDeckFull(), "cannot add card. cause deck is full"
        for i in range(4):
            if self.__cards[i] == 0:
                self.__cards[i] = card
                break

    def isDeckFull(self):
        for i in range(4):
            if self.__cards[i] == 0:
                return False
        return True
    
    def __str__(self):
        return "%2s|%2s|%2s|%2s" % (self.__cards[0], self.__cards[1], self.__cards[2], self.__cards[3])



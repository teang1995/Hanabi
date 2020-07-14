# [하나비] 이력

2020.06.26 Assemble

2020.07.11 역할 분담 완료 
|GUI|SERVER|LOGIC(GAME)|총괄|
|---|---|---|---|
|임용택, 최현진|우진영, 임용택|문영빈, 조시호|임용택, 조시호|


# [하나비] 코딩 표준
=============

본 문서는 하나비 프로젝트 공동 작업에서 일관된 코드 작성을 위한 파이썬 코딩 규칙이 담김. 그다지 많은 경우를 고려하지 않았기에 부족한 내용이 많으니 이해되지 않는 부분이있거나 추가할 법한 내용이 있다면 언제든지 이야기 해주길 바람.   

History 
* 2020.07.14 초안 작성 - 조시호

참고한 문서
* [PEP 8 — Style Guide for Python Code | Python.org](https://www.python.org/dev/peps/pep-0008/))
* [Bites of Code: PyQt Coding Style Guidelines](http://bitesofcode.blogspot.com/2011/10/pyqt-coding-style-guidelines.html)


## 기본 규칙
1. 코드의 가독성을 최우선한다.
2. 기본적인 들여쓰기 및 공백 여부는 IDE(파이참)의 자동 서식을 따른다. (Ctrl + Alt + l) 아래 공백과 관련된 항목 대부분 자동서식으로 해결된다.
3. 문제가 있는 상황에서 최대한 빨리 크래시가 나도록 하여 프로그램이 계속 동작하지 않게 한다. (이에 대한 설명은 다음 오프라인 모임에서 설명)


## 이름 짓기
1. 변수, 함수, 클래스 등 모든 이름은 그 의미를 알 수 있도록 지어야 한다. 의미가 없거나 한 글자로된 변수는 피해야 한다. 단, 반복문 등에서 사용하는 i, j 와 같은 단순 일회성 변수들은 허용한다.
2. 변수, 함수(메소드) 이름은 단어의 시작을 대문자로 하여 구분하되 첫 단어의 시작은 소문자를 사용한다.(캐멀 표기법)
``` python
cardListIndex = 5;
def canAttackTo():
    pass

# 약어 또한 첫 시작만 대문자, 나머지는 소문자이다.
myHTTPPort = 80      # 잘못된 변수명
- myHttpPort = 80      # 올바른 변수명
```
3. 상수로 사용하고자 하는 변수는 전부 대문자를 사용하고 언더바를 통해 단어를 구분한다.
``` python
TOTAL_CARD_NUM = 52
```
4. 클래스 이름은 파스칼 표기법을 따른다.(캐멀 표기법 + 첫단어 또한 대문자로 시작)
``` python
class SimulationManager:
    pass
```
5. 함수는 동사로 시작한다.
``` python
def move():
    pass

def playGame():
    pass
```
6. bool 자료형 변수명은 아래  [링크](https://soojin.ro/blog/naming-boolean-variables) 를 참조하여 작성한다.
7. 전역 변수는 위 규칙들과 동일하나 맨 앞에 GLOBAL을 붙인다.(ex) GLOBALcardDeck)


## 주석
1. 기본적으로 현재 코드 위치의 들여쓰기를 따른다.
``` python
# 이 반복문은
for i in range(10):
    # i가 짝수일 때
    if i % 2 == 0:
        # i를 출력합니다.
        print(i)
```
2. 한 줄 주석 사용시 # 뒤로 한칸의 공백을 두고 작성한다.
3. 인라인 주석(코드 바로 뒤에 이어지는 주석)을 작성 할 시 기존 코드에서 최소 두 개의 탭으로 공백을 두고 작성한다.
``` python
x = 3 # 이렇게 딱 붙이지 않고
y = 4      # 어느정도 여유를 두자
```
4. 코드 그대로 의미를 파악 할 수 있다면 굳이 주석을 달지 않는 것이 좋다. 과도한 주석은 코드의 가독성을 해칠 수 있다.

5. 함수 선언 시, 함수 선언 아래 매개변수와 반환값에 대해 주석으로 서술한다. (파이참의 경우 함수명 아래에 ''' '''를 입력하면 자동으로 틀을 생성해줌.)

``` python
def TestForRemark(num1, num2, num3):
    '''
    :param num1:
    :param num2:
    :param num3:
    :return:
    '''
```

## 들여쓰기 및 공백
1. 함수의 끝과 새로운 함수 사이에 2칸 이상의 공백을 둔다.
2. 수식을 사용 할 떄는 공백을 두어 연산자와 피연산자가 확실히 구분되도록 한다.
``` python
result=3+5      # 잘못된 예
result = 3 + 5   # 올바른 예
```
3. 쉼표 이후엔 공백을 두어 이후 열거되는 요소를 확실히 구분되도록 한다.
``` python
myList = [1,a,2,b,3,c]         # 잘못된 예
myList = [1, a, 2, b, 3, c]      # 올바른 예
```
4. 함수 호출, 인덱싱 등에서 시작 괄호를 열기 전에 공백을 두지 않는다.
``` python
# 잘못된 예
myList [3]
doSomething ()

# 올바른 예
myList[3]
doSomething()
```
5. 다른 코드와 줄 맞춤을 위해 연산자 주위로 공백을 두지 않는다.
``` python
# 안좋은 예
x =         3
y         = 9
cardIndex = 4
```


## 기타
1. 문자열은 큰 따옴표를 사용한다.
2. if, for, while문에서 조건식과 몸체를 한 줄에 작성하는 것은 허용하나 여러줄에 걸쳐 나타나지 않도록 주의하도록 한다.
``` python
if x > 0: doSomething()      # 혼자 쓰는건 괜찮다.

if x > 0: doSomething()
for i in list1: doSomething1()
for i in list2: doSomething2()      # 이렇게 연달아 쓰지만 말 것
```
3. import시 * 를 통해 전부를 가져오는 것이 아닌 사용하고자 하는 요소를 확실하게 명시하도록 한다.
4. import는 한 줄에 한 요소만 작성한다.
5. 함수 선언 시, 매개변수의 자료형에 대해 명시한다.

``` python
def TestForStateDataType(num1: int, num2, num3):
    num1 = num1[:]
    '''
    :param num1:
    :param num2:
    :param num3:
    :return:
    '''
    return num1


TestForStateDataType('a', 3, 4)      #이와 같이 사용시 'a'에서 warning을 확인할 수 있다.
```
6.시호는 천재니깐 시호 말을 다 듣는다.

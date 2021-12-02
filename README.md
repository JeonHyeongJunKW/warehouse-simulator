# warehouse-simulator
물류로봇 시물레이션과 Dynamic TSP를 구현하기 위해서 개발되었습니다.

### 업데이트 현황 
0.1 : 기본 시물레이션 및 시각화 코드 

추가 계획 : 
- 중간에 노드 추가 기능 넣어두기
- 각 알고리즘을 동시에 돌려서 비교할 수 있게 하기 
- 로봇간에 경로회피 알고리즘 추가하기



달성한 것:
- 선반간 이동경로를 A*star로 찾기(현재 대각선 이동도 가능)(v)
- 선반의 경로 대신에 선반에 할당된 노드들 표시하기(v)
- 남아있는 주문 GUI에 넣기(v)
- tsp 알고리즘 추가 및 고를 수 있게 해두기(v)
- ACO(v)
- 유전알고리즘
- PSO
- 로봇의 이전경로 보여주기(v)
- 아이템 추가가 아닌 주문량 수정(v)
- 패킹지점에 따른 색깔표시 다르게 하기(v)
- 맵 사이즈 전반적으로 키우기(v)
- 로봇의 전체경로 보여주기(v)

# 동적 시뮬레이션 영상 
## 시뮬레이션 영상

<p align="center"> <img width="60%"  src="https://user-images.githubusercontent.com/63538314/143274558-39752f06-0fc3-4e96-8a86-a97a4a3cb544.gif"   /></p>

## 알고리즘별 결과 출력 영상

<p align="center"> <img width="60%" height="20%"  src="https://user-images.githubusercontent.com/63538314/143274699-f87d4fc0-ccce-4078-af67-c2243f49cbbe.gif" /></p>

### 알고리즘 출력결과


### 시물레이션 목적
- 주문을 할당 받은 멀티 로봇의 최적 동선 스케줄링
- 기존 방식(order grouping과 robot sceduling)에서 Task allocation<sup>[1](#footnote_1)</sup>과 Task sequencing<sup>[2](#footnote_2)</sup> 구조로 개선 

### 문제 정의 
- j개의 아이템으로 이루어진 i개의 주문이 동시에 들어옴 : i = 약 1000개
- 로봇이 한 번에 k개의 주문을 처리 가능할 때, 어떤주문을 할당할 것인가.



### 시물레이션의 초기 환경정의 
- 로봇 : 포인트 모델(기구학 고려 x)
- 2D grid world map
- 5 action : up, down, left, right, idle
- 각 그리드 이동 방식을 directed 와 undirected 중에서 고를 수 있다.


### 시물레이션 구현의 차후 목표
- 맵(물류환경)의 생성, 저장 및 선택이 가능해야한다.
- 로봇의 구동방식이나 크기등의 선정이 자유로워야한다.
- 시물레이션의 방식(기구학 고려)이 선택 가능해야한다. 
- 확장성을 가질 수 있게한다. 


### 구현방식
- 파이썬 기반의 시물레이션 구현
- PyQT5 라이브러리를 이용하여, 시각적으로 시물레이션을 생성 및 실행  

## 사용방법
### 기본실행 
 - main.py를 빌드하여 실행합니다. 
 
### 맵 확인하기 
- 실행 후, '맵 생성 및 확인하기' 버튼을 누르면, '맵 생성도구' 창이 나옵니다. 
- 이때, '맵불러오기'를 누르면, 만들어진 맵을 확인할 수 있습니다. 현재 샘플 맵(saved_map.json)은 Map폴더에 저장되어있습니다.  
- 불러온 맵의 resolution이나 크기는 바꾸면 안되지만, 그외에 벽, 선반, 패킹 지점, 시작 지점은 추가 및 삭제후, 다시 저장할 수 있습니다.  
- 초록색은 선반을 나타내며, 2*3짜리 크기의 선반이 기본적으로 2개씩 붙어있습니다.
- 파란색은 패킹 지점을 나타내며, 모바일로봇이 재고들을 가지고 오는 장소입니다. 
- 빨간색은 시작 지점이며, 모바일로봇이 맨처음 시작하고, 패킹장소에 재고들을 두고 다시 돌아오는 곳입니다. 
- x표시로 된 블럭은 벽을 의미합니다.  
- 닫기버튼을 눌러서 '맵 생성도구'창을 나갈 수 있습니다.

### 맵 생성하기
- 실행 후, '맵 생성 및 확인하기' 버튼을 누르면, '맵 생성도구' 창이 나옵니다. 
- 가로크기와 세로크기를 조정하여, 맵사이즈를 바꿀 수 있습니다.(직접 입력하거나, 슬라이더바를 조정가능)
- 가로 분해능과 세로 분해능을 조정하여, 맵의 분해능을 바꿀 수 있습니다.(직접 입력하거나, 슬라이더바를 조정가능)
- 위의 두가지를 모두 골랐다면, '맵 크기, 분해능 저장' 버튼을 누릅니다.(한번 바꾼 사이즈는 변경할 수 없습니다.)
- 이후에 선반의 '가로크기','세로크기', '아이템수', '단면 선반 여부'등을 고른 후에, '선반 생성하기'버튼을 눌러서 만들어진 맵에 선반을 배치할 수 있습니다. 
- 배치간에 키보드에 R버튼을 누르면 선반의 방향이 돌아갑니다.
- 만약에 잘못 둔 선반이 있다면 '선반 수정하기'버튼을 누르고, 잘못된 선반을 클릭후에, 키보드 Delete버튼을 누르면 해당 선반이 없어집니다.  
- '선반 다시만들기' 버튼을 누르면, 다시 벽, 선반, 패킹 지점, 시작 지점중에서 추가할 수 잇습니다. 
- 나머지 벽, 패킹, 시작 지점은 resolution으로 정해진 격자 사이즈로 크기가 정해집니다. 그외에 추가 및 삭제는 선반배치와 동일합니다.
- 완성이 다되었다면, 맵 저장하기를 눌러서, json형식으로 저장합니다. 

### 맵 정하기 
- 실행 후, '맵 불러오기' 버튼을 누르면, 시물레이션 맵으로 설정됩니다. 

### 추가내역 
- 21-11-21 Dynamic tsp와 online order picking을 위한 시뮬레이션 추가
- 21-11-23 GUI추가 및 파라미터 조정파트 생성. 큰버그 수정
- 21-11-23 : 다양한 결과보는 부분 추가. 아직 조정필요
- 21-11-28 : Queue에서 batch를 생성하는경우에는 bound를 개선, 만료시간을 빠르게하여 지연되는것을 방지.
- 21-12-02 : 에러수정, 2차원 공유변수 일부수정

<a name="footnote_1">[1] Task allocation </a>: 비슷한 작업을 묶어서 멀티 로봇에게 실시간으로 작업을 분배 

<a name="footnote_2">[2] Task sequencing</a>: 실시간으로 로봇이 방문해야하는 지점이 달라지는 경우에도 최적의 경로를 찾아내는 Dynamic TSP문제해결

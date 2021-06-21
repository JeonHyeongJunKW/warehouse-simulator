# warehouse-simulator
물류로봇 시물레이션과 Dynamic TSP를 구현하기 위해서 개발되었습니다.
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

<a name="footnote_1">[1] Task allocation </a>: 비슷한 작업을 묶어서 멀티 로봇에게 실시간으로 작업을 분배 

<a name="footnote_2">[2] Task sequencing</a>: 실시간으로 로봇이 방문해야하는 지점이 달라지는 경우에도 최적의 경로를 찾아내는 Dynamic TSP문제해결

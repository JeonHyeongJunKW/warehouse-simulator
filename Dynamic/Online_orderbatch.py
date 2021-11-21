from Dynamic.DEBUG_tool import DEBUG_log,DEBUG_log_tag

def online_order_batch_FIFO(readonly_orders, init_batch_size, max_batch_size, readonly_current_robot_batch):
    #로봇들이 기본적인 할당량을 가지고 있는지 확인하고,
    solved_orders_index = []
    solved_batches = readonly_current_robot_batch  # 최종적으로 할당된 배치들
    changed_robot_index = []  # 배치가 바뀐 로봇의 인덱스
    assigned_flag = [False for _ in range(len(readonly_current_robot_batch))]#초기할당이라면 order를 추가할당하지 않습니다.
    #1. init_batch이하인 로봇들의 배치를 가져온다. 더이상 남은 order가 없다면 리턴, 있다면 FIFO방식으로 할당


    start_order = 0
    for robot_index, robot_batch in enumerate(readonly_current_robot_batch):

        if len(readonly_orders) < init_batch_size:
            return solved_orders_index,solved_batches,changed_robot_index

        if len(robot_batch) ==0:
            #order를 할당합니다.
            solved_batches[robot_index] = readonly_orders[start_order:start_order+init_batch_size]
            DEBUG_log_tag("초기 주문 수", len(solved_batches[robot_index]), "VERY_DETAIL")
            DEBUG_log_tag("초기 주문", solved_batches[robot_index], "VERY_DETAIL")
            DEBUG_log_tag("초기 배치 사이즈", init_batch_size, "VERY_DETAIL")
            changed_robot_index.append(robot_index)#바뀐 로봇 배치를 기록합니다.
            solved_orders_index = solved_orders_index + list(range(start_order, start_order+init_batch_size,1))
            start_order += init_batch_size#새롭게 할당할 때 사용할 start_order를 수정합니다.
            assigned_flag[robot_index] = True

    # 2. max_batch_size이하인 로봇들의 배치를 가져온다. 더이상 남은 order가 없거나 로봇들이 전부 max_batch_size 이상이라면 리턴, 있다면 FIFO방식으로 할당
    additional_orders_number =max_batch_size-init_batch_size
    for robot_index, robot_batch in enumerate(readonly_current_robot_batch):

        if assigned_flag[robot_index]:
            continue

        if len(readonly_orders) < additional_orders_number:
            return solved_orders_index, solved_batches, changed_robot_index

        if len(robot_batch) < max_batch_size:
            solved_batches[robot_index] += readonly_orders[start_order:start_order+additional_orders_number]

            changed_robot_index.append(robot_index)  # 바뀐 로봇 배치를 기록합니다.
            solved_orders_index = solved_orders_index + list(range(start_order, start_order + additional_orders_number, 1))
            start_order += additional_orders_number  # 새롭게 할당할 때 사용할 start_order를 수정합니다.
    DEBUG_log("\n--------------------\n","DETAIL")
    DEBUG_log("남은 주문수", "SIMPLE")
    DEBUG_log(len(readonly_orders), "SIMPLE")
    DEBUG_log("처리되어야하는 주문들", "VERY_DETAIL")
    DEBUG_log(solved_orders_index[0:5],"VERY_DETAIL")

    DEBUG_log("바뀐 배치들 일부 ", "VERY_DETAIL")
    DEBUG_log(solved_batches[0:1],"VERY_DETAIL")
    DEBUG_log("바뀐로봇들 일부", "DETAIL")
    DEBUG_log(changed_robot_index[0:1],"DETAIL")

    return solved_orders_index,solved_batches,changed_robot_index

def online_order_batch(orders, item_position, init_batch_size, max_batch_size, current_robot_batch):
    '''
    ********************************************************************
    ******************************Input*********************************
    ********************************************************************
    -------------------------------------------------------------------
     orders,
        - 자료형 : 2차원 list,
        - 설명 : 1차원 list 자료형의 새로들어온 order를 가지고 잇음.
                각각의 order는 int 자료형의 item(물품)을 가지고 있다.
     ex) 1,2,3 item들을 가진 order와 2,3,4 item들을 가진 order가 있을때
     orders  -> [[1,2,3], [2,3,4]]
     -------------------------------------------------------------------
     item_position,
        - 자료형 : 2차원 list,
        - 설명 : 1차원 list 자료형으로 아이템들의 위치 좌표(x, y)를 가지고 있다.
                각 아이템에 위치는 다음과같이 찾을 수 있다.
     ex) k item의 위치를 찾는다면
     k item의 위치(좌표) -> item_position[k] , k item의 x 좌표 -> item_position[k][0], k item의 y 좌표 -> item_position[k][1]
     --------------------------------------------------------------------
    init_batch_size,
        - 자료형 : int
        - 설명 : 초기 batch가 가질 수 있는 최대 item 수
    ---------------------------------------------------------------------
    max_batch_size,
        - 자료형 : int
        - 설명 : online order batch간에 로봇이 가질 수 있는 최대 item 수
    ---------------------------------------------------------------------
    current_robot_batch,
        - 자료형 : 2차원 list
        - 설명 : online order batch간에 로봇들이 현재 가진 batch
                특정 로봇에게 batch가 할당이 되었다면, 할당된 batch로 채워져있다.
                특정 로봇에게 batch가 할당이 안되있다면,[]로 채워져있다.

    ex) 현재 4개의 로봇중에서 , 0번과 2번에게만 batch([1,2,3]과 [2,4,5])가 각각 할당되어있다면
    current_robot_batch =  [[1,2,3],[],[2,4,5],[]]
    ---------------------------------------------------------------------
    ********************************************************************
    ******************************Output********************************
    ********************************************************************
    return_robot_batch,
        - 자료형 : 2차원 list,
        - 설명 : 인자로 준 orders에서 batch로 묶은 결과를 로봇에게 할당한 결과
    ---------------------------------------------------------------------
    remain_order,
        - 자료형 : 2차원 list,
        - 설명 : 인자로 준 orders에서 batch로 묶은 결과를 로봇에게 할당하고 남은 order의 집합
    ---------------------------------------------------------------------

    ex) A = [1, 2, 3] / B = [4, 5, 6]  / C = [1, 2, 4] / D = [1, 7, 5] 을 가지는 order에 대해서
    init_batch_size가 6이고, max_batch_size = 12라면, current_robot_batch를 고려하여 다음과 같이 만든다.

    (입력)
    orders = [[1, 2, 3],[4, 5, 6],[1, 2, 4],[1, 7, 5]]
    init_batch_size = 6
    max_batch_size = 12
    current_robot_batch =  [[1,2,3],[],[2,4,5],[]]



    (출력)
    return_robot_batch =  [[1, 2, 3, 1, 2, 3, 1, 2, 4], [], [2, 4, 5, 4, 5, 6],[]]
    remain_order = [[1, 7, 5]]

    '''
    return_robot_batch = []
    remain_order = []

    #todo

    return return_robot_batch, remain_order
from Dynamic.DEBUG_tool import DEBUG_log,DEBUG_log_tag
import copy
def online_order_batch_FIFO(readonly_orders, init_batch_size, max_batch_size, robot_data):
    #로봇들이 기본적인 할당량을 가지고 있는지 확인하고,
    solved_orders_index = []
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])#현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch  # 현재의 로봇배치
    changed_robot_index = []  # 배치가 바뀐 로봇의 인덱스
    assigned_flag = [False for _ in range(len(readonly_current_robot_batch))]#초기할당이라면 order를 추가할당하지 않습니다.
    #1. init_batch이하인 로봇들의 배치를 가져온다. 더이상 남은 order가 없다면 리턴, 있다면 FIFO방식으로 할당


    start_order = 0
    for robot_index, robot_batch in enumerate(readonly_current_robot_batch):

        if len(readonly_orders)-start_order < init_batch_size:
            # print("남은게 없어..")
            return solved_orders_index,solved_batches,changed_robot_index
        #큰일날 수 있는부분..
        if len(robot_batch) ==0:
            #order를 할당합니다.
            solved_batches[robot_index] = readonly_orders[start_order:start_order+init_batch_size]#현재 order들에서 일정그룹만을 가져와서 넣습니다.
            # print("현재 잔존량", readonly_orders)
            changed_robot_index.append(robot_index)#바뀐 로봇 배치를 기록합니다.
            solved_orders_index = solved_orders_index + list(range(start_order, start_order+init_batch_size,1))
            # print("없애버릴 주문 인덱스", list(range(start_order, start_order+init_batch_size,1)))
            start_order += init_batch_size#새롭게 할당할 때 사용할 start_order를 수정합니다.
            assigned_flag[robot_index] = True

    # 2. max_batch_size이하인 로봇들의 배치를 가져온다. 더이상 남은 order가 없거나 로봇들이 전부 max_batch_size 이상이라면 리턴, 있다면 FIFO방식으로 할당
    additional_orders_number =max_batch_size-init_batch_size#추가할 수 있는 배치량
    for robot_index, robot_batch in enumerate(readonly_current_robot_batch):

        if assigned_flag[robot_index]:
            continue
        if len(readonly_orders[start_order:]) ==0: #만약에 이제 더넣을 게 없다 그냥 끝내
            return solved_orders_index, solved_batches, changed_robot_index

        if len(readonly_orders[start_order:]) < additional_orders_number:#주문의 수가 추가할 수 있는 배치량보다 적을때,
            #앞으로 더넣을 수 있는 order들이
            solved_batches[robot_index] += readonly_orders[start_order:]#그냥 끝까지 다 넣어버려
            # print("주문수는 적지만 그냥 지울게~")
            changed_robot_index.append(robot_index)  # 바뀐 로봇 배치를 기록합니다.
            solved_orders_index = solved_orders_index + list(
                range(start_order, start_order + len(readonly_orders[start_order:]), 1))
            start_order += len(readonly_orders[start_order:])  # 새롭게 할당할 때 사용할 start_order를 수정합니다.

        elif len(robot_batch) < max_batch_size:# 풀로 더넣을 수 있고, 기존 로봇이 가진 배치가 최대량보다 작아서 더넣을 수 있을 때
            # "order가 너무 작아 그래도 넣어"
            if robot_data["current_robot_batch"][robot_index] ==0:
                print("뭔가 이상합니다.")
            # print("---------------------")
            # print("기존에 나는 이미 이만큼을 할당받았어..",solved_batches[robot_index])
            # print("앞으로 이거 넣을 꺼야",readonly_orders[start_order:start_order+additional_orders_number])
            solved_batches[robot_index] += readonly_orders[start_order:start_order+additional_orders_number]
            # print("근데 이만큼 더넣었어.. 남아서", solved_batches[robot_index])
            # print("배치는 남지만 그냥 지울게~")
            changed_robot_index.append(robot_index)  # 바뀐 로봇 배치를 기록합니다.
            # print("너는 원래 몇겨였니.", solved_orders_index)
            # print("현재 order 풀린거 시작은 이래", start_order)
            solved_orders_index = solved_orders_index + list(range(start_order, start_order + additional_orders_number, 1))
            # print("너는 왜 6개나 있는거니.", solved_orders_index)
            start_order += additional_orders_number  # 새롭게 할당할 때 사용할 start_order를 수정합니다.
    DEBUG_log("\n--------------------\n","DETAIL")
    DEBUG_log("남은 주문수", "VERY_DETAIL")
    DEBUG_log(len(readonly_orders), "VERY_DETAIL")
    DEBUG_log("처리되어야하는 주문들", "VERY_DETAIL")
    # DEBUG_log(solved_orders_index[0:5],"VERY_DETAIL")

    DEBUG_log("바뀐 배치들 일부 ", "VERY_DETAIL")
    DEBUG_log(solved_batches,"VERY_DETAIL")
    DEBUG_log("바뀐로봇들 일부", "DETAIL")
    # DEBUG_log(changed_robot_index[0:1],"DETAIL")

    return solved_orders_index,solved_batches,changed_robot_index

def online_order_batch(orders, item_position, init_batch_size, max_batch_size, current_robot_batch):

    return_robot_batch = []
    remain_order = []

    #todo

    return return_robot_batch, remain_order
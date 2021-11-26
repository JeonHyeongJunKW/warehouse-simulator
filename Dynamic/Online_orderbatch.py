from Dynamic.DEBUG_tool import DEBUG_log,DEBUG_log_tag
from Dynamic.HCOB import *
import copy
import time
def online_order_batch_FIFO(readonly_orders, init_batch_size, max_batch_size, robot_data, end_flag):

    #로봇들이 기본적인 할당량을 가지고 있는지 확인하고,
    solved_orders_index = []
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])#현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch  # 현재의 로봇배치
    changed_robot_index = []  # 배치가 바뀐 로봇의 인덱스
    assigned_flag = [False for _ in range(len(readonly_current_robot_batch))]#초기할당이라면 order를 추가할당하지 않습니다.

    #1. init_batch이하인 로봇들의 배치를 가져온다. 더이상 남은 order가 없다면 리턴, 있다면 FIFO방식으로 할당

    start_order = 0
    for robot_index, robot_batch in enumerate(readonly_current_robot_batch):
        if end_flag:
            if len(robot_batch) == 0 and len(readonly_orders)-start_order < init_batch_size:#로봇의 배치사이즈가 0이고, 남은 주문의 사이즈가 초기 배치사이즈보다 작다면
                # order를 할당합니다.
                solved_batches[robot_index] = readonly_orders[
                                              start_order:len(readonly_orders)]  # 현재 order들에서 일정그룹만을 가져와서 넣습니다.
                if len(readonly_orders)-start_order !=0:
                    changed_robot_index.append(robot_index)  # 바뀐 로봇 배치를 기록합니다.
                solved_orders_index = solved_orders_index + list(range(start_order, len(readonly_orders), 1))
                start_order += len(readonly_orders)-start_order  # 새롭게 할당할 때 사용할 start_order를 수정합니다.
                assigned_flag[robot_index] = True
            elif len(robot_batch) == 0:
                # order를 할당합니다.
                solved_batches[robot_index] = readonly_orders[
                                              start_order:start_order + init_batch_size]  # 현재 order들에서 일정그룹만을 가져와서 넣습니다.
                changed_robot_index.append(robot_index)  # 바뀐 로봇 배치를 기록합니다.
                solved_orders_index = solved_orders_index + list(range(start_order, start_order + init_batch_size, 1))
                start_order += init_batch_size  # 새롭게 할당할 때 사용할 start_order를 수정합니다.
                assigned_flag[robot_index] = True
        elif len(readonly_orders)-start_order < init_batch_size:
            # print("현재 배치의 오더 배치들",solved_batches)
            # print("이번 step에 풀린 index : ", solved_orders_index)
            # print("현재까지 풀린 배치들 : ", solved_batches)
            # print("배치가 수정된 로봇들 : ", changed_robot_index)
            return solved_orders_index,solved_batches,changed_robot_index
        #큰일날 수 있는부분..
        elif len(robot_batch) ==0:
            #order를 할당합니다.
            solved_batches[robot_index] = readonly_orders[start_order:start_order+init_batch_size]#현재 order들에서 일정그룹만을 가져와서 넣습니다.
            changed_robot_index.append(robot_index)#바뀐 로봇 배치를 기록합니다.
            solved_orders_index = solved_orders_index + list(range(start_order, start_order+init_batch_size,1))
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
    # print("이번 step에 풀린 index : ", solved_orders_index)
    # print("현재까지 풀린 배치들 : ", solved_batches)
    # print("배치가 수정된 로봇들 : ", changed_robot_index)
    return solved_orders_index,solved_batches,changed_robot_index

def online_order_batch_HCOB(readonly_orders, init_batch_size, max_batch_size, robot_data, node_point_y_x):
    '''
    이미 버퍼링되던 시간
    online_order_batch_HCOB.buffered_order = []
    online_order_batch_HCOB.buffered_order_time = []
    '''
    start_time = time.time()
    # print("HCOB")
    buffer_order_ind = online_order_batch_HCOB.buffered_order_ind  #현재 order 큐에서해당하는 주문의 인덱스
    buffer_orders = online_order_batch_HCOB.buffered_order #현재 큐에있는 주문들
    buffer_time = online_order_batch_HCOB.buffered_order_time#각 주문들이 만료되는 시간

    # print(buffer_orders)
    expired_list = []#현재 step에서 만료된 주문의 큐 내에서 인덱스, 매번갱신된다.
    #readonly_orders를 확인하고 추가되었으면 버퍼에 넣고, 시간을 기록한다.
    expired_time =60#주문이 들어와서, 만료되는 시간 / 10초 뒤에 만료됩니다.

    solved_orders_index = []
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch  # 현재의 로봇배치
    changed_robot_index = []  # 배치가 바뀐 로봇의 인덱스
    new_order = False
    if len(readonly_orders) > len(online_order_batch_HCOB.past_order): #order가 추가되었는지 확인한다.
        for order in readonly_orders[len(online_order_batch_HCOB.past_order):]:#새로 추가된 order에 대해서
            buffer_orders.append(order)#해당 order를 추가한다.
            buffer_time.append(time.time()+expired_time)#order가 만료되는 시간을 기록합니다.
            buffer_order_ind.append(online_order_batch_HCOB.order_num) #order가 가지는 index를 기록합니다.

            online_order_batch_HCOB.order_num +=1 # 인덱스 번호를 올립니다.
            new_order = True


    if Is_Expiration(buffer_time,expired_list,buffer_order_ind):# 유통기한을 검사한다. 만약에 넘는게 있는가?
        # print("1. 유통기한이 지났어...")
        if Is_picking_robot_cap_max(robot_data,max_batch_size):#이동중인 로봇의 용량이 꽉찾는가?
            # print("2. 이동중인 로봇이 다 꽉찼어")
            if Is_remaining_robot(robot_data):# 네, 그럼 아직 이동하지않은 로봇이 있는가?
                #유사도를 따지지 않고 보냅니다.
                # print("3. 남은 로봇이 있어")
                solved_orders_index,solved_batches,changed_robot_index, deleted_order =\
                    Do_make_Q_robot(robot_data,
                                buffer_orders,
                                expired_list,
                                init_batch_size,
                                buffer_order_ind)# 현재 남는 order랑 유사도가 좋은 order를 할당 및 새로운 로봇 출발

                Delete_orders_in_Buffer(buffer_order_ind,buffer_orders,buffer_time,deleted_order)
            else:# 모든 로봇이 바쁘다면?
                # print("4. 남은 로봇도 없어")
                Do_Idle()#그냥 큐안에 둔다.
        else:
            # print("5. 이동중인 로봇한테 더넣을 수 있어!")
            good_match = Is_good_to_picking_robot_apply(robot_data,
                                                        buffer_orders,
                                                        buffer_order_ind,
                                                        expired_list,
                                                        max_batch_size,
                                                        node_point_y_x)
            if [] != good_match:#꽉차지않았다면 수행하기에 적절한가?
                # print("6. 이동중인 로봇한테 더넣으면 좋을거같아!")
                solved_orders_index,solved_batches,changed_robot_index = Do_apply_order(good_match,
                               robot_data,
                               buffer_order_ind,
                               buffer_orders,
                               buffer_time)#배치를 수정해버린다.
            else:
                # print("7. 너무 안어울려서 이동중인 로봇한테 넣으면 안된데!")
                if Is_remaining_robot(robot_data):  # 아직 이동하지않은 로봇이 있는가?
                    # print("8. 남은 로봇이 있어서 억지로 출발시켰어")
                    solved_orders_index, solved_batches, changed_robot_index, deleted_order = \
                        Do_make_Q_robot(robot_data,
                                        buffer_orders,
                                        expired_list,
                                        init_batch_size,
                                        buffer_order_ind)  # 현재 남는 order랑 유사도가 좋은 order를 할당 및 새로운 로봇 출발

                    Delete_orders_in_Buffer(buffer_order_ind, buffer_orders, buffer_time, deleted_order)  # 현재 남는 order랑 유사도가 좋은 order를 할당 및 새로운 로봇 출발
                else:
                    # print("9. 남는 로봇에 제약없이 넣어버리자.")
                    good_match = Is_good_to_picking_robot_apply(robot_data,
                                                                buffer_orders,
                                                                buffer_order_ind,
                                                                expired_list,
                                                                max_batch_size,
                                                                node_point_y_x,
                                                                True) ## 임계값 제약을 없애고 추가해준다.
                    solved_orders_index, solved_batches, changed_robot_index = Do_apply_order(good_match,
                                                                                              robot_data,
                                                                                              buffer_order_ind,
                                                                                              buffer_orders,
                                                                                              buffer_time)  # 배치를 수정해버린다.
    else : #넘는게 없다면
        # print("10. 아직 유통기한 넘은게 없어")
        if Is_new_Order(new_order):
            # print("11. 새로운 주문이 들어왔데!")
            new_orders = buffer_order_ind[len(online_order_batch_HCOB.past_order):]  # 새로 추가된 order에 대해서
            if Is_picking_robot_cap_max(robot_data,max_batch_size):#이동중인 로봇의 용량이 꽉차지 않았는가?

                good_match,no_insert = Is_good_to_picking_robot_apply_new_order(robot_data,
                                                                      buffer_orders,
                                                                      buffer_order_ind,
                                                                      new_orders,
                                                                      max_batch_size,
                                                                      node_point_y_x)  # 꽉차지않았다면 수행하기에 적절한가?
                if [] != good_match:
                    solved_orders_index, solved_batches, changed_robot_index = Do_apply_order(good_match,
                                                                                              robot_data,
                                                                                              buffer_order_ind,
                                                                                              buffer_orders,
                                                                                              buffer_time)  # 배치를 수정해버린다.
                #     print("12. 이동중인 로봇중에 더 넣을 게")
                # else:
                #     if no_insert:
                #         print("13-1. 피킹로봇에 자리가 없어")
                #     else :
                #         print("13-2. 이동로봇에 넣으려고 했는데, 너무 안어울려")
            else:
                # print("14. 이동로봇의 용량이 꽉찼거나 이동로봇이 아직 없어")
                if Is_remaining_robot(robot_data):  # 아직 이동하지않은 로봇이 있는가?

                    good_match = Is_maded_good_batch_in_Queue(buffer_orders,node_point_y_x,init_batch_size)
                    if [] != good_match :
                        solved_orders_index, solved_batches, changed_robot_index = Do_make_Q_robot_new_order(good_match,
                                                  robot_data,
                                                  buffer_order_ind,
                                                  buffer_orders,
                                                  buffer_time)# 현재 남는 order랑 유사도가 좋은 order를 할당 및 새로운 로봇 출발
                        # print("15. 남은 로봇중에 괜찮아서 넣을게")
                    else:
                        Do_save_in_Queue()# 아직 애매한 배치면 저장해버린다.
                        # print("16. 대기중인 로봇에 넣으려고 했는데, 너무 안어울려")
                else:
                    # print("17. 전부 일하는중이야")
                    Do_save_in_Queue()# 아직 애매한 배치면 저장하지 않는다.
        else:#새로운 주문이 없다면
            # print("18. 새로운 주문이 없어")
            # Do_Idle()#그냥 큐안에 둔다.
            if Is_remaining_robot(robot_data):  # 아직 이동하지않은 로봇이 있는가?

                good_match = Is_maded_good_batch_in_Queue(buffer_orders, node_point_y_x, init_batch_size)
                # print("19. 혹시 대기중인 괜찮은 주문이 있는가?")
                if [] != good_match:
                    solved_orders_index, solved_batches, changed_robot_index = Do_make_Q_robot_new_order(good_match,
                                                                                                         robot_data,
                                                                                                         buffer_order_ind,
                                                                                                         buffer_orders,
                                                                                                         buffer_time)  # 현재 남는 order랑 유사도가 좋은 order를 할당 및 새로운 로봇 출발
                    # print("20. 괜찮은 주문이 있어서 출발")
                else:
                    Do_save_in_Queue()  # 아직 애매한 배치면 저장해버린다.
                    # print("21. 이래도 없어서 큐에 무한대기")

    online_order_batch_HCOB.past_order = copy.deepcopy(online_order_batch_HCOB.buffered_order)
    # print("현재 버퍼에 남은 order의 index",online_order_batch_HCOB.buffered_order_ind)
    # print("이번 step에 풀린 index : ", solved_orders_index)
    # print("현재까지 풀린 배치들 : ", solved_batches)
    # print("배치가 수정된 로봇들 : ", changed_robot_index)
    # print(" ")
    # print(time.time()-start_time)
    return solved_orders_index,solved_batches,changed_robot_index

online_order_batch_HCOB.buffered_order = []
online_order_batch_HCOB.buffered_order_ind = []
online_order_batch_HCOB.buffered_order_time = []
online_order_batch_HCOB.expired = []
online_order_batch_HCOB.past_order = []
online_order_batch_HCOB.order_num = 0


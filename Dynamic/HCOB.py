import time
import datetime
import copy
import numpy as np
from Dynamic.DEBUG_tool import DEBUG_log,DEBUG_log_tag
# distance_bound = 500
def Is_Expiration(buffer_time,expired_list,buffer_order_ind):
    return_flag = False
    for i, exp_time in enumerate(buffer_time):
        if exp_time - time.time() < 0:#만료시간을 넘겼다면?
            expired_list.append(buffer_order_ind[i])#현재 큐에서 만료된걸 넣는다. ===>주문의 고유 인덱스를 넣는다.
            return_flag = True#만약에 하나라도 만료된게 있으면 True를 반환

    if return_flag:
        return True

    return False

def Is_picking_robot_cap_max(robot_data,max_batch_size):
    current_batch = robot_data["current_robot_batch"]
    for batch in current_batch:#현재 이동중인 로봇의 배치에서
        if len(batch) ==0:#이동중이 아니면 넘긴다.
            continue
        elif len(batch)<max_batch_size:#이동중인데 널널하다.
            return True
    return False

def Is_new_Order(new_order):
    return new_order

def Is_remaining_robot(robot_data):
    current_batch = robot_data["current_robot_batch"]
    for batch in current_batch:  # 현재 이동중인 로봇의 배치에서
        if len(batch) == 0:  # 남는 로봇이 있는가?
            return True
    return False

def Do_Idle():
    pass

def Do_make_Q_robot(robot_data,buffer_orders,expired_list,init_batch_size,buffer_order_ind):
    #현재 배치내에서 만기된 주문들로 일정크기의 배치 만들어서 보낸다.
    #만들고나서, 바뀐 로봇인덱스, solved_batches(전체 배치), solved_orders_index(배치가된 order 번호)를 반환해야함..
    current_batch = []
    current_batch_ind_in_buffer = []

    #추가할 주문선별
    for ind, expired_ind in enumerate(expired_list):#만료된 주문에 대해서, 먼저 들어온 순서대로 없애버린다.
        if ind > init_batch_size:#초기 사이즈만큼만 받는다.
            break
        else :
            index_in_buffer = buffer_order_ind.index(expired_ind)#주문의 고유번호로 버퍼에서의 위치를 찾는다.
            current_batch_ind_in_buffer.append(index_in_buffer)#버퍼에서의 위치를 저장한다.
            current_batch.append(buffer_orders[index_in_buffer])#만료된 인덱스를 가지는 주문을 새로운 배치에 추가한다.

    #solved_batch에 추가, solver_orders_index에 추가, 바뀐 로봇인덱스 추가.

    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch  # 현재의 로봇배치
    changed_robot_index = []  # 배치가 바뀐 로봇의 인덱스
    solved_orders_index = []
    readonly_current_robot = copy.deepcopy(robot_data["robot"])
    robot_index = []
    robot_steps = []
    for robot_ind, batch in enumerate(readonly_current_robot_batch):
        if len(batch) ==0: #===> step 사이즈가 적은 수의 로봇에게 할당한다.
            robot_index.append(robot_ind)
            robot_steps.append(readonly_current_robot[robot_ind].step)
            # break
    min_step = min(robot_steps)
    target_ind = robot_index[robot_steps.index(min_step)]
    solved_batches[target_ind] = current_batch  # 비어있는 로봇에게 추가합니다.
    changed_robot_index.append(target_ind)
    # solved_orders_index += expired_list#실제 만료되는 인덱스
    solved_orders_index += current_batch_ind_in_buffer

    #후처리, 풀린 order에 대한 기록을 지워야합니다. 현재 버퍼에서의 인덱스를 넣습니다.
    deleted_order = current_batch_ind_in_buffer#버퍼내에서의 인덱스면... 실제 order로써의 인덱스가 같을까?
    return solved_orders_index,solved_batches,changed_robot_index, deleted_order

def Is_good_to_picking_robot_apply(robot_data,buffer_orders,buffer_order_ind, expired_list,max_batch_size,node_point_y_x,bound_size,no_bound = False):
    good_match = []
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.

    #현재 0개이상의 solved_bathch에 대해서 유사도 검사
    for expired_ind in expired_list:
        index_in_buffer = buffer_order_ind.index(expired_ind)  # 주문의 고유번호로 버퍼에서의 위치를 찾는다.
        compare_order = buffer_orders[index_in_buffer] #비교되는 주문
        small_robot_ind = -1
        for robot_ind, batch in enumerate(readonly_current_robot_batch):
            union_batch = list(set(sum(batch, [])))
            if len(batch) > 0 and len(batch) <max_batch_size: #적절한 배치사이즈 범위 안이라면

                already_gone_node = robot_data['already_gone_node'][robot_ind]
                union_batch_notgo = [node for node in union_batch if node not in already_gone_node]#앞으로 로봇이 가야하는 노드 수
                current_coordinate = recovery(robot_data["packing_pose_recovery"], robot_data["robot"][robot_ind].current_point)#현재 로봇의 좌표
                normalize_dis = Similarity_btw_robot_order(union_batch_notgo,current_coordinate,compare_order,node_point_y_x)
                # print("작은 거리들", normalize_dis)
                if normalize_dis< bound_size or no_bound: #일정한 거리를 넘어가면 배치하지않는다.
                    if normalize_dis < small_robot_dis:  # 가장 거리가 작은 로봇을 찾는다.
                        small_robot_dis = normalize_dis
                        small_robot_ind = robot_ind

        if small_robot_ind != -1:
            readonly_current_robot_batch[small_robot_ind].append(compare_order)
            good_match.append([index_in_buffer, robot_ind])

    return good_match

def Similarity_btw_robot_order(union_batch_notgo,current_coordinate,compare_order,node_point_y_x):
    #현재 로봇이 가야하는 노드와 현재 위치에 대한 실제 값 변환을 한 벡터(x,y)를 얻습니다.
    #비교대상 노드별로 실제 좌표를 얻는다.
    #비교대상으로 쓰일 order들에 대해서 각각의 가장 작은 거리를 numpy연산을 통해서 찾는다.
    #전체 거리에 대해서 평균을 내어서 가장가까운 노드를 찾는다.

    sim_time = time.time()
    orders = [node_point_y_x[order] for order in union_batch_notgo]
    orders.append(current_coordinate)
    seed_orders = [node_point_y_x[order] for order in compare_order]
    small_seed_dis = find_small_dis(seed_orders,orders)
    DEBUG_log_tag("작은 거리 찾는데 걸리는 시간", time.time()-sim_time)
    return small_seed_dis/len(seed_orders)#노멀라이즈된 거리


def find_small_dis(seed_orders, orders):#시드 오더는 적은쪽, orders는 많은쪽
    sum_smallest_seed_dis = 0
    for seed_order_one in seed_orders:#시드 오더에 대해서
        orders_np = np.array(orders)#모든 order에 대해서
        orders_np[:, 0] = orders_np[:, 0] - seed_order_one[0]#x값 거리차이를 구한다.
        orders_np[:, 1] = orders_np[:, 1] - seed_order_one[1]#y값 거리차이를 구한다.
        sum_smallest_seed_dis += np.min(np.sqrt(orders_np[:, 0] ** 2 + orders_np[:, 1] ** 2))
    return sum_smallest_seed_dis

def recovery(recovery_param,point):
    point = [point[0]*recovery_param[3]+recovery_param[0], point[1]*recovery_param[2]+recovery_param[1]]
    return point

def Do_apply_order(good_match,robot_data,buffer_order_ind,buffer_orders,buffer_time):
    # 만들고나서, 바뀐 로봇인덱스, solved_batches(전체 배치), solved_orders_index(배치가된 order 번호)를 반환해야함..
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch
    for match in good_match:#[index_in_buffer, small_robot_ind]
        solved_batches[match[1]].append(buffer_orders[match[0]])

    changed_robot_index = list(set([match[1] for match in good_match]))
    deleted_order = list(set([match[0] for match in good_match]))
    solved_orders_index = deleted_order
    deleted_order.sort(reverse =True)
    for order_ind in deleted_order:
        del buffer_order_ind[order_ind]#버퍼내의 주문의 실제 고유번호를 삭제
        del buffer_orders[order_ind]#버퍼내의 주문 자체를 삭제
        del buffer_time[order_ind]#버퍼내의 주문의 만료시간을 삭제
    return solved_orders_index,solved_batches,changed_robot_index

def Is_maded_good_batch_in_Queue(buffer_orders,node_point_y_x,init_batch_size,bound_size):
    #좋은 집합이 만들어지는가?
    for i, seed_order_ind in enumerate(buffer_orders):
        seed_order = [node_point_y_x[j] for j in seed_order_ind]
        other_order =copy.deepcopy(buffer_orders)
        del other_order[i]
        item_min_distance = []
        for k, other_order_ind in enumerate(other_order):
           one_other_order = [node_point_y_x[j] for j in other_order_ind]
           distance = find_small_dis(seed_order,one_other_order)
           item_min_distance.append(distance)
        item_dis = np.array(item_min_distance)
        same_batch_ind = np.argsort(item_dis).tolist()[:init_batch_size-1]
        if len(same_batch_ind) ==0:
            continue
        # print("마지막 거리", item_dis[same_batch_ind[-1]]/len(seed_order_ind))
        if item_dis[same_batch_ind[-1]]/len(seed_order_ind) >bound_size:
            continue
        else :
            #현재 seed order(i)에 대해서, same_batch_ind에 속하는 order를 찾아서 하나로 묶는다.
            seed_order_last = i
            other_order_last = [ind  if ind <i else ind+1 for ind in same_batch_ind]#만약에 seed의 index보다 크거나 같다면 인덱스 값을 하나 더 올린다.
            other_order_last.append(seed_order_last)
            return other_order_last
    return []
def Do_make_Q_robot_new_order(good_match, robot_data, buffer_order_ind, buffer_orders, buffer_time):
    # 만들고나서, 바뀐 로봇인덱스, solved_batches(전체 배치), solved_orders_index(배치가된 order 번호)를 반환해야함..
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.
    solved_batches = readonly_current_robot_batch
    good_robot = -1
    for ind, possible_batch in enumerate(solved_batches):
        if len(possible_batch) ==0:
            good_robot =ind
            break
    for i in good_match:
        solved_batches[good_robot].append(buffer_orders[i])#해당하는 order들을 추가한다.

    changed_robot_index = [good_robot]
    deleted_order = good_match
    solved_orders_index = deleted_order
    deleted_order.sort(reverse=True)
    for order_ind in deleted_order:
        del buffer_order_ind[order_ind]  # 버퍼내의 주문의 실제 고유번호를 삭제
        del buffer_orders[order_ind]  # 버퍼내의 주문 자체를 삭제
        del buffer_time[order_ind]  # 버퍼내의 주문의 만료시간을 삭제
    return solved_orders_index, solved_batches, changed_robot_index


def Do_save_in_Queue():
    pass

def Delete_orders_in_Buffer(buffer_order_ind,buffer_orders,buffer_time,deleted_order):
    deleted_order.sort(reverse =True)
    for order_ind in deleted_order:
        del buffer_order_ind[order_ind]#버퍼내의 주문의 실제 고유번호를 삭제
        del buffer_orders[order_ind]#버퍼내의 주문 자체를 삭제
        del buffer_time[order_ind]#버퍼내의 주문의 만료시간을 삭제

def Is_good_to_picking_robot_apply_new_order(robot_data,buffer_orders,buffer_order_ind, new_orders,max_batch_size,node_point_y_x,bound_size):
    good_match = []
    readonly_current_robot_batch = copy.deepcopy(robot_data["current_robot_batch"])  # 현재의 로봇배치를 넣는다.
    no_insert = True
    robot_info_data = copy.deepcopy(robot_data)
    # 현재 0개이상의 solved_bathch에 대해서 유사도 검사
    # print("새로운 주문들이야 : ", new_orders)
    for new_ind in new_orders:
        check_time_2 = time.time()
        index_in_buffer = buffer_order_ind.index(new_ind)  # 주문의 고유번호로 버퍼에서의 위치를 찾는다.
        # print("실제 번호 : ", new_ind)
        # print("버퍼내에서 번호 : ",index_in_buffer)
        compare_order = buffer_orders[index_in_buffer]  # 비교되는 주문
        small_robot_ind = -1
        small_robot_dis = 10000
        # print("이게 현재 로봇의 배치들이야", readonly_current_robot_batch)
        for robot_ind, batch in enumerate(readonly_current_robot_batch):
            union_batch = list(set(sum(batch, [])))
            # print("넣으려고 하는 로봇의 배치사이즈야 : ", len(batch))
            if len(batch) > 0 and len(batch) < max_batch_size:  # 적절한 배치사이즈 범위 안이라면
                no_insert = False
                check_time = datetime.datetime.now()
                already_gone_node = robot_info_data['already_gone_node'][robot_ind]
                DEBUG_log_tag("그냥 이미 간 노드 가져오는데 걸리는 시간 us", (datetime.datetime.now() - check_time).microseconds)
                DEBUG_log_tag("union batch 갯수", len(union_batch))
                DEBUG_log_tag("이미 간 노드 갯수", len(already_gone_node))
                # union_batch = np.array(union_batch)
                # already_gone_node =np.array(already_gone_node)
                # union_batch_notgo = [node for node in union_batch if node not in already_gone_node]  # 앞으로 로봇이 가야하는 노드 수
                # union_batch_notgo = np.intersect1d(union_batch,already_gone_node).tolist()
                check_time_3 =datetime.datetime.now()
                union_batch_notgo = robot_info_data['not_go'][robot_ind]
                DEBUG_log_tag("아직 가지않는 노드만 발라 내는 데 걸리는 시간 us", (datetime.datetime.now() - check_time_3).microseconds)
                check_time_4 = datetime.datetime.now()
                current_coordinate = recovery(robot_info_data["packing_pose_recovery"],
                                              robot_info_data["robot"][robot_ind].current_point)  # 현재 로봇의 좌표
                DEBUG_log_tag("리커버리에 걸리는 시간", (datetime.datetime.now() - check_time_4).microseconds)
                DEBUG_log_tag("로봇과의 유사도 비교전에 걸리는 시간 us", (datetime.datetime.now() - check_time).microseconds)
                normalize_dis = Similarity_btw_robot_order(union_batch_notgo, current_coordinate, compare_order,
                                                           node_point_y_x)
                DEBUG_log_tag("로봇과의 유사도 비교에 걸리는 시간 us",(datetime.datetime.now() - check_time).microseconds)
                # print("유통기한 안지난 애들의 거리 ", normalize_dis)
                if normalize_dis < bound_size:  # 일정한 거리를 넘어가면 배치하지않는다.
                    if normalize_dis < small_robot_dis:  # 가장 거리가 작은 로봇을 찾는다.
                        small_robot_dis = normalize_dis
                        small_robot_ind = robot_ind

        if small_robot_ind != -1:
            readonly_current_robot_batch[small_robot_ind].append(compare_order)
            good_match.append([index_in_buffer, small_robot_ind])
        DEBUG_log_tag("새 주문별로 로봇과의 유사도 비교에 걸리는 시간", time.time() - check_time_2)
    # print("매칭결과야 ", good_match)
    # print("---------")
    return good_match, no_insert
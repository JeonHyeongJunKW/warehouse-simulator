#시각화 필요
#동시에 여러개미가 돌게하려면, 쓰레드나 for문을써야하지 않을까?
#확률기반으로 해야하니까 그것도 해야하지 않을까?
import matplotlib.pyplot as plt
import random
import numpy as np
import math
def get_path(refined_orders,distance_cost):
    alpha = 1  # 페로몬 가중치
    beta = 5  # 휴리스틱 가중치
    evap = 0.80  # 남는비율 (1-증발율)
    evap_step = 1  # 증발주기
    evap_count = 0
    w_elit = 0.2  # 엘리트 엔트 추가율
    ant_size = 100  # 엔트 사이즈
    cur_it = 0
    max_it = 100
    map_size = len(refined_orders)
    heuristic_map = np.zeros((map_size, map_size))
    for i in range(map_size):
        for j in range(map_size):
            heuristic_map[i, j] = math.sqrt(distance_cost[refined_orders[i]][refined_orders[j]])

    # 페로몬 맵을 생성합니다.
    pheromone_map = np.ones((map_size, map_size))
    pheromone_map[np.eye(map_size) == 1] = 0
    pheromone_map = pheromone_map

    # 엘리트 맵을 생성합니다.
    elit_map = np.ones((map_size, map_size))
    elit_map[np.eye(map_size) == 1] = 0

    sum_map = pheromone_map * (1 - w_elit) + elit_map * w_elit
    sub_pheromone_map = []
    for _ in range(ant_size):
        sub_pheromone_map.append(np.zeros((map_size, map_size)))
    # 각 개미에 대해서, 초기 페로몬이 0.1인 상태에서 시작한다.
    best_ant_ind = 0
    best_ant_length = 100000
    best_ant_changed = False
    best_ant_path = []
    best_path = []
    # print(heuristic_map)
    no_change =0
    while True:
        path_list = []
        path_length = []
        for ant_ind in range(ant_size):
            '''
            처음에 개미가 시작지점을 무조건 0번이라고 하자. 그상태에서 시작임 
            각 도시에서 확률적으로 검사함
            '''
            is_not_go = list(range(map_size))
            is_not_go.remove(0)  # 0번도시를 제거
            current_city = 0  # 현재 있는 도시
            city_path = [0]
            while True:
                current_pheromone = [
                    math.pow(sum_map[current_city, i], alpha) * math.pow(1 / heuristic_map[current_city, i], beta) for i
                    in is_not_go]#남은 노드중에서 페로몬을 다시구한다.

                rand_pro = random.random()
                pro_current_pheromone = [current_pheromone[h] / sum(current_pheromone) for h in
                                         range(len(current_pheromone))]
                # print(pro_current_pheromone)
                cum_ind = 0
                cum_pro = 0
                for k, sub_pro in enumerate(pro_current_pheromone):
                    cum_pro += sub_pro
                    if rand_pro < cum_pro:
                        cum_ind = is_not_go[k]
                        break
                is_not_go.remove(cum_ind)#이 노드는 들렸기때문에 제외한다.
                current_city = cum_ind
                city_path.append(cum_ind)#경로에 추가한다.
                if len(is_not_go) == 0:
                    city_path.append(0)
                    break

            # 해당 경로의 길이를 구한다.
            city_path_length = 0
            for i in range(len(city_path) - 1):
                city_path_length += heuristic_map[city_path[i], city_path[i + 1]]#전체 경로를 구한다.
            path_list.append(city_path)
            path_length.append(city_path_length)

            if best_ant_length > city_path_length:
                best_ant_path = city_path
                best_ant_ind = ant_ind
                best_ant_length = city_path_length
                best_ant_changed = True

        # 가장 적은 경로 확인
        small_path_index = path_length.index(min(path_length))
        small_path = path_list[small_path_index]
        # print("small_path =",  small_path)
        if evap_count % evap_step == 0:
            pheromone_map = pheromone_map * evap
        for i in range(len(small_path) - 1):
            start = small_path[i]
            end = small_path[i + 1]
            pheromone_map[start, end] += 1 / min(path_length)
            pheromone_map[end, start] += 1 / min(path_length)
        pheromone_map = pheromone_map / pheromone_map.sum()  # 정규화

        # 만약에 지금까지 가장 낮은 해가 나왔다면
        if best_ant_changed:
            best_ant_changed = False
            elit_map = np.ones((map_size, map_size)) / (map_size * map_size)
            for i in range(len(path_list[best_ant_ind]) - 1):
                start = path_list[best_ant_ind][i]
                end = path_list[best_ant_ind][i + 1]
                elit_map[start, end] = 1 / path_length[best_ant_ind]
                elit_map[end, start] = 1 / path_length[best_ant_ind]
            elit_map = elit_map / elit_map.sum()
            best_path = [refined_orders[i] for i in best_ant_path]
            no_change =0
            # print(cur_it," : ",best_ant_path)

        sum_map = pheromone_map * (1 - w_elit) + elit_map * w_elit

        no_change +=1
        if no_change >20:
            break
        evap_count += 1
        cur_it += 1
        if cur_it > max_it:
            break
    print(cur_it)
    return best_path[0:-1]

def TSP_ant_colony_elit(city_size,seed_value):
    #세부 파라미터
    alpha  =1# 페로몬 가중치
    beta =5# 휴리스틱 가중치
    evap = 0.80#남는비율 (1-증발율)
    evap_step = 1 # 증발주기
    evap_count =0
    w_elit = 0.2 #엘리트 엔트 추가율
    ant_size = 300 #엔트 사이즈
    cur_it = 0
    max_it = 400
    #도시를 생성합니다.
    random.seed(seed_value)
    x_sample = random.sample(list(range(1000)),city_size)
    random.shuffle(x_sample)
    random.seed(seed_value*2)
    y_sample = random.sample(list(range(1000)),city_size)
    random.shuffle(y_sample)

    city_pos = []
    for pos in zip(x_sample,y_sample):
        city_pos.append(pos)

    #휴리스틱 맵을 생성합니다.
    heuristic_map = np.zeros((city_size,city_size))
    for i in range(city_size):
        for j in range(city_size):
            heuristic_map[i,j] = math.sqrt(math.pow((city_pos[i][0]-city_pos[j][0]),2)+math.pow((city_pos[i][1]-city_pos[j][1]),2))

    #페로몬 맵을 생성합니다.
    pheromone_map = np.ones((city_size, city_size))
    pheromone_map[np.eye(city_size) == 1] = 0
    pheromone_map = pheromone_map

    # 엘리트 맵을 생성합니다.
    elit_map = np.ones((city_size, city_size))
    elit_map[np.eye(city_size) == 1] = 0

    sum_map = pheromone_map*(1 - w_elit) + elit_map*w_elit
    sub_pheromone_map =[]
    for _ in range(ant_size):
        sub_pheromone_map.append(np.zeros((city_size,city_size)))
    # 각 개미에 대해서, 초기 페로몬이 0.1인 상태에서 시작한다.
    best_ant_ind = 0
    best_ant_length = 100000
    best_ant_changed = False
    while True:
        plt.cla()
        plt.gcf().canvas.mpl_connect('key_release_event',lambda event: [exit(0) if event.key == 'escape' else None])
        plt.scatter(x_sample,y_sample,c="b", s=50)
        path_list =[]
        path_length = []
        for ant_ind in range(ant_size):
            '''
            처음에 개미가 시작지점을 무조건 0번이라고 하자. 그상태에서 시작임 
            각 도시에서 확률적으로 검사함
            '''
            is_not_go = list(range(city_size))
            is_not_go.remove(0)#0번도시를 제거
            current_city = 0#현재 있는 도시
            city_path =[0]
            while True:
                current_pheromone = [ math.pow(sum_map[current_city,i],alpha)*math.pow(1/heuristic_map[current_city,i],beta) for i in is_not_go]

                rand_pro = random.random()
                pro_current_pheromone = [current_pheromone[h]/sum(current_pheromone) for h in range(len(current_pheromone)) ]
                # print(pro_current_pheromone)
                cum_ind =0
                cum_pro = 0
                for k, sub_pro in enumerate(pro_current_pheromone):
                    cum_pro += sub_pro
                    if rand_pro < cum_pro:
                        cum_ind = is_not_go[k]
                        break
                # print(cum_ind)
                is_not_go.remove(cum_ind)
                # print(is_not_go)
                current_city = cum_ind
                city_path.append(cum_ind)
                if len(is_not_go) ==0:
                    city_path.append(0)
                    break

            #해당 경로의 길이를 구한다.
            city_path_length = 0
            for i in range(len(city_path)-1):
                city_path_length += heuristic_map[city_path[i],city_path[i+1]]
            path_list.append(city_path)
            path_length.append(city_path_length)

            if best_ant_length > city_path_length:
                best_ant_ind = ant_ind
                best_ant_length = city_path_length
                best_ant_changed = True

        #가장 적은 경로 확인
        small_path_index = path_length.index(min(path_length))
        small_path = path_list[small_path_index]
        # print("small_path =",  small_path)
        if evap_count % evap_step ==0:
            pheromone_map = pheromone_map*evap
        for i in range(len(small_path)-1):
            start = small_path[i]
            end = small_path[i+1]
            pheromone_map[start, end] += 1/min(path_length)
            pheromone_map[end, start] += 1/min(path_length)
        pheromone_map = pheromone_map/pheromone_map.sum()# 정규화

        #만약에 지금까지 가장 낮은 해가 나왔다면
        font_color ='k'
        if best_ant_changed :
            best_ant_changed = False
            elit_map = np.ones((city_size, city_size))/(city_size*city_size)
            for i in range(len(path_list[best_ant_ind]) - 1):
                start = path_list[best_ant_ind][i]
                end = path_list[best_ant_ind][i + 1]
                elit_map[start, end] = 1 / path_length[best_ant_ind]
                elit_map[end, start] = 1 / path_length[best_ant_ind]
            font_color = 'r'
            elit_map = elit_map/elit_map.sum()

        sum_map = pheromone_map * (1 - w_elit) + elit_map * w_elit
        best_x_list = [x_sample[i] for i in small_path]
        best_y_list = [y_sample[i] for i in small_path]

        plt.title("the length"+str(min(path_length)),color =font_color)
        plt.plot(best_x_list,best_y_list, '-r')


        evap_count +=1
        cur_it +=1
        if cur_it >max_it :
            break
        plt.grid(False)
        plt.pause(0.001)


if __name__ == '__main__':
    TSP_ant_colony_elit(40,300)
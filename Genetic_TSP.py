import sys
import numpy as np
import random
import itertools as iter
import queue
import time
import math
import ACO
from multiprocessing import Pool

g_numOfGenerate = 1000
g_eliteRate = 0.2        # 아직 사용하지 않음
g_randRate = 0.2

class chr:
   def __init__(self, chromesome_indexs, cost):
      self.cost = cost
      self.indexs = chromesome_indexs

   def __lt__(self, other):
      return self.cost < other.cost


class Genetic:
   # cost-matrix:costs is float64
   def __init__(self, costs):
      _len, size = costs.shape
      if _len != size:
         print("Module:Geneic_TSP >> Class:Genetic >> init >> error:not square matrix")
         return
      self.costs = costs

      # rand_gen
      num = min(g_numOfGenerate, _len * 5)
      que = queue.PriorityQueue()
      for _ in iter.repeat(None, num):
         arr = np.array(range(_len))
         np.random.shuffle(arr)
         cost = self.get_cost(arr)
         que.put(chr(arr.tolist(), cost))

      self.que = que
      self.generation = 0

      self.enum = int(num * g_eliteRate)
      self.rnum = int(num * g_randRate)
      self.onum = num - self.rnum - self.enum
      self.num = _len

      self.opt_cost = 0
      self.opt_Flag = 0


   def rand_gen(self):
      arr = np.range(self.num)
      np.random.shuffle(arr)
      return arr



   def _printAll(self):
      print(" ** Gnetic method's printAll [", self.num, "/", self.rate*100, "% ] ** \n")
      print("Cost Matrix")
      print(self.costs)
      self._print()



   def _print(self):
      sol = self.que.get()
      self.que.put(sol)
      paths = sol.indexs
      c = paths.index(0)
      paths = paths[c:] + paths[:c]

      print(" ** Gnetic method's print [ generation : ", self.generation, " ] **")
      print("Most Optimal Solution", paths)
      print("Most Optimal Cost", sol.cost)


   # should input only one line(1 dem)
   def get_cost(self, indexs):
      p = indexs[-1]
      sum = 0.
      for n in indexs:
         sum = sum + self.costs[n, p]
         p = n
      return sum



   # 다음 세대는 가장 뛰어난 개체의 유전체를 사용함
   # 엘리트들의 유전체를 사용하면 더 큰 scale의 TSP를 해결할 수 있음.(개선방향)
   # 엘리트는 무성생식(cloning)
   def generate(self):
      self.generation = self.generation + 1
      pque = self.que
      tmp_que = queue.PriorityQueue()
      nque = queue.PriorityQueue()

      eparent = []
      # 엘리트 선정
      _chr = pque.get()
      eparent.append(_chr.indexs)
      nque.put(_chr)
      for _ in iter.repeat(None, self.enum - 1):
         _chr = pque.get()
         eparent.append(_chr.indexs)
         # flip
         _chr.indexs, _chr.cost = self.Otp_2_mutation(_chr.indexs, _chr.cost)
         nque.put(_chr)

      # 엘리트와 일반인, 이전 랜덤 개체의 자손생성
      for _ in iter.repeat(None, self.onum + self.rnum):
         pnum1 = np.random.randint(self.enum)
         # pnum2 = np.random.randint(self.enum)
         parent = pque.get().indexs
         self.offspring(eparent[pnum1], parent, tmp_que)
         # self.offspring(eparent[pnum2], parent, tmp_que)
      # 생성된 자손중 약한 자손은 도태 되고 랜덤 개체가 나타남
      for _ in iter.repeat(None, self.onum):
         nque.put(tmp_que.get())

      # 랜덤 개체 생성
      for _ in iter.repeat(None, self.rnum):
         arr = np.array(range(self.num))
         np.random.shuffle(arr)
         cost = self.get_cost(arr)
         nque.put(chr(arr.tolist(), cost))

      # que update
      self.que = nque
      # Termination condition, 종료조건
      opt_cost = self.get_opt_cost()
      if self.opt_cost == opt_cost:
         self.opt_Flag += 1
      else:
         self.opt_Flag += 0
      self.opt_cost = opt_cost



   def generates(self, numOfGenerate):
      for _ in iter.repeat(None, numOfGenerate):  # # #
         self.generate()
         if self.opt_Flag == numOfGenerate/5:
            self.opt_Flag = 0
            break



   def Otp_2_mutation(self, H, cost):  # 2-Opt algorithm
      H.append(H[0])
      for i in range(self.num):
         i_next = H[i + 1]  # H는 처음과 시작 Node가 중복으로 되어있어 Node_num+1개의 Node를 가짐
         for j in range(-1, i - 1):
            j_next = H[j + 1]

            before = self.costs[H[i]][i_next] + self.costs[H[j]][j_next]
            after = self.costs[H[j]][H[i]] + self.costs[j_next][i_next]

            if before > after:
               buf = H[j + 1:i + 1]  # 슬라이싱할 때 end+1값으로
               buf.reverse()
               H[j + 1:i + 1] = buf
               cost = cost - before + after
      return H[:self.num], cost



   def offspring(self, parent, bace, que):
      c0 = np.random.randint(self.num)     # 0 ~ self.num-1
      c1 = np.random.randint(self.num)   # 0 ~ self.num-1
      c2 = np.random.randint(2)         # 0 or 1
      # c3 = np.random.randint(self.num)
      c4 = np.random.randint(self.num-2)+1   # 돌연변이 상수
      c5 = np.random.randint(self.num-2)+1    # 돌연변이 상수
      while c4 == c5:
         c5 = np.random.randint(self.num-2)+1   # 상수는 같으면 안됨
      c6 = min(c4, c5)    # 돌연변이 상수
      c7 = max(c4, c5)    # 돌연변이 상수

      C0 = min(c0, c1)
      C1 = max(c0, c1)
      # 2-point crossover
      if c2 is True:
         # offs = parent[c0:] + bace[:c1]
         offs = parent[:C0] + bace[C0:C1] + parent[C1:]
      else:
         # offs = bace[c0:] + parent[:c1]
         offs = bace[:C0] + parent[C0:C1] + bace[C1:]

      pring = list(range(self.num))               # 선택되지 않은 노드들 추가용
      # offs = offs[-c3:] + offs[:-c3]  # 계속 같은 지점에 붙이는 것을 방지하기 위해서 1차-회전
      random.shuffle(pring)
      offspring = list(dict.fromkeys(offs + pring))   # 중복을 제거하고 제거되었거나 선택되지 않은 노드를 랜덤으로 삽입

      # offspring = self.SCX(parent, bace)
      off_cost = self.get_cost(offspring)

      # slide 1
      be = self.costs[offspring[c4-1]][offspring[c4]] + self.costs[offspring[c4]][offspring[c4+1]] + self.costs[offspring[0]][offspring[self.num-1]]
      af = self.costs[offspring[c4-1]][offspring[c4+1]] + self.costs[offspring[c4]][offspring[0]] + self.costs[offspring[c4]][offspring[self.num-1]]
      if be > af:
         mutation1 = offspring[:c4] + offspring[c4+1:] + [offspring[c4]]
         mut_cost1 = off_cost - be + af
         que.put(chr(mutation1, mut_cost1))
         return

      # swap
      # be = self.costs[offspring[c6]][offspring[c6 - 1]] + self.costs[offspring[c6]][offspring[c6 + 1]] + \
      #     self.costs[offspring[c7]][offspring[c7 - 1]] + self.costs[offspring[c7]][offspring[c7 + 1]]
      # af = self.costs[offspring[c7]][offspring[c6 - 1]] + self.costs[offspring[c7]][offspring[c6 + 1]] + \
      #     self.costs[offspring[c6]][offspring[c7 - 1]] + self.costs[offspring[c6]][offspring[c7 + 1]]
      # if be > af:
      #    mutation3 = offspring[:c6] + [offspring[c7]] + offspring[c6 + 1:c7] + [offspring[c6]] + offspring[c7 + 1:]
      #    mut_cost3 = off_cost - be + af
      #    que.put(chr(mutation3, mut_cost3))
      #    return

      que.put(chr(offspring, off_cost))

      # print(offspring, mutation1, mutation2, mutation3, mutation4)
      # print(parent, off_cost, mut_cost1, mut_cost2, mut_cost3, mut_cost4)
      ' end offspring '


   def get(self):
      sol = self.que.get()
      self.que.put(sol)
      return sol.indexs

   def get_opt_cost(self):
      sol = self.que.get()
      self.que.put(sol)
      return sol.cost


def processing(refined_orders, distance_cost):
   map_size = len(refined_orders)
   costs = np.zeros((map_size, map_size), dtype=float)
   for i in range(map_size):
      for j in range(map_size):
         costs[i, j] = distance_cost[refined_orders[i]][refined_orders[j]]
   return costs


def get_path(refined_orders, distance_cost):
   _costs = processing(refined_orders, distance_cost)
   _gen = Genetic(_costs)
   _gen.generates(500)
   paths = _gen.get()
   new_refined_orders = []
   for p in paths:
      new_refined_orders.append(refined_orders[p])
   c = new_refined_orders.index(refined_orders[0])
   new_refined_orders = new_refined_orders[c:] + new_refined_orders[:c]   # 1차 회전
   del _gen
   return new_refined_orders



def get_length(refined_orders, distance_cost):
    full_length = 0
    for i in range(len(refined_orders)-1):
        full_length += distance_cost[refined_orders[i]][refined_orders[i+1]]
    full_length += distance_cost[refined_orders[-1]][refined_orders[0]]

    return full_length


if __name__ == "__main__":
   print(sys.version)
   print("본 모듈은 Python 3.8.7 및 Visaul Studio 2019와 Jupyter에서 개발되었습니다. Ver. 1 \n\n")

   # __inti__
   costs = np.arange(900).reshape(30, 30)
   for i in range(30):
      costs[i, i] = 0
      for j in range(i, 30):
         costs[i, j] = costs[j, i]

   L = [[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870],
   [30, 0, 61, 91, 121, 151, 181, 211, 241, 271, 301, 331, 361, 391, 421, 451, 481, 511, 541, 571, 601, 631, 661, 691, 721, 751, 781, 811, 841, 871],
   [60, 61, 0, 92, 122, 152, 182, 212, 242, 272, 302, 332, 362, 392, 422, 452, 482, 512, 542, 572, 602, 632, 662, 692, 722, 752, 782, 812, 842, 872],
   [90, 91, 92, 0, 123, 153, 183, 213, 243, 273, 303, 333, 363, 393, 423, 453, 483, 513, 543, 573, 603, 633, 663, 693, 723, 753, 783, 813, 843, 873],
   [120, 121, 122, 123, 0, 154, 184, 214, 244, 274, 304, 334, 364, 394, 424, 454, 484, 514, 544, 574, 604, 634, 664, 694, 724, 754, 784, 814, 844, 874],
   [150, 151, 152, 153, 154, 0, 185, 215, 245, 275, 305, 335, 365, 395, 425, 455, 485, 515, 545, 575, 605, 635, 665, 695, 725, 755, 785, 815, 845, 875],
   [180, 181, 182, 183, 184, 185, 0, 216, 246, 276, 306, 336, 366, 396, 426, 456, 486, 516, 546, 576, 606, 636, 666, 696, 726, 756, 786, 816, 846, 876],
   [210, 211, 212, 213, 214, 215, 216, 0, 247, 277, 307, 337, 367, 397, 427, 457, 487, 517, 547, 577, 607, 637, 667, 697, 727, 757, 787, 817, 847, 877],
   [240, 241, 242, 243, 244, 245, 246, 247, 0, 278, 308, 338, 368, 398, 428, 458, 488, 518, 548, 578, 608, 638, 668, 698, 728, 758, 788, 818, 848, 878],
   [270, 271, 272, 273, 274, 275, 276, 277, 278, 0, 309, 339, 369, 399, 429, 459, 489, 519, 549, 579, 609, 639, 669, 699, 729, 759, 789, 819, 849, 879],
   [300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 0, 340, 370, 400, 430, 460, 490, 520, 550, 580, 610, 640, 670, 700, 730, 760, 790, 820, 850, 880],
   [330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 0, 371, 401, 431, 461, 491, 521, 551, 581, 611, 641, 671, 701, 731, 761, 791, 821, 851, 881],
   [360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 0, 402, 432, 462, 492, 522, 552, 582, 612, 642, 672, 702, 732, 762, 792, 822, 852, 882],
   [390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 0, 433, 463, 493, 523, 553, 583, 613, 643, 673, 703, 733, 763, 793, 823, 853, 883],
   [420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 0, 464, 494, 524, 554, 584, 614, 644, 674, 704, 734, 764, 794, 824, 854, 884],
   [450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 0, 495, 525, 555, 585, 615, 645, 675, 705, 735, 765, 795, 825, 855, 885],
   [480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 0, 526, 556, 586, 616, 646, 676, 706, 736, 766, 796, 826, 856, 886],
   [510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 0, 557, 587, 617, 647, 677, 707, 737, 767, 797, 827, 857, 887],
   [540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 0, 588, 618, 648, 678, 708, 738, 768, 798, 828, 858, 888],
   [570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 0, 619, 649, 679, 709, 739, 769, 799, 829, 859, 889],
   [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 0, 650, 680, 710, 740, 770, 800, 830, 860, 890],
   [630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 0, 681, 711, 741, 771, 801, 831, 861, 891],
   [660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 0, 712, 742, 772, 802, 832, 862, 892],
   [690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 0, 743, 773, 803, 833, 863, 893],
   [720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 0, 774, 804, 834, 864, 894],
   [750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 0, 805, 835, 865, 895],
   [780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 0, 836, 866, 896],
   [810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 0, 867, 897],
   [840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 0, 898],
   [870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 0]]

   for i in range(30):
      for j in range(30):
         costs[i, j] = L[i][j]

   start = time.time()
   # __main work__
   gen = Genetic(costs)
   gen.generates(1000)                   # cost : 14326
   print(time.time() - start)


   # __main work__2
   start = time.time()
   aco_path = ACO.get_path(range(30), costs)    # cost : 14326
   print(time.time() - start)


   # __showing__
   # gen._print()
   # gen._printAll()
   ga_path = gen.get()
   ga_cost = get_length(ga_path, costs)
   aco_cost = get_length(aco_path, costs)

   print("GA  : ", ga_cost)
   print("ACO : ", aco_cost)
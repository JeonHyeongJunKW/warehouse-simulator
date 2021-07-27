import sys
import numpy as np
import random
import itertools as iter
import queue
import time
import math

g_numOfGenerate = 1000
g_eliteRate = 0.2        # 아직 사용하지 않음
g_randRate = 0.2
num_limite = 5

class chr:
	def __init__(self, chromesome_indexs, cost):
		self.cost = cost
		self.indexs = chromesome_indexs

	def __lt__(self, other): 
		return self.cost < other.cost


class Genetic:
	# cost-matrix:costs is float64
	def __init__(self, costs, numOfGenerate = g_numOfGenerate, eliteRate = g_eliteRate):
		_len, size = costs.shape
		if _len != size:
			print("Module:Geneic_TSP >> Class:Genetic >> init >> error:not square matrix")
			return
		self.costs = costs

		# rand_gen
		num = min(num_limite, _len * 5)
		que = queue.PriorityQueue()
		for _ in iter.repeat(None, num):
			arr = np.array(range(_len))
			np.random.shuffle(arr)
			cost = self.get_cost(arr)
			que.put(chr(arr.tolist(), cost))

		self.que = que
		self.rate = eliteRate
		self.numGen = numOfGenerate

		self.generation = 0

		self.enum = int(num * g_eliteRate)
		self.rnum = int(num * g_randRate)
		self.onum = num - self.rnum - self.enum
		self.num = _len


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
		nque = queue.PriorityQueue()


		eparent = []
		# 엘리트 선정
		for _ in iter.repeat(None, self.enum):
			_chr = pque.get()
			eparent.append(_chr.indexs)
			nque.put(_chr)

		# 엘리트와 일반인의 자손생성
		for _ in iter.repeat(None, self.onum):
			pnum = np.random.randint(self.enum)
			parent = pque.get().indexs
			self.offspring(eparent[pnum], parent, nque)

		# 랜덤 개체 생성
		for _ in iter.repeat(None, self.rnum):
			arr = np.array(range(self.num))
			np.random.shuffle(arr)
			cost = self.get_cost(arr)
			nque.put(chr(arr.tolist(), cost))
		# que update
		self.que = nque


	def generates(self, numOfGenerate):
		for _ in iter.repeat(None, numOfGenerate):  # # #
			self.generate()


	def offspring(self, parent, bace, que):
		c1 = np.random.randint(self.num)	# 0 ~ self.num-1
		c2 = np.random.randint(2)			# 0 or 1
		c3 = np.random.randint(self.num)
		c4 = np.random.randint(self.num)	# 돌연변이 상수
		c5 = np.random.randint(self.num)    # 돌연변이 상수
		c6 = np.random.randint(self.num)    # 돌연변이 상수
		c7 = np.random.randint(self.num)    # 돌연변이 상수

		# 이거 느리면 bit-mask
		if c1 is True:
			offs = bace[:c2]
			offs.reverse()
			offs = offs + parent[c2:]
		else:
			offs = parent[:c2]
			offs.reverse()
			offs = offs + bace[c2:]

		pring = list(range(self.num))					# 선택되지 않은 노드들 추가용
		offs = offs[-c3:] + offs[:-c3]  # 계속 같은 지점에 붙이는 것을 방지하기 위해서 1차-회전
		random.shuffle(pring)
		offspring = list(dict.fromkeys(offs + pring))	# 중복을 제거하고 제거되었거나 선택되지 않은 노드를 랜덤으로 삽입

		tmp_que = queue.PriorityQueue()
		off_cost = self.get_cost(offspring)
		tmp_que.put(chr(offspring, off_cost))

		mutation1 = offspring[:c4] + offspring[c4+1:]+ [offspring[c4]]
		mut_cost1 = self.get_cost(mutation1)
		tmp_que.put(chr(mutation1, mut_cost1))

		mutation2 = offspring[:c5] + offspring[c5 + 1:]+ [offspring[c5]]
		mut_cost2 = self.get_cost(mutation1)
		tmp_que.put(chr(mutation2, mut_cost2))

		mutation3 = offspring[:c6] + offspring[c6 + 1:] + [offspring[c6]]
		mut_cost3 = self.get_cost(mutation1)
		tmp_que.put(chr(mutation3, mut_cost3))

		mutation4 = offspring[:c7] + offspring[c7 + 1:] + [offspring[c7]]
		mut_cost4 = self.get_cost(mutation1)
		tmp_que.put(chr(mutation4, mut_cost4))

		# print(offspring, mutation1, mutation2, mutation3, mutation4)
		que.put(tmp_que.get())
		' end offspring '

	def get(self):
		sol = self.que.get()
		self.que.put(sol)
		return sol.indexs



def processing(refined_orders, distance_cost):
	map_size = len(refined_orders)
	costs = np.zeros((map_size, map_size), dtype=float)
	for i in range(map_size):
		for j in range(map_size):
			costs[i, j] = math.sqrt(distance_cost[refined_orders[i]][refined_orders[j]])
	return costs


def get_path(refined_orders, distance_cost):
	_costs = processing(refined_orders, distance_cost)
	_gen = Genetic(_costs)
	_gen.generates(1000)
	paths = _gen.get()
	new_refined_orders = []
	for p in paths:
		new_refined_orders.append(refined_orders[p])
	c = new_refined_orders.index(refined_orders[0])
	new_refined_orders = new_refined_orders[c:] + new_refined_orders[:c]	# 1차 회전

	return new_refined_orders


if __name__ == "__main__":
	print(sys.version)
	print("본 모듈은 Python 3.8.7 및 Visaul Studio 2019와 Jupyter에서 개발되었습니다. Ver. 1 \n\n")

	# __inti__
	costs = np.arange(100).reshape(10, 10)
	for i in range(10):
		costs[i, i] = 0
		for j in range(i, 10):
			costs[i, j] = costs[j, i]

	L = [[0, 0, 20, 30, 0, 50, 60, 70, 80, 90],
	     [0, 0, 21, 0, 0, 51, 0, 71, 0, 91],
	 	 [20, 21, 0, 32, 0, 52, 0, 72, 82, 0],
	 	 [30, 0, 32, 0, 43, 0, 63, 73, 0, 93],
	 	 [0, 0, 0, 43, 0, 0, 0, 74, 84, 0],
	 	 [50, 51, 52, 0, 0, 0, 65, 0, 85, 95],
	 	 [60, 0, 0, 63, 0, 65, 0, 0, 0, 96],
	 	 [70, 71, 72, 73, 74, 0, 0, 0, 87, 0],
	 	 [80, 0, 82, 0, 84, 85, 0, 87, 0, 98],
		 [90, 91, 0, 93, 0, 95, 96, 0, 98, 0]]

	for i in range(10):
		for j in range(10):
			costs[i, j] = L[i][j]

	start = time.time()

	# __main work__
	gen = Genetic(costs)
	# gen.generates(10000)
	# 동일한 코드
	for _ in iter.repeat(None, 1000): # # #
		gen.generate()



	print(time.time()-start)

	# __showing__
	gen._print()
	# gen._printAll()
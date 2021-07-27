import math
import time

class DivideConquer:
    def __init__(self, points, distance, cordinate):
        self.points = points
        self.solution = []
        self.distance = distance
        self.cordinate = cordinate

    def run(self):
        self.solution = self.solve(self.points)

        return self.solution

    def solve(self, points):
        if len(points) < 1:
            raise Exception("no city here!")
        elif len(points) == 1:
            return points[0]
        elif len(points) == 2:
            return [(points[0], points[1])]
        else:
            div_1, div_2 = self.split_points(points)
            graph_1 = self.solve(div_1)
            graph_2 = self.solve(div_2)
            merge = self.merge(graph_1, graph_2)

            return merge

    def split_points(self, points):
        middle = len(points) // 2
        points_by_x = sorted(points, key=lambda point: self.cordinate[point][1])
        points_by_y = sorted(points, key=lambda point: self.cordinate[point][0])

        if abs(self.cordinate[points_by_x[0]][1] - self.cordinate[points_by_x[-1]][1]) > \
                abs(self.cordinate[points_by_y[0]][0] - self.cordinate[points_by_y[-1]][0]):
            return points_by_x[:middle], points_by_x[middle:]
        else:
            return points_by_y[:middle], points_by_y[middle:]

    def merge(self, graph_1, graph_2):
        if isinstance(graph_1, int):
            graph_2.append((graph_1, graph_2[0][0]))
            graph_2.append((graph_1, graph_2[0][1]))
            return graph_2

        min_cost = math.inf
        # print(graph_1)
        for edge_1_id, (point_0, point_1) in enumerate(graph_1):
            for edge_2_id, (point_2, point_3) in enumerate(graph_2):
                cost = self.distance[point_0][point_2] + self.distance[point_1][point_3] - self.distance[point_0][point_1] - self.distance[point_1][point_2]
                cost2 = self.distance[point_0][point_3] + self.distance[point_1][point_2] - self.distance[point_0][point_1] - self.distance[point_1][point_2]

            if cost < min_cost:
                min_cost = cost
                min_edge_1 = (point_0, point_2)
                min_edge_2 = (point_1, point_3)
                old_edge_1_id = edge_1_id
                old_edge_2_id = edge_2_id
            if cost2 < min_cost:
                min_cost = cost
                min_edge_1 = (point_0, point_3)
                min_edge_2 = (point_1, point_2)
                old_edge_1_id = edge_1_id
                old_edge_2_id = edge_2_id

        if len(graph_1) + len(graph_2) > 4:
            del graph_1[old_edge_1_id]
            del graph_2[old_edge_2_id]
        elif len(graph_1) + len(graph_2) == 4:
            del graph_2[old_edge_2_id]
        graph_1.extend([min_edge_1, min_edge_2])
        graph_1.extend(graph_2)

        return graph_1


def tsp_dc(index, distance, cordinate):

    divide_process = DivideConquer(index, distance, cordinate)
    path = divide_process.run()

    path_index = [index[0]]
    route_check = True
    while route_check:

        for num, edge in enumerate(path):
            if edge[0] == path_index[-1]:
                path_index.append(edge[1])
                del path[num]
                continue
            elif edge[1] == path_index[-1]:
                path_index.append(edge[0])
                del path[num]
                continue
        if not path:
            del path_index[-1]
            route_check = False

    return path_index







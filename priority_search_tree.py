from tkinter import Tk, Canvas
import random
import math

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class DrawHandler:
    def __init__(self) -> None:
        self.window = Tk()
        self.window_x = 800
        self.window_y = 800
        self.canvas = Canvas(self.window, width=800, height=800)
        self.canvas.pack()
        self.points = []
        self.create_random_points()
        for point in self.points:
            self.print_point(point.x, point.y)
        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.canvas.bind("<Button-3>", self.handle_rclick)
        pst = PrioritySearchTree()
        pst.create(self.points)
        self.window.mainloop()

    def print_point(self, x, y):
        self.canvas.create_oval(x, y, x, y)

    def handle_lclick(self, event):
        pass

    def handle_rclick(self, event):
        pass

    def create_random_points(self):
        for i in range(10):
            x = random.randint(0, self.window_x)
            y = random.randint(0, self.window_y)
            self.points.append(Point(x, y))

class Node: 
    def __init__(self, point, l_child=None, r_child=None):
        self.l_child = l_child
        self.r_child = r_child
        self.point = point

class PrioritySearchTree:
    def __init__(self) -> None:
        self.root = None

    def half_list(self, points):
        n_points = len(points)
        midpoint = math.floor(n_points / 2)
        left_points = points[0:midpoint]
        right_points = points[midpoint:n_points]
        return left_points, right_points

    def find_max_point(self, points):
        max_y = 2 ** 32
        # root is point with lowest y coordinate, maybe generalize to arbitrary dimension
        max_idx = -1
        for idx, point in enumerate(points):
            if point.y < max_y:
                max_y = point.y
                max_idx = idx
        return points[max_idx], max_idx
    
    def create_node(self, points):
        # new node is at the max y coordinate
        max_point, max_idx = self.find_max_point(points)
        node = Node(max_point)
        del points[max_idx]
        return node

    def create(self, points):
        if not points:
            return
        self.root = self.create_node(points)
        points_sorted = sorted(points, key = lambda p: p.x)
        left_points, right_points = self.half_list(points_sorted)

        self.root.l_child = self.subdivide(left_points)
        self.root.r_child = self.subdivide(right_points)

    # TODO: fix
    def subdivide(self, points):
        new_node = self.create_node(points)
        # I don't think we really need this if check, because both sublists will be empty 
        # if not points:
        #     return new_node

        left_points, right_points = self.half_list(points)
        if left_points:
            new_node.l_child = self.subdivide(left_points)
        if right_points:
            new_node.r_child = self.subdivide(right_points)
        return new_node

pst = DrawHandler()
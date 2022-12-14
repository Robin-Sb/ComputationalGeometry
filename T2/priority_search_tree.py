from tkinter import Tk, Canvas, Entry, LEFT, Label, Button, BOTTOM
import random
import math
import time

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

# class is only used for handling the UI and storing a reference to the tree 
class DrawHandler:
    def __init__(self) -> None:
        self.benchmark = True
        self.window = Tk()
        self.canvas_x = 800
        self.canvas_y = 800
        self.canvas = Canvas(self.window, width=self.canvas_x, height=self.canvas_y)
        self.points = []
        
        # UI handling
        self.x_lb_field = Entry(self.window, text="x lower bound", bd=5)
        self.x_ub_field = Entry(self.window, text="x upper bound", bd=5)
        self.y_lb_field = Entry(self.window, text="y lower bound", bd=5)
        self.canvas.pack() 
        Label(self.window, text="x lower bound").pack(side=LEFT)
        self.x_lb_field.pack(side=LEFT)
        Label(self.window, text="x upper bound").pack(side=LEFT)
        self.x_ub_field.pack(side=LEFT)       
        Label(self.window, text="y lower bound").pack(side=LEFT)
        self.y_lb_field.pack(side=LEFT)       
        self.algo_start_button = Button(self.window, text="Search", command=self.query_pst)
        self.algo_start_button.pack(side=LEFT)

        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.canvas.bind("<Button-3>", self.handle_rclick)
        #self.create_random_points()

        self.window.mainloop()

    def query_pst(self):
        self.canvas.delete("all")
        x_lower = int(self.x_lb_field.get())
        x_upper = int(self.x_ub_field.get())
        y_lower = int(self.y_lb_field.get())
        # very simple benchmarking
        if self.benchmark:
            startTimeNaive = time.time()
            naive_result = self.computeNaiveSolution(x_lower, x_upper, y_lower)
            naive_result 
            print("time naive: " + str(time.time() - startTimeNaive))

        startTimePST = time.time()
        self.pst.query(x_lower, x_upper, y_lower)
        print("time pst: " + str(time.time() - startTimePST))
        print("Number of points: " + str(len(self.points)))
        print("Number of points observed: " + str(self.pst.count))

        for point in self.points:
            if point in self.pst.result:
                self.print_point(point.x, point.y, "orange")
            else:
                self.print_point(point.x, point.y, "black")
        print("Number of found points: " + str(len(self.pst.result)))
        self.print_box(x_lower, x_upper, 0, y_lower)

    def print_point(self, x, y, color="black"):
        self.canvas.create_oval(x, y, x, y, outline=color, width=2)

    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.print_point(x, y)
        self.points.append(Point(x, y))
        self.pst = PrioritySearchTree()
        self.pst.create(self.points)

    def handle_rclick(self, event):
        self.create_random_points()

    def print_box(self, x_min, x_max, y_min, y_max):
        self.canvas.create_rectangle(x_min, y_min, x_max, y_max, outline="blue")

    def computeNaiveSolution(self, x_lower, x_upper, y_lower):
        result = []
        for point in self.points:
            if point.x >= x_lower and point.x <= x_upper and point.y <= y_lower:
                result.append(point)
        return result
    
    def create_random_points(self):
        for i in range(1000):
            x = random.randint(0, self.canvas_x)
            y = random.randint(0, self.canvas_y)
            self.points.append(Point(x, y))
            self.print_point(x, y)
        self.pst = PrioritySearchTree()
        self.pst.create(self.points)

class Node: 
    def __init__(self, point):
        self.l_child = None
        self.r_child = None
        self.point = point
        self.x_divisor = -1

class PrioritySearchTree:
    def __init__(self) -> None:
        self.root = None

    # split list into left and right half according to x coordinate
    def half_list(self, points):
        n_points = len(points)
        mid_idx = math.floor(n_points / 2)
        left_points = points[0:mid_idx]
        right_points = points[mid_idx:n_points]
        if n_points % 2 == 0:
            x_divisor = (points[mid_idx - 1].x + points[mid_idx].x) / 2
        else: 
            x_divisor = (points[mid_idx - 1].x + points[mid_idx].x) / 2
        return left_points, right_points, x_divisor

    def find_max_point(self, points):
        top_y = 2 ** 32
        max_idx = -1
        for idx, point in enumerate(points):
            if point.y < top_y:
                top_y = point.y
                max_idx = idx
        return max_idx
    
    def create_node(self, points):
        # new node is at the max y coordinate
        top_idx = self.find_max_point(points)
        node = Node(points[top_idx])
        del points[top_idx]
        return node

    def assign_subnodes(self, node, points):
        left_points, right_points, x_divisor = self.half_list(points)
        node.x_divisor = x_divisor

        if left_points:
            node.l_child = self.subdivide(left_points)
        if right_points:
            node.r_child = self.subdivide(right_points)

    def create(self, input):
        points = input.copy()
        if not points:
            return
        self.root = self.create_node(points)
        if not points:
            return    
        points_sorted = sorted(points, key = lambda p: p.x)

        self.assign_subnodes(self.root, points_sorted)

    def subdivide(self, points) -> Node:
        new_node = self.create_node(points)
        if not points:
            return new_node
        self.assign_subnodes(new_node, points)
        return new_node

    def query(self, x_lower, x_upper, y_lower):
        self.count = 0
        self.result = set()
        self.rec_search(self.root, x_lower, x_upper, y_lower)
    
    def rec_search(self, node, x_lower, x_upper, y_lower):
        self.count += 1
        if node.point.y > y_lower:
            return
        
        if x_upper >= node.point.x and node.point.x >= x_lower:
            self.result.add(node.point)
        
        if x_lower <= node.x_divisor:
            if node.l_child:
                self.rec_search(node.l_child, x_lower, x_upper, y_lower)
        
        if x_upper >= node.x_divisor:
            if node.r_child:
                self.rec_search(node.r_child, x_lower, x_upper, y_lower)

dh = DrawHandler()
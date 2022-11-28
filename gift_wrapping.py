from tkinter import Tk, Canvas
from numpy import Infinity
import time

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class GiftWrapping:
    def __init__(self) -> None:
        self.points = []
        self.window = Tk()
        self.canvas = Canvas(self.window, width=600, height=600)
        self.canvas.pack()
        self.convex_hull = None
        self.pq = None
        self.qr = None
        for point in self.points:
            self.print_point(point.x, point.y)
        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.canvas.bind("<Button-3>", self.handle_rclick)
        self.window.mainloop()

    def read_points_from(self, file):
        points = []
        with open(file) as f:
            for line in f:
                x_str, y_str = line.split()
                coords = (float(x_str), float(y_str))
                points.append(Point(coords[0], coords[1]))
        return points
    
    def draw_convex_hull(self, points):
        if self.convex_hull:
            self.canvas.delete(self.convex_hull)
        poly_input = []
        for point in points:
            poly_input.append(point.x)
            poly_input.append(point.y)
        self.convex_hull = self.canvas.create_polygon(poly_input, outline="orange", fill="")

    def print_point(self, x, y):
        self.canvas.create_oval(x, y, x, y)

    def print_edge(self, x_start, y_start, x_end, y_end):
        self.canvas.create_line(x_start, x_end, y_start, y_end)

    def print_box(self, x_min, x_max, y_min, y_max):
        return self.canvas.create_rectangle(x_min, y_min, x_max, y_max)

    def handle_rclick(self, click_event):
        self.compute_convex_hull()
        self.canvas.delete(self.pq)
        self.canvas.delete(self.qr)
        self.pq = None
        self.qr = None

    def handle_lclick(self, click_event):
        x = self.canvas.canvasx(click_event.x)
        y = self.canvas.canvasy(click_event.y)
        self.print_point(x, y)
        self.points.append(Point(x, y))

    def draw_line_between(self, p, q, r):
        if self.pq:
            self.canvas.delete(self.pq)
        if self.qr:
            self.canvas.delete(self.qr)
        
        self.pq = self.canvas.create_line(p.x, p.y, q.x, q.y, fill="green")
        self.qr = self.canvas.create_line(q.x, q.y, r.x, r.y, fill="green")

    def compute_AABB(self):
        #arbitrary start value
        x_min = 2 ** 32
        x_max = -2 ** 32
        y_min = 2 ** 32
        y_max = -2 ** 32
        for point in self.points:
            if point.x < x_min:
                x_min = point.x
            if point.x > x_max:
                x_max = point.x
            if point.y < y_min:
                y_min = point.y
            if point.y > y_max:
                y_max = point.y
        return self.print_box(x_min, x_max, y_min, y_max)
    
    def compute_orientation(self, p, r, q):
        # cross product of q - p and q - r
        cp = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if cp > 0:
            return True
        else:
            return False

    def compute_convex_hull(self):
        # find minimum y coordinate
        start_point = Point(0, -Infinity)
        for point in self.points:
            if point.y > start_point.y:
                start_point = point
        
        convex_hull = [start_point]
        self.draw_convex_hull(convex_hull)
        while True:
            endpoint = self.points[0]
            for point_to_test in self.points:
                p = convex_hull[-1]
                q = endpoint
                r = point_to_test
                self.draw_line_between(p, q, r)
                self.window.update()
                time.sleep(0.3)
                if q == p or self.compute_orientation(p, q, r):
                    endpoint = point_to_test
            convex_hull.append(endpoint)
            self.draw_convex_hull(convex_hull)
            self.window.update()
            time.sleep(0.5)
            if endpoint == start_point:
                break
        return convex_hull

gw = GiftWrapping()
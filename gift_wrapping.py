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
        #self.current_rectangle = self.compute_AABB()
        # set this initially to a polygon around all points
        self.poly = None
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
        if self.poly:
            self.canvas.delete(self.poly)
        poly_input = []
        for point in points:
            poly_input.append(point.x)
            poly_input.append(point.y)
        self.poly = self.canvas.create_polygon(poly_input, outline="orange", fill="")

    def print_point(self, x, y):
        self.canvas.create_oval(x, y, x, y)

    def print_edge(self, x_start, y_start, x_end, y_end):
        self.canvas.create_line(x_start, x_end, y_start, y_end)

    def print_box(self, x_min, x_max, y_min, y_max):
        return self.canvas.create_rectangle(x_min, y_min, x_max, y_max)

    def handle_rclick(self, click_event):
        self.compute_convex_hull()

    def handle_lclick(self, click_event):
        x = self.canvas.canvasx(click_event.x)
        y = self.canvas.canvasy(click_event.y)
        self.print_point(x, y)
        self.points.append(Point(x, y))

    def compute_AABB(self):
        x_min = Infinity
        x_max = -Infinity
        y_min = Infinity
        y_max = -Infinity
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
                # we have to span a line here between self.points[-1] and endpoint
                # and then check if current_point is on the right of that line
                # q is (x, y), r is endpoint and p is self.points[-1] 
                if endpoint == convex_hull[-1] or self.compute_orientation(convex_hull[-1], endpoint, point_to_test):
                    endpoint = point_to_test
            convex_hull.append(endpoint)
            self.draw_convex_hull(convex_hull)
            self.window.update()
            time.sleep(0.5)
            if endpoint == start_point:
                break
        return convex_hull

gw = GiftWrapping()
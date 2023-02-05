from tkinter import Tk, Canvas, Button, Entry
import math
import random
import time

EPS = 0.0001
class Vec2:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class Circle:
    def __init__(self, x, y, r) -> None:
        self.x = x
        self.y = y
        self.r = r

    def encloses(self, point):
        dist = (point.x - self.x) ** 2 + (point.y - self.y) ** 2
        if dist < self.r ** 2 + EPS:
            return True
        return False

    def encloses_all(self, points):
        for point in points:
            if not self.encloses(point):
                return False
        return True 

class MSW:
    def __init__(self) -> None:
        self.points = []
        self.circle = None
        self.basis = []
        self.circle_log = []

    def generate_points(self, n, x_dim, y_dim, margin = 250):
        points = []
        for i in range(n):
            x = random.random() * (x_dim - margin) + (margin / 2)
            y = random.random() * (y_dim - margin) + (margin / 2)
            points.append(Vec2(x,y))
        self.points += points
        return points

    def encloses_all(self, circle):
        for point in self.points:
            if not circle.encloses(point):
                return False
        return True

    def construct_circle_2(self, p1, p2):
        x = (p1.x + p2.x) / 2
        y = (p1.y + p2.y) / 2
        r = math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) / 2
        return Circle(x, y, r)

    def construct_circle_3(self, p1, p2, p3):
        a2 = p1.x - p2.x
        a3 = p1.x - p3.x
        b2 = p1.y - p2.y
        b3 = p1.y - p3.y
        d1 = p1.x ** 2 + p1.y ** 2
        d2 = d1 - p2.x ** 2 - p2.y ** 2
        d3 = d1 - p3.x ** 2 - p3.y ** 2
        # this can be 0 in theory i think 
        ab = a3 * b2 - a2 * b3
        xa = (b2 * d3 - b3 * d2) / (ab * 2) - p1.x
        ya = (a3 * d2 - a2 * d3) / (ab * 2) - p1.y
        C = xa ** 2 + ya ** 2
        r = -((math.sqrt(4 * C)) / -2)
        return Circle(p1.x + xa, p1.y + ya, r)

    def enclosing_basis(self):
        b = self.basis
        if len(b) == 2:
            return self.construct_circle_2(b[0], b[1])
        else:
            return self.construct_circle_3(b[0], b[1], b[2])

    def extend_basis(self, p):
        for point in self.basis:
            circle = self.construct_circle_2(p, point)
            if circle.encloses_all(self.basis):
                self.basis = [point, p]
                return
        for i in range(0, len(self.basis) - 1):
            for j in  range(i + 1, len(self.basis)):
                p1 = self.basis[i]
                p2 = self.basis[j]
                circle_opt_0 = self.construct_circle_2(p1, p2)
                circle_opt_1 = self.construct_circle_2(p1, p)
                circle_opt_2 = self.construct_circle_2(p2, p)
                circle_opt_3 = self.construct_circle_3(p1, p2, p)
                if (not circle_opt_0.encloses(p) and 
                    not circle_opt_1.encloses(p2) and 
                    not circle_opt_2.encloses(p1) and 
                    circle_opt_3.encloses_all(self.basis)):
                    self.basis = [p, p1, p2]
                    return
    
    def check_if_in_basis(self, p):
        for pb in self.basis:
            if pb == p:
                return True
        return False

    # main method for msw
    def find_enclosing_circle(self):
        self.basis = random.sample(self.points, 2) # [self.points[0], self.points[1]]
        self.circle = self.construct_circle_2(self.basis[0], self.basis[1])
        # store a log of all circles for animation
        self.circle_log = []        
        i = 0
        n = len(self.points)
        while i < n:
            p = self.points[i]
            # if point does not violate, just increase the index by 1
            if self.check_if_in_basis(p):
                i += 1
                continue
            if self.circle and self.circle.encloses(p):
                i += 1
            # if one violates, compute a new basis with the violating point
            else:
                self.extend_basis(p)
                self.circle = self.enclosing_basis()
                self.circle_log.append(self.circle)
                i = 0
        return self.circle
    
    def solve_naive(self):
        min_r = 2 ** 32
        # check for all pairs whether one encloses all points (and is minimal)
        for i in range(len(self.points)):
            for j in range(len(self.points)):
                if i == j:
                    continue
                circle = self.construct_circle_2(self.points[i], self.points[j])
                if circle.encloses_all(self.points):
                    if circle.r < min_r:
                        min_r = circle.r
                        self.circle = circle

        # check for all 3-point pairs whether one encloses all points (and is minimal)
        for i in range(len(self.points)):
            for j in range(len(self.points)):
                for k in range(len(self.points)):
                    if i == j or j == k or k == i:
                        continue
                    circle = self.construct_circle_3(self.points[i], self.points[j], self.points[k])
                    if circle.encloses_all(self.points):
                        if circle.r < min_r:
                            min_r = circle.r
                            self.circle = circle
        return self.circle

class DrawHandler:
    def __init__(self) -> None:
        self.window = Tk()
        self.canvas_x = 800
        self.canvas_y = 800
        self.canvas = Canvas(self.window, width=self.canvas_x, height=self.canvas_y)
        self.canvas.pack()
        self.msw = MSW()
        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.circle_obj = None
        self.entry = Entry(self.window, text="Number of Points", bd=5)
        self.entry.pack()        
        self.tk_points = []
        self.tk_circles = []

        Button(self.window, text="Generate and Solve", command=self.gen_and_solve).pack()
        Button(self.window, text="Generate", command=self.generate).pack()
        Button(self.window, text="Solve", command=self.solve).pack()
        Button(self.window, text="Reset", command=self.reset).pack()
        self.window.mainloop()

    def draw_point(self, point):
        return self.canvas.create_oval(point.x -1, point.y - 1, point.x + 1, point.y + 1, fill="black")

    def draw_circle(self, circle, color, size):
        if self.circle_obj:
            self.canvas.delete(self.circle_obj)
        return self.canvas.create_oval(circle.x + circle.r, circle.y + circle.r, circle.x - circle.r, circle.y - circle.r, outline=color, width=size)

    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        point = Vec2(x, y)
        self.msw.points.append(point)
        new_point = self.draw_point(point)
        self.tk_points.append(new_point)    

    def generate(self):
        self.reset()
        n = int(self.entry.get())
        points = self.msw.generate_points(n, self.canvas_x, self.canvas_y, self.canvas_x / 3)
        if len(points) < 50000:
            for point in points:
                new_point = self.draw_point(point)
                self.tk_points.append(new_point)
        self.window.update()

    def clear_all(self):
        self.clear_circles()
        self.clear_points()

    def clear_points(self):
        for tk_point in self.tk_points:
            self.canvas.delete(tk_point)
        self.tk_points = []

    def clear_circles(self):
        for tk_circle in self.tk_circles:
            self.canvas.delete(tk_circle) 
        self.tk_circles = []

    def solve(self):
        if len(self.msw.points) < 2:
            print("At least two points needed")
            return
        self.clear_circles()
        start = time.time()
        circle_msw = self.msw.find_enclosing_circle()
        end = time.time()
        print("Center: " + str(circle_msw.x) + ", " + str(circle_msw.y) + ", radius: " + str(circle_msw.r))
        print("Time taken MSW: " + str(end - start))
        if len(self.msw.points) < 50000:
            self.animate() 
        self.circle_obj = self.draw_circle(circle_msw, "pink", 3)
        self.tk_circles.append(self.circle_obj)
        self.window.update()
        
        if len(self.msw.points) < 200:
            start_naive = time.time()
            circle_naive = self.msw.solve_naive()
            end_naive = time.time()
            print("Center: " + str(circle_naive.x) + ", " + str(circle_naive.y) + ", radius: " + str(circle_naive.r))
            print("Time taken naive: " + str(end_naive - start_naive))
    
    def reset(self):
        self.clear_all()
        self.msw = MSW()

    def gen_and_solve(self):
        self.generate()
        self.solve()

    def animate(self):
        for circle in self.msw.circle_log:
            tk_circle = self.draw_circle(circle, "green", 1)
            self.tk_circles.append(tk_circle)
            self.window.update()
            time.sleep(0.5)

dh = DrawHandler()
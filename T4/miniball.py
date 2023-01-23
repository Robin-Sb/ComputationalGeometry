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
        # maybe take care of floating point precision here
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

    def encloses_all(self, circle):
        for point in self.points:
            if not circle.encloses(point):
                return False
        return True
    
    def test_circle(self):
        if len(self.points) == 3:
            return self.construct_circle_3(self.points[0], self.points[1], self.points[2])
        return None

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
        # this can be 0 somehow
        # in theory by chance i guess 
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
                #self.circle = circle
                return
        for i in range(0, len(self.basis) - 1):
            for j in  range(i + 1, len(self.basis)):
                p1 = self.basis[i]
                p2 = self.basis[j]
                old_circle = self.construct_circle_2(p1, p2)
                circle_opt_1 = self.construct_circle_2(p1, p)
                circle_opt_2 = self.construct_circle_2(p2, p)
                circle_opt_3 = self.construct_circle_3(p1, p2, p)
                if (not old_circle.encloses(p) and 
                    not circle_opt_1.encloses(p2) and 
                    not circle_opt_2.encloses(p1) and 
                    circle_opt_3.encloses_all([p, p1, p2])):
                    self.basis = [p, p1, p2]
                    return
    
    def check_if_in_basis(self,p):
        for pb in self.basis:
            if pb == p:
                return True
        return False

    def find_enclosing_circle(self):
        self.basis = [self.points[0], self.points[1]]
        self.circle = self.construct_circle_2(self.basis[0], self.basis[1])
        i = 0
        n = len(self.points)
        while i < n:
            p = self.points[i]
            if self.check_if_in_basis(p):
                i += 1
                continue
            if self.circle and self.circle.encloses(p):
                i += 1
            else:
                self.extend_basis(p)
                self.circle = self.enclosing_basis()
                i = 0
        return self.circle
    
    def solve_naive(self):
        min_r = 2 ** 32
        for i in range(len(self.points)):
            for j in range(len(self.points)):
                if i == j:
                    continue
                circle = self.construct_circle_2(self.points[i], self.points[j])
                if circle.encloses_all(self.points):
                    if circle.r < min_r:
                        min_r = circle.r
                        self.circle = circle

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
        self.canvas_x = 600
        self.canvas_y = 600
        self.canvas = Canvas(self.window, width=self.canvas_x, height=self.canvas_y)
        self.canvas.pack()
        self.msw = MSW()
        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.circle_obj = None
        Button(self.window, text="Solve", command=self.solve).pack()
        self.window.mainloop()

    def draw_point(self, point):
        return self.canvas.create_oval(point.x -1, point.y - 1, point.x + 1, point.y + 1)

    def draw_circle(self, circle):
        if self.circle_obj:
            self.canvas.delete(self.circle_obj)
        return self.canvas.create_oval(circle.x + circle.r, circle.y + circle.r, circle.x - circle.r, circle.y - circle.r)

    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        point = Vec2(x, y)
        self.msw.points.append(point)
        self.draw_point(point)    

    def solve(self):
        #circle = self.msw.find_enclosing_circle()
        circle = self.msw.solve_naive()
        self.circle_obj = self.draw_circle(circle)

dh = DrawHandler()
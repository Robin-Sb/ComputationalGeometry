from tkinter import Tk, Canvas, Button, Entry
import math
import random
import time

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
        if dist < self.r ** 2:
            return True
        return False

class MSW:
    def __init__(self) -> None:
        self.points = []
        self.circle = None

    def encloses_all(self):
        for point in self.points:
            if not self.circle.encloses(point):
                return False
        return True
    
    def test_circle(self):
        if len(self.points) == 3:
            return self.construct_circle_3(self.points[0], self.points[1], self.points[2])
        return None

    def construct_circle_2(self, p1, p2):
        x = (p1.x + p2.x) / 2
        y = (p1.y + p2.y) / 2
        r = (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
        return Circle(x, y, r)

    def construct_circle_3(self, p1, p2, p3):
        a2 = p1.x - p2.x
        a3 = p1.x - p3.x
        b2 = p1.y - p2.y
        b3 = p1.y - p3.y
        c2 = 0
        c3 = 0
        d1 = p1.x ** 2 + p1.y ** 2
        d2 = d1 - p2.x ** 2 - p2.y ** 2
        d3 = d1 - p3.x ** 2 - p3.y ** 2
        ab = a3 * b2 - a2 * b3
        xa = (b2 * d3 - b3 * d2) / (ab * 2) - p1.x
        xb = (b3 * c2 - b2 * c3) / ab
        ya = (a3 * d2 - a2 * d3) / (ab * 2) - p1.y
        yb = (a2 * c3 - a3 * c2) / ab
        A = xb ** 2 + yb ** 2 - 1
        B = 2 * (xa * xb + ya * yb)
        C = xa ** 2 + ya ** 2
        if A:
            r = (B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
        else:
            r = C / B
        return Circle(p1.x + xa + xb, p1.y + ya + yb, r)

class DrawHandler:
    def __init__(self) -> None:
        self.window = Tk()
        self.canvas_x = 800
        self.canvas_y = 800
        self.canvas = Canvas(self.window, width=self.canvas_x, height=self.canvas_y)
        self.canvas.pack()
        # self.start_pos = None
        # self.end_pos = None
        self.msw = MSW()
        self.canvas.bind("<Button-1>", self.handle_lclick)
        #self.points = []
        self.window.mainloop()

    def draw_point(self, point):
        point_idx = self.canvas.create_oval(point.x -1, point.y - 1, point.x + 1, point.y + 1)

    def draw_circle(self, circle):
        self.canvas.create_oval(circle.x + circle.r, circle.y + circle.r, circle.x - circle.r, circle.y - circle.r)

    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        point = Vec2(x, y)
        self.msw.points.append(point)
        self.draw_point(point)    
        circle = self.msw.test_circle()
        if circle:
            self.draw_circle(circle)

dh = DrawHandler()
from tkinter import Tk, Canvas, Button
import math

class Vec2:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class Constraint:
    def __init__(self, start, end) -> None:
        self.p1 = start 
        self.p2 = end
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        length = math.sqrt(dx ** 2 + dy ** 2)
        self.normal = Vec2(-dy / length, dx / length)
        self.m = dy / dx
        self.b = start.y - self.m * start.x
        # self.x_term = -m
        # self.y_term = 1
        # self.b = intercept

class LinearProgram:
    def __init__(self) -> None:
        self.constraints = []

    def add_constraint(self, start, end):
        constraint = Constraint(start, end)
        self.constraints.append(constraint)
        return constraint

    def compute_intersection(self, l1, l2):
        # intersect_x = (l1.y_term * l2.b - l2.y_term * l1.b) / (l1.x_term * l2.y_term - l2.x_term * l1.y_term)
        # intersect_y = (l1.b * l2.x_term - l2.b * l1.x_term) / (l1.x_term * l2.y_term - l2.x_term * l1.y_term)
        # x1 = l1.p1.x
        # x2 = l1.p2.x
        # x3 = l2.p1.x
        # x4 = l2.p2.x
        # y1 = l1.p1.y
        # y2 = l1.p2.y
        # y3 = l2.p1.y
        # y4 = l2.p2.y

        # denom = (x1 - x2)*(y3-y4) - (y1-y2)*(x3-x4)
        
        # px = (x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)/denom
        # py = (x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)/denom

        x = (l2.b - l1.b) / (l1.m - l2.m)
        y = l1.m * x + l1.b
        return Vec2(x, y)

    def prune(self):
        up = []
        down = []
        for constraint in self.constraints:
            if constraint.normal.y > 0:
                up.append(constraint)
            else:
                down.append(constraint)
        
        if len(up) and len(down) < 2:
            return

        if len(down) >= 2:
            intersection = self.compute_intersection(down[0], down[1])
        elif (len(up) >= 2):
            intersection = self.compute_intersection(up[0], up[1])
        
        

class DrawHandler:
    def __init__(self) -> None:
        self.window = Tk()
        self.canvas_x = 600
        self.canvas_y = 600
        self.canvas = Canvas(self.window, width=self.canvas_x, height=self.canvas_y)
        self.canvas.pack()
        self.start_pos = None
        self.end_pos = None
        self.lp = LinearProgram()
        self.canvas.bind("<Button-1>", self.handle_lclick)
        self.canvas.bind("<Button-3>", self.handle_rclick)
        Button(self.window, text="Prune and Search", command=self.prune_and_search).pack()

        self.window.mainloop()

        
    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.start_pos = self.to_cartesian(Vec2(x, y))
        self.add_constraint()

    def handle_rclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.end_pos = self.to_cartesian(Vec2(x, y))
        self.add_constraint()

    def to_cartesian(self, point):
        x = 1 - (point.x / self.canvas_x)
        y = 1 - (point.y / self.canvas_y)
        return Vec2(x, y)

    def from_cartesian(self, point):
        x = self.canvas_x - (point.x * self.canvas_x)
        y = self.canvas_y - (point.y * self.canvas_y)
        return Vec2(x, y)

    def draw_line(self, start, end, color = "black"):
        p1 = self.from_cartesian(start)
        p2 = self.from_cartesian(end)
        self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, width=5, fill=color)

    def draw_constraint(self, constraint):
        y_right = constraint.m * 1 + constraint.b
        y_left = constraint.m * 0 + constraint.b
        x_bottom = (0 - constraint.b) / constraint.m
        x_top = (1 - constraint.b) / constraint.m
        points = []
        # theoretically there are two special cases:
        # vertical lines
        # diagonal lines, where the condition is true for 4 points
        # maybe take care of those later
        if y_right >= 0 and y_right <=1:
            points.append(Vec2(1, y_right))
        if y_left >= 0 and y_left <=1:
            points.append(Vec2(0, y_left))
        if x_bottom >= 0 and x_top <=1:
            points.append(Vec2(x_bottom, 0))
        if x_top >= 0 and x_top <= 1:
            points.append(Vec2(x_top, 1))
        self.draw_line(points[0], points[1])
        # normal
        midpoint = Vec2((constraint.p1.x + constraint.p2.x) / 2, (constraint.p1.y + constraint.p2.y) / 2)
        endpoint = Vec2(midpoint.x + constraint.normal.x * 0.05, midpoint.y + constraint.normal.y * 0.05)
        self.draw_line(midpoint, endpoint, "blue")
        

    # maybe call this from some other event instead of when points are set
    def add_constraint(self):
        if self.start_pos and self.end_pos:
            constraint = self.lp.add_constraint(self.start_pos, self.end_pos)
            self.draw_constraint(constraint)
            #self.draw_line(self.start_pos, self.end_pos)
            self.start_pos = None
            self.end_pos = None
    
    def draw_point(self, point):
        point = self.from_cartesian(point)
        self.canvas.create_oval(point.x - 5, point.y -5, point.x + 5, point.y + 5, fill="green")

    def prune_and_search(self):
        self.lp.prune()

dh = DrawHandler()
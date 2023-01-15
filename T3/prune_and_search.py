# paper: https://theory.stanford.edu/~megiddo/pdf/lp3.pdf

from tkinter import Tk, Canvas, Button
import math

# this is actually 2 ** 32 and not the real max int in python
MAX_INT = 4294967296
# floating point offset
EPS = 0.000001

class Vec2():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

def same_sign(x1, x2):
    return (x1 < 0) == (x2 < 0)

class Constraint:
    def __init__(self, start, end) -> None:
        if end.x > start.x:
            self.p1 = start 
            self.p2 = end
        else:
            self.p2 = start
            self.p1 = end
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        length = math.sqrt(dx ** 2 + dy ** 2)
        self.normal = Vec2(-(end.y - start.y) / length, (end.x - start.x) / length)
        self.m = dy / dx
        self.b = self.p1.y - self.m * self.p1.x

    def calc_y(self, x):
        return self.m * x + self.b

class LinearProgram:
    def __init__(self) -> None:
        self.constraints = []

    def add_constraint(self, start, end):
        constraint = Constraint(start, end)
        self.constraints.append(constraint)
        return constraint

    def compute_intersection(self, l1, l2):
        x = (l2.b - l1.b) / (l1.m - l2.m)
        y = l1.m * x + l1.b
        return Vec2(x, y)
    
    # this one seems to work
    def brute_force(self, constraints):
        result = Vec2(0, MAX_INT)
        feasible = False
        for i, c1 in enumerate(constraints):
            for j, c2 in enumerate(constraints):
                if i == j:
                    continue
                intersection = self.compute_intersection(c1, c2)
                local_feasible = True
                for k, c3 in enumerate(constraints):
                    if k == i or k == j:
                        continue
                    y = c3.calc_y(intersection.x)
                    if same_sign(y - intersection.y, c3.normal.y):
                        local_feasible = False
                if not local_feasible:
                    continue
                feasible = True
                if intersection.y < result.y:
                    result = intersection
        if feasible:
            return result
        else:
            return None

    def generate_tuple(self, constraint_list):
        length = len(constraint_list)
        if length < 2:
            return None
        result = []
        for idx in range(0, length - length % 2, 2):
            result.append((constraint_list[idx], constraint_list[idx + 1]))
        return result

    def find_median(self, pairs):
        intersections = []
        for constraint1, constraint2 in pairs:
            intersection = self.compute_intersection(constraint1, constraint2)
            intersections.append(intersection)
        median_x = intersections[math.floor(len(intersections) / 2)].x
        median_y = intersections[math.floor(len(intersections) / 2)].y        
        return Vec2(median_x, median_y)

    def find_bound(self, constraints, median, isUp):
        bound = []
        if isUp:
            value = -MAX_INT
        else: 
            value = MAX_INT
        for constraint in constraints:
            y_intersect = constraint.calc_y(median.x) 
            # constraint that fulfills 'value' with equality
            if abs(value - y_intersect) < EPS:
                bound.append(constraint)
            elif (isUp and y_intersect > value) or (not isUp and y_intersect < value):
                value = y_intersect
                bound = [constraint]
        return value, bound

    def find_slopes(self, bound):
        val_min = MAX_INT
        val_max = -MAX_INT
        for constraint in bound:
            val_min = min(constraint.m, val_min)
            val_max = max(constraint.m, val_max)
        return val_min, val_max

    # op is > in up case and < in down case
    def prune_one(self, pairs, a, b, out, op):
        if not pairs:
            return
        # op = >
        for l1, l2 in pairs:
            # we could also store this somewhere ig
            intersection = self.compute_intersection(l1, l2)
            if abs(l1.m - l2.m) < EPS:
                if op(l1.b, l2.b):
                    # this is not really linear anymore, fix later
                    out.remove(l1)
                else:
                    out.remove(l2)
            # intersection is left of lower bound
            elif (intersection.x - EPS) < a:
                # remove constraint with lower slope
                if op(l1.m, l2.m):
                    out.remove(l2)
                else:
                    out.remove(l1)
            elif (intersection.x + EPS) > b:
                # remove constraint with higher slope
                if op(l1.m, l2.m):
                    out.remove(l1)
                else:
                    out.remove(l2)

    def prune(self, up_pairs, down_pairs, a, b, up, down):
        self.prune_one(up_pairs, a, b, up, lambda x, y: x > y)
        self.prune_one(down_pairs, a, b, down, lambda x, y: x < y)
        return up, down

    def prune_and_search(self, up, down):
        a = -MAX_INT
        b = MAX_INT
        while (len(up) + len(down)) > 4:
            up_pairs = self.generate_tuple(up)
            down_pairs = self.generate_tuple(down)
            if len(up) >= len(down):
                pairs = up_pairs
            else:
                pairs = down_pairs
            
            median = self.find_median(pairs)
            # g denotes the lower bound, so the maximum constraint where the normal points upwards (at pos x)
            g, lower = self.find_bound(up, median, True)
            # h denotes the upper bound
            # h seems wrong
            h, upper = self.find_bound(down, median, False)
            
            # min, max slope wrt g
            g_min, g_max = self.find_slopes(lower) #sg, Sg
            # min, max slope wrt h
            h_min, h_max = self.find_slopes(upper) #sh, Sh


            # point is not feasible, change interval in correct direction
            if g > h:
                # median is left of feasible region -> go right
                if g_min > h_max:
                    b = median.x
                # median is right of feasible region -> go left
                if g_max < h_min:
                    a = median.x
                # no feasible solution exists
                if g_min <= h_max and g_max >= h_min:
                    return None

            # point is feasible, check which constraints to prune
            elif g < h:
                if g_min > 0:
                    b = median.x
                if g_max < 0:
                    a = median.x
                # optimal solution
                if g_min < 0 and g_max > 0:
                    return median
            # point is feasible and g = h
            # somewhat theoretical case because of floating point precision
            # i could see that this actually returns wrong results if two lines are exactly the same, one pointing up and one down
            # and the one pointing up is slightly shifted above because of floating point precision
            else:
                if g_min > 0 and g_min >= h_max:
                    b = median.x
                if g_max < 0 and g_max <= h_min:
                    a = median.x
                # optimal solution
                if g_min < 0 and g_max > 0:
                    return median
            up, down = self.prune(up_pairs, down_pairs, a, b, up, down)                    
        return self.brute_force(up + down)

    def solve(self):
        #return self.brute_force(self.constraints)
        up = []
        down = []
        for constraint in self.constraints:
            if constraint.normal.y > 0:
                up.append(constraint)
            else:
                down.append(constraint)
    
        return self.prune_and_search(up, down)

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
        Button(self.window, text="Prune and Search", command=self.solve_lp).pack()
        self.add_constraint(Vec2(500, 160), Vec2(100, 150)) 
        self.add_constraint(Vec2(100, 150), Vec2(120, 460))
        self.add_constraint(Vec2(200, 500), Vec2(310, 510))
        self.add_constraint(Vec2(450, 450), Vec2(440, 200))

        self.window.mainloop()

        
    def handle_lclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.start_pos = Vec2(x, y)
        self.add_constraint(self.start_pos, self.end_pos)

    def handle_rclick(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.end_pos = Vec2(x, y)
        self.add_constraint(self.start_pos, self.end_pos)

    def to_cartesian(self, point):
        x = point.x / self.canvas_x
        y = 1 - (point.y / self.canvas_y)
        return Vec2(x, y)

    def from_cartesian(self, point):
        x = point.x * self.canvas_x
        y = self.canvas_y - (point.y * self.canvas_y)
        return Vec2(x, y)

    def draw_line(self, start, end, color = "black"):
        p1 = self.from_cartesian(start)
        p2 = self.from_cartesian(end)
        self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, width=2, fill=color)

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
        if x_bottom >= 0 and x_bottom <=1:
            points.append(Vec2(x_bottom, 0))
        if x_top >= 0 and x_top <= 1:
            points.append(Vec2(x_top, 1))
        self.draw_line(points[0], points[1])
        # normal
        midpoint = Vec2((constraint.p1.x + constraint.p2.x) / 2, (constraint.p1.y + constraint.p2.y) / 2)
        endpoint = Vec2(midpoint.x + constraint.normal.x * 0.05, midpoint.y + constraint.normal.y * 0.05)
        self.draw_line(midpoint, endpoint, "blue")
        

    # maybe call this from some other event instead of when points are set
    def add_constraint(self, start, end):
        if start and end:
            p1 = self.to_cartesian(start)
            p2 = self.to_cartesian(end)
            constraint = self.lp.add_constraint(p1, p2)
            self.draw_constraint(constraint)
            #self.draw_line(self.start_pos, self.end_pos)
            self.start_pos = None
            self.end_pos = None
    
    def draw_point(self, point):
        point = self.from_cartesian(point)
        self.canvas.create_oval(point.x - 5, point.y - 5, point.x + 5, point.y + 5, fill="green")

    def solve_lp(self):
        result = self.lp.solve()
        if result:
            self.draw_point(result)

dh = DrawHandler()
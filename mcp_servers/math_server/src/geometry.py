import matplotlib.pyplot as plt
import numpy as np
import os
import math
import cmath

# Use non-interactive backend
plt.switch_backend('Agg')

# --- Analytic Geometry Classes ---

def solve_quadratic_internal(a, b, c):
    """
    Internal helper to solve ax^2 + bx + c = 0.
    Returns list of roots (real or complex).
    Uses the quadratic formula: (-b ± sqrt(b^2 - 4ac)) / 2a
    """
    if abs(a) < 1e-10:
        if abs(b) < 1e-10:
            return [] # No solution or infinite
        return [-c/b] # Linear solution
    
    delta = b**2 - 4*a*c
    sqrt_delta = cmath.sqrt(delta)
    r1 = (-b + sqrt_delta) / (2*a)
    r2 = (-b - sqrt_delta) / (2*a)
    
    # Clean up small imaginary parts
    roots = []
    for r in [r1, r2]:
        if abs(r.imag) < 1e-10:
            roots.append(r.real)
        else:
            roots.append(r)
    return roots

class AnalyticShape:
    def get_x(self, y: float) -> list[float]:
        raise NotImplementedError
    def get_y(self, x: float) -> list[float]:
        raise NotImplementedError
    def get_equation_string(self) -> str:
        raise NotImplementedError
    def get_general_coeffs(self):
        """Returns A, C, D, E, F for Ax^2 + Cy^2 + Dx + Ey + F = 0"""
        raise NotImplementedError
    def plot_on_ax(self, ax, x_range):
        pass

class Line(AnalyticShape):
    def __init__(self, A: float, B: float, C: float):
        # Ax + By + C = 0
        self.A = float(A)
        self.B = float(B)
        self.C = float(C)

    def get_x(self, y: float) -> list[float]:
        # Ax = -By - C
        if abs(self.A) < 1e-10:
            return [] # Horizontal line, undefined x for specific y unless consistent
        return [(-self.B * y - self.C) / self.A]

    def get_y(self, x: float) -> list[float]:
        # By = -Ax - C
        if abs(self.B) < 1e-10:
            return [] # Vertical line
        return [(-self.A * x - self.C) / self.B]

    def get_equation_string(self) -> str:
        return f"{self.A}x + {self.B}y + {self.C} = 0"
    
    def get_general_coeffs(self):
        # 0x^2 + 0y^2 + Ax + By + C = 0
        return (0, 0, self.A, self.B, self.C)

    def plot_on_ax(self, ax, x_range):
        # Plot line across the view
        # If B != 0, y = (-Ax-C)/B
        if abs(self.B) > 1e-10:
            xs = np.array(x_range)
            ys = (-self.A * xs - self.C) / self.B
            ax.plot(xs, ys, label=self.get_equation_string())
        else:
            # Vertical line x = -C/A
            x_val = -self.C / self.A
            ax.axvline(x=x_val, linestyle='--', label=self.get_equation_string())

class Circle(AnalyticShape):
    def __init__(self, h: float, k: float, r: float):
        self.h = float(h)
        self.k = float(k)
        self.r = float(r)

    def get_x(self, y: float) -> list[float]:
        # (x-h)^2 = r^2 - (y-k)^2
        # x = h ± sqrt(...)
        term = self.r**2 - (y - self.k)**2
        if term < 0: return []
        if term == 0: return [self.h]
        s = math.sqrt(term)
        return [self.h + s, self.h - s]

    def get_y(self, x: float) -> list[float]:
        term = self.r**2 - (x - self.h)**2
        if term < 0: return []
        if term == 0: return [self.k]
        s = math.sqrt(term)
        return [self.k + s, self.k - s]

    def get_equation_string(self) -> str:
        return f"(x - {self.h})^2 + (y - {self.k})^2 = {self.r**2}"

    def get_general_coeffs(self):
        # x^2 - 2hx + h^2 + y^2 - 2ky + k^2 - r^2 = 0
        # A=1, C=1, D=-2h, E=-2k, F=h^2+k^2-r^2
        return (1, 1, -2*self.h, -2*self.k, self.h**2 + self.k**2 - self.r**2)

    def plot_on_ax(self, ax, x_range):
        theta = np.linspace(0, 2*np.pi, 100)
        x = self.h + self.r * np.cos(theta)
        y = self.k + self.r * np.sin(theta)
        ax.plot(x, y, label='Circle')

class Ellipse(AnalyticShape):
    def __init__(self, h: float, k: float, a: float, b: float):
        self.h, self.k, self.a, self.b = float(h), float(k), float(a), float(b)

    def get_y(self, x: float) -> list[float]:
        # (y-k)^2 / b^2 = 1 - (x-h)^2 / a^2
        term = 1 - ((x - self.h) / self.a)**2
        if term < 0: return []
        val = self.b * math.sqrt(term)
        return [self.k + val, self.k - val]

    def get_x(self, y: float) -> list[float]:
        term = 1 - ((y - self.k) / self.b)**2
        if term < 0: return []
        val = self.a * math.sqrt(term)
        return [self.h + val, self.h - val]

    def get_equation_string(self) -> str:
        return f"(x-{self.h})^2/{self.a**2} + (y-{self.k})^2/{self.b**2} = 1"

    def get_general_coeffs(self):
        # b^2(x-h)^2 + a^2(y-k)^2 - a^2b^2 = 0
        # b^2(x^2 - 2hx + h^2) + a^2(y^2 - 2ky + k^2) - a^2b^2 = 0
        A = self.b**2
        C = self.a**2
        D = -2 * self.b**2 * self.h
        E = -2 * self.a**2 * self.k
        F = self.b**2 * self.h**2 + self.a**2 * self.k**2 - self.a**2 * self.b**2
        return (A, C, D, E, F)

    def plot_on_ax(self, ax, x_range):
        theta = np.linspace(0, 2*np.pi, 100)
        x = self.h + self.a * np.cos(theta)
        y = self.k + self.b * np.sin(theta)
        ax.plot(x, y, label='Ellipse')

class Hyperbola(AnalyticShape):
    def __init__(self, h: float, k: float, a: float, b: float, orientation: str = 'x'):
        # orientation 'x': (x-h)^2/a^2 - (y-k)^2/b^2 = 1
        # orientation 'y': (y-k)^2/a^2 - (x-h)^2/b^2 = 1
        self.h, self.k, self.a, self.b = float(h), float(k), float(a), float(b)
        self.orientation = orientation

    def get_equation_string(self) -> str:
        if self.orientation == 'x':
            return f"(x-{self.h})^2/{self.a**2} - (y-{self.k})^2/{self.b**2} = 1"
        return f"(y-{self.k})^2/{self.a**2} - (x-{self.h})^2/{self.b**2} = 1"

    def get_general_coeffs(self):
        if self.orientation == 'x':
            # b^2(x-h)^2 - a^2(y-k)^2 - a^2b^2 = 0
            A = self.b**2
            C = -self.a**2
            D = -2 * self.b**2 * self.h
            E = 2 * self.a**2 * self.k
            F = self.b**2 * self.h**2 - self.a**2 * self.k**2 - self.a**2 * self.b**2
        else:
            # b^2(y-k)^2 - a^2(x-h)^2 - a^2b^2 = 0 -> -a^2(x-h)^2 + b^2(y-k)^2 - a^2b^2 = 0
            A = -self.a**2 # coeff of x^2
            C = self.b**2  # coeff of y^2
            D = 2 * self.a**2 * self.h
            E = -2 * self.b**2 * self.k
            F = -self.a**2 * self.h**2 + self.b**2 * self.k**2 - self.a**2 * self.b**2
        return (A, C, D, E, F)
    
    def get_y(self, x: float) -> list[float]:
        # Implement evaluating y for plotting points
        # For 'x': (y-k)^2 = b^2 * ((x-h)^2/a^2 - 1)
        if self.orientation == 'x':
            term = ((x - self.h)/self.a)**2 - 1
            if term < 0: return []
            val = self.b * math.sqrt(term)
            return [self.k + val, self.k - val]
        else:
            # (y-k)^2/a^2 = 1 + (x-h)^2/b^2 -> always solvable
            term = 1 + ((x - self.h)/self.b)**2
            val = self.a * math.sqrt(term)
            return [self.k + val, self.k - val]

    def get_x(self, y: float) -> list[float]:
         # Similar to get_y... (omitted for brevity, can implement if needed)
         return []

    def plot_on_ax(self, ax, x_range):
        # Parametric plot
        t = np.linspace(-2, 2, 100) # limited hyperbolic range
        cosh_t = np.cosh(t)
        sinh_t = np.sinh(t)
        
        if self.orientation == 'x':
            # Right branch
            x1 = self.h + self.a * cosh_t
            y1 = self.k + self.b * sinh_t
            ax.plot(x1, y1, 'g')
            # Left branch
            x2 = self.h - self.a * cosh_t
            y2 = self.k + self.b * sinh_t
            ax.plot(x2, y2, 'g', label='Hyperbola')
        else:
            # Top branch
            y1 = self.k + self.a * cosh_t
            x1 = self.h + self.b * sinh_t
            ax.plot(x1, y1, 'g')
            # Bottom branch
            y2 = self.k - self.a * cosh_t
            x2 = self.h + self.b * sinh_t
            ax.plot(x2, y2, 'g', label='Hyperbola')

class Parabola(AnalyticShape):
    def __init__(self, h: float, k: float, p: float, orientation: str = 'up'):
        self.h, self.k, self.p = float(h), float(k), float(p)
        self.orientation = orientation
    
    def get_equation_string(self) -> str:
        if self.orientation == 'up': return f"(x-{self.h})^2 = {2*self.p}(y-{self.k})"
        if self.orientation == 'down': return f"(x-{self.h})^2 = -{2*self.p}(y-{self.k})"
        if self.orientation == 'right': return f"(y-{self.k})^2 = {2*self.p}(x-{self.h})"
        if self.orientation == 'left': return f"(y-{self.k})^2 = -{2*self.p}(x-{self.h})"
        return "Unknown Parabola"

    def get_general_coeffs(self):
        # Returns A, C, D, E, F
        if self.orientation == 'up':
            # x^2 - 2hx + h^2 - 2py + 2pk = 0
            return (1, 0, -2*self.h, -2*self.p, self.h**2 + 2*self.p*self.k)
        elif self.orientation == 'down':
             # x^2 - 2hx + h^2 = -2py + 2pk -> x^2 - 2hx + 2py + h^2 - 2pk = 0
             return (1, 0, -2*self.h, 2*self.p, self.h**2 - 2*self.p*self.k)
        elif self.orientation == 'right':
             # y^2 - 2ky + k^2 - 2px + 2ph = 0
             return (0, 1, -2*self.p, -2*self.k, self.k**2 + 2*self.p*self.h)
        elif self.orientation == 'left':
              # y^2 - 2ky + k^2 + 2px - 2ph = 0
             return (0, 1, 2*self.p, -2*self.k, self.k**2 - 2*self.p*self.h)
        return (0,0,0,0,0)

    def get_y(self, x: float) -> list[float]:
        # 'up': y = k + (x-h)^2/2p
        if self.orientation == 'up':
            return [self.k + (x - self.h)**2 / (2*self.p)]
        if self.orientation == 'down':
            return [self.k - (x - self.h)**2 / (2*self.p)]
        # 'right': (y-k)^2 = 2p(x-h) -> y = k +- sqrt(...)
        if self.orientation == 'right':
            term = 2*self.p*(x - self.h)
            if term < 0: return []
            return [self.k + math.sqrt(term), self.k - math.sqrt(term)]
        if self.orientation == 'left':
             term = -2*self.p*(x - self.h)
             if term < 0: return []
             return [self.k + math.sqrt(term), self.k - math.sqrt(term)]
        return []
    
    def get_x(self, y: float) -> list[float]:
        # Implement symmetrical logic if needed...
        return []

    def plot_on_ax(self, ax, x_range):
        # For x-based parabolas (up/down)
        if self.orientation in ['up', 'down']:
            xs = np.array(x_range)
            if self.orientation == 'up':
                ys = self.k + (xs - self.h)**2 / (2*self.p)
            else:
                ys = self.k - (xs - self.h)**2 / (2*self.p)
            ax.plot(xs, ys, label='Parabola')
        else:
            # y-based via parametric t
            t = np.linspace(-10, 10, 100)
            ys = self.k + t
            if self.orientation == 'right':
                xs = self.h + t**2 / (2*self.p)
            else:
                xs = self.h - t**2 / (2*self.p)
            ax.plot(xs, ys, label='Parabola')


class Geometry2D:
    def __init__(self):
        self.points = {}
        self.segments = []  # List of (label1, label2)
        self.vectors = []   # List of (start_label, end_label)
        self.circles = []   # Legacy list support might be needed or deprecated
        self.shapes = {}    # New dict for analytic shapes: label -> AnalyticShape

    def clear(self):
        self.points = {}
        self.segments = []
        self.vectors = []
        self.circles = []
        self.shapes = {}

    def add_analytic_shape(self, label: str, shape: AnalyticShape) -> str:
        self.shapes[label] = shape
        return f"Shape '{label}' added: {shape.get_equation_string()}"

    def get_intersection(self, label1: str, label2: str) -> str:
        """Finds intersection points between two shapes."""
        if label1 not in self.shapes or label2 not in self.shapes:
            raise ValueError("Shapes not found")
        
        s1 = self.shapes[label1]
        s2 = self.shapes[label2]
        
        # Dispatch logic
        # 1. Check if one is Line
        line_shape = None
        other_shape = None
        
        if isinstance(s1, Line):
            line_shape = s1
            other_shape = s2
        elif isinstance(s2, Line):
            line_shape = s2
            other_shape = s1
            
        if line_shape:
            return self._intersect_line_conic(line_shape, other_shape)
            
        # 2. Check Line-Line (covered above if both are Lines)
        # 3. Two non-Line Conics
        return f"Intersection between {type(s1).__name__} and {type(s2).__name__} is not yet supported."

    def _intersect_line_conic(self, line: Line, conic: AnalyticShape) -> str:
        # Line: Ax + By + C = 0
        # Conic: A2 x^2 + C2 y^2 + D2 x + E2 y + F2 = 0 (General Coeffs)
        
        A, B, C = line.A, line.B, line.C
        A2, C2, D2, E2, F2 = conic.get_general_coeffs()
        
        points = []
        
        # Case 1: B != 0 -> y = -(A/B)x - (C/B) = mx + c_
        if abs(B) > 1e-10:
            m = -A / B
            c_ = -C / B
            
            # Substitute y into Conic
            # A2 x^2 + C2 (mx+c_)^2 + D2 x + E2 (mx+c_) + F2 = 0
            # A2 x^2 + C2 (m^2 x^2 + 2mc_ x + c_^2) + ...
            # Coeff of x^2: A2 + C2 m^2
            # Coeff of x: 2 C2 m c_ + D2 + E2 m
            # Constant: C2 c_^2 + E2 c_ + F2
            
            qa = A2 + C2 * m**2
            qb = 2 * C2 * m * c_ + D2 + E2 * m
            qc = C2 * c_**2 + E2 * c_ + F2
            
            x_roots = solve_quadratic_internal(qa, qb, qc)
            for x in x_roots:
                # y = mx + c_
                if isinstance(x, complex):
                    y = m * x + c_
                    # points.append((x, y)) # Skip complex intersection for simpler output unless requested? 
                    # User asked for roots including complex in general, but intersection usually implies geometry on real plane.
                    # However, solve_quadratic_internal already helps.
                    # Let's stringify
                    points.append(f"({x:.2f}, {y:.2f})")
                else:
                    y = m * x + c_
                    points.append(f"({x:.2f}, {y:.2f})")
                    
        else:
            # Case 2: Vertical Line x = -C/A = k_
            if abs(A) < 1e-10:
                return "Invalid Line (0x + 0y + C = 0)"
            
            k_ = -C / A
            # Substitute x = k_
            # A2 k_^2 + C2 y^2 + D2 k_ + E2 y + F2 = 0
            # C2 y^2 + E2 y + (A2 k_^2 + D2 k_ + F2) = 0
            
            qa = C2
            qb = E2
            qc = A2 * k_**2 + D2 * k_ + F2
            
            y_roots = solve_quadratic_internal(qa, qb, qc)
            for y in y_roots:
                points.append(f"({k_:.2f}, {y:.2f})")
                
        return str(points)

    def eval_shape(self, label: str, val: float, axis: str = 'x') -> str:
        if label not in self.shapes: return "Shape not found"
        s = self.shapes[label]
        if axis == 'x':
            res = s.get_y(val)
        else:
            res = s.get_x(val)
        return str(res)

    def add_point(self, label: str, x: float, y: float):
        self.points[label] = np.array([float(x), float(y)])
        return f"Point {label} added at ({x}, {y})"

    def add_segment(self, label1: str, label2: str):
        if label1 not in self.points or label2 not in self.points:
            raise ValueError("One or both points not defined")
        self.segments.append((label1, label2))
        return f"Segment {label1}-{label2} added"

    def distance(self, label1: str, label2: str) -> float:
        if label1 not in self.points or label2 not in self.points:
            raise ValueError("Points not defined")
        p1 = self.points[label1]
        p2 = self.points[label2]
        return float(np.linalg.norm(p1 - p2))

    def plot(self, filename: str = "plot_2d.png") -> str:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Determine view range. Default to -10, 10 unless points exist
        x_min, x_max = -10, 10
        if self.points:
            xs = [p[0] for p in self.points.values()]
            if xs:
                x_min, x_max = min(xs)-2, max(xs)+2
        
        x_range = np.linspace(x_min, x_max, 400)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(x_min, x_max) # Keep square aspect ratio roughly

        # Plot analytic shapes
        for label, shape in self.shapes.items():
            shape.plot_on_ax(ax, x_range)

        # Plot segments
        for l1, l2 in self.segments:
            p1 = self.points[l1]
            p2 = self.points[l2]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-')

        # Plot points
        for label, coord in self.points.items():
            ax.plot(coord[0], coord[1], 'ro')
            ax.text(coord[0]+0.1, coord[1]+0.1, label, fontsize=12)

        ax.set_aspect('equal')
        ax.grid(True)
        ax.legend()
        
        # Save
        full_path = os.path.abspath(filename)
        plt.savefig(full_path)
        plt.close()
        return full_path



class Geometry3D:
    def __init__(self):
        self.points = {}
        self.segments = []
        
    def clear(self):
        self.points = {}
        self.segments = []

    def add_point(self, label: str, x: float, y: float, z: float):
        self.points[label] = np.array([float(x), float(y), float(z)])
        return f"Point {label} added at ({x}, {y}, {z})"

    def add_segment(self, label1: str, label2: str):
        if label1 not in self.points or label2 not in self.points:
            raise ValueError("One or both points not defined")
        self.segments.append((label1, label2))
        return f"Segment {label1}-{label2} added"
        
    def distance(self, label1: str, label2: str) -> float:
        if label1 not in self.points or label2 not in self.points:
            raise ValueError("Points not defined")
        p1 = self.points[label1]
        p2 = self.points[label2]
        return float(np.linalg.norm(p1 - p2))

    def plot(self, filename: str = "plot_3d.png") -> str:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot segments
        for l1, l2 in self.segments:
            p1 = self.points[l1]
            p2 = self.points[l2]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'b-')

        # Plot points
        for label, coord in self.points.items():
            ax.scatter(coord[0], coord[1], coord[2], c='r', marker='o')
            ax.text(coord[0], coord[1], coord[2], label, fontsize=12)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Save
        full_path = os.path.abspath(filename)
        plt.savefig(full_path)
        plt.close()
        return full_path

# Global instances (State for the server)
scene_2d = Geometry2D()
scene_3d = Geometry3D()

# Wrapper functions for the MCP server tools

# 2D Tools - Analytic Geometry
def geo_2d_add_line(label: str, A: float, B: float, C: float) -> str:
    """Add a line Ax + By + C = 0"""
    return scene_2d.add_analytic_shape(label, Line(A, B, C))

def geo_2d_add_circle(label: str, h: float, k: float, r: float) -> str:
    """Add a circle (x-h)^2 + (y-k)^2 = r^2"""
    return scene_2d.add_analytic_shape(label, Circle(h, k, r))

def geo_2d_add_ellipse(label: str, h: float, k: float, a: float, b: float) -> str:
    """Add an ellipse (x-h)^2/a^2 + (y-k)^2/b^2 = 1"""
    return scene_2d.add_analytic_shape(label, Ellipse(h, k, a, b))

def geo_2d_add_hyperbola(label: str, h: float, k: float, a: float, b: float, orientation: str = 'x') -> str:
    """Add a hyperbola. orientation='x' -> (x-h)^2/a^2 - (y-k)^2/b^2 = 1. 'y' -> y term positive."""
    return scene_2d.add_analytic_shape(label, Hyperbola(h, k, a, b, orientation))

def geo_2d_add_parabola(label: str, h: float, k: float, p: float, orientation: str = 'up') -> str:
    """Add a parabola. 'up' -> (x-h)^2 = 2p(y-k), 'right' -> (y-k)^2 = 2p(x-h) etc."""
    return scene_2d.add_analytic_shape(label, Parabola(h, k, p, orientation))

def geo_2d_get_intersection(label1: str, label2: str) -> str:
    """Calculate intersection points between two analytic shapes (Line vs Conic supported)"""
    return scene_2d.get_intersection(label1, label2)

def geo_2d_eval_y(label: str, x: float) -> str:
    """Given x, calculate y values on the curve"""
    return scene_2d.eval_shape(label, x, axis='x')

def geo_2d_eval_x(label: str, y: float) -> str:
    """Given y, calculate x values on the curve"""
    return scene_2d.eval_shape(label, y, axis='y')

# 2D Tools - Basic
def geo_2d_clear() -> str:
    """Clear the 2D geometry scene"""
    scene_2d.clear()
    return "2D Scene cleared"

def geo_2d_add_point(label: str, x: float, y: float) -> str:
    """Add a point to the 2D scene"""
    return scene_2d.add_point(label, x, y)


def geo_2d_add_segment(label1: str, label2: str) -> str:
    """Add a line segment between two points in the 2D scene"""
    return scene_2d.add_segment(label1, label2)

def geo_2d_get_distance(label1: str, label2: str) -> float:
    """Calculate distance between two points in 2D"""
    return scene_2d.distance(label1, label2)

def geo_2d_plot() -> str:
    """Generate a plot of the 2D scene and return the file path"""
    return scene_2d.plot()

# 3D Tools
def geo_3d_clear() -> str:
    """Clear the 3D geometry scene"""
    scene_3d.clear()
    return "3D Scene cleared"

def geo_3d_add_point(label: str, x: float, y: float, z: float) -> str:
    """Add a point to the 3D scene"""
    return scene_3d.add_point(label, x, y, z)

def geo_3d_add_segment(label1: str, label2: str) -> str:
    """Add a line segment between two points in the 3D scene"""
    return scene_3d.add_segment(label1, label2)

def geo_3d_get_distance(label1: str, label2: str) -> float:
    """Calculate distance between two points in 3D"""
    return scene_3d.distance(label1, label2)

def geo_3d_plot() -> str:
    """Generate a plot of the 3D scene and return the file path"""
    return scene_3d.plot()

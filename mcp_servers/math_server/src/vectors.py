from sympy import symbols, Matrix, sympify, solve, latex, simplify
import numpy as np
import json
from src import geometry

def _parse_vector(v_input) -> Matrix:
    """
    Parses a vector input which can be:
    - A list/tuple of numbers or strings: [1, 2, 't']
    - A JSON string representing a list: "[1, 2, 3]"
    - A string representing a point label in scene_3d: "A"
    """
    if isinstance(v_input, str):
        # Check if it is a point label in the 3D scene
        if v_input in geometry.scene_3d.points:
            # It's a point label, convert to vector from origin
            pt = geometry.scene_3d.points[v_input]
            return Matrix([pt[0], pt[1], pt[2]])
        
        # Try JSON parse
        try:
            parsed = json.loads(v_input)
            if isinstance(parsed, list):
                return Matrix([sympify(x) for x in parsed])
        except json.JSONDecodeError:
            pass
            
        # Try parsing as a list string explicitly if json failed or it was not valid json
        # e.g. "a, b, c" -> [a, b, c]
        try:
            # Evaluate as a sympy expression list?
            # Safer: Treat as single expression? No, it's a vector.
            # Let's assume input format is compliant
            pass
        except:
            pass
            
    if isinstance(v_input, (list, tuple)):
        return Matrix([sympify(x) for x in v_input])
    
    raise ValueError(f"Could not parse input as vector: {v_input}")

def vector_add(v1, v2) -> str:
    """v1 + v2"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    return str(list((vec1 + vec2)))

def vector_sub(v1, v2) -> str:
    """v1 - v2"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    return str(list((vec1 - vec2)))

def vector_scalar_mul(k, v) -> str:
    """k * v"""
    scalar = sympify(k)
    vec = _parse_vector(v)
    return str(list((scalar * vec)))

def vector_dot(v1, v2) -> str:
    """Dot product (Scalar product) v1 . v2"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    return str(vec1.dot(vec2))

def vector_cross(v1, v2) -> str:
    """Cross product (Vector product) v1 x v2"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    return str(list(vec1.cross(vec2)))

def vector_magnitude(v) -> str:
    """Magnitude (Length) of vector |v|"""
    vec = _parse_vector(v)
    return str(vec.norm())

def vector_angle_cos(v1, v2) -> str:
    """Cosine of angle between v1 and v2"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    # cos(theta) = (v1 . v2) / (|v1|*|v2|)
    dot = vec1.dot(vec2)
    norm1 = vec1.norm()
    norm2 = vec2.norm()
    return str(simplify(dot / (norm1 * norm2)))

def vector_from_points(p1_label: str, p2_label: str) -> str:
    """
    Create vector from Point 1 to Point 2.
    Inputs can be point labels (in Geometry3D) or coordinate lists.
    """
    vec1 = _parse_vector(p1_label)
    vec2 = _parse_vector(p2_label)
    return str(list(vec2 - vec1))

def get_plane_normal(v1, v2) -> str:
    """
    Get normal vector of a plane defined by two non-collinear vectors.
    Returns v1 x v2.
    """
    return vector_cross(v1, v2)

def are_vectors_perpendicular(v1, v2) -> str:
    """Check if vectors are perpendicular (dot product is 0)"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    dot = vec1.dot(vec2)
    is_zero = simplify(dot) == 0
    return str(is_zero) + f" (Dot product: {dot})"

def are_vectors_parallel(v1, v2) -> str:
    """Check if vectors are parallel (cross product is 0)"""
    vec1 = _parse_vector(v1)
    vec2 = _parse_vector(v2)
    cross = vec1.cross(vec2)
    is_zero = cross == Matrix([0, 0, 0])
    return str(is_zero) + f" (Cross product: {list(cross)})"


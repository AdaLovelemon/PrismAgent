from mcp.server.fastmcp import FastMCP
from src import real_ops
from src import complex_ops
from src import calculus
from src import geometry
from src import equations
from src import symbolic
from src import vectors
from src import stats
from src import sequences

# Create an MCP server
mcp = FastMCP("Math Server")

# --- Basic Arithmetic ---
mcp.tool()(real_ops.add)
mcp.tool()(real_ops.subtract)
mcp.tool()(real_ops.multiply)
mcp.tool()(real_ops.divide)
mcp.tool()(real_ops.power)

# --- Complex Numbers ---
# Registering with custom names to avoid conflict with basic arithmetic tools
mcp.tool(name="complex_add")(complex_ops.add)
mcp.tool(name="complex_subtract")(complex_ops.subtract)
mcp.tool(name="complex_multiply")(complex_ops.multiply)
mcp.tool(name="complex_divide")(complex_ops.divide)
mcp.tool(name="complex_modulus")(complex_ops.modulus)
mcp.tool(name="complex_conjugate")(complex_ops.conjugate)
mcp.tool(name="complex_argument")(complex_ops.argument)

# --- Vectors (3D/Symbolic) ---
@mcp.tool(name="vector_add")
def vector_add(v1: str, v2: str) -> str:
    """Add two vectors. Inputs: list '[x,y,z]' or point label 'A'."""
    return vectors.vector_add(v1, v2)

@mcp.tool(name="vector_sub")
def vector_sub(v1: str, v2: str) -> str:
    """Subtract two vectors (v1 - v2). Inputs: '[x,y,z]' or 'A'."""
    return vectors.vector_sub(v1, v2)

@mcp.tool(name="vector_dot")
def vector_dot(v1: str, v2: str) -> str:
    """Dot product of two vectors."""
    return vectors.vector_dot(v1, v2)

@mcp.tool(name="vector_cross")
def vector_cross(v1: str, v2: str) -> str:
    """Cross product of two vectors."""
    return vectors.vector_cross(v1, v2)

@mcp.tool(name="vector_magnitude")
def vector_magnitude(v: str) -> str:
    """Magnitude of a vector."""
    return vectors.vector_magnitude(v)

@mcp.tool(name="vector_scalar_mul")
def vector_scalar_mul(k: str, v: str) -> str:
    """Multiply scalar k with vector v."""
    return vectors.vector_scalar_mul(k, v)

@mcp.tool(name="vector_angle_cos")
def vector_angle_cos(v1: str, v2: str) -> str:
    """Calculate the cosine of the angle between two vectors."""
    return vectors.vector_angle_cos(v1, v2)

@mcp.tool(name="vector_from_points")
def vector_from_points(p1: str, p2: str) -> str:
    """Create a vector from Point 1 to Point 2 (supports 'A', 'B' labels)."""
    return vectors.vector_from_points(p1, p2)

@mcp.tool(name="vector_is_perp")
def vector_is_perp(v1: str, v2: str) -> str:
    """Check if vectors are perpendicular (dot product = 0)."""
    return vectors.are_vectors_perpendicular(v1, v2)

@mcp.tool(name="vector_is_parallel")
def vector_is_parallel(v1: str, v2: str) -> str:
    """Check if vectors are parallel (cross product = 0)."""
    return vectors.are_vectors_parallel(v1, v2)

@mcp.tool(name="vector_plane_normal")
def vector_plane_normal(v1: str, v2: str) -> str:
    """Get normal vector of plane defined by two non-collinear vectors."""
    return vectors.get_plane_normal(v1, v2)

# --- Calculus ---
mcp.tool()(calculus.calculate_derivative)
mcp.tool()(calculus.calculate_indefinite_integral)
mcp.tool()(calculus.calculate_definite_integral)

# --- Statistics & Probability ---
mcp.tool()(stats.linear_regression)
mcp.tool()(stats.calculate_stats)
mcp.tool()(stats.binom_probability)
mcp.tool()(stats.normal_dist_cdf)
mcp.tool()(stats.normal_dist_interval)

# --- Sequences & Series ---
mcp.tool()(sequences.arithmetic_sequence_general_term)
mcp.tool()(sequences.arithmetic_sequence_sum)
mcp.tool()(sequences.geometric_sequence_general_term)
mcp.tool()(sequences.geometric_sequence_sum)
mcp.tool()(sequences.solve_recurrence_relation)
mcp.tool()(sequences.calculate_sequence_term_iteratively)
mcp.tool()(sequences.calculate_sequence_summation)

# --- Equations & Algebra (Exact/Numerical) ---
mcp.tool()(equations.solve_quadratic_formula)
mcp.tool()(equations.solve_linear_system)

# --- Symbolic Reasoning (SymPy) ---
mcp.tool()(symbolic.simplify_expression)
mcp.tool()(symbolic.expand_expression)
mcp.tool()(symbolic.factor_expression)
mcp.tool()(symbolic.solve_equation)

# --- Geometry 2D ---
mcp.tool()(geometry.geo_2d_clear)
mcp.tool()(geometry.geo_2d_add_point)
mcp.tool()(geometry.geo_2d_add_segment)
mcp.tool()(geometry.geo_2d_get_distance)
mcp.tool()(geometry.geo_2d_plot)

# --- Geometry 2D - Analytic ---
mcp.tool()(geometry.geo_2d_add_line)
mcp.tool()(geometry.geo_2d_add_circle)
mcp.tool()(geometry.geo_2d_add_ellipse)
mcp.tool()(geometry.geo_2d_add_hyperbola)
mcp.tool()(geometry.geo_2d_add_parabola)
mcp.tool()(geometry.geo_2d_get_intersection)
mcp.tool()(geometry.geo_2d_eval_y)
mcp.tool()(geometry.geo_2d_eval_x)

# --- Geometry 3D ---
mcp.tool()(geometry.geo_3d_clear)
mcp.tool()(geometry.geo_3d_add_point)
mcp.tool()(geometry.geo_3d_add_segment)
mcp.tool()(geometry.geo_3d_get_distance)
mcp.tool()(geometry.geo_3d_plot)

# --- Resources ---
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
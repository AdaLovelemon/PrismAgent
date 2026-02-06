import numpy as np
import cmath

def solve_quadratic_formula(a: float, b: float, c: float) -> dict:
    """
    Solve a quadratic equation ax^2 + bx + c = 0 using the root formula.
    Returns roots in a dictionary format.
    """
    if a == 0:
        if b == 0:
            if c == 0:
                raise ValueError("Infinite solutions (0x^2 + 0x + 0 = 0)")
            else:
                raise ValueError("No solution (0x^2 + 0x + c = 0 where c != 0)")
        else:
            # Linear equation bx + c = 0 -> x = -c/b
            return {"root1": -c/b, "root2": None, "discriminant": None, "note": "Linear equation"}
    
    delta = b**2 - 4*a*c
    
    # We use cmath.sqrt to handle negative discriminant automatically
    sqrt_delta = cmath.sqrt(delta)
    
    root1 = (-b + sqrt_delta) / (2*a)
    root2 = (-b - sqrt_delta) / (2*a)
    
    # Format results to be cleaner if they are real
    r1_formatted = root1.real if abs(root1.imag) < 1e-10 else root1
    r2_formatted = root2.real if abs(root2.imag) < 1e-10 else root2
    
    return {
        "root1": str(r1_formatted), 
        "root2": str(r2_formatted), 
        "discriminant": delta,
        "formula": "(-b ± sqrt(b^2 - 4ac)) / 2a"
    }

def solve_linear_system(matrix_a: list[list[float]], vector_b: list[float]) -> dict:
    """
    Solve a system of linear equations Ax = b using a numerically stable method (Gaussian Elimination with pivoting/LU Decomposition).
    
    Args:
        matrix_a: The coefficient matrix A (n x n list of lists)
        vector_b: The dependent variable vector b (list of length n)
        
    Returns:
        Dictionary containing the solution vector 'x'.
    """
    try:
        a_np = np.array(matrix_a, dtype=float)
        b_np = np.array(vector_b, dtype=float)
        
        if a_np.shape[0] != a_np.shape[1]:
            raise ValueError("Coefficient matrix must be square (n x n)")
        
        if a_np.shape[0] != b_np.shape[0]:
            raise ValueError("Dimension mismatch between Matrix A and Vector b")
            
        # np.linalg.solve uses LAPACK (gesv), which employs LU decomposition with partial pivoting.
        # This is the standard numerically stable way to solve dense linear systems.
        solution = np.linalg.solve(a_np, b_np)
        
        return {
            "solution": solution.tolist(),
            "method": "Gaussian Elimination (LU Decomposition with Partial Pivoting)"
        }
    except np.linalg.LinAlgError as e:
        return {"error": str(e), "message": "Matrix is singular or system is inconsistent"}


from sympy import symbols, simplify, expand, factor, solve, sympify, latex

def simplify_expression(expression: str) -> str:
    """Simplify a mathematical expression symbolically."""
    expr = sympify(expression)
    result = simplify(expr)
    return latex(result)

def expand_expression(expression: str) -> str:
    """Expand a mathematical expression symbolically (e.g., (x+1)^2 -> x^2 + 2x + 1)."""
    expr = sympify(expression)
    result = expand(expr)
    return latex(result)

def factor_expression(expression: str) -> str:
    """Factor a mathematical expression symbolically (e.g., x^2 - 1 -> (x-1)(x+1))."""
    expr = sympify(expression)
    result = factor(expr)
    return latex(result)

def solve_equation(equation: str, variable: str) -> str:
    """
    Solve a symbolic equation for a variable.
    Assumes equation equals 0 if no '=' is present, or parse "LHS = RHS".
    """
    # Simple handling for LHS=RHS string formats if passed directly, 
    # but sympy.solve usually expects an expression that equals 0.
    # If the string contains '=', we split it.
    if "=" in equation:
        lhs, rhs = equation.split("=")
        eq_expr = sympify(lhs) - sympify(rhs)
    else:
        eq_expr = sympify(equation)
        
    x = symbols(variable)
    solutions = solve(eq_expr, x)
    
    # Format solutions as a list of latex strings
    return str([latex(sol) for sol in solutions])

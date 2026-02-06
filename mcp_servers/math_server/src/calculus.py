from sympy import symbols, diff, integrate, sympify, latex, simplify

def calculate_derivative(expression: str, variable: str) -> str:
    """
    Calculate the symbolic derivative of an expression.
    
    Args:
        expression: The mathematical expression (e.g., "x**2 + sin(x)")
        variable: The variable to differentiate with respect to (e.g., "x")
        
    Returns:
        The derivative in LaTeX format.
    """
    x = symbols(variable)
    expr = sympify(expression)
    result = diff(expr, x)
    return latex(result)

def calculate_indefinite_integral(expression: str, variable: str) -> str:
    """
    Calculate the symbolic indefinite integral of an expression.
    
    Args:
        expression: The mathematical expression (e.g., "x**2")
        variable: The variable to integrate with respect to (e.g., "x")
        
    Returns:
        The integral in LaTeX format (excluding the constant C by default in sympy, but implied).
    """
    x = symbols(variable)
    expr = sympify(expression)
    # SymPy integrates symbolically
    result = integrate(expr, x)
    return latex(result)

def calculate_definite_integral(expression: str, variable: str, lower_limit: str, upper_limit: str) -> str:
    """
    Calculate the symbolic definite integral of an expression.
    
    Args:
        expression: The function to integrate (e.g., "sin(x)")
        variable: The integration variable (e.g., "x")
        lower_limit: Lower bound (can be number like "0" or symbol "-oo")
        upper_limit: Upper bound (can be number like "pi" or symbol "oo")
        
    Returns:
        The definite integral result in LaTeX.
    """
    x = symbols(variable)
    expr = sympify(expression)
    a = sympify(lower_limit)
    b = sympify(upper_limit)
    
    result = integrate(expr, (x, a, b))
    return latex(result)


def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent

import cmath
import math

def add(real1: float, imag1: float, real2: float, imag2: float) -> dict:
    """Add two complex numbers: (real1 + imag1*i) + (real2 + imag2*i)"""
    c1 = complex(real1, imag1)
    c2 = complex(real2, imag2)
    res = c1 + c2
    return {"real": res.real, "imag": res.imag, "string": str(res)}

def subtract(real1: float, imag1: float, real2: float, imag2: float) -> dict:
    """Subtract two complex numbers: (real1 + imag1*i) - (real2 + imag2*i)"""
    c1 = complex(real1, imag1)
    c2 = complex(real2, imag2)
    res = c1 - c2
    return {"real": res.real, "imag": res.imag, "string": str(res)}

def multiply(real1: float, imag1: float, real2: float, imag2: float) -> dict:
    """Multiply two complex numbers"""
    c1 = complex(real1, imag1)
    c2 = complex(real2, imag2)
    res = c1 * c2
    return {"real": res.real, "imag": res.imag, "string": str(res)}

def divide(real1: float, imag1: float, real2: float, imag2: float) -> dict:
    """Divide two complex numbers"""
    c1 = complex(real1, imag1)
    c2 = complex(real2, imag2)
    if c2 == 0:
        raise ValueError("Cannot divide by zero complex number")
    res = c1 / c2
    return {"real": res.real, "imag": res.imag, "string": str(res)}

def modulus(real: float, imag: float) -> float:
    """Calculate the modulus (absolute value) of a complex number"""
    return abs(complex(real, imag))

def conjugate(real: float, imag: float) -> dict:
    """Calculate the complex conjugate"""
    c = complex(real, imag)
    res = c.conjugate()
    return {"real": res.real, "imag": res.imag, "string": str(res)}

def argument(real: float, imag: float) -> float:
    """Calculate the argument (phase) of a complex number in radians"""
    return cmath.phase(complex(real, imag))

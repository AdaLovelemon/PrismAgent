import numpy as np
import math
from sympy import sympify, latex

def linear_regression(x_data: list[float], y_data: list[float]) -> dict:
    """
    Perform simple linear regression (Least Squares).
    Returns slope, intercept, equation, and R-squared value.
    """
    x = np.array(x_data)
    y = np.array(y_data)
    
    if len(x) != len(y):
        raise ValueError("x and y lists must have the same length")
        
    n = len(x)
    # y = bx + a (Standard high school notation in China often uses y = bx + a or y = ax + b, let's use y = mx + c logic but label clearly)
    # Slope (b) and Intercept (a)
    
    # Using numpy polyfit for stability
    slope, intercept = np.polyfit(x, y, 1)
    
    # Calculate R^2
    y_pred = slope * x + intercept
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean)**2)
    ss_res = np.sum((y - y_pred)**2)
    
    # Check for division by zero (if all y are same)
    if ss_tot == 0:
        r_squared = 1.0 if ss_res == 0 else 0.0
    else:
        r_squared = 1 - (ss_res / ss_tot)
        
    # Correlation coefficient r
    correlation = math.sqrt(r_squared) if slope >= 0 else -math.sqrt(r_squared)
    
    return {
        "slope": slope,
        "intercept": intercept,
        "equation": f"y = {slope:.4f}x + {intercept:.4f}",
        "r_squared": r_squared,
        "correlation_r": correlation,
        "x_mean": np.mean(x),
        "y_mean": np.mean(y)
    }

def calculate_stats(data: list[float]) -> dict:
    """Calculate basic statistics: mean, variance (population & sample), std dev."""
    arr = np.array(data)
    mean_val = np.mean(arr)
    # Population variance (divide by n) - standard in Chinese high school for "variance" unless specified sample
    var_pop = np.var(arr) 
    std_pop = np.std(arr)
    # Sample variance (divide by n-1)
    var_sample = np.var(arr, ddof=1)
    std_sample = np.std(arr, ddof=1)
    
    return {
        "mean": mean_val,
        "variance_population": var_pop,
        "std_dev_population": std_pop,
        "variance_sample": var_sample,
        "std_dev_sample": std_sample,
        "median": np.median(arr),
        "min": np.min(arr),
        "max": np.max(arr)
    }

def binom_probability(n: int, k: int, p: float) -> dict:
    """
    Calculate Binomial Probability P(X=k) for X ~ B(n, p).
    Includes expected value and variance.
    """
    if not (0 <= p <= 1):
        raise ValueError("Probability p must be between 0 and 1")
    if k < 0 or k > n:
        prob = 0.0
    else:
        # C(n, k) * p^k * (1-p)^(n-k)
        comb = math.comb(n, k)
        prob = comb * (p**k) * ((1-p)**(n-k))
        
    expectation = n * p
    variance = n * p * (1-p)
    
    return {
        "P(X=k)": prob,
        "Expectation_E(X)": expectation,
        "Variance_D(X)": variance,
        "formula": f"C({n}, {k}) * {p}^{k} * (1-{p})^{n-k}"
    }

def normal_dist_cdf(mean: float, std_dev: float, x: float) -> float:
    """
    Calculate Cumulative Distribution Function (CDF) for Normal Distribution N(mu, sigma^2).
    P(X <= x)
    """
    # Using error function
    # CDF(x) = 0.5 * (1 + erf((x - mean) / (std_dev * sqrt(2))))
    return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))

def normal_dist_interval(mean: float, std_dev: float, lower: float, upper: float) -> float:
    """Calculate P(lower <= X <= upper) for Normal Distribution"""
    cdf_upper = normal_dist_cdf(mean, std_dev, upper)
    cdf_lower = normal_dist_cdf(mean, std_dev, lower)
    return cdf_upper - cdf_lower

from sympy import symbols, simplify, solve, latex, summation, oo, rsolve, Function, Eq, Symbol, sympify
import re

def arithmetic_sequence_general_term(a1: str, d: str, n: str = 'n') -> str:
    """
    General term of Arithmetic Sequence: an = a1 + (n-1)d
    """
    n_sym = symbols(n)
    a1_sym = sympify(a1)
    d_sym = sympify(d)
    
    an = a1_sym + (n_sym - 1) * d_sym
    return latex(simplify(an))

def arithmetic_sequence_sum(a1: str, d: str, n: str = 'n') -> str:
    """
    Sum of first n terms of Arithmetic Sequence: Sn = n*a1 + n(n-1)d/2
    """
    n_sym = symbols(n)
    a1_sym = sympify(a1)
    d_sym = sympify(d)
    
    sn = n_sym * a1_sym + n_sym * (n_sym - 1) * d_sym / 2
    return latex(simplify(sn))

def geometric_sequence_general_term(a1: str, q: str, n: str = 'n') -> str:
    """
    General term of Geometric Sequence: an = a1 * q^(n-1)
    """
    n_sym = symbols(n)
    a1_sym = sympify(a1)
    q_sym = sympify(q)
    
    an = a1_sym * (q_sym ** (n_sym - 1))
    return latex(simplify(an))

def geometric_sequence_sum(a1: str, q: str, n: str = 'n') -> str:
    """
    Sum of first n terms of Geometric Sequence.
    """
    n_sym = symbols(n)
    a1_sym = sympify(a1)
    q_sym = sympify(q)
    
    # Case q=1 handling is tricky in pure symbolic without piecewise, but standard formula:
    # a1(1-q^n)/(1-q)
    
    # We return the standard formula assuming q != 1 usually, 
    # but sympy might simplify to Piecewise if we are careful, 
    # lets just return the q!=1 form as it's the "formula" requested usually.
    # Users can check q=1 manually.
    
    sn = a1_sym * (1 - q_sym**n_sym) / (1 - q_sym)
    return latex(simplify(sn))

def solve_recurrence_relation(recurrence_eq: str, initial_conditions: dict, target_term: str = 'n') -> str:
    """
    Solve a recurrence relation.
    Supports a_n, a_{n+1}, a(n) notation and auto-converts to SymPy format.
    """
    n = symbols('n', integer=True)
    y = Function('y')
    
    # Preprocessing: convert common notations to y(n)
    # 1. Handle LaTeX-style subscripts a_{n+1} -> y(n+1)
    processed_eq = re.sub(r'[a-zA-Z]_{(.*?)}', r'y(\1)', recurrence_eq)
    # 2. Handle simple subscripts a_n -> y(n)
    processed_eq = re.sub(r'[a-zA-Z]_(\w+)', r'y(\1)', processed_eq)
    # 3. Handle function notation a(n) -> y(n)
    processed_eq = re.sub(r'[a-zA-Z]\((.*?)\)', r'y(\1)', processed_eq)
    # 4. Replace ^ with ** for powers
    processed_eq = processed_eq.replace('^', '**')
    
    # Parse equation. We assume left side = 0 if no '='.
    if "=" in processed_eq:
        lhs_str, rhs_str = processed_eq.split("=")
        eq_expr = sympify(lhs_str) - sympify(rhs_str)
    else:
        eq_expr = sympify(processed_eq)
        
    # Parse initial conditions.
    init_conds_sympy = {}
    for k, v in initial_conditions.items():
        # k can be "0" or "a_0" or "a(0)"
        idx_match = re.search(r'\d+', str(k))
        if idx_match:
            idx = int(idx_match.group())
            init_conds_sympy[y(idx)] = sympify(str(v).replace('^', '**'))
        
    try:
        result = rsolve(eq_expr, y(n), init_conds_sympy)
        if result is None:
            return "No symbolic solution found by rsolve."
        return latex(result)
    except Exception as e:
        return f"Error in rsolve: {str(e)}. Note: rsolve only supports linear recurrence relations."


def calculate_sequence_term_iteratively(recurrence_eq: str, initial_conditions: dict, target_n: int) -> str:
    """
    Calculate the n-th term of a sequence by direct iteration.
    Useful for non-linear recurrences where rsolve fails.
    
    Example: recurrence_eq="a_{n+1} = a_n^3 - 3*a_n", initial_conditions={"0": "2 + sqrt(3)"}, target_n=3
    """
    # 1. Preprocess the equation to extract the RHS
    if "=" not in recurrence_eq:
        return "Please provide equation in 'a_{n+1} = ...' format for iteration."
    
    # Simple preprocessing similar to solve_recurrence_relation but specifically for iteration
    lhs, rhs = recurrence_eq.split("=")
    rhs_str = rhs.replace('^', '**').strip()
    
    # Detect the index variable (n, k, etc.) from LHS
    idx_var_match = re.search(r'[a-zA-Z]_{(.*?)}|[a-zA-Z]_(\w+)|[a-zA-Z]\((.*?)\)', lhs)
    if not idx_var_match:
         return "Could not parse LHS of recurrence equation."
    
    full_idx = idx_var_match.group(1) or idx_var_match.group(2) or idx_var_match.group(3)
    var_match = re.search(r'[a-zA-Z]', full_idx)
    idx_var = var_match.group() if var_match else 'n'
    
    idx_sym = symbols(idx_var)
    prev_sym = symbols('prev_val')
    
    # Replace sequence terms (a_n, a_{n}, a(n)) with prev_val
    processed_rhs = re.sub(rf'[a-zA-Z]_{{{idx_var}}}|[a-zA-Z]_{idx_var}|[a-zA-Z]\({idx_var}\)', 'prev_val', rhs_str)
    
    try:
        expr = sympify(processed_rhs)
        
        # Determine starting index and value
        start_idx = None
        current_val = None
        for k, v in initial_conditions.items():
            m = re.search(r'\d+', str(k))
            if m:
                idx = int(m.group())
                if start_idx is None or idx < start_idx:
                    start_idx = idx
                    current_val = sympify(str(v).replace('^', '**'))
        
        if start_idx is None:
            return "No valid starting index found in initial_conditions."
        
        if target_n < start_idx:
            return f"Target n ({target_n}) is less than start index ({start_idx})"

        # If n is very large, iteration is likely the wrong approach but we try a small limit
        if target_n - start_idx > 10000:
             return f"Iteration range too large ({target_n - start_idx})."

        for i in range(start_idx, target_n):
            # Substitute both the sequence value and the current index 'i'
            current_val = expr.subs({prev_sym: current_val, idx_sym: i})
            if (i - start_idx) % 100 == 0:
                current_val = simplify(current_val)
                if current_val.is_number and abs(current_val.evalf()) > 1e100:
                    return f"Numerical overflow at index {i+1}."
        
        return latex(simplify(current_val))
    except Exception as e:
        return f"Iteration error: {str(e)}"


def calculate_sequence_summation(general_term: str, lower: str, upper: str, var: str = 'k') -> str:
    """
    Calculate generic summation: Sigma(term, k=lower..upper)
    """
    k = symbols(var, integer=True)
    # Preprocess inputs
    term_expr = sympify(general_term.replace('^', '**'))
    # Handle cases like lower="k=1"
    lower_val = lower.split('=')[-1].strip()
    upper_val = upper.split('=')[-1].strip()
    
    a = sympify(lower_val.replace('^', '**'))
    b = sympify(upper_val.replace('^', '**'))
    
    res = summation(term_expr, (k, a, b))
    return latex(res)

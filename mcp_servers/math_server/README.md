# Math MCP Server (PrismAgent)

A specialized Model Context Protocol (MCP) server providing high-school and college level mathematical tools.

## Features

- **Basic Arithmetic**: Precision operations for real numbers.
- **Complex Numbers**: Operations for complex numbers ($a + bi$).
- **Calculus**: Symbolic differentiation and integration.
- **Vectors**: 2D/3D vector operations and geometry.
- **Equations**: Symbolic equation solving.
- **Statistics**: Linear regression and statistical analysis.
- **Symbolic Math**: Simplification, expansion, and factoring of expressions.

## Installation

```bash
pip install -e .
```

## Usage

This server is designed to be used as an MCP tool. You can run it directly:

```bash
python server.py
```

Or use it with an MCP client by configuring the command:
`python -m server` (if installed as a package) or the direct path to `server.py`.

## Dependencies

- `mcp`
- `fastmcp`
- `sympy`: Used for symbolic mathematics.
- `numpy`: Used for statistical calculations.

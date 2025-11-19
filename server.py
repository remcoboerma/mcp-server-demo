from fastmcp import FastMCP

mcp = FastMCP("demo-calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Tel twee getallen op"""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Vermenigvuldig twee getallen"""
    return a * b

@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Genereer random getal"""
    import random
    return random.randint(min_val, max_val)

if __name__ == "__main__":
    mcp.run()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BMI Server")

print(f"Starting server {mcp.name}")

@mcp.tool()
def calculate_bmi(height:float, weight:float)-> float:
    """
    Calculate bmi for given weight in kg and height in meters.
    """
    if height<= 0:
        raise ValueError("Height must be greater than 0")
    return weight / (height ** 2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
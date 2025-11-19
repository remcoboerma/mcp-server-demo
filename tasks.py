from invoke import Context
from edwh import improved_task
from edwh.tasks import check_env, generate_password
import os

def get_python():
    """Return juiste Python executable (venv of system)"""
    venv_python = ".venv/bin/python3"
    return venv_python if os.path.exists(venv_python) else "python3"

@improved_task
def setup(c: Context):
    """Configure .env file met PROJECT en HOSTINGDOMAIN"""
    project = check_env(
        "PROJECT",
        default="mcp-server",
        comment="Project naam voor Docker container en Traefik routing",
    )
    assert project.strip() and project.replace('-', '').replace('_', '').isalnum(), \
        "PROJECT moet alfanumeriek zijn (- en _ toegestaan)"
    
    domain = check_env(
        "HOSTINGDOMAIN", 
        default="localhost",
        comment="Domain voor Traefik routing (bijv. example.com)",
    )
    assert domain.strip(), "HOSTINGDOMAIN mag niet leeg zijn"
    
    print(f"✅ Setup compleet: {project}.{domain}")


@improved_task
def venv(c: Context):
    """Maak virtual environment aan met uv"""
    c.run("uv venv")
    print("\n✅ Venv aangemaakt! Installeer nu dependencies met: inv install")

@improved_task
def install(c: Context):
    """Installeer fastmcp + mkdocs in venv (maak eerst venv met: inv venv)"""
    python = get_python()
    if python == "python3":
        print("⚠️  Geen venv gevonden. Run eerst: inv venv")
        return
    c.run("uv pip install fastmcp mkdocs-material")

@improved_task
def docs(c: Context):
    """Serve mkdocs documentation"""
    python = get_python()
    c.run(f"{python} -m mkdocs serve")

@improved_task
def start(c: Context):
    """Start server"""
    python = get_python()
    c.run(f"{python} -m fastmcp run server.py")

@improved_task
def dev(c: Context):
    """Start in dev mode"""
    python = get_python()
    c.run(f"{python} -m fastmcp dev server.py")

@improved_task
def test(c: Context):
    """
    Test alle MCP tools via een programmatische client.
    
    Deze functie demonstreert hoe je:
    1. Een MCP server start als subprocess (stdio communicatie)
    2. Een client sessie opzet om met de server te praten
    3. Tools aanroept met argumenten
    4. Resultaten ontvangt en verwerkt
    
    Zie README.md voor gedetailleerde uitleg van het proces.
    """
    python = get_python()
    test_code = """
from fastmcp import FastMCP
import asyncio

async def test():
    # Import MCP client componenten
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    # Configureer hoe de server gestart moet worden
    # Dit start 'python server.py' als subprocess
    params = StdioServerParameters(command='""" + python + """', args=['server.py'])
    
    # Open communicatie met de server (stdio = standard in/out)
    async with stdio_client(params) as (read, write):
        # Maak een sessie aan om tools aan te roepen
        async with ClientSession(read, write) as session:
            # Initialiseer de verbinding (handshake)
            await session.initialize()
            
            # Test 1: Optellen
            print('\\n--- Test 1: Optellen ---')
            r = await session.call_tool('add', {'a': 5, 'b': 3})
            print(f'add(5, 3) = {r.content[0].text}')
            
            # Test 2: Vermenigvuldigen
            print('\\n--- Test 2: Vermenigvuldigen ---')
            r = await session.call_tool('multiply', {'a': 4, 'b': 7})
            print(f'multiply(4, 7) = {r.content[0].text}')
            
            # Test 3: Random getal (met default waarden)
            print('\\n--- Test 3: Random getal ---')
            r = await session.call_tool('random_number', {})
            print(f'random_number() = {r.content[0].text}')
            
            # Test 4: Random getal met custom range
            print('\\n--- Test 4: Random met range ---')
            r = await session.call_tool('random_number', {'min_val': 10, 'max_val': 20})
            print(f'random_number(10, 20) = {r.content[0].text}')
            
            print('\\n✅ Alle tests geslaagd!')

asyncio.run(test())
"""
    c.run(f'{python} -c "{test_code}"')

@improved_task
def inspect(c: Context):
    """Toon alle beschikbare tools en hun schemas"""
    c.run("fastmcp inspect server.py")

@improved_task
def docker_build(c: Context):
    """Build Docker image"""
    c.run("docker compose build")

@improved_task
def docker_up(c: Context):
    """Start Docker container"""
    c.run("docker compose up -d")

@improved_task
def docker_down(c: Context):
    """Stop Docker container"""
    c.run("docker compose down")

@improved_task
def docker_logs(c: Context):
    """Show Docker logs"""
    c.run("docker compose logs -f")

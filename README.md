# FastMCP Demo - Calculator Server

Een eenvoudige demonstratie van een **Model Context Protocol (MCP)** server gebouwd met FastMCP.

## Wat is MCP?

**Model Context Protocol (MCP)** is een standaard protocol waarmee AI assistenten (zoals Claude) kunnen communiceren met externe tools en diensten. Denk aan het als een "stopcontact" waar AI's hun "stekker" in kunnen steken om extra functies te krijgen.

### Waarom is dit handig?

- AI's kunnen dan rekenen, databases raadplegen, bestanden lezen, etc.
- Je hoeft de AI niet alle context te geven - de AI vraagt het zelf op
- Herbruikbaar: één server werkt met alle MCP-compatible AI's

## Wat is FastMCP?

**FastMCP** is een Python framework dat het bouwen van MCP servers super eenvoudig maakt. Het werkt vergelijkbaar met FastAPI - je schrijft gewone Python functies en voegt een `@mcp.tool()` decorator toe.

## Deze Demo

Deze demo bevat een simpele calculator met 3 tools:
- `add` - Tel twee getallen op
- `multiply` - Vermenigvuldig twee getallen  
- `random_number` - Genereer een willekeurig getal

## Installatie

### Stap 1: Virtual Environment aanmaken

```bash
inv venv
```

Dit maakt een `.venv` directory aan met een geïsoleerde Python omgeving.

**Waarom een virtual environment?**
- Dependencies blijven gescheiden van je systeem Python
- Geen conflicten met andere projecten
- Makkelijk te verwijderen (delete gewoon `.venv/`)

### Stap 2: Dependencies installeren

```bash
inv install
```

Dit installeert FastMCP en alle dependencies in de venv.

**Technische achtergrond:**
- De tasks gebruiken automatisch `.venv/bin/python3` als die bestaat
- Anders valt het terug naar systeem `python3`
- Dit zorgt ervoor dat alle tools in de juiste omgeving draaien

## Gebruik

### 1. Server starten (development mode)

```bash
inv dev
```

De server draait nu en luistert naar commando's via stdio (standard input/output).

### 2. Beschikbare tools inspecteren

```bash
inv inspect
```

Dit toont alle tools die de server aanbiedt, inclusief hun parameters en documentatie.

### 3. Tools testen

```bash
inv test
```

Dit draait een volledig testscript dat laat zien hoe je:
- Een verbinding maakt met de MCP server
- Tools aanroept met argumenten
- Resultaten verwerkt

## Hoe werkt de test functie? (technische uitleg)

De `inv test` functie demonstreert de volledige client-server flow:

### Stap 1: Server als subprocess starten

```python
params = StdioServerParameters(command='python', args=['server.py'])
```

**Wat gebeurt er?**  
We starten `python server.py` als een apart proces (subprocess). We communiceren met dit proces via **stdio** - dat betekent dat we JSON berichten heen en weer sturen via standard input en output.

**Waarom stdio?**  
- Eenvoudig: werkt overal waar Python draait
- Veilig: de server draait in zijn eigen proces
- Standaard: de meeste MCP servers gebruiken stdio

### Stap 2: Client verbinding opzetten

```python
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
```

**Wat gebeurt er?**  
- `stdio_client` maakt twee "kanalen": één om te lezen, één om te schrijven
- `ClientSession` beheert de communicatie volgens het MCP protocol
- De `async with` zorgt dat alles netjes wordt afgesloten (ook bij errors)

**Waarom async?**  
MCP is gebouwd op asynchrone communicatie. Dit betekent dat de client niet hoeft te wachten totdat de server klaar is - hij kan meerdere requests tegelijk versturen.

### Stap 3: Verbinding initialiseren

```python
await session.initialize()
```

**Wat gebeurt er?**  
De client en server doen een "handshake" - ze wisselen informatie uit over:
- Welke protocol versie ze gebruiken
- Welke capabilities ze ondersteunen
- Welke tools beschikbaar zijn

Dit is vergelijkbaar met het opzetten van een telefoonverbinding voordat je gaat praten.

### Stap 4: Tool aanroepen

```python
result = await session.call_tool('add', {'a': 5, 'b': 3})
print(f"Result: {result.content[0].text}")
```

**Wat gebeurt er?**  
1. De client stuurt een JSON-RPC bericht naar de server: "roep tool 'add' aan met a=5, b=3"
2. De server ontvangt dit, voert de `add` functie uit
3. De server stuurt het resultaat terug als JSON
4. De client parsed het resultaat en geeft het terug

**Wat zit er in `result`?**
- `result.content` is een lijst van content items
- `result.content[0]` is het eerste item (meestal het enige)
- `result.content[0].text` is de tekstuele representatie van het resultaat

### Volledige flow visualisatie

┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Server  │
│ (test)  │                                    │(server.py)│
└────┬────┘                                    └────┬────┘
     │                                              │
     │  1. Start subprocess: python server.py       │
     ├─────────────────────────────────────────────>│
     │                                              │
     │  2. Initialize (handshake)                   │
     ├─────────────────────────────────────────────>│
     │<─────────────────────────────────────────────┤
     │     (server info, available tools)           │
     │                                              │
     │  3. call_tool('add', {a:5, b:3})            │
     ├─────────────────────────────────────────────>│
     │                                              │ (berekent 5+3)
     │<─────────────────────────────────────────────┤
     │     result: "8"                              │
     │                                              │
     │  4. call_tool('multiply', {a:4, b:7})       │
     ├─────────────────────────────────────────────>│
     │                                              │ (berekent 4*7)
     │<─────────────────────────────────────────────┤
     │     result: "28"                             │
     │                                              │
     │  5. Close connection                         │
     ├─────────────────────────────────────────────>│
     │                                              │ (server stopt)
     └──────────────────────────────────────────────┘

## Je eigen tool maken

Voeg een nieuwe tool toe aan `server.py`:

```python
@mcp.tool()
def divide(a: float, b: float) -> str:
    """Deel twee getallen. Let op deling door nul!"""
    if b == 0:
        return "Error: Kan niet delen door nul"
    return str(a / b)
```

Test met: `inv test` (voeg eerst een test toe in tasks.py)

## Praktische oefeningen voor studenten

### Oefening 1: String manipulatie tool
Maak een tool die een string omkeert:
```python
@mcp.tool()
def reverse_string(text: str) -> str:
    """Keer een string om"""
    return text[::-1]
```

### Oefening 2: Lijst bewerking
Maak een tool die het gemiddelde berekent van een lijst getallen:
```python
@mcp.tool()
def average(numbers: list[float]) -> float:
    """Bereken gemiddelde van een lijst getallen"""
    return sum(numbers) / len(numbers)
```

### Oefening 3: Eigen idee
Bedenk zelf een nuttige tool. Ideeën:
- Temperatuur conversie (Celsius ↔ Fahrenheit)
- BMI calculator
- Wachtwoord sterkte checker
- String naar morse code
- JSON validator

## Troubleshooting

**"ModuleNotFoundError: No module named 'fastmcp'"**
→ Run `inv install` eerst

**"Server start niet"**
→ Check of Python actief is: `python --version`
→ Check of server.py geen syntax errors heeft

**"Tools geven geen output"**
→ Check of de return type klopt (moet str, int, float, etc zijn)
→ Kijk in de functie of er wel een `return` statement is

## Volgende stappen

1. **Gebruik met Claude Desktop**  
   Voeg deze server toe aan je Claude Desktop configuratie

2. **Complexere tools bouwen**  
   - Database queries uitvoeren
   - Bestanden lezen/schrijven
   - API's aanroepen
   - Externe services integreren

3. **Meer leren over MCP**
   - [FastMCP documentatie](https://github.com/jlowin/fastmcp)
   - [MCP specificatie](https://modelcontextprotocol.io)
   - [Officiële MCP servers](https://github.com/modelcontextprotocol/servers)

## Licentie

Public domain - gebruik vrij voor educatieve doeleinden.

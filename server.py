from fastmcp import FastMCP
from datetime import datetime
from pathlib import Path
import logging
import sqlite3

logger = logging.getLogger(__name__)
mcp = FastMCP("democalculator")

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

@mcp.tool()
def projectnames_for_username(username: str) -> list[str]:
    """Geef alle projectnamen voor een gebruiker"""
    db_path = Path("/data/captains_log.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT DISTINCT projectname FROM captains_log WHERE username = ? ORDER BY projectname",
        (username,)
    )
    
    projects = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return projects

@mcp.tool()
def data_for_new_report(username: str, projects: list[str]) -> dict:
    """Haal nieuwe data op sinds laatste high watermark en update watermarks.
    
    Parameters:
    - username: Naam van de gebruiker
    - projects: Lijst van projectnamen
    
    Returns:
    - Dict met per project de nieuwe entries sinds laatste watermark
    """
    db_path = Path("/data/captains_log.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Maak high_watermarks tabel als die nog niet bestaat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS high_watermarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tablename TEXT NOT NULL,
            username TEXT NOT NULL,
            projectname TEXT NOT NULL,
            watermark_id INTEGER NOT NULL DEFAULT 0,
            UNIQUE(tablename, username, projectname)
        )
    """)
    
    result = {}
    
    for project in projects:
        # Haal huidige watermark op
        cursor.execute("""
            SELECT watermark_id FROM high_watermarks 
            WHERE tablename = 'captains_log' 
            AND username = ? 
            AND projectname = ?
        """, (username, project))
        
        row = cursor.fetchone()
        watermark = row[0] if row else 0
        
        # Haal nieuwe entries op
        cursor.execute("""
            SELECT id, timestamp, message 
            FROM captains_log 
            WHERE username = ? 
            AND projectname = ? 
            AND id > ?
            ORDER BY id
        """, (username, project, watermark))
        
        entries = cursor.fetchall()
        
        # Sla entries op in result
        result[project] = [
            {"id": entry[0], "timestamp": entry[1], "message": entry[2]}
            for entry in entries
        ]
        
        # Update watermark als er nieuwe entries zijn
        if entries:
            new_watermark = entries[-1][0]
            
            cursor.execute("""
                INSERT INTO high_watermarks (tablename, username, projectname, watermark_id)
                VALUES ('captains_log', ?, ?, ?)
                ON CONFLICT(tablename, username, projectname) 
                DO UPDATE SET watermark_id = ?
            """, (username, project, new_watermark, new_watermark))
    
    conn.commit()
    conn.close()
    
    return result

@mcp.tool()
def captains_log(username: str, projectname: str, message: str) -> str:
    """Log een bericht met timestamp, username en projectname naar sqlite3 database.
    
    BELANGRIJK: Vraag de gebruiker ALTIJD expliciet om hun naam en projectnaam.
    Gebruik NOOIT verzonnen, aangenomen of standaardwaarden.
    De gebruiker moet deze informatie zelf verstrekken voordat je deze tool aanroept.
    
    Parameters:
    - username: Naam van de gebruiker (MOET door gebruiker opgegeven worden)
    - projectname: Naam van het project (MOET door gebruiker opgegeven worden)
    - message: Het log bericht
    """
    db_path = Path("/data/captains_log.db")
    
    # Maak connectie en tabel als die nog niet bestaat
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS captains_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            projectname TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    
    # Insert log entry
    cursor.execute(
        "INSERT INTO captains_log (username, projectname, message) VALUES (?, ?, ?)",
        (username, projectname, message)
    )
    
    conn.commit()
    log_id = cursor.lastrowid
    
    # Haal de entry op om de timestamp te krijgen
    cursor.execute("SELECT timestamp FROM captains_log WHERE id = ?", (log_id,))
    timestamp = cursor.fetchone()[0]
    
    conn.close()
    
    log_entry = f"[{timestamp}] {username}@{projectname}: {message}"
    print(log_entry)
    
    return log_entry

if __name__ == "__main__":
    logger.info(f"Server name: {mcp.name}")
    mcp.run()

"""Case law knowledge base for AgentForLaw"""
import sqlite3
from pathlib import Path
import json

class CaseLawDatabase:
    def __init__(self):
        self.db_path = Path.home() / ".claw_memory" / "case_law.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY,
                name TEXT,
                citation TEXT,
                year INTEGER,
                court TEXT,
                holding TEXT,
                facts TEXT,
                reasoning TEXT,
                keywords TEXT,
                url TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_relationships (
                case_id INTEGER,
                related_case_id INTEGER,
                relationship_type TEXT
            )
        """)
        self.conn.commit()
    
    def add_case(self, case_data):
        """Add a case to the knowledge base"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO cases 
            (name, citation, year, court, holding, facts, reasoning, keywords, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_data.get('name'),
            case_data.get('citation'),
            case_data.get('year'),
            case_data.get('court'),
            case_data.get('holding'),
            case_data.get('facts'),
            case_data.get('reasoning'),
            case_data.get('keywords'),
            case_data.get('url')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def search_cases(self, query):
        """Search cases by keyword or name"""
        self.cursor.execute("""
            SELECT name, citation, year, holding, keywords
            FROM cases
            WHERE name LIKE ? OR keywords LIKE ? OR holding LIKE ?
            LIMIT 10
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        return self.cursor.fetchall()
    
    def get_case(self, name):
        """Get a specific case by name"""
        self.cursor.execute("SELECT * FROM cases WHERE name LIKE ?", (f"%{name}%",))
        return self.cursor.fetchone()
    
    def list_landmark_cases(self):
        """List all landmark cases"""
        self.cursor.execute("SELECT name, citation, year, holding FROM cases ORDER BY year")
        return self.cursor.fetchall()

# Initialize with landmark cases
def init_landmark_cases():
    kb = CaseLawDatabase()
    
    landmark_cases = [
        {"name": "Marbury v. Madison", "citation": "5 U.S. 137", "year": 1803, "court": "Supreme Court", 
         "holding": "Established judicial review - Supreme Court can declare laws unconstitutional",
         "keywords": "judicial review, constitution, supreme court"},
        
        {"name": "McCulloch v. Maryland", "citation": "17 U.S. 316", "year": 1819, "court": "Supreme Court",
         "holding": "Federal government has implied powers, states cannot tax federal institutions",
         "keywords": "implied powers, federal supremacy, necessary and proper"},
        
        {"name": "Brown v. Board of Education", "citation": "347 U.S. 483", "year": 1954, "court": "Supreme Court",
         "holding": "Separate educational facilities are inherently unequal, violates 14th Amendment",
         "keywords": "equal protection, segregation, 14th amendment"},
        
        {"name": "Miranda v. Arizona", "citation": "384 U.S. 436", "year": 1966, "court": "Supreme Court",
         "holding": "Custodial interrogations require Miranda warnings (right to remain silent, right to attorney)",
         "keywords": "miranda rights, fifth amendment, self-incrimination"},
        
        {"name": "Roe v. Wade", "citation": "410 U.S. 113", "year": 1973, "court": "Supreme Court",
         "holding": "Right to privacy under Due Process Clause extends to abortion",
         "keywords": "privacy, due process, abortion"},
        
        {"name": "Citizens United v. FEC", "citation": "558 U.S. 310", "year": 2010, "court": "Supreme Court",
         "holding": "Corporate political spending is protected speech under First Amendment",
         "keywords": "first amendment, campaign finance, corporate speech"},
        
        {"name": "SEC v. W.J. Howey Co.", "citation": "328 U.S. 293", "year": 1946, "court": "Supreme Court",
         "holding": "Investment contract test: money invested in common enterprise with expectation of profits from others' efforts",
         "keywords": "securities, howey test, investment contract"},
        
        {"name": "Chevron U.S.A. v. NRDC", "citation": "467 U.S. 837", "year": 1984, "court": "Supreme Court",
         "holding": "Courts defer to agency interpretations of ambiguous statutes",
         "keywords": "chevron deference, administrative law, agency interpretation"},
        
        {"name": "Roe v. Wade", "citation": "410 U.S. 113", "year": 1973, "court": "Supreme Court",
         "holding": "Right to privacy under Due Process Clause extends to abortion",
         "keywords": "privacy, due process, abortion"}
    ]
    
    for case in landmark_cases:
        kb.add_case(case)
    
    print(f"✅ Added {len(landmark_cases)} landmark cases to knowledge base")

if __name__ == "__main__":
    init_landmark_cases()

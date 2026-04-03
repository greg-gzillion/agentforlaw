#!/usr/bin/env python3
"""
agentforlaw - Agent that studies statutes, codes, regulations, and rules
Part of the claw ecosystem: rustypycraw, eagleclaw, crustyclaw, claw-coder, agentforlaw
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Shared memory path
SHARED_MEMORY_DIR = Path.home() / ".claw_memory"
SHARED_MEMORY_DIR.mkdir(exist_ok=True)
DB_PATH = SHARED_MEMORY_DIR / "shared_memory.db"

class SharedMemory:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                tags TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_registry (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                repo TEXT,
                capabilities TEXT,
                last_seen TEXT
            )
        ''')
        self.conn.commit()
    
    def remember(self, key: str, value: str, tags: str = ""):
        self.cursor.execute(
            "INSERT INTO memories (agent, key, value, timestamp, tags) VALUES (?, ?, ?, ?, ?)",
            ("agentforlaw", key, value, datetime.now().isoformat(), tags)
        )
        self.conn.commit()
    
    def recall(self, key: str) -> list:
        self.cursor.execute(
            "SELECT agent, key, value, tags FROM memories WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 10",
            (f"%{key}%",)
        )
        return self.cursor.fetchall()
    
    def register(self):
        self.cursor.execute(
            "INSERT OR REPLACE INTO agent_registry VALUES (?, ?, ?, ?, ?)",
            ("agentforlaw", "AgentForLaw", "https://github.com/greg-gzillion/agentforlaw", 
             "law study, case law, constitution, statutes, regulations", datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        
        self.regulatory_agencies = {
            "sec": {"name": "Securities and Exchange Commission", "url": "https://www.sec.gov/"},
            "cftc": {"name": "Commodity Futures Trading Commission", "url": "https://www.cftc.gov/"},
            "dttc": {"name": "Depository Trust & Clearing Corporation", "url": "https://www.dtcc.com/"},
            "finra": {"name": "FINRA", "url": "https://www.finra.org/"},
            "federal_reserve": {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/"},
            "fdic": {"name": "FDIC", "url": "https://www.fdic.gov/"},
            "occ": {"name": "OCC", "url": "https://www.occ.treas.gov/"},
            "irs": {"name": "IRS", "url": "https://www.irs.gov/"},
            "treasury": {"name": "US Treasury", "url": "https://home.treasury.gov/"},
            "fincen": {"name": "FinCEN", "url": "https://www.fincen.gov/"},
            "ofac": {"name": "OFAC", "url": "https://ofac.treasury.gov/"},
            "cfpb": {"name": "CFPB", "url": "https://www.consumerfinance.gov/"},
            "ftc": {"name": "FTC", "url": "https://www.ftc.gov/"},
            "fatf": {"name": "FATF", "url": "https://www.fatf-gafi.org/"},
            "iosco": {"name": "IOSCO", "url": "https://www.iosco.org/"}
        }
        
        self.free_law_resources = {
            "court_listener": {"name": "CourtListener", "url": "https://www.courtlistener.com/"},
            "google_scholar": {"name": "Google Scholar", "url": "https://scholar.google.com/"},
            "justia": {"name": "Justia", "url": "https://law.justia.com/"},
            "cornell": {"name": "Cornell LII", "url": "https://www.law.cornell.edu/"}
        }
        
        self.constitution_resources = {
            "archives": "https://www.archives.gov/founding-docs/constitution",
            "congress": "https://constitution.congress.gov/",
            "cornell": "https://www.law.cornell.edu/constitution"
        }
        
        self.domains = {
            "constitutional": "Constitution, fundamental law",
            "statutory": "Written laws",
            "regulatory": "Agency rules",
            "common_law": "Case law precedent",
            "securities": "SEC, FINRA rules",
            "banking": "Federal Reserve, FDIC, OCC",
            "tax": "IRS code",
            "aml": "FinCEN, FATF"
        }
    
    def get_agency(self, name: str) -> Dict:
        return self.regulatory_agencies.get(name.lower(), {"error": "Agency not found"})
    
    def get_all_agencies(self) -> List[str]:
        return list(self.regulatory_agencies.keys())
    
    def search_cases(self, query: str) -> List[Dict]:
        return [{"source": "CourtListener", "url": f"https://www.courtlistener.com/search/?q={query.replace(' ', '+')}"}]
    
    def get_constitution(self) -> Dict:
        return self.constitution_resources

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw")
    parser.add_argument("--agencies", action="store_true", help="List agencies")
    parser.add_argument("--agency", help="Get agency info")
    parser.add_argument("--search-cases", help="Search case law")
    parser.add_argument("--constitution", action="store_true", help="Get constitution")
    parser.add_argument("--domains", action="store_true", help="List domains")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store memory")
    parser.add_argument("--recall", help="Recall memory")
    parser.add_argument("--agents", action="store_true", help="Show other agents")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    if args.agencies:
        print("\nRegulatory Agencies:")
        for a in agent.get_all_agencies():
            print(f"  {a.upper()}")
    elif args.agency:
        print(json.dumps(agent.get_agency(args.agency), indent=2))
    elif args.search_cases:
        print(json.dumps(agent.search_cases(args.search_cases), indent=2))
    elif args.constitution:
        print(json.dumps(agent.get_constitution(), indent=2))
    elif args.domains:
        print("\nLaw Domains:")
        for d, desc in agent.domains.items():
            print(f"  {d}: {desc}")
    elif args.remember:
        agent.shared.remember(args.remember[0], args.remember[1])
        print(f"✅ Memory stored: {args.remember[0]}")
    elif args.recall:
        results = agent.shared.recall(args.recall)
        if results:
            for r in results:
                print(f"\n🦞 {r[0]}: {r[1]}")
                print(f"   {r[2][:200]}...")
        else:
            print("No memories found")
    elif args.agents:
        agents = agent.shared.get_other_agents()
        print("\nOther Agents:")
        for name, caps in agents:
            print(f"  {name}: {caps[:60]}...")
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()

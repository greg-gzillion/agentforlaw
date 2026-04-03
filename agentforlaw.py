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

import requests
from datetime import datetime, timedelta

class LawRetriever:
    """Retrieve full text of cases, statutes, regulations"""
    
    @staticmethod
    def get_case_text(case_name: str) -> Dict:
        """Fetch case text from CourtListener API"""
        try:
            # Search CourtListener API
            url = f"https://www.courtlistener.com/api/rest/v3/opinions/?search={case_name.replace(' ', '+')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    return {
                        "case": case_name,
                        "citation": result.get('citation', 'Unknown'),
                        "court": result.get('court', 'Unknown'),
                        "date_filed": result.get('date_filed', 'Unknown'),
                        "url": result.get('absolute_url', ''),
                        "text_preview": result.get('plain_text', '')[:500] if result.get('plain_text') else ''
                    }
            return {"error": f"Could not retrieve {case_name}", "url": f"https://www.courtlistener.com/?q={case_name.replace(' ', '+')}"}
        except Exception as e:
            return {"error": str(e), "url": f"https://scholar.google.com/scholar?q={case_name.replace(' ', '+')}"}
    
    @staticmethod
    def get_statute(usc_citation: str) -> Dict:
        """Retrieve statute text from US Code"""
        # Format: "15 USC 78a" -> "15/78a"
        parts = usc_citation.upper().replace('USC', '').strip().split()
        if len(parts) >= 2:
            title = parts[0]
            section = parts[1]
            url = f"https://www.law.cornell.edu/uscode/text/{title}/{section}"
            return {
                "citation": usc_citation,
                "url": url,
                "title": f"Title {title}, Section {section}",
                "note": "Full text available at Cornell LII"
            }
        return {"error": "Invalid citation format", "example": "15 USC 78a"}
    
    @staticmethod
    def get_regulation(cfr_citation: str) -> Dict:
        """Retrieve regulation from eCFR"""
        # Format: "17 CFR 240.10b-5" -> "17/240.10b-5"
        parts = cfr_citation.upper().replace('CFR', '').strip().split()
        if len(parts) >= 2:
            title = parts[0]
            section = parts[1]
            url = f"https://www.ecfr.gov/current/title-{title}/section-{section}"
            return {
                "citation": cfr_citation,
                "url": url,
                "title": f"Title {title}, Section {section}",
                "agency": "CFR"
            }
        return {"error": "Invalid citation format"}

class LegalReasoner:
    """AI-powered legal analysis using Groq"""
    
    def __init__(self):
        self.groq_available = False
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.client = Groq(api_key=api_key)
                self.groq_available = True
        except:
            pass
    
    def analyze(self, question: str, context: str = "") -> str:
        """Analyze legal question using AI"""
        if not self.groq_available:
            return "GROQ_API_KEY not set. Install groq and set API key for AI analysis."
        
        prompt = f"""You are an agent of law analyzing this question:

Question: {question}

Context: {context}

Provide analysis based on legal principles, statutes, and case law."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis error: {e}"
    
    def apply_law_to_facts(self, law: str, facts: str) -> str:
        """Apply legal rule to specific facts"""
        if not self.groq_available:
            return "GROQ_API_KEY not set"
        
        prompt = f"""Apply this law to these facts:

LAW: {law}

FACTS: {facts}

Provide a legal analysis and conclusion."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis error: {e}"

class RealTimeMonitor:
    """Monitor for legal updates"""
    
    @staticmethod
    def get_recent_scotus() -> List[Dict]:
        """Get recent Supreme Court opinions"""
        try:
            url = "https://www.courtlistener.com/api/rest/v3/opinions/?court=scotus&order_by=date_filed&limit=5"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "case": r.get('case_name', 'Unknown'),
                    "date": r.get('date_filed', 'Unknown'),
                    "url": r.get('absolute_url', '')
                } for r in data.get('results', [])]
            return []
        except:
            return []
    
    @staticmethod
    def get_recent_sec_rulings() -> List[Dict]:
        """Get recent SEC releases"""
        try:
            url = "https://www.sec.gov/rules.shtml"
            return [{
                "source": "SEC",
                "url": "https://www.sec.gov/rules.shtml",
                "note": "Check SEC website for latest releases"
            }]
        except:
            return []

class JurisdictionComparator:
    """Compare laws across jurisdictions"""
    
    @staticmethod
    def compare(topic: str, jurisdictions: List[str]) -> Dict:
        """Compare legal treatment across jurisdictions"""
        results = {}
        for jur in jurisdictions:
            results[jur] = {
                "status": "Research needed",
                "search_url": f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}+{jur.replace('_', '+')}"
            }
        return {
            "topic": topic,
            "jurisdictions": jurisdictions,
            "comparison": results,
            "note": "Full comparison requires jurisdiction-specific research"
        }

    elif args.case_text:
        result = LawRetriever.get_case_text(args.case_text)
        print(json.dumps(result, indent=2))
    elif args.statute:
        result = LawRetriever.get_statute(args.statute)
        print(json.dumps(result, indent=2))
    elif args.regulation:
        result = LawRetriever.get_regulation(args.regulation)
        print(json.dumps(result, indent=2))
    elif args.analyze:
        reasoner = LegalReasoner()
        result = reasoner.analyze(args.analyze)
        print(f"\n🤖 Legal Analysis:\n{result}\n")
    elif args.apply:
        # Format: --apply "law text" --facts "fact pattern"
        if hasattr(args, 'facts') and args.facts:
            reasoner = LegalReasoner()
            result = reasoner.apply_law_to_facts(args.apply, args.facts)
            print(f"\n⚖️ Analysis:\n{result}\n")
        else:
            print("Use --apply 'law' --facts 'facts'")
    elif args.recent:
        if args.recent == "scotus":
            results = RealTimeMonitor.get_recent_scotus()
            print(json.dumps(results, indent=2))
        elif args.recent == "sec":
            results = RealTimeMonitor.get_recent_sec_rulings()
            print(json.dumps(results, indent=2))
    elif args.compare:
        # --compare topic jur1 jur2 jur3
        jurisdictions = args.compare.split(',') if ',' in args.compare else args.compare.split()
        comparator = JurisdictionComparator()
        result = comparator.compare(args.topic if hasattr(args, 'topic') else "legal issue", jurisdictions)
        print(json.dumps(result, indent=2))

# Add to argument parser
parser.add_argument("--case-text", help="Get full case text")
parser.add_argument("--statute", help="Get statute by citation (e.g., '15 USC 78a')")
parser.add_argument("--regulation", help="Get regulation by citation (e.g., '17 CFR 240.10b-5')")
parser.add_argument("--analyze", help="Analyze a legal question using AI")
parser.add_argument("--apply", help="Apply law to facts (use with --facts)")
parser.add_argument("--facts", help="Fact pattern for --apply")
parser.add_argument("--recent", choices=["scotus", "sec"], help="Get recent legal updates")
parser.add_argument("--compare", help="Compare jurisdictions: --compare 'topic jur1 jur2'")
parser.add_argument("--topic", help="Topic for jurisdiction comparison")

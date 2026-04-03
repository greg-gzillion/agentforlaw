#!/usr/bin/env python3
"""
agentforlaw - Agent of Law
Studies and applies LAW (statutes, codes, regulations, constitutions)
Does NOT practice law. Does NOT give legal advice. Does NOT engage in legal practice.
"""

import json
import sqlite3
import os
import requests
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
             "law study, statutes, codes, regulations, constitutions, document drafting", datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LawDocumentDrafting:
    """Draft law documents - statutes, codes, regulations, constitutions"""
    
    @staticmethod
    def draft(document_type: str, params: Dict) -> str:
        """Draft a law document"""
        
        if document_type == "statute":
            return LawDocumentDrafting._draft_statute(params)
        elif document_type == "regulation":
            return LawDocumentDrafting._draft_regulation(params)
        elif document_type == "code_section":
            return LawDocumentDrafting._draft_code_section(params)
        elif document_type == "constitutional_article":
            return LawDocumentDrafting._draft_constitutional_article(params)
        elif document_type == "notice":
            return LawDocumentDrafting._draft_notice(params)
        elif document_type == "writ":
            return LawDocumentDrafting._draft_writ(params)
        elif document_type == "rule":
            return LawDocumentDrafting._draft_rule(params)
        elif document_type == "order":
            return LawDocumentDrafting._draft_order(params)
        elif document_type == "finding":
            return LawDocumentDrafting._draft_finding(params)
        else:
            return f"Unknown document type: {document_type}"
    
    @staticmethod
    def _draft_statute(params: Dict) -> str:
        date = datetime.now().strftime("%Y")
        return f"""
[STATUTE]
Title: {params.get('title', 'An Act')}
Citation: {params.get('citation', 'Public Law ___')}
Enacted: {date}

Section 1. {params.get('section_1', 'Short title.')}
Section 2. {params.get('section_2', 'Findings.')}
Section 3. {params.get('section_3', 'Definitions.')}
Section 4. {params.get('section_4', 'Substance.')}
Section 5. {params.get('section_5', 'Enforcement.')}
Section 6. {params.get('section_6', 'Effective date.')}

Passed by the Legislature.
"""
    
    @staticmethod
    def _draft_regulation(params: Dict) -> str:
        return f"""
[REGULATION]
Agency: {params.get('agency', 'Agency')}
Citation: {params.get('citation', '___ CFR ___')}
Title: {params.get('title', 'Rule')}

§ {params.get('section', '1.0')} Purpose.
{params.get('purpose', 'Purpose statement.')}

§ {params.get('section', '2.0')} Definitions.
{params.get('definitions', 'Definitions.')}

§ {params.get('section', '3.0')} Requirements.
{params.get('requirements', 'Requirements.')}

§ {params.get('section', '4.0')} Enforcement.
{params.get('enforcement', 'Enforcement.')}

Effective: {params.get('effective', '30 days after publication')}
"""
    
    @staticmethod
    def _draft_code_section(params: Dict) -> str:
        return f"""
[CODE SECTION]
Code: {params.get('code', 'Code')}
Title: {params.get('title', '___')}
Section: {params.get('section', '§ ___')}

(a) {params.get('subsection_a', 'Rule.')}
(b) {params.get('subsection_b', 'Exception.')}
(c) {params.get('subsection_c', 'Penalty.')}
"""
    
    @staticmethod
    def _draft_constitutional_article(params: Dict) -> str:
        return f"""
[CONSTITUTION]
Article: {params.get('article', '___')}
Section: {params.get('section', '___')}

Clause 1. {params.get('clause_1', 'Text.')}
Clause 2. {params.get('clause_2', 'Text.')}
Clause 3. {params.get('clause_3', 'Text.')}

Ratified: {params.get('ratified', 'Date')}
"""
    
    @staticmethod
    def _draft_notice(params: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[NOTICE]
Date: {date}
To: {params.get('to', 'Parties')}
From: {params.get('from', 'Authority')}
Subject: {params.get('subject', 'Notice')}

Notice is given that:
{params.get('body', 'Notice text.')}

Effective: {params.get('effective', 'Upon publication')}
"""
    
    @staticmethod
    def _draft_writ(params: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[WRIT]
Date: {date}
To: {params.get('to', 'Recipient')}
From: {params.get('from', 'Authority')}

ORDERED: {params.get('order', 'Order text.')}

Returnable by: {params.get('return_date', 'Date')}
"""
    
    @staticmethod
    def _draft_rule(params: Dict) -> str:
        return f"""
[RULE]
Number: {params.get('number', '___')}
Title: {params.get('title', 'Rule')}

(a) {params.get('subpart_a', 'Rule text.')}
(b) {params.get('subpart_b', 'Rule text.')}
(c) {params.get('subpart_c', 'Rule text.')}

Effective: {params.get('effective', 'Date')}
"""
    
    @staticmethod
    def _draft_order(params: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[ORDER]
Date: {date}
Case: {params.get('case', 'Case')}

ORDERED: {params.get('decree', 'Order text.')}

So ordered.
"""
    
    @staticmethod
    def _draft_finding(params: Dict) -> str:
        return f"""
[FINDING]
Case: {params.get('case', 'Case')}

The finder finds that:
{params.get('finding', 'Finding text.')}

Conclusion: {params.get('conclusion', 'Conclusion.')}
"""

class LawRetriever:
    @staticmethod
    def get_statute(citation: str) -> Dict:
        parts = citation.upper().replace('USC', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.law.cornell.edu/uscode/text/{parts[0]}/{parts[1]}"}
        return {"error": "Invalid format. Example: 15 USC 78a"}
    
    @staticmethod
    def get_regulation(citation: str) -> Dict:
        parts = citation.upper().replace('CFR', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.ecfr.gov/current/title-{parts[0]}/section-{parts[1]}"}
        return {"error": "Invalid format. Example: 17 CFR 240.10b-5"}

class LawReasoner:
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
    
    def analyze(self, question: str) -> str:
        if not self.groq_available:
            return "GROQ_API_KEY not set."
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Answer this question about statutes, codes, regulations, or constitutions: {question}"}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        self.reasoner = LawReasoner()
        
        self.regulatory_agencies = {
            "sec": {"name": "Securities and Exchange Commission", "url": "https://www.sec.gov/"},
            "cftc": {"name": "Commodity Futures Trading Commission", "url": "https://www.cftc.gov/"},
            "finra": {"name": "FINRA", "url": "https://www.finra.org/"}
        }
        
        self.domains = {
            "constitutional": "Constitution",
            "statutory": "Statutes",
            "regulatory": "Regulations",
            "securities": "Securities laws"
        }
    
    def get_agency(self, name: str) -> Dict:
        return self.regulatory_agencies.get(name.lower(), {"error": "Not found"})
    
    def get_all_agencies(self) -> List[str]:
        return list(self.regulatory_agencies.keys())

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw - Agent of Law")
    
    parser.add_argument("--agencies", action="store_true", help="List agencies")
    parser.add_argument("--agency", help="Get agency info")
    parser.add_argument("--domains", action="store_true", help="List law domains")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store in shared memory")
    parser.add_argument("--recall", help="Recall from shared memory")
    parser.add_argument("--agents", action="store_true", help="Show other agents")
    parser.add_argument("--statute", help="Get statute URL")
    parser.add_argument("--regulation", help="Get regulation URL")
    parser.add_argument("--analyze", help="Analyze law question")
    parser.add_argument("--draft", choices=["statute", "regulation", "code_section", "constitutional_article", "notice", "writ", "rule", "order", "finding"], help="Draft a law document")
    parser.add_argument("--params", help="JSON parameters for drafting")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    if args.agencies:
        print("\nAgencies:")
        for a in agent.get_all_agencies():
            print(f"  {a.upper()}")
    elif args.agency:
        print(json.dumps(agent.get_agency(args.agency), indent=2))
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
                print(f"\n🦞 {r[0]}: {r[1]}\n   {r[2][:200]}...")
        else:
            print("No memories found")
    elif args.agents:
        others = agent.shared.get_other_agents()
        print("\nOther Agents:")
        for name, caps in others:
            print(f"  {name}: {caps[:60]}...")
    elif args.statute:
        print(json.dumps(LawRetriever.get_statute(args.statute), indent=2))
    elif args.regulation:
        print(json.dumps(LawRetriever.get_regulation(args.regulation), indent=2))
    elif args.analyze:
        print(f"\n{agent.reasoner.analyze(args.analyze)}\n")
    elif args.draft:
        params = json.loads(args.params) if args.params else {}
        result = LawDocumentDrafting.draft(args.draft, params)
        print(result)
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()

class CaseLaw:
    """Case law - judicial decisions that interpret statutes, regulations, constitutions"""
    
    @staticmethod
    def get_case(citation: str) -> Dict:
        """Get case by citation (e.g., 'Marbury v. Madison', '5 U.S. 137')"""
        try:
            # Search CourtListener
            url = f"https://www.courtlistener.com/api/rest/v3/opinions/?search={citation.replace(' ', '+')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    r = data['results'][0]
                    return {
                        "case_name": r.get('case_name', citation),
                        "citation": r.get('citation', 'Unknown'),
                        "court": r.get('court', 'Unknown'),
                        "date": r.get('date_filed', 'Unknown'),
                        "url": r.get('absolute_url', ''),
                        "summary": r.get('plain_text', '')[:500] if r.get('plain_text') else ''
                    }
            return {"error": "Case not found", "search_url": f"https://scholar.google.com/scholar?q={citation.replace(' ', '+')}"}
        except Exception as e:
            return {"error": str(e), "search_url": f"https://www.courtlistener.com/?q={citation.replace(' ', '+')}"}
    
    @staticmethod
    def search_cases(query: str, court: str = None) -> List[Dict]:
        """Search case law by keyword"""
        try:
            url = f"https://www.courtlistener.com/api/rest/v3/opinions/?search={query.replace(' ', '+')}"
            if court:
                url += f"&court={court}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "case_name": r.get('case_name', 'Unknown'),
                    "citation": r.get('citation', 'Unknown'),
                    "court": r.get('court', 'Unknown'),
                    "date": r.get('date_filed', 'Unknown'),
                    "url": r.get('absolute_url', '')
                } for r in data.get('results', [])[:10]]
            return []
        except:
            return []
    
    @staticmethod
    def get_cases_by_citation(citation: str) -> Dict:
        """Get case by standard citation (e.g., '347 U.S. 483' for Brown v. Board)"""
        # Parse citation like "347 U.S. 483"
        return CaseLaw.get_case(citation)
    
    @staticmethod
    def get_landmark_cases() -> List[Dict]:
        """Return list of landmark US cases"""
        return [
            {"name": "Marbury v. Madison", "citation": "5 U.S. 137", "year": 1803, "holding": "Judicial review established"},
            {"name": "McCulloch v. Maryland", "citation": "17 U.S. 316", "year": 1819, "holding": "Federal supremacy, implied powers"},
            {"name": "Brown v. Board of Education", "citation": "347 U.S. 483", "year": 1954, "holding": "Separate educational facilities are inherently unequal"},
            {"name": "Miranda v. Arizona", "citation": "384 U.S. 436", "year": 1966, "holding": "Fifth Amendment right against self-incrimination"},
            {"name": "Roe v. Wade", "citation": "410 U.S. 113", "year": 1973, "holding": "Right to privacy under Due Process Clause"},
            {"name": "Citizens United v. FEC", "citation": "558 U.S. 310", "year": 2010, "holding": "Corporate political spending is free speech"},
            {"name": "SEC v. W.J. Howey Co.", "citation": "328 U.S. 293", "year": 1946, "holding": "Howey test for investment contracts"},
            {"name": "Chevron U.S.A. v. NRDC", "citation": "467 U.S. 837", "year": 1984, "holding": "Chevron deference to agency interpretations"}
        ]

# Add to argument parser
parser.add_argument("--case", help="Get case by name or citation")
parser.add_argument("--search-cases", help="Search case law by keyword")
parser.add_argument("--landmark-cases", action="store_true", help="List landmark cases")
parser.add_argument("--court", help="Filter by court (scotus, ca1, ca2, etc.)")

# Add to main
elif args.case:
    result = CaseLaw.get_case(args.case)
    print(json.dumps(result, indent=2))
elif args.search_cases:
    results = CaseLaw.search_cases(args.search_cases, args.court)
    print(json.dumps(results, indent=2))
elif args.landmark_cases:
    cases = CaseLaw.get_landmark_cases()
    print("\n📜 LANDMARK CASES:")
    print("=" * 60)
    for c in cases:
        print(f"\n{c['name']} ({c['year']})")
        print(f"   Citation: {c['citation']}")
        print(f"   Holding: {c['holding']}")

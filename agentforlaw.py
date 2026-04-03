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

class USLawResources:
    """Complete US law resources - case law, statutes, regulations, dictionaries"""
    
    # Primary law sources
    PRIMARY_SOURCES = {
        "us_constitution": {
            "url": "https://constitution.congress.gov/",
            "annotated": "https://www.law.cornell.edu/constitution-conan",
            "full_text": "https://www.archives.gov/founding-docs/constitution-transcript"
        },
        "us_code": {
            "url": "https://uscode.house.gov/",
            "cornell": "https://www.law.cornell.edu/uscode/text",
            "govinfo": "https://www.govinfo.gov/app/collection/uscode"
        },
        "code_of_federal_regulations": {
            "url": "https://www.ecfr.gov/",
            "cornell": "https://www.law.cornell.edu/cfr/text"
        },
        "federal_rules": {
            "civil_procedure": "https://www.law.cornell.edu/rules/frcp",
            "criminal_procedure": "https://www.law.cornell.edu/rules/frcrmp",
            "evidence": "https://www.law.cornell.edu/rules/fre",
            "appellate": "https://www.law.cornell.edu/rules/frap"
        }
    }
    
    # Case law sources
    CASE_Law_SOURCES = {
        "supreme_court": {
            "official": "https://www.supremecourt.gov/opinions/opinions.aspx",
            "oyez": "https://www.oyez.org/",
            "cornell": "https://www.law.cornell.edu/supremecourt/",
            "justia": "https://supreme.justia.com/",
            "scotusblog": "https://www.scotusblog.com/"
        },
        "federal_courts": {
            "courtlistener": "https://www.courtlistener.com/",
            "google_scholar": "https://scholar.google.com/",
            "findlaw": "https://caselaw.findlaw.com/",
            "justia": "https://law.justia.com/cases/federal/",
            "open_case_law": "https://open.case.law/",
            "harvard_case_law": "https://case.law/"
        },
        "state_courts": {
            "cornell_states": "https://www.law.cornell.edu/states/",
            "justia_states": "https://law.justia.com/cases/",
            "findlaw_states": "https://caselaw.findlaw.com/court"
        }
    }
    
    # Legal dictionaries
    LAW_DICTIONARIES = {
        "blacks_law_dictionary": {
            "name": "Black's Law Dictionary",
            "url": "https://thelawdictionary.org/",
            "cornell": "https://www.law.cornell.edu/wex",
            "alternative": "https://dictionary.law.com/"
        },
        "law_dictionary": {
            "name": "Law Dictionary",
            "url": "https://dictionary.law.com/",
            "merriam_webster_law": "https://www.merriam-webster.com/law"
        }
    }
    
    # Secondary sources
    SECONDARY_SOURCES = {
        "restatements": {
            "name": "Restatements of Law",
            "ali": "https://www.ali.org/publications/restatements-law/"
        },
        "law_reviews": {
            "harvard_law_review": "https://harvardlawreview.org/",
            "yale_law_journal": "https://www.yalelawjournal.org/",
            "columbia_law_review": "https://columbialawreview.org/"
        },
        "treatises": {
            "cornell_lii": "https://www.law.cornell.edu/wex",
            "legal_information_institute": "https://www.law.cornell.edu/"
        }
    }
    
    # Subject-specific law
    SUBJECT_LAW = {
        "constitutional_law": {
            "cornell": "https://www.law.cornell.edu/constitution",
            "justia": "https://law.justia.com/constitution/us/",
            "congress": "https://constitution.congress.gov/"
        },
        "criminal_law": {
            "us_code_title_18": "https://www.law.cornell.edu/uscode/text/18",
            "federal_rules_criminal": "https://www.law.cornell.edu/rules/frcrmp",
            "justia_criminal": "https://law.justia.com/criminal/"
        },
        "civil_law": {
            "federal_rules_civil": "https://www.law.cornell.edu/rules/frcp",
            "cornell_civil": "https://www.law.cornell.edu/wex/civil_law"
        },
        "contract_law": {
            "cornell_contracts": "https://www.law.cornell.edu/wex/contract",
            "uniform_commercial_code": "https://www.law.cornell.edu/ucc",
            "restatement_contracts": "https://www.ali.org/publications/restatement-law-second-contracts/"
        },
        "tort_law": {
            "cornell_torts": "https://www.law.cornell.edu/wex/tort",
            "restatement_torts": "https://www.ali.org/publications/restatement-law-second-torts/",
            "justia_torts": "https://law.justia.com/injury/"
        },
        "property_law": {
            "cornell_property": "https://www.law.cornell.edu/wex/property",
            "justia_property": "https://law.justia.com/property/"
        },
        "evidence_law": {
            "federal_rules_evidence": "https://www.law.cornell.edu/rules/fre",
            "cornell_evidence": "https://www.law.cornell.edu/wex/evidence"
        },
        "civil_procedure": {
            "federal_rules_civil_procedure": "https://www.law.cornell.edu/rules/frcp",
            "cornell_civil_procedure": "https://www.law.cornell.edu/wex/civil_procedure"
        },
        "criminal_procedure": {
            "federal_rules_criminal_procedure": "https://www.law.cornell.edu/rules/frcrmp",
            "cornell_criminal_procedure": "https://www.law.cornell.edu/wex/criminal_procedure"
        }
    }
    
    @staticmethod
    def get_primary_source(name: str) -> Dict:
        """Get primary law source URL"""
        return USLawResources.PRIMARY_SOURCES.get(name, {"error": "Not found"})
    
    @staticmethod
    def get_case_source(name: str) -> Dict:
        """Get case law source URL"""
        return USLawResources.CASE_Law_SOURCES.get(name, {"error": "Not found"})
    
    @staticmethod
    def get_law_dictionary(name: str = "blacks_law_dictionary") -> Dict:
        """Get law dictionary URL"""
        return USLawResources.LAW_DICTIONARIES.get(name, USLawResources.LAW_DICTIONARIES["blacks_law_dictionary"])
    
    @staticmethod
    def get_subject_law(subject: str) -> Dict:
        """Get subject-specific law resources"""
        return USLawResources.SUBJECT_LAW.get(subject, {"error": f"Subject '{subject}' not found"})
    
    @staticmethod
    def list_subjects() -> List[str]:
        """List all available law subjects"""
        return list(USLawResources.SUBJECT_LAW.keys())
    
    @staticmethod
    def blacks_dictionary_term(term: str) -> str:
        """Search Black's Law Dictionary for a term"""
        return f"https://thelawdictionary.org/?s={term.replace(' ', '+')}"
    
    @staticmethod
    def wex_definition(term: str) -> str:
        """Search Cornell WEX legal dictionary"""
        return f"https://www.law.cornell.edu/wex/{term.replace(' ', '_')}"

# Add to argument parser
parser.add_argument("--primary-source", help="Get primary law source (us_constitution, us_code, code_of_federal_regulations)")
parser.add_argument("--case-source", help="Get case law source (supreme_court, federal_courts, state_courts)")
parser.add_argument("--dictionary", help="Get law dictionary (blacks_law_dictionary)")
parser.add_argument("--define", help="Define a law term using Black's Law Dictionary")
parser.add_argument("--subject", help="Get subject-specific law (constitutional_law, criminal_law, contract_law, tort_law, etc.)")
parser.add_argument("--list-subjects", action="store_true", help="List all law subjects")

# Add to main
elif args.primary_source:
    result = USLawResources.get_primary_source(args.primary_source)
    print(json.dumps(result, indent=2))
elif args.case_source:
    result = USLawResources.get_case_source(args.case_source)
    print(json.dumps(result, indent=2))
elif args.dictionary:
    result = USLawResources.get_law_dictionary(args.dictionary)
    print(json.dumps(result, indent=2))
elif args.define:
    url = USLawResources.blacks_dictionary_term(args.define)
    wex_url = USLawResources.wex_definition(args.define)
    print(f"\n📖 BLACK'S LAW DICTIONARY - '{args.define}'")
    print(f"   Search: {url}")
    print(f"   WEX Definition: {wex_url}")
elif args.subject:
    result = USLawResources.get_subject_law(args.subject)
    print(json.dumps(result, indent=2))
elif args.list_subjects:
    subjects = USLawResources.list_subjects()
    print("\n📚 LAW SUBJECTS:")
    for s in subjects:
        print(f"  • {s.replace('_', ' ').title()}")

class USCourts:
    """Access to all public US courts - federal and state"""
    
    # Federal Courts
    FEDERAL_COURTS = {
        "supreme_court": {
            "name": "Supreme Court of the United States",
            "url": "https://www.supremecourt.gov/",
            "opinions": "https://www.supremecourt.gov/opinions/opinions.aspx",
            "oral_arguments": "https://www.oyez.org/",
            "docket": "https://www.supremecourt.gov/docket/docket.aspx"
        },
        "circuit_courts": {
            "first_circuit": {"name": "1st Circuit Court of Appeals", "url": "https://www.ca1.uscourts.gov/"},
            "second_circuit": {"name": "2nd Circuit Court of Appeals", "url": "https://www.ca2.uscourts.gov/"},
            "third_circuit": {"name": "3rd Circuit Court of Appeals", "url": "https://www.ca3.uscourts.gov/"},
            "fourth_circuit": {"name": "4th Circuit Court of Appeals", "url": "https://www.ca4.uscourts.gov/"},
            "fifth_circuit": {"name": "5th Circuit Court of Appeals", "url": "https://www.ca5.uscourts.gov/"},
            "sixth_circuit": {"name": "6th Circuit Court of Appeals", "url": "https://www.ca6.uscourts.gov/"},
            "seventh_circuit": {"name": "7th Circuit Court of Appeals", "url": "https://www.ca7.uscourts.gov/"},
            "eighth_circuit": {"name": "8th Circuit Court of Appeals", "url": "https://www.ca8.uscourts.gov/"},
            "ninth_circuit": {"name": "9th Circuit Court of Appeals", "url": "https://www.ca9.uscourts.gov/"},
            "tenth_circuit": {"name": "10th Circuit Court of Appeals", "url": "https://www.ca10.uscourts.gov/"},
            "eleventh_circuit": {"name": "11th Circuit Court of Appeals", "url": "https://www.ca11.uscourts.gov/"},
            "dc_circuit": {"name": "DC Circuit Court of Appeals", "url": "https://www.cadc.uscourts.gov/"},
            "federal_circuit": {"name": "Federal Circuit Court of Appeals", "url": "https://www.cafc.uscourts.gov/"}
        },
        "district_courts": {
            "search": "https://www.uscourts.gov/court-locator",
            "list": "https://www.uscourts.gov/district-courts",
            "opinions": "https://www.courtlistener.com/?court=district"
        },
        "bankruptcy_courts": {
            "list": "https://www.uscourts.gov/bankruptcy-courts",
            "pacer": "https://pacer.uscourts.gov/"
        },
        "specialized_courts": {
            "court_of_international_trade": "https://www.cit.uscourts.gov/",
            "court_of_federal_claims": "https://www.uscfc.uscourts.gov/",
            "tax_court": "https://www.ustaxcourt.gov/",
            "veterans_claims": "https://www.uscourts.cavc.gov/",
            "armed_forces": "https://www.armfor.uscourts.gov/"
        }
    }
    
    # State Courts - All 50 States
    STATE_COURTS = {
        "alabama": {"supreme": "https://judicial.alabama.gov/library/docs.cfm", "appellate": "https://judicial.alabama.gov/library/appellate"},
        "alaska": {"supreme": "https://akcourts.gov/courts/supreme-court", "appellate": "https://akcourts.gov/courts/court-of-appeals"},
        "arizona": {"supreme": "https://www.azcourts.gov/courts/az-supreme-court", "appellate": "https://www.azcourts.gov/courts/court-of-appeals"},
        "arkansas": {"supreme": "https://arcourts.gov/courts/supreme-court", "appellate": "https://arcourts.gov/courts/court-of-appeals"},
        "california": {"supreme": "https://supreme.courts.ca.gov/", "appellate": "https://www.courts.ca.gov/courtsofappeal.htm"},
        "colorado": {"supreme": "https://www.courts.state.co.us/Courts/Supreme_Court/Index.cfm", "appellate": "https://www.courts.state.co.us/Courts/Court_of_Appeals/Index.cfm"},
        "connecticut": {"supreme": "https://www.jud.ct.gov/supapp/default.htm", "appellate": "https://www.jud.ct.gov/courts/appellate.html"},
        "delaware": {"supreme": "https://courts.delaware.gov/supreme/", "chancery": "https://courts.delaware.gov/chancery/"},
        "florida": {"supreme": "https://www.floridasupremecourt.org/", "appellate": "https://www.flcourts.gov/Florida-Courts/District-Courts-of-Appeal"},
        "georgia": {"supreme": "https://www.gasupreme.us/", "appellate": "https://www.gaappeals.us/"},
        "hawaii": {"supreme": "https://www.courts.state.hi.us/courts/supreme_court", "appellate": "https://www.courts.state.hi.us/courts/intermediate_court_of_appeals"},
        "idaho": {"supreme": "https://isc.idaho.gov/", "appellate": "https://isc.idaho.gov/appellate"},
        "illinois": {"supreme": "https://illinoiscourts.gov/courts/supreme-court", "appellate": "https://illinoiscourts.gov/courts/appellate-court"},
        "indiana": {"supreme": "https://www.in.gov/courts/supreme/", "appellate": "https://www.in.gov/courts/appeals/"},
        "iowa": {"supreme": "https://www.iowacourts.gov/for-the-public/court-directory/supreme-court/", "appellate": "https://www.iowacourts.gov/for-the-public/court-directory/court-of-appeals/"},
        "kansas": {"supreme": "https://www.kscourts.org/Courts/Supreme-Court", "appellate": "https://www.kscourts.org/Courts/Court-of-Appeals"},
        "kentucky": {"supreme": "https://kycourts.gov/Courts/Supreme-Court/Pages/default.aspx", "appellate": "https://kycourts.gov/Courts/Court-of-Appeals/Pages/default.aspx"},
        "louisiana": {"supreme": "https://www.lasc.org/", "appellate": "https://www.la-courtofappeal.org/"},
        "maine": {"supreme": "https://www.courts.maine.gov/courts/sjc/", "appellate": "https://www.courts.maine.gov/courts/sjc/appellate"},
        "maryland": {"supreme": "https://www.courts.state.md.us/courts/appellate/supremecourt", "appellate": "https://www.courts.state.md.us/courts/appellate/appellatecourt"},
        "massachusetts": {"supreme": "https://www.mass.gov/orgs/supreme-judicial-court", "appellate": "https://www.mass.gov/orgs/appeals-court"},
        "michigan": {"supreme": "https://www.courts.michigan.gov/courts/michigan-supreme-court/", "appellate": "https://www.courts.michigan.gov/courts/court-of-appeals/"},
        "minnesota": {"supreme": "https://www.mncourts.gov/SupremeCourt.aspx", "appellate": "https://www.mncourts.gov/CourtofAppeals.aspx"},
        "mississippi": {"supreme": "https://courts.ms.gov/supremecourt/supremecourt.php", "appellate": "https://courts.ms.gov/courtofappeals/courtofappeals.php"},
        "missouri": {"supreme": "https://www.courts.mo.gov/page.jsp?id=27", "appellate": "https://www.courts.mo.gov/page.jsp?id=28"},
        "montana": {"supreme": "https://courts.mt.gov/supreme", "appellate": "https://courts.mt.gov/other_courts/appellate"},
        "nebraska": {"supreme": "https://supremecourt.nebraska.gov/", "appellate": "https://supremecourt.nebraska.gov/courts/court-appeals"},
        "nevada": {"supreme": "https://nvcourts.gov/Supreme/", "appellate": "https://nvcourts.gov/Court_of_Appeals/"},
        "new_hampshire": {"supreme": "https://www.courts.state.nh.us/supreme/", "appellate": "https://www.courts.state.nh.us/supreme/appellate"},
        "new_jersey": {"supreme": "https://www.njcourts.gov/courts/supreme", "appellate": "https://www.njcourts.gov/courts/appellate"},
        "new_mexico": {"supreme": "https://supremecourt.nmcourts.gov/", "appellate": "https://coa.nmcourts.gov/"},
        "new_york": {"supreme": "https://www.nycourts.gov/ctapps/", "appellate": "https://www.nycourts.gov/courts/ad1/"},  # Court of Appeals is highest
        "north_carolina": {"supreme": "https://www.nccourts.gov/courts/supreme-court", "appellate": "https://www.nccourts.gov/courts/court-of-appeals"},
        "north_dakota": {"supreme": "https://www.ndcourts.gov/court/supreme-court", "appellate": "https://www.ndcourts.gov/court/court-of-appeals"},
        "ohio": {"supreme": "https://www.supremecourt.ohio.gov/", "appellate": "https://www.supremecourt.ohio.gov/appellate"},
        "oklahoma": {"supreme": "https://www.oscn.net/", "appellate": "https://www.okhistory.org/courts"},
        "oregon": {"supreme": "https://www.courts.oregon.gov/courts/supreme/Pages/default.aspx", "appellate": "https://www.courts.oregon.gov/courts/court-of-appeals/Pages/default.aspx"},
        "pennsylvania": {"supreme": "https://www.pacourts.us/courts/supreme-court", "appellate": "https://www.pacourts.us/courts/commonwealth-court"},
        "rhode_island": {"supreme": "https://www.courts.ri.gov/Courts/SupremeCourt/Pages/default.aspx", "appellate": "https://www.courts.ri.gov/Courts/SuperiorCourt/Pages/default.aspx"},
        "south_carolina": {"supreme": "https://www.sccourts.org/supreme/", "appellate": "https://www.sccourts.org/courtAppeals/"},
        "south_dakota": {"supreme": "https://ujs.sd.gov/Supreme_Court/", "appellate": "https://ujs.sd.gov/Appellate_Court/"},
        "tennessee": {"supreme": "https://www.tncourts.gov/courts/supreme-court", "appellate": "https://www.tncourts.gov/courts/court-appeals"},
        "texas": {"supreme": "https://www.txcourts.gov/supreme/", "criminal_appeals": "https://www.txcourts.gov/cca/", "appellate": "https://www.txcourts.gov/courts-of-appeals/"},
        "utah": {"supreme": "https://www.utcourts.gov/courts/supreme/", "appellate": "https://www.utcourts.gov/courts/appellate/"},
        "vermont": {"supreme": "https://www.vermontjudiciary.org/supreme-court", "appellate": "https://www.vermontjudiciary.org/appellate-division"},
        "virginia": {"supreme": "https://www.vacourts.gov/courts/scv/home.html", "appellate": "https://www.vacourts.gov/courts/cav/home.html"},
        "washington": {"supreme": "https://www.courts.wa.gov/appellate_trial_courts/supreme/", "appellate": "https://www.courts.wa.gov/appellate_trial_courts/court_of_appeals/"},
        "west_virginia": {"supreme": "https://www.courtswv.gov/supreme-court", "appellate": "https://www.courtswv.gov/intermediate-court"},
        "wisconsin": {"supreme": "https://www.wicourts.gov/courts/supreme/index.htm", "appellate": "https://www.wicourts.gov/courts/appeals/index.htm"},
        "wyoming": {"supreme": "https://www.courts.state.wy.us/supreme-court", "appellate": "https://www.courts.state.wy.us/appellate-court"}
    }
    
    # Court opinion databases (public access)
    OPINION_DATABASES = {
        "courtlistener": "https://www.courtlistener.com/",
        "google_scholar_cases": "https://scholar.google.com/scholar?as_sdt=4%2C5&as_vis=1",
        "justia_federal": "https://law.justia.com/cases/federal/",
        "justia_state": "https://law.justia.com/cases/",
        "findlaw_cases": "https://caselaw.findlaw.com/",
        "cornell_lii": "https://www.law.cornell.edu/opinions.html",
        "open_case_law": "https://open.case.law/",
        "harvard_case_law": "https://case.law/",
        "pacer": "https://pacer.uscourts.gov/",
        "recap": "https://www.courtlistener.com/recap/"
    }
    
    @staticmethod
    def get_federal_court(court_name: str) -> Dict:
        """Get federal court by name"""
        if court_name == "supreme_court":
            return USCourts.FEDERAL_COURTS["supreme_court"]
        elif court_name in USCourts.FEDERAL_COURTS["circuit_courts"]:
            return USCourts.FEDERAL_COURTS["circuit_courts"][court_name]
        else:
            return {"error": f"Court '{court_name}' not found"}
    
    @staticmethod
    def get_state_court(state: str, court_type: str = "supreme") -> Dict:
        """Get state court by state name"""
        state_key = state.lower().replace(" ", "_")
        if state_key in USCourts.STATE_COURTS:
            court = USCourts.STATE_COURTS[state_key]
            return court.get(court_type, court.get("supreme", {"error": "Court type not found"}))
        return {"error": f"State '{state}' not found"}
    
    @staticmethod
    def list_federal_circuits() -> List[str]:
        """List all federal circuit courts"""
        return list(USCourts.FEDERAL_COURTS["circuit_courts"].keys())
    
    @staticmethod
    def list_states() -> List[str]:
        """List all states"""
        return list(USCourts.STATE_COURTS.keys())
    
    @staticmethod
    def search_all_courts(query: str) -> Dict:
        """Search all courts for a case"""
        return {
            "search_term": query,
            "supreme_court": f"https://www.supremecourt.gov/search.aspx?search={query.replace(' ', '%20')}",
            "courtlistener": f"https://www.courtlistener.com/search/?q={query.replace(' ', '+')}",
            "justia": f"https://law.justia.com/cases/?q={query.replace(' ', '+')}",
            "google_scholar": f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
        }

# Add to argument parser
parser.add_argument("--federal-court", help="Get federal court (supreme_court, first_circuit, second_circuit, etc.)")
parser.add_argument("--state-court", nargs=2, metavar=('STATE', 'TYPE'), help="Get state court (e.g., 'california supreme')")
parser.add_argument("--list-circuits", action="store_true", help="List all federal circuits")
parser.add_argument("--list-states", action="store_true", help="List all states")
parser.add_argument("--search-courts", help="Search all courts for a case")
parser.add_argument("--opinion-dbs", action="store_true", help="List opinion databases")

# Add to main
elif args.federal_court:
    result = USCourts.get_federal_court(args.federal_court)
    print(json.dumps(result, indent=2))
elif args.state_court:
    state, court_type = args.state_court
    result = USCourts.get_state_court(state, court_type)
    print(json.dumps(result, indent=2))
elif args.list_circuits:
    circuits = USCourts.list_federal_circuits()
    print("\n🏛️ FEDERAL CIRCUIT COURTS:")
    for c in circuits:
        print(f"  • {c.replace('_', ' ').title()}")
elif args.list_states:
    states = USCourts.list_states()
    print("\n🗺️ ALL 50 STATES:")
    for s in states[:25]:
        print(f"  • {s.replace('_', ' ').title()}")
    print("  ... and 25 more")
elif args.search_courts:
    result = USCourts.search_all_courts(args.search_courts)
    print(json.dumps(result, indent=2))
elif args.opinion_dbs:
    dbs = USCourts.OPINION_DATABASES
    print("\n📚 PUBLIC OPINION DATABASES:")
    for name, url in dbs.items():
        print(f"  • {name.title()}: {url}")

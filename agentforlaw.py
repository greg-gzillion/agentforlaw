#!/usr/bin/env python3
"""
agentforlaw - Agent that studies statutes, codes, regulations, and rules
Part of the claw ecosystem: rustypycraw, eagleclaw, crustyclaw, claw-coder, agentforlaw
"""

import json
from datetime import datetime
from typing import List, Dict

class AgentForLaw:
    """AgentForLaw - understands law as a system of rules across all jurisdictions"""
    
    def __init__(self):
        # FREE LAW RESOURCES - Court cases, case law, constitutions
        self.free_law_resources = {
            # US Supreme Court & Federal Cases
            "supreme_court": {
                "name": "US Supreme Court",
                "url": "https://www.supremecourt.gov/opinions/opinions.aspx",
                "cases": "https://www.oyez.org/",
                "oral_arguments": "https://www.oyez.org/cases",
                "recent_opinions": "https://www.supremecourt.gov/opinions/slipopinion.aspx"
            },
            "court_listener": {
                "name": "CourtListener - Free case law",
                "url": "https://www.courtlistener.com/",
                "search": "https://www.courtlistener.com/search/",
                "api": "https://www.courtlistener.com/api/rest/v3/",
                "opinions": "https://www.courtlistener.com/opinions/"
            },
            "google_scholar": {
                "name": "Google Scholar - Legal Opinions",
                "url": "https://scholar.google.com/scholar?as_ylo=2024&q=&hl=en&as_sdt=0,5&as_vis=1",
                "cases": "https://scholar.google.com/intl/en/scholar/legal.html",
                "state_cases": "https://scholar.google.com/scholar_case",
                "federal_cases": "https://scholar.google.com/scholar_case?q=federal&hl=en&as_sdt=2006"
            },
            "findlaw": {
                "name": "FindLaw - Cases and Codes",
                "url": "https://caselaw.findlaw.com/",
                "us_supreme": "https://caselaw.findlaw.com/court/us-supreme-court",
                "state_courts": "https://caselaw.findlaw.com/court",
                "federal_courts": "https://caselaw.findlaw.com/court/us-federal-courts"
            },
            "justia": {
                "name": "Justia - Free Law",
                "url": "https://law.justia.com/",
                "us_supreme": "https://supreme.justia.com/",
                "federal_courts": "https://law.justia.com/cases/federal/",
                "state_courts": "https://law.justia.com/cases/",
                "constitution": "https://law.justia.com/constitution/us/"
            },
            "cornell_law": {
                "name": "Cornell LII - Legal Information Institute",
                "url": "https://www.law.cornell.edu/",
                "us_code": "https://www.law.cornell.edu/uscode/text",
                "constitution": "https://www.law.cornell.edu/constitution",
                "supreme_court": "https://www.law.cornell.edu/supremecourt/",
                "cfr": "https://www.law.cornell.edu/cfr/text"
            },
            "open_case_law": {
                "name": "Open Case Law",
                "url": "https://open.case.law/",
                "api": "https://open.case.law/api/",
                "courts": "https://open.case.law/courts/",
                "search": "https://open.case.law/search/"
            },
            "caselaw_access": {
                "name": "Caselaw Access Project (Harvard)",
                "url": "https://case.law/",
                "api": "https://case.law/api/",
                "bulk_data": "https://case.law/download/",
                "search": "https://case.law/search/"
            },
            "fastcase": {
                "name": "Fastcase - Free Case Law",
                "url": "https://www.fastcase.com/",
                "search": "https://www.fastcase.com/search/",
                "coverage": "https://www.fastcase.com/coverage/"
            },
            "versuslaw": {
                "name": "VersusLaw",
                "url": "https://www.versuslaw.com/",
                "search": "https://www.versuslaw.com/search"
            },
            "fed_courts": {
                "name": "Federal Court Opinions",
                "url": "https://www.uscourts.gov/opinions",
                "circuit_courts": "https://www.uscourts.gov/about-federal-courts/court-role-and-structure",
                "scotus": "https://www.uscourts.gov/about-federal-courts/educational-resources/supreme-court"
            }
        }
        
        # CONSTITUTION RESOURCES
        self.constitution_resources = {
            "us_constitution_full": {
                "transcription": "https://www.archives.gov/founding-docs/constitution-transcript",
                "high_resolution": "https://www.archives.gov/founding-docs/constitution",
                "amendments": "https://www.archives.gov/founding-docs/amendments-11-27",
                "bill_of_rights": "https://www.archives.gov/founding-docs/bill-of-rights"
            },
            "constitution_annotated": {
                "name": "Constitution Annotated (Congress.gov)",
                "url": "https://constitution.congress.gov/",
                "search": "https://constitution.congress.gov/browse/",
                "amendments": "https://constitution.congress.gov/browse/amendment-1/"
            },
            "lii_constitution": {
                "name": "Cornell LII Constitution",
                "url": "https://www.law.cornell.edu/constitution",
                "annotated": "https://www.law.cornell.edu/constitution-conan",
                "preamble": "https://www.law.cornell.edu/constitution/preamble"
            },
            "justia_constitution": {
                "name": "Justia US Constitution",
                "url": "https://law.justia.com/constitution/us/",
                "amendments": "https://law.justia.com/constitution/us/amendments/",
                "article_1": "https://law.justia.com/constitution/us/article-1/"
            }
        }
        
        # STATUTES AND CODES
        self.statute_resources = {
            "us_code": {
                "name": "United States Code",
                "url": "https://uscode.house.gov/",
                "search": "https://uscode.house.gov/search/search.shtml",
                "download": "https://uscode.house.gov/download/download.shtml"
            },
            "cfr": {
                "name": "Code of Federal Regulations",
                "url": "https://www.ecfr.gov/",
                "search": "https://www.ecfr.gov/search",
                "browse": "https://www.ecfr.gov/current/title-1"
            },
            "federal_register": {
                "name": "Federal Register",
                "url": "https://www.federalregister.gov/",
                "search": "https://www.federalregister.gov/documents/search",
                "agencies": "https://www.federalregister.gov/agencies"
            },
            "state_statutes": {
                "name": "State Statutes by State",
                "url": "https://www.law.cornell.edu/states/listing",
                "california": "https://leginfo.legislature.ca.gov/",
                "new_york": "https://www.nysenate.gov/legislation/laws",
                "texas": "https://statutes.capitol.texas.gov/",
                "florida": "https://www.flsenate.gov/Laws/Statutes"
            }
        }
        
        # INTERNATIONAL LAW
        self.international_resources = {
            "un_law": {
                "name": "United Nations Treaty Collection",
                "url": "https://treaties.un.org/",
                "search": "https://treaties.un.org/Pages/UNTSOnline.aspx",
                "status": "https://treaties.un.org/Pages/ParticipationStatus.aspx"
            },
            "icj": {
                "name": "International Court of Justice",
                "url": "https://www.icj-cij.org/",
                "cases": "https://www.icj-cij.org/cases",
                "decisions": "https://www.icj-cij.org/decisions"
            },
            "eu_law": {
                "name": "European Union Law",
                "url": "https://eur-lex.europa.eu/",
                "treaties": "https://eur-lex.europa.eu/collection/eu-law/treaties.html",
                "case_law": "https://eur-lex.europa.eu/collection/eu-law/case-law.html"
            },
            "oas": {
                "name": "Organization of American States - Treaties",
                "url": "https://www.oas.org/en/sla/dil/treaties_agreements.asp",
                "inter_american": "https://www.oas.org/en/sla/dil/inter_american_treaties.asp"
            }
        }
        
        self.domains = {
            "constitutional": "Constitution, fundamental law, bill of rights, separation of powers, federalism, judicial review",
            "statutory": "written laws passed by legislatures",
            "regulatory": "agency rules and regulations",
            "common_law": "judge-made law from precedent",
            "contract": "agreements and obligations",
            "property": "rights in things and land",
            "tort": "civil wrongs and damages",
            "criminal": "crimes and punishments",
            "evidence": "proof and admissibility",
            "civil_procedure": "court process rules",
            "corporate": "business entity laws",
            "securities": "financial instrument laws",
            "banking": "financial institution laws",
            "tax": "revenue and collection laws",
            "labor": "employment laws",
            "family": "domestic relations",
            "immigration": "entry and citizenship laws",
            "environmental": "conservation and pollution laws",
            "international": "treaties and customary law",
            "cyber": "internet and data laws",
            "space": "outer space laws",
            "maritime": "sea and shipping laws"
        }
        
        self.jurisdictions = {
            "us_federal": "United States federal law",
            "us_state": "All 50 US states",
            "uk": "United Kingdom",
            "canada": "Canada",
            "eu": "European Union",
            "australia": "Australia",
            "japan": "Japan",
            "south_korea": "South Korea",
            "singapore": "Singapore",
            "switzerland": "Switzerland"
        }
        
        self.constitutions = {
            "us_constitution": "https://www.archives.gov/founding-docs/constitution",
            "us_bill_of_rights": "https://www.archives.gov/founding-docs/bill-of-rights",
            "magna_carta": "https://www.archives.gov/exhibits/featured-documents/magna-carta",
            "declaration_of_independence": "https://www.archives.gov/founding-docs/declaration",
            "federalist_papers": "https://www.archives.gov/founding-docs/federalist-papers"
        }
        
        self.constitutional_principles = {
            "separation_of_powers": "Legislative, Executive, Judicial branches",
            "checks_and_balances": "Each branch limits the others",
            "federalism": "Power divided between federal and state",
            "judicial_review": "Courts can strike down laws (Marbury v. Madison)",
            "due_process": "5th and 14th Amendments",
            "equal_protection": "14th Amendment",
            "free_speech": "1st Amendment",
            "establishment_clause": "1st Amendment - separation of church and state",
            "free_exercise": "1st Amendment - religious freedom",
            "right_to_bear_arms": "2nd Amendment",
            "search_and_seizure": "4th Amendment",
            "self_incrimination": "5th Amendment",
            "speedy_trial": "6th Amendment",
            "cruel_and_unusual": "8th Amendment",
            "reserved_powers": "10th Amendment"
        }
    
    def get_law_resources(self, category: str = None) -> Dict:
        """Get free law resources by category"""
        if category == "cases":
            return self.free_law_resources
        elif category == "constitution":
            return self.constitution_resources
        elif category == "statutes":
            return self.statute_resources
        elif category == "international":
            return self.international_resources
        else:
            return {
                "case_law": self.free_law_resources,
                "constitution": self.constitution_resources,
                "statutes": self.statute_resources,
                "international": self.international_resources
            }
    
    def search_case_law(self, query: str) -> List[Dict]:
        """Search for case law resources"""
        return [
            {"source": "CourtListener", "url": f"https://www.courtlistener.com/search/?q={query.replace(' ', '+')}"},
            {"source": "Google Scholar", "url": f"https://scholar.google.com/scholar?as_ylo=2024&q={query.replace(' ', '+')}&hl=en&as_sdt=0,5&as_vis=1"},
            {"source": "Justia", "url": f"https://law.justia.com/cases/?q={query.replace(' ', '+')}"},
            {"source": "Cornell LII", "url": f"https://www.law.cornell.edu/wex/{query.replace(' ', '_')}"}
        ]
    
    def get_constitution(self, constitution_name: str = "us_constitution") -> Dict:
        """Retrieve constitutional text and information"""
        return {
            "constitution": constitution_name,
            "url": self.constitutions.get(constitution_name, "Not found"),
            "resources": self.constitution_resources,
            "principles": self.constitutional_principles,
            "ratified": "1788 for US Constitution",
            "amendments": 27 if constitution_name == "us_constitution" else "Unknown"
        }
    
    def get_statute(self, citation: str, jurisdiction: str = "us_federal") -> Dict:
        """Retrieve a statute by citation"""
        return {
            "citation": citation,
            "jurisdiction": jurisdiction,
            "search_url": f"https://uscode.house.gov/search/search.shtml?q={citation.replace(' ', '+')}",
            "resources": self.statute_resources
        }
    
    def search_law(self, query: str, domain: str = None) -> List[Dict]:
        """Search for law across domains"""
        results = []
        if domain and domain in self.domains:
            results.append({
                "domain": domain,
                "description": self.domains[domain],
                "query": query,
                "case_search": f"https://www.courtlistener.com/search/?q={query.replace(' ', '+')}",
                "statute_search": f"https://uscode.house.gov/search/search.shtml?q={query.replace(' ', '+')}"
            })
        else:
            for d, desc in list(self.domains.items())[:10]:
                results.append({
                    "domain": d,
                    "description": desc,
                    "query": query
                })
        return results
    
    def get_constitutional_principle(self, principle: str) -> Dict:
        """Get information about a constitutional principle"""
        if principle in self.constitutional_principles:
            return {
                "principle": principle,
                "description": self.constitutional_principles[principle],
                "source": "US Constitution",
                "url": "https://www.law.cornell.edu/constitution"
            }
        return {"error": f"Principle '{principle}' not found"}
    
    def compare_jurisdictions(self, topic: str, jurisdictions: List[str]) -> Dict:
        """Compare law on a topic across jurisdictions"""
        return {
            "topic": topic,
            "jurisdictions": jurisdictions,
            "comparison": f"Analysis of {topic} law across {', '.join(jurisdictions)}",
            "search_url": f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}+{'+'.join(jurisdictions)}",
            "note": "Full comparison requires statute retrieval"
        }
    
    def get_regulation(self, agency: str, citation: str) -> Dict:
        """Retrieve a regulation by agency and citation"""
        return {
            "agency": agency,
            "citation": citation,
            "title": f"Regulation {citation}",
            "url": f"https://www.ecfr.gov/current/title-{citation.split()[0] if citation else '1'}",
            "search": f"https://www.ecfr.gov/search?q={citation}"
        }
    
    def cite(self, source: str, citation_format: str = "bluebook") -> str:
        """Generate a citation"""
        formats = {
            "bluebook": f"{source} (Bluebook format)",
            "apa": f"{source} (APA format)",
            "mla": f"{source} (MLA format)",
            "chicago": f"{source} (Chicago format)"
        }
        return formats.get(citation_format, formats["bluebook"])

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw - Studies law")
    parser.add_argument("--domains", action="store_true", help="List law domains")
    parser.add_argument("--jurisdictions", action="store_true", help="List jurisdictions")
    parser.add_argument("--resources", help="Show law resources (cases, constitution, statutes, international)")
    parser.add_argument("--search-cases", help="Search case law")
    parser.add_argument("--constitution", help="Get constitution by name")
    parser.add_argument("--principle", help="Get constitutional principle")
    parser.add_argument("--statute", help="Get statute by citation")
    parser.add_argument("--search", help="Search for law")
    parser.add_argument("--domain", help="Limit search to domain")
    parser.add_argument("--compare", nargs="+", help="Compare jurisdictions")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    if args.domains:
        print("\nLaw Domains:")
        for d, desc in agent.domains.items():
            print(f"  {d}: {desc}")
    elif args.jurisdictions:
        print("\nJurisdictions:")
        for j, desc in agent.jurisdictions.items():
            print(f"  {j}: {desc}")
    elif args.resources:
        result = agent.get_law_resources(args.resources)
        print(json.dumps(result, indent=2))
    elif args.search_cases:
        results = agent.search_case_law(args.search_cases)
        print(json.dumps(results, indent=2))
    elif args.constitution:
        result = agent.get_constitution(args.constitution)
        print(json.dumps(result, indent=2))
    elif args.principle:
        result = agent.get_constitutional_principle(args.principle)
        print(json.dumps(result, indent=2))
    elif args.statute:
        result = agent.get_statute(args.statute)
        print(json.dumps(result, indent=2))
    elif args.search:
        results = agent.search_law(args.search, args.domain)
        print(json.dumps(results, indent=2))
    elif args.compare:
        topic = args.compare[0]
        jurisdictions = args.compare[1:]
        result = agent.compare_jurisdictions(topic, jurisdictions)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

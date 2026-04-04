#!/usr/bin/env python3
"""
Automatically learn case law from queries
"""

import sys
import sqlite3
from pathlib import Path
from groq import Groq
import os

def learn_from_query(query):
    """Find and store relevant cases for a query"""
    
    db_path = Path.home() / ".claw_memory" / "case_law.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Ask AI to identify relevant cases
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "For the given legal question, identify the most relevant US Supreme Court case. Return ONLY: case_name|citation|year|one_sentence_holding"},
            {"role": "user", "content": query}
        ],
        max_tokens=200,
        temperature=0.3
    )
    
    result = response.choices[0].message.content.strip()
    parts = result.split('|')
    
    if len(parts) >= 4:
        case_data = {
            'name': parts[0].strip(),
            'citation': parts[1].strip(),
            'year': int(parts[2].strip()) if parts[2].strip().isdigit() else 0,
            'holding': parts[3].strip(),
            'keywords': query[:100]
        }
        
        # Check if already exists
        cursor.execute("SELECT id FROM cases WHERE name = ?", (case_data['name'],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO cases (name, citation, year, holding, keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (case_data['name'], case_data['citation'], case_data['year'], 
                  case_data['holding'], case_data['keywords']))
            conn.commit()
            print(f"✅ Learned: {case_data['name']}")
            return case_data
    
    conn.close()
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        learn_from_query(q)
    else:
        print("Usage: python learn_cases.py 'What case established X?'")

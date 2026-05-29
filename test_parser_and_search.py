"""
Comprehensive test suite for parser_engine.py and search_engine.py
Tests multi-sector support, Arabic/bilingual parsing, and sector-aware search ranking.
"""

import sys
from parser_engine import parse_resume_text, classify_sector_and_role, is_arabic, extract_name_from_email
from search_engine import extract_query_parameters, rank_candidates, extract_skills_from_query

# ============================================================================
# TEST 1: Arabic Detection
# ============================================================================
def test_arabic_detection():
    print("\n" + "="*70)
    print("TEST 1: Arabic Detection (is_arabic)")
    print("="*70)
    
    test_cases = [
        ("مهندس برمجيات بخبرة 5 سنوات", True, "Full Arabic text"),
        ("Ingénieur chez [nom arabe]", False, "Mostly French with some Arabic"),
        ("This is English text", False, "Full English"),
        ("Français مع بعض العربية", True, "Mixed with 10%+ Arabic"),
    ]
    
    for text, expected, description in test_cases:
        result = is_arabic(text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status} | {description}: {result} (expected {expected})")

# ============================================================================
# TEST 2: Name Extraction from Email
# ============================================================================
def test_email_name_extraction():
    print("\n" + "="*70)
    print("TEST 2: Name Extraction from Email")
    print("="*70)
    
    test_cases = [
        ("souad.boughari255@gmail.com", "Souad Boughari", "Typical French name"),
        ("ahmed_ben_salem@example.com", "Ahmed Ben Salem", "Arabic name"),
        ("john.doe123@work.com", "John Doe", "Name with numbers"),
        ("a@domain.com", "", "Single letter (invalid)"),
    ]
    
    for email, expected, description in test_cases:
        result = extract_name_from_email(email)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"     Email: {email}")
        print(f"     Result: '{result}' (expected '{expected}')")

# ============================================================================
# TEST 3: Sector Classification
# ============================================================================
def test_sector_classification():
    print("\n" + "="*70)
    print("TEST 3: Sector Classification")
    print("="*70)
    
    test_cases = [
        (
            "Développeur Python avec 3 ans d'expérience en programmation web.",
            ["Python", "React"],
            "it",
            "IT Developer"
        ),
        (
            "Commercial technico-commercial spécialisé en vente de solutions.",
            ["Vente & Négociation", "Relation Client"],
            "commercial",
            "Commercial Sales"
        ),
        (
            "Secrétaire administrative avec maîtrise d'Excel et Word.",
            ["Bureautique", "Secrétariat"],
            "administration",
            "Administrative Secretary"
        ),
        (
            "Responsable RH en charge du recrutement et gestion de la paie.",
            ["Recrutement", "Gestion de la Paie"],
            "rh",
            "HR Manager"
        ),
        (
            "Comptable avec expérience en audit financier et gestion de trésorerie.",
            ["Comptabilité", "Gestion Financière"],
            "finance",
            "Accountant Finance"
        ),
    ]
    
    for text, skills, expected_sector, description in test_cases:
        sector, role_fr, role_ar = classify_sector_and_role(text, skills)
        status = "✓ PASS" if sector == expected_sector else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"     Detected Sector: {sector} (expected {expected_sector})")
        print(f"     French Role: {role_fr}")
        print(f"     Arabic Role: {role_ar}")

# ============================================================================
# TEST 4: Resume Parsing - Commercial Profile
# ============================================================================
def test_parse_commercial_resume():
    print("\n" + "="*70)
    print("TEST 4: Resume Parsing - Commercial Profile")
    print("="*70)
    
    resume_text = """
    Nom: Ahmed Bennaceur
    Email: ahmed.bennaceur@example.com
    Téléphone: +213 555 123456
    
    PROFIL PROFESSIONNEL
    Commercial avec 4 ans d'expérience en vente B2B.
    Spécialiste en négociation commerciale et relation client.
    
    EXPERIENCE
    - Commercial Senior chez TechSales (2 ans)
    - Agent de Vente chez RetailCorp (2 ans)
    
    COMPETENCES
    - Vente et Négociation
    - Relation Client
    - Prospection commerciale
    - Marketing Digital
    - Bureautique (Excel, Word)
    
    FORMATION
    Licence en Sciences Commerciales - Université d'Alger (2020)
    """
    
    result = parse_resume_text(resume_text, filename="ahmed_commercial.pdf")
    
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Sector: {result['sector']} (expected: commercial)")
    print(f"Role FR: {result['role_fr']}")
    print(f"Role AR: {result['role_ar']}")
    print(f"Experience Years: {result['experience_years']}")
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"AI Score: {result['ai_score']}/100")
    print(f"\nAI Summary (Arabic):")
    print(f"{result['ai_summary']}\n")
    print(f"Strengths:")
    for s in result['strengths']:
        print(f"  • {s}")
    print(f"Weaknesses:")
    for w in result['weaknesses']:
        print(f"  • {w}")
    
    # Validate
    checks = [
        ("Sector", result['sector'] == 'commercial'),
        ("Has Commercial Skills", any(s in result['skills'] for s in ["Vente & Négociation", "Relation Client"])),
        ("Experience Detected", result['experience_years'] >= 2),
        ("AI Score Valid", 35 <= result['ai_score'] <= 98),
    ]
    
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}")

# ============================================================================
# TEST 5: Resume Parsing - Arabic Administrative Profile
# ============================================================================
def test_parse_arabic_admin_resume():
    print("\n" + "="*70)
    print("TEST 5: Resume Parsing - Arabic Administrative Profile")
    print("="*70)
    
    resume_text = """
    فاطمة سعدي
    البريد الإلكتروني: fatima.saadi@example.com
    الهاتف: +213 666 789012
    
    الملف الشخصي
    مساعد إداري بخبرة سنتين في الأعمال الإدارية والسكرتارية.
    متقن في استخدام أدوات المكتب والبرامج الإدارية.
    
    الخبرة المهنية
    - مساعد إداري في شركة AdminSoft (سنتان)
    - سكرتيرة في مكتب الاستشارات (سنة)
    
    المهارات
    - سكرتارية وإدارة
    - برامج المكتبية (إكسيل، وورد)
    - إدخال البيانات
    - أرشيف وتسيير الوثائق
    
    التعليم
    شهادة تقني سامي في السكرتارية - معهد الجزائر
    """
    
    result = parse_resume_text(resume_text, filename="fatima_admin.pdf")
    
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Sector: {result['sector']} (expected: administration)")
    print(f"Role FR: {result['role_fr']}")
    print(f"Role AR: {result['role_ar']}")
    print(f"Experience Years: {result['experience_years']}")
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"Wilaya: {result['wilaya']}")
    print(f"AI Score: {result['ai_score']}/100")
    print(f"\nAI Summary (Arabic):")
    print(f"{result['ai_summary']}\n")
    
    # Validate
    checks = [
        ("Sector", result['sector'] == 'administration'),
        ("Arabic Detected", is_arabic(resume_text)),
        ("Admin Skills", any(s in result['skills'] for s in ["Secrétariat", "Bureautique", "Saisie de données"])),
        ("Name Extracted", result['name'] != "Candidate"),
    ]
    
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}")

# ============================================================================
# TEST 6: Query Parameter Extraction
# ============================================================================
def test_query_parameter_extraction():
    print("\n" + "="*70)
    print("TEST 6: Query Parameter Extraction (Multi-Sector)")
    print("="*70)
    
    test_cases = [
        (
            "Développeur Flutter 3 ans Tlemcen",
            ["Flutter"],
            "it",
            "IT Query"
        ),
        (
            "secrétaire Excel Alger",
            ["Bureautique", "Secrétariat"],
            "administration",
            "Admin Query"
        ),
        (
            "Commercial vente négociation Oran",
            ["Vente & Négociation"],
            "commercial",
            "Commercial Query"
        ),
        (
            "comptable finance audit Constantine",
            ["Comptabilité", "Gestion Financière", "Audit & Contrôle"],
            "finance",
            "Finance Query"
        ),
        (
            "مطور بايثون 5 سنوات الجزائر",
            ["Python"],
            "it",
            "Arabic IT Query"
        ),
    ]
    
    for query, expected_skills_subset, expected_sector_hint, description in test_cases:
        params = extract_query_parameters(query)
        skills_match = any(s in params['skills'] for s in expected_skills_subset)
        
        print(f"\nQuery: {query}")
        print(f"Description: {description}")
        print(f"Extracted Skills: {params['skills']}")
        print(f"Wilaya: {params['wilaya']}")
        print(f"Experience: {params['experience']}")
        
        status = "✓ PASS" if skills_match else "✗ FAIL"
        print(f"{status} | Expected skills found: {expected_skills_subset}")

# ============================================================================
# TEST 7: Search Ranking with Sector Awareness
# ============================================================================
def test_search_ranking():
    print("\n" + "="*70)
    print("TEST 7: Search Ranking with Sector Awareness")
    print("="*70)
    
    # Mock candidates database
    candidates = [
        {
            "id": "1",
            "name": "Ahmed Commercial",
            "email": "ahmed@example.com",
            "skills": ["Vente & Négociation", "Relation Client"],
            "sector": "commercial",
            "wilaya": "Alger",
            "experience_years": 3,
            "ai_score": 75,
            "file_content_text": "Commercial avec expérience en vente directe"
        },
        {
            "id": "2",
            "name": "Fatima Admin",
            "email": "fatima@example.com",
            "skills": ["Bureautique", "Secrétariat"],
            "sector": "administration",
            "wilaya": "Alger",
            "experience_years": 2,
            "ai_score": 70,
            "file_content_text": "Secrétaire administrative compétente en Excel"
        },
        {
            "id": "3",
            "name": "Ahmed Dev",
            "email": "dev@example.com",
            "skills": ["Python", "React", "SQL"],
            "sector": "it",
            "wilaya": "Oran",
            "experience_years": 4,
            "ai_score": 85,
            "file_content_text": "Développeur Full Stack Python React"
        },
    ]
    
    # Test Case 1: Search for Secretary (Administration)
    print("\n--- Test Case 1: Search for Secretary ---")
    query1 = "secrétaire Excel Alger"
    ranked1, scores1 = rank_candidates(candidates, query1)
    
    print(f"Query: {query1}")
    print(f"Results (ranked by relevance):")
    for i, cand in enumerate(ranked1, 1):
        score = scores1.get(cand['id'], 0)
        print(f"{i}. {cand['name']} (Sector: {cand['sector']}) - Score: {score}")
        print(f"   Skills: {', '.join(cand['skills'])}")
    
    # Verify admin candidate ranked first
    if ranked1[0]['sector'] == 'administration':
        print("✓ PASS | Administration sector candidate ranked first")
    else:
        print("✗ FAIL | Wrong sector candidate ranked first")
    
    # Test Case 2: Search for Developer
    print("\n--- Test Case 2: Search for Developer ---")
    query2 = "Développeur Python 4 ans"
    ranked2, scores2 = rank_candidates(candidates, query2)
    
    print(f"Query: {query2}")
    print(f"Results (ranked by relevance):")
    for i, cand in enumerate(ranked2, 1):
        score = scores2.get(cand['id'], 0)
        print(f"{i}. {cand['name']} (Sector: {cand['sector']}) - Score: {score}")
        print(f"   Skills: {', '.join(cand['skills'])}")
    
    # Verify IT candidate ranked first
    if ranked2[0]['sector'] == 'it':
        print("✓ PASS | IT sector candidate ranked first")
    else:
        print("✗ FAIL | Wrong sector candidate ranked first")

# ============================================================================
# RUN ALL TESTS
# ============================================================================
def run_all_tests():
    print("\n" + "█"*70)
    print("█ AICV PARSER & SEARCH ENGINE - COMPREHENSIVE TEST SUITE")
    print("█"*70)
    
    try:
        test_arabic_detection()
        test_email_name_extraction()
        test_sector_classification()
        test_parse_commercial_resume()
        test_parse_arabic_admin_resume()
        test_query_parameter_extraction()
        test_search_ranking()
        
        print("\n" + "█"*70)
        print("█ ALL TESTS COMPLETED")
        print("█"*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

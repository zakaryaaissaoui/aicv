import re
from parser_engine import WILAYAS, TECH_SKILLS

# Arabic to French Wilaya Mapping for search queries
WILAYAS_AR_TO_FR = {
    "أدرار": "Adrar", "الشلف": "Chlef", "الأغواط": "Laghouat", "أم البواقي": "Oum El Bouaghi",
    "باتنة": "Batna", "بجاية": "Béjaïa", "بسكرة": "Biskra", "بشار": "Béchar", "البليدة": "Blida",
    "البويرة": "Bouira", "تمنراست": "Tamanrasset", "تبسة": "Tébessa", "تلمسان": "Tlemcen",
    "تيارت": "Tiaret", "تيزي وزو": "Tizi Ouzou", "الجزائر": "Alger", "الجزائر العاصمة": "Alger",
    "الجلفة": "Djelfa", "جيجل": "Jijel", "سطيف": "Sétif", "سعيدة": "Saïda", "سكيكدة": "Skikda",
    "سيدي بلعباس": "Sidi Bel Abbès", "عنابة": "Annaba", "قالمة": "Guelma", "قسنطينة": "Constantine",
    "المدية": "Médéa", "مستغانم": "Mostaganem", "المسيلة": "M'Sila", "معسكر": "Mascara",
    "ورقلة": "Ouargla", "وهران": "Oran", "البيض": "El Bayadh", "إليزي": "Illizi",
    "برج بوعريريج": "Bordj Bou Arréridj", "بومرداس": "Boumerdès", "الطارف": "El Tarf",
    "تندوف": "Tindouf", "تيسمسيلت": "Tissemsilt", "الوادي": "El Oued", "خنشلة": "Khenchela",
    "سوق أهراس": "Souk Ahras", "تيبازة": "Tipaza", "ميلة": "Mila", "عين الدفلى": "Aïn Defla",
    "النعامة": "Naâma", "عين تموشنت": "Aïn Témouchent", "غرداية": "Ghardaïa", "غليزان": "Relizane",
    "المغير": "El M'Ghair", "تقرت": "Touggourt", "أولاد جلال": "Ouled Djellal", "بني عباس": "Béni Abbès",
    "عين صالح": "In Salah", "عين قزام": "In Guezzam", "جانت": "Djanet"
}

def normalize_text(text):
    if not text:
        return ""
    # Lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return " ".join(text.split())

def extract_query_parameters(query_str):
    """
    Parses a query string like "Développeur Flutter 3 ans Tlemcen" or "مطور فلاتر 3 سنوات تلمسان"
    Returns: {
        "skills": [list of skills found],
        "wilaya": "found wilaya or None",
        "experience": float or None,
        "keywords": [list of general words]
    }
    """
    normalized_query = normalize_text(query_str)
    words = normalized_query.split()
    
    # 1. Extract wilaya
    target_wilaya = None
    # Check French wilayas first
    for w in WILAYAS:
        if re.search(r'\b' + re.escape(w.lower()) + r'\b', normalized_query):
            target_wilaya = w
            break
            
    # Check Arabic wilayas if not found
    if not target_wilaya:
        for ar_name, fr_name in WILAYAS_AR_TO_FR.items():
            if ar_name in query_str:
                target_wilaya = fr_name
                break
            
    # 2. Extract tech skills
    target_skills = []
    for s in TECH_SKILLS:
        pattern = r'\b' + re.escape(s.lower()) + r'\b'
        if s == "C++":
            pattern = r'c\+\+'
        elif s == "C#":
            pattern = r'c#'
        elif s == ".NET":
            pattern = r'\.net'
            
        if re.search(pattern, normalized_query):
            target_skills.append(s)

    # 3. Extract experience years (e.g. "3 ans", "3 years", "3ans", "exp 3", "3 سنوات")
    experience_years = None
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:years?|ans?|سنوات|سنة|عام|أعوام|سنوات خبرة|سنة خبرة)\b', query_str.lower())
    if exp_matches:
        try:
            experience_years = float(exp_matches[0])
        except ValueError:
            pass
    else:
        # Check if there is a number standing alone near "experience" or just a number
        # e.g., "Flutter 3 Tlemcen"
        number_matches = re.findall(r'\b(\d+)\b', query_str)
        if number_matches:
            # If a number is found, see if it could represent experience (e.g. < 25)
            for num in number_matches:
                val = float(num)
                if 1 <= val <= 20:
                    experience_years = val
                    break

    return {
        "skills": target_skills,
        "wilaya": target_wilaya,
        "experience": experience_years,
        "keywords": words
    }

def rank_candidates(candidates, query_str):
    """
    Ranks candidates based on query relevance using:
    - Skills match with BOOST (weight 20)
    - Location match with PENALTY (weight 25, penalty -15)
    - Normalized experience distance (weight 20)
    - Text search keyword match (weight 2)
    """
    if not query_str or not query_str.strip():
        # If query is empty, return candidates ranked by AI score
        return sorted(candidates, key=lambda c: c.get("ai_score", 0), reverse=True), {}

    params = extract_query_parameters(query_str)
    ranked_results = []
    
    query_skills = [s.lower() for s in params["skills"]]
    query_wilaya = params["wilaya"]
    query_exp = params["experience"]
    query_keywords = params["keywords"]

    for candidate in candidates:
        relevance_score = 0.0
        details = {
            "skills_match": 0.0,
            "location_match": 0.0,
            "experience_match": 0.0,
            "keyword_match": 0.0
        }
        
        # 1. Skills Matching with BOOST
        cand_skills = [s.strip().lower() for s in candidate.get("skills", "").split(",") if s.strip()]
        for q_skill in query_skills:
            if q_skill in cand_skills:
                # Direct skill match - HUGE BOOST
                relevance_score += 20.0
                details["skills_match"] += 20.0
            elif any(q_skill in s or s in q_skill for s in cand_skills):
                # Fuzzy/Partial skill match
                relevance_score += 10.0
                details["skills_match"] += 10.0
            elif q_skill in candidate.get("file_content_text", "").lower():
                # Skill found in text but not extracted as main skill
                relevance_score += 5.0
                details["skills_match"] += 5.0

        # 2. Location Matching with PENALTY
        cand_wilaya = candidate.get("wilaya", "").strip().lower()
        if query_wilaya:
            if cand_wilaya == query_wilaya.lower():
                # Matching location
                relevance_score += 25.0
                details["location_match"] += 25.0
            else:
                # PENALTY for mismatch location
                relevance_score -= 15.0
                details["location_match"] -= 15.0

        # 3. Experience Scoring (Normalized)
        cand_exp = float(candidate.get("experience_years", 0))
        if query_exp is not None:
            # Normalized score based on difference (linear distance)
            diff = abs(cand_exp - query_exp)
            # If difference is 0 -> 20 points
            # If difference is 5 or more -> 0 points
            exp_points = max(0.0, 20.0 * (1 - (diff / 5.0)))
            relevance_score += exp_points
            details["experience_match"] += exp_points
        else:
            # Default experience contribution
            exp_points = min(10.0, cand_exp * 1.0)
            relevance_score += exp_points
            details["experience_match"] += exp_points

        # 4. General Keyword Search (Name, Text)
        cand_text = normalize_text(candidate.get("file_content_text", "") + " " + candidate.get("name", "") + " " + candidate.get("notes", ""))
        keyword_hits = 0
        for kw in query_keywords:
            if kw in cand_text:
                keyword_hits += 1
                
        kw_score = keyword_hits * 2.0
        relevance_score += kw_score
        details["keyword_match"] += kw_score

        # Add AI Score base influence (normalized to 5 points max)
        ai_influence = (candidate.get("ai_score", 0) / 100.0) * 5.0
        relevance_score += ai_influence

        # Store candidate with calculated relevance
        ranked_results.append({
            "candidate": candidate,
            "relevance_score": round(relevance_score, 1),
            "match_details": details
        })

    # Sort candidates by relevance score descending
    ranked_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return [item["candidate"] for item in ranked_results], {item["candidate"]["id"]: item["relevance_score"] for item in ranked_results}

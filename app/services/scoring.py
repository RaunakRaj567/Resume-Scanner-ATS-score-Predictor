import numpy as np
from typing import Dict, List, Any
from app.services.ontology import ontology_loader
from app.utils.logging import get_logger

logger = get_logger(__name__)

try:
    from rapidfuzz import fuzz
    def fuzzy_ratio(s1: str, s2: str) -> float:
        return float(fuzz.ratio(s1, s2))
except ImportError:
    from difflib import SequenceMatcher
    def fuzzy_ratio(s1: str, s2: str) -> float:
        return float(SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100.0)

KEYWORD_SCORE_TABLE = {
    0: 0.0,
    1: 3.0,
    2: 5.0,
    3: 8.0,
    4: 10.0,
    5: 13.0,
    6: 15.0,
    7: 18.0,
    8: 20.0,
    9: 23.0,
    10: 25.0,
    11: 28.0,
    12: 30.0,
    13: 33.0,
    14: 35.0,
    15: 38.0,
    16: 40.0,
    17: 43.0,
    18: 45.0,
    19: 48.0,
    20: 50.0,
    21: 53.0,
    22: 57.0,
    23: 60.0,
    24: 63.0,
    25: 67.0,
    26: 70.0,
    27: 73.0,
    28: 77.0,
    29: 80.0,
    30: 83.0,
    31: 87.0,
    32: 90.0,
    33: 93.0,
    34: 97.0,
    35: 100.0
}

def get_keyword_pct(count_weight: float) -> float:
    """Return exact percentage mark for keyword match count strictly following user marking scheme."""
    if count_weight <= 0:
        return 0.0
    if count_weight >= 35.0:
        return 100.0
    low = int(np.floor(count_weight))
    high = int(np.ceil(count_weight))
    if low == high:
        return KEYWORD_SCORE_TABLE.get(low, 100.0)
    frac = count_weight - low
    low_pct = KEYWORD_SCORE_TABLE.get(low, 0.0)
    high_pct = KEYWORD_SCORE_TABLE.get(high, 100.0)
    return low_pct + frac * (high_pct - low_pct)

class ScoringEngine:
    def __init__(self):
        pass

    def evaluate_resume(
        self,
        extracted_text: str,
        sections: Dict[str, List[str]],
        tokens: List[str],
        sentences: List[str],
        entities: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate resume against all available domain ontologies and return scores, subscores, and matched keywords."""
        domain_keys = ontology_loader.list_available_domains()
        domain_results = {}

        for domain in domain_keys:
            ontology_entries = ontology_loader.get_domain_ontology(domain)
            domain_results[domain] = self.evaluate_domain(
                domain_key=domain,
                ontology_entries=ontology_entries,
                extracted_text=extracted_text,
                sections=sections,
                tokens=tokens,
                sentences=sentences,
                entities=entities
            )

        return domain_results

    def evaluate_domain(
        self,
        domain_key: str,
        ontology_entries: List[Dict[str, Any]],
        extracted_text: str,
        sections: Dict[str, List[str]],
        tokens: List[str],
        sentences: List[str],
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute score (0-100), subscore breakdowns, and matched keyword evidence for a target domain."""
        if not ontology_entries:
            return {"score": 50, "subscores": {"keyword": 25.0, "experience": 12.5, "education": 7.5, "format": 5.0}, "matched_keywords": []}

        # 1. Keyword Match Subscore (Max 50.0 points - 50% Weightage)
        matched_keywords, keyword_subscore = self._compute_keyword_match(ontology_entries, tokens, sections, extracted_text)

        # 2. Experience Signal Subscore (Max 25.0 points - 25% Weightage)
        experience_subscore = self._compute_experience_signal(sections, entities, extracted_text)

        # 3. Education & Certifications Subscore (Max 15.0 points - 15% Weightage)
        education_subscore = self._compute_education_signal(sections, entities)

        # 4. Format & Readability Subscore (Max 10.0 points - 10% Weightage)
        format_subscore = self._compute_format_signal(sections, entities, extracted_text)

        # Strictly cap all subscores at their respective category max limits
        keyword_subscore = max(0.0, min(50.0, keyword_subscore))
        experience_subscore = max(0.0, min(25.0, experience_subscore))
        education_subscore = max(0.0, min(15.0, education_subscore))
        format_subscore = max(0.0, min(10.0, format_subscore))

        total_score = round(keyword_subscore + experience_subscore + education_subscore + format_subscore)
        total_score = max(0, min(100, total_score))

        return {
            "score": total_score,
            "subscores": {
                "keyword": round(keyword_subscore, 1),
                "experience": round(experience_subscore, 1),
                "education": round(education_subscore, 1),
                "format": round(format_subscore, 1)
            },
            "matched_keywords": matched_keywords,
            "confidence": 0.92
        }

    def _compute_keyword_match(
        self,
        ontology_entries: List[Dict[str, Any]],
        tokens: List[str],
        sections: Dict[str, List[str]],
        full_text: str
    ):
        matched_keywords = []
        seen_matched_kws = set()
        matched_weight_sum = 0.0

        full_text_lower = full_text.lower()
        skills_text = " ".join(sections.get("skills", [])).lower()
        exp_text = " ".join(sections.get("experience", [])).lower()
        proj_text = " ".join(sections.get("projects", [])).lower()

        for entry in ontology_entries:
            kw = entry["keyword"]
            kw_key = kw.strip().lower()

            # Ensure each technical keyword concept is credited EXACTLY ONCE regardless of repetition
            if kw_key in seen_matched_kws:
                continue

            synonyms = entry.get("synonyms", [])
            kw_lower = kw.lower()

            match_type = None
            location = "skills" if kw_lower in skills_text else ("experience" if kw_lower in exp_text else ("projects" if kw_lower in proj_text else "summary"))

            # Check exact match
            if kw_lower in full_text_lower:
                match_type = "exact"
            else:
                # Check synonyms
                for syn in synonyms:
                    if syn.lower() in full_text_lower:
                        match_type = "exact"
                        break

            # Check fuzzy match if exact match not found
            if not match_type:
                for token in tokens:
                    if fuzzy_ratio(kw_lower, token.lower()) >= 88:
                        match_type = "fuzzy"
                        break

            if match_type:
                seen_matched_kws.add(kw_key)
                # Normalize match weight: 1.0 unit per exact keyword concept, 0.75 for fuzzy
                match_unit = 1.0 if match_type == "exact" else 0.75
                matched_weight_sum += match_unit
                contrib = round((match_unit / 35.0) * 50.0, 1)
                matched_keywords.append({
                    "kw": kw,
                    "type": match_type,
                    "location": location,
                    "contribution": contrib
                })

        # Strict User Keyword Marking Scheme lookup (Max 50.0 points)
        pct_marks = get_keyword_pct(matched_weight_sum)
        keyword_subscore = (pct_marks / 100.0) * 50.0

        return matched_keywords, min(50.0, keyword_subscore)

    def _compute_experience_signal(self, sections: Dict[str, List[str]], entities: Dict[str, Any], full_text: str) -> float:
        """Compute experience signal score (0 to 25 points - 25% Weightage)."""
        score = 0.0
        full_text_lower = full_text.lower()

        # 1. Base Employment History (10.0 points)
        durations = entities.get("durations_found", [])
        years_count = len(entities.get("years_mentioned", []))
        exp_lines = len(sections.get("experience", []))
        
        if durations or years_count >= 1 or exp_lines >= 1 or "experience" in full_text_lower:
            score += 10.0

        # 2. Title & Seniority Keyword Match (8.0 points)
        seniority_keywords = ["lead", "senior", "principal", "staff", "manager", "head", "architect", "engineer", "developer", "analyst", "specialist"]
        found_seniority = any(kw in full_text_lower for kw in seniority_keywords)
        if found_seniority:
            score += 8.0

        # 3. Section Depth (7.0 points)
        if exp_lines >= 3:
            score += 7.0
        elif exp_lines >= 1 or len(full_text.split('\n')) > 8:
            score += 5.0

        return min(25.0, score)

    def _compute_education_signal(self, sections: Dict[str, List[str]], entities: Dict[str, Any]) -> float:
        """Compute education & certs score (0 to 15 points - 15% Weightage)."""
        score = 0.0
        edu_lines = len(sections.get("education", []))
        degrees = entities.get("degrees", [])

        # 1. Degree / Edu Present (9.0 points)
        if degrees or edu_lines >= 1:
            score += 9.0
        
        # 2. Advanced Degree or Certifications (6.0 points)
        full_edu = " ".join(sections.get("education", [])).lower()
        if "master" in full_edu or "phd" in full_edu or "doctor" in full_edu or "certified" in full_edu or "b.tech" in full_edu or "b.s." in full_edu:
            score += 6.0
        elif score > 0:
            score += 3.0

        return min(15.0, score)

    def _compute_format_signal(self, sections: Dict[str, List[str]], entities: Dict[str, Any], full_text: str) -> float:
        """Compute layout, sections, contact info, and bullet format score (0 to 10 points - 10% Weightage)."""
        score = 0.0

        # Check presence of major sections (5.0 points)
        standard_sections = ["experience", "education", "skills"]
        present_count = sum(1 for sec in standard_sections if len(sections.get(sec, [])) > 0)
        score += (present_count / len(standard_sections)) * 5.0

        # Check contact info (3.0 points)
        if entities.get("email") or entities.get("phone"):
            score += 3.0

        # Check bullets or bullet indicators (2.0 points)
        if "-" in full_text or "•" in full_text or len(full_text.split('\n')) > 10:
            score += 2.0

        return min(10.0, score)

scoring_engine = ScoringEngine()

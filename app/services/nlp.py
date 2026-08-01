import re
from typing import Dict, Any, List
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Pre-compiled regexes for PII and entities
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_REGEX = re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
DEGREE_REGEX = re.compile(r'\b(bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech|doctorate|degree|b\.e\.|m\.e\.)\b', re.IGNORECASE)
YEAR_REGEX = re.compile(r'\b(19\d\d|20\d\d)\b')
DURATION_REGEX = re.compile(r'(\d+)\+?\s*(?:years?|yrs?|months?|mos?)', re.IGNORECASE)

# Technical tokens regex to preserve special characters during tokenization
TECH_TOKEN_REGEX = re.compile(r'\b(c\+\+|c#|\.net|node\.js|vue\.js|react\.js|d3\.js|express\.js|three\.js)\b', re.IGNORECASE)

class NLPService:
    def __init__(self):
        self.nlp = None
        self._load_spacy()

    def _load_spacy(self):
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                logger.info("en_core_web_sm spacy model not found locally. Will use regex and fallback NLP tokenizer.")
                self.nlp = None
        except ImportError:
            logger.warning("spaCy library not installed. Using fallback regex NLP pipeline.")
            self.nlp = None

    def process_text(self, text: str) -> Dict[str, Any]:
        """Tokenize, extract entities, and segment sentences from input text."""
        emails = EMAIL_REGEX.findall(text)
        phones = PHONE_REGEX.findall(text)
        degrees = list(set(DEGREE_REGEX.findall(text)))
        years = YEAR_REGEX.findall(text)
        durations = DURATION_REGEX.findall(text)

        # Name extraction heuristic (first line or prominent text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        candidate_name = lines[0] if lines else "Unknown Candidate"
        if len(candidate_name) > 40 or "@" in candidate_name or any(char.isdigit() for char in candidate_name):
            candidate_name = "Candidate Profile"

        sentences = self.split_sentences(text)
        tokens, lemmas = self.tokenize_and_lemmatize(text)

        entities = {
            "name": candidate_name,
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "degrees": degrees,
            "years_mentioned": years,
            "durations_found": durations
        }

        if self.nlp:
            try:
                doc = self.nlp(text[:10000]) # Cap for performance
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
                entities["companies"] = list(set(orgs))[:10]
                entities["dates"] = list(set(dates))[:10]
            except Exception as e:
                logger.warning(f"spaCy NER processing error: {e}")

        return {
            "tokens": tokens,
            "lemmas": lemmas,
            "sentences": sentences,
            "entities": entities
        }

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentence units."""
        if not text:
            return []
        if self.nlp:
            try:
                doc = self.nlp(text[:20000])
                return [s.text.strip() for s in doc.sents if len(s.text.strip()) > 10]
            except Exception:
                pass
        # Fallback splitting by line/punctuation
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def tokenize_and_lemmatize(self, text: str):
        """Extract tokens and lemmas while preserving tech terms like C++, .NET, Node.js."""
        if not text:
            return [], []

        # Find tech tokens first
        tech_matches = TECH_TOKEN_REGEX.findall(text)
        tech_tokens = [t.lower() for t in tech_matches]

        if self.nlp:
            try:
                doc = self.nlp(text[:20000])
                tokens = [t.text.lower() for t in doc if not t.is_punct and not t.is_space]
                lemmas = [t.lemma_.lower() for t in doc if not t.is_punct and not t.is_space]
                # Re-add tech tokens
                tokens.extend(tech_tokens)
                lemmas.extend(tech_tokens)
                return list(set(tokens)), list(set(lemmas))
            except Exception:
                pass

        # Regex fallback
        words = re.findall(r'\b[a-zA-Z0-9\+\#\.]+\b', text.lower())
        tokens = list(set(words + tech_tokens))
        return tokens, tokens

nlp_service = NLPService()

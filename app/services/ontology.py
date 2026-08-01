import json
from pathlib import Path
from typing import Dict, List, Any
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class OntologyLoader:
    def __init__(self, ontologies_dir: Path = None):
        self.ontologies_dir = ontologies_dir or settings.ONTOLOGIES_DIR
        self.ontologies: Dict[str, List[Dict[str, Any]]] = {}
        self.load_all_ontologies()

    def load_all_ontologies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all JSON files in the ontologies directory."""
        if not self.ontologies_dir.exists():
            logger.warning(f"Ontology directory {self.ontologies_dir} does not exist.")
            return {}

        self.ontologies = {}
        for file_path in self.ontologies_dir.glob("*.json"):
            domain_key = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    self.ontologies[domain_key] = entries
                    logger.info(f"Loaded ontology for domain '{domain_key}' with {len(entries)} keywords.")
            except Exception as e:
                logger.error(f"Failed to load ontology file {file_path}: {e}")
        return self.ontologies

    def get_domain_ontology(self, domain_key: str) -> List[Dict[str, Any]]:
        """Get keyword list for a given domain key, reloading from disk to catch live JSON edits."""
        self.load_all_ontologies()
        return self.ontologies.get(domain_key, [])

    def list_available_domains(self) -> List[str]:
        """List available domain keys, reloading from disk to catch live JSON edits."""
        self.load_all_ontologies()
        return list(self.ontologies.keys())

ontology_loader = OntologyLoader()

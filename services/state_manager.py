import json
from pathlib import Path
from typing import Dict, List

class StateManager:
    def __init__(self, file_path: str = "data/state.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load(self) -> Dict:
        if not self.file_path.exists():
            return {"interpretations": [], "settings": {}}
            
        try:
            return json.loads(self.file_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return {"interpretations": [], "settings": {}}
            
    def save(self, state: Dict) -> None:
        self.file_path.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
        
    def add_interpretation(self, interpretation: Dict) -> None:
        state = self.load()
        state["interpretations"].append(interpretation)
        self.save(state)
        
    def get_interpretations(self) -> List[Dict]:
        return self.load()["interpretations"]
        
    def clear(self) -> None:
        self.save({"interpretations": [], "settings": {}})
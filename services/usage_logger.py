import json
from datetime import datetime
import re
from pathlib import Path
from typing import Dict, List

class UsageLogger:
    PRICING = {
        "3-5-sonnet": {
            "input": 3.0,    # $3/MTok
            "output": 15.0   # $15/MTok
        },
        "3-5-haiku": {
            "input": 1.0,    # $1/MTok
            "output": 5.0    # $5/MTok
        },
        "3-opus": {
            "input": 15.0,   # $15/MTok
            "output": 75.0   # $75/MTok
        }
    }

    def __init__(self, log_file: str = "data/usage_log.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_model_type(self, model_name: str) -> str:
        pattern = r"claude-(\d-\d-\w+|\d-\w+)"
        match = re.search(pattern, model_name)
        if match:
            return match.group(1)
        raise ValueError(f"Unknown model format: {model_name}")
    
    def log_usage(self, model_name: str, usage: Dict) -> None:
        model_type = self._get_model_type(model_name)
        
        input_cost = (usage["input_tokens"] / 1_000_000) * self.PRICING[model_type]["input"]
        output_cost = (usage["output_tokens"] / 1_000_000) * self.PRICING[model_type]["output"]
        total_cost = input_cost + output_cost
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "model_type": model_type,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "cost_usd": total_cost
        }
        
        logs = []
        if self.log_file.exists():
            try:
                logs = json.loads(self.log_file.read_text())
            except json.JSONDecodeError:
                logs = []
        
        logs.append(log_entry)
        self.log_file.write_text(json.dumps(logs, indent=2))
    
    def get_usage_stats(self) -> Dict:
        if not self.log_file.exists():
            return {"total_cost": 0.0, "total_tokens": 0, "calls_count": 0}
            
        try:
            logs = json.loads(self.log_file.read_text())
            return {
                "total_cost": sum(log["cost_usd"] for log in logs),
                "total_tokens": sum(log["input_tokens"] + log["output_tokens"] for log in logs),
                "calls_count": len(logs),
                "per_model": self._get_per_model_stats(logs)
            }
        except (json.JSONDecodeError, KeyError):
            return {"total_cost": 0.0, "total_tokens": 0, "calls_count": 0}
    
    def _get_per_model_stats(self, logs: List[Dict]) -> Dict:
        stats = {}
        for log in logs:
            model = log["model_type"]
            if model not in stats:
                stats[model] = {
                    "calls": 0,
                    "total_tokens": 0,
                    "cost": 0.0
                }
            stats[model]["calls"] += 1
            stats[model]["total_tokens"] += log["input_tokens"] + log["output_tokens"]
            stats[model]["cost"] += log["cost_usd"]
        return stats
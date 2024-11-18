INTERPRETATION_TOOLS = [
    {
        "name": "print_interpretation",
        "description": "Prints a structured interpretation of the text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "main_themes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string"},
                            "explanation": {"type": "string"}
                        }
                    }
                },
                "literary_devices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "device": {"type": "string"},
                            "example": {"type": "string"},
                            "effect": {"type": "string"}
                        }
                    }
                },
                "deeper_meaning": {"type": "string"},
                "historical_context": {"type": "string", "description": "Optional historical/cultural context"},
                "key_insights": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["main_themes", "literary_devices", "deeper_meaning", "key_insights"]
        }
    }
] 
def create_interpretation_txt(interpretation):
    """Create a formatted text file from the interpretation"""
    
    output = []
    
    # Letter (centered)
    letter = interpretation["letter"]
    output.append(f"{letter:^80}")
    
    # Original text
    output.append(interpretation["original_text"])
    
    # Two line breaks
    output.extend(["", ""])
    
    # Difficult words in one line
    difficult_words = []
    for i, word in enumerate(interpretation["difficult_words"]):
        separator = "; " if i < len(interpretation["difficult_words"]) - 1 else ""
        difficult_words.append(f"**{word['word']}** - {word['explanation']}{separator}")
    output.append("".join(difficult_words))
    
    # Two line breaks
    output.extend(["", ""])
    
    # Detailed interpretation
    detailed = []
    for i, detail in enumerate(interpretation["detailed_interpretation"]):
        separator = "; " if i < len(interpretation["detailed_interpretation"]) - 1 else "."
        detailed.append(f"**{detail['quote']}** - {detail['explanation']}{separator}")
    output.append("".join(detailed))
    
    return "\n".join(output) 
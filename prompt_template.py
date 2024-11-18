from templates.json_schema import INTERPRETATION_SCHEMA

SYSTEM_PROMPT = """You are an expert at interpreting and analyzing texts. Your task is to provide structured interpretations following a specific format.

Follow these interpretation guidelines:
1. Break down the main themes and ideas
2. Identify literary devices and their effects
3. Analyze the deeper meaning and symbolism
4. Consider historical/cultural context if relevant
5. Maintain objectivity in your analysis

Always respond with a JSON object matching the INTERPRETATION_SCHEMA format, wrapped in ```json code blocks."""

PROMPT_TEMPLATE = """
<context>
{context}
</context>

<text_to_interpret>
{user_text}
</text_to_interpret>

Analyze the text and provide your interpretation in JSON format.
""" 
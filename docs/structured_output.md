
Extracting Structured JSON using Claude and Tool Use
In this cookbook, we'll explore various examples of using Claude and the tool use feature to extract structured JSON data from different types of input. We'll define custom tools that prompt Claude to generate well-structured JSON output for tasks such as summarization, entity extraction, sentiment analysis, and more.

If you want to get structured JSON data without using tools, take a look at our "How to enable JSON mode" cookbook.

Set up the environment
First, let's install the required libraries and set up the Anthropic API client.

%pip install anthropic requests beautifulsoup4
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup
import json

client = Anthropic()
MODEL_NAME = "claude-3-haiku-20240307"
Example 1: Article Summarization
In this example, we'll use Claude to generate a JSON summary of an article, including fields for the author, topics, summary, coherence score, persuasion score, and a counterpoint.

tools = [
    {
        "name": "print_summary",
        "description": "Prints a summary of the article.",
        "input_schema": {
            "type": "object",
            "properties": {
                "author": {"type": "string", "description": "Name of the article author"},
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": 'Array of topics, e.g. ["tech", "politics"]. Should be as specific as possible, and can overlap.'
                },
                "summary": {"type": "string", "description": "Summary of the article. One or two paragraphs max."},
                "coherence": {"type": "integer", "description": "Coherence of the article's key points, 0-100 (inclusive)"},
                "persuasion": {"type": "number", "description": "Article's persuasion score, 0.0-1.0 (inclusive)"}
            },
            "required": ['author', 'topics', 'summary', 'coherence', 'persuasion', 'counterpoint']
        }
    }
]

url = "https://www.anthropic.com/news/third-party-testing"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
article = " ".join([p.text for p in soup.find_all("p")])

query = f"""
<article>
{article}
</article>

Use the `print_summary` tool.
"""

response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": query}]
)
json_summary = None
for content in response.content:
    if content.type == "tool_use" and content.name == "print_summary":
        json_summary = content.input
        break

if json_summary:
    print("JSON Summary:")
    print(json.dumps(json_summary, indent=2))
else:
    print("No JSON summary found in the response.")
JSON Summary:
{
  "author": "Anthropic",
  "topics": [
    "AI policy",
    "AI safety",
    "third-party testing"
  ],
  "summary": "The article argues that the AI sector needs effective third-party testing for frontier AI systems to avoid societal harm, whether deliberate or accidental. It discusses what third-party testing looks like, why it's needed, and the research Anthropic has done to arrive at this policy position. The article states that such a testing regime is necessary because frontier AI systems like large-scale generative models don't fit neatly into use-case and sector-specific frameworks, and can pose risks of serious misuse or AI-caused accidents. Though Anthropic and other organizations have implemented self-governance systems, the article argues that industry-wide third-party testing is ultimately needed to be broadly trusted. The article outlines key components of an effective third-party testing regime, including identifying national security risks, and discusses how it could be accomplished by a diverse ecosystem of organizations. Anthropic plans to advocate for greater funding and public sector infrastructure for AI testing and evaluation, as well as developing tests for specific capabilities.",
  "coherence": 90,
  "persuasion": 0.8
}
Example 2: Named Entity Recognition
In this example, we'll use Claude to perform named entity recognition on a given text and return the entities in a structured JSON format.

tools = [
    {
        "name": "print_entities",
        "description": "Prints extract named entities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The extracted entity name."},
                            "type": {"type": "string", "description": "The entity type (e.g., PERSON, ORGANIZATION, LOCATION)."},
                            "context": {"type": "string", "description": "The context in which the entity appears in the text."}
                        },
                        "required": ["name", "type", "context"]
                    }
                }
            },
            "required": ["entities"]
        }
    }
]

text = "John works at Google in New York. He met with Sarah, the CEO of Acme Inc., last week in San Francisco."

query = f"""
<document>
{text}
</document>

Use the print_entities tool.
"""

response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": query}]
)

json_entities = None
for content in response.content:
    if content.type == "tool_use" and content.name == "print_entities":
        json_entities = content.input
        break

if json_entities:
    print("Extracted Entities (JSON):")
    print(json_entities)
else:
    print("No entities found in the response.")
Extracted Entities (JSON):
{'entities': [{'name': 'John', 'type': 'PERSON', 'context': 'John works at Google in New York.'}, {'name': 'Google', 'type': 'ORGANIZATION', 'context': 'John works at Google in New York.'}, {'name': 'New York', 'type': 'LOCATION', 'context': 'John works at Google in New York.'}, {'name': 'Sarah', 'type': 'PERSON', 'context': 'He met with Sarah, the CEO of Acme Inc., last week in San Francisco.'}, {'name': 'Acme Inc.', 'type': 'ORGANIZATION', 'context': 'He met with Sarah, the CEO of Acme Inc., last week in San Francisco.'}, {'name': 'San Francisco', 'type': 'LOCATION', 'context': 'He met with Sarah, the CEO of Acme Inc., last week in San Francisco.'}]}
Example 3: Sentiment Analysis
In this example, we'll use Claude to perform sentiment analysis on a given text and return the sentiment scores in a structured JSON format.

tools = [
    {
        "name": "print_sentiment_scores",
        "description": "Prints the sentiment scores of a given text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "positive_score": {"type": "number", "description": "The positive sentiment score, ranging from 0.0 to 1.0."},
                "negative_score": {"type": "number", "description": "The negative sentiment score, ranging from 0.0 to 1.0."},
                "neutral_score": {"type": "number", "description": "The neutral sentiment score, ranging from 0.0 to 1.0."}
            },
            "required": ["positive_score", "negative_score", "neutral_score"]
        }
    }
]

text = "The product was okay, but the customer service was terrible. I probably won't buy from them again."

query = f"""
<text>
{text}
</text>

Use the print_sentiment_scores tool.
"""

response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": query}]
)

json_sentiment = None
for content in response.content:
    if content.type == "tool_use" and content.name == "print_sentiment_scores":
        json_sentiment = content.input
        break

if json_sentiment:
    print("Sentiment Analysis (JSON):")
    print(json.dumps(json_sentiment, indent=2))
else:
    print("No sentiment analysis found in the response.")
Sentiment Analysis (JSON):
{
  "negative_score": 0.6,
  "neutral_score": 0.3,
  "positive_score": 0.1
}
Example 4: Text Classification
In this example, we'll use Claude to classify a given text into predefined categories and return the classification results in a structured JSON format.

tools = [
    {
        "name": "print_classification",
        "description": "Prints the classification results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The category name."},
                            "score": {"type": "number", "description": "The classification score for the category, ranging from 0.0 to 1.0."}
                        },
                        "required": ["name", "score"]
                    }
                }
            },
            "required": ["categories"]
        }
    }
]

text = "The new quantum computing breakthrough could revolutionize the tech industry."

query = f"""
<document>
{text}
</document>

Use the print_classification tool. The categories can be Politics, Sports, Technology, Entertainment, Business.
"""

response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": query}]
)

json_classification = None
for content in response.content:
    if content.type == "tool_use" and content.name == "print_classification":
        json_classification = content.input
        break

if json_classification:
    print("Text Classification (JSON):")
    print(json.dumps(json_classification, indent=2))
else:
    print("No text classification found in the response.")
Text Classification (JSON):
{
  "categories": [
    {
      "name": "Politics",
      "score": 0.1
    },
    {
      "name": "Sports",
      "score": 0.1
    },
    {
      "name": "Technology",
      "score": 0.7
    },
    {
      "name": "Entertainment",
      "score": 0.1
    },
    {
      "name": "Business",
      "score": 0.5
    }
  ]
}
Example 5: Working with unknown keys
In some cases you may not know the exact JSON object shape up front. In this example we provide an open ended input_schema and instruct Claude via prompting how to interact with the tool.

tools = [
    {
        "name": "print_all_characteristics",
        "description": "Prints all characteristics which are provided.",
        "input_schema": {
            "type": "object",
            "additionalProperties": True
        }
    }
]

query = f"""Given a description of a character, your task is to extract all the characteristics of the character and print them using the print_all_characteristics tool.

The print_all_characteristics tool takes an arbitrary number of inputs where the key is the characteristic name and the value is the characteristic value (age: 28 or eye_color: green).

<description>
The man is tall, with a beard and a scar on his left cheek. He has a deep voice and wears a black leather jacket.
</description>

Now use the print_all_characteristics tool."""

response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    tools=tools,
    tool_choice={"type": "tool", "name": "print_all_characteristics"},
    messages=[{"role": "user", "content": query}]
)

tool_output = None
for content in response.content:
    if content.type == "tool_use" and content.name == "print_all_characteristics":
        tool_output = content.input
        break

if tool_output:
    print("Characteristics (JSON):")
    print(json.dumps(json_classification, indent=2))
else:
    print("Something went wrong.")
Characteristics (JSON):
{
  "height": "tall",
  "facial_hair": "beard",
  "facial_features": "scar on left cheek",
  "voice": "deep voice",
  "clothing": "black leather jacket"
}
These examples demonstrate how you can use Claude and the tool use feature to extract structured JSON data for various natural language processing tasks. By defining custom tools with specific input schemas, you can guide Claude to generate well-structured JSON output that can be easily parsed and utilized in your applications.
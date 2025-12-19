import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List

# Load environement variables
load_dotenv()

# Instantiate Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Choose Gemini model
MODEL_NAME = "gemini-2.5-flash"

# Fix the prompt
PROMPT = """
**INSTRUCTIONS STRICTES :**

Tu es un générateur de quiz pédagogique expert. Ta mission est de créer un ensemble de questions à choix multiples (QCM) basées **uniquement** sur le cours fourni ci-dessous.

**Règle absolue :**
- N’utilise **aucune connaissance externe**.
- Chaque question et sa réponse correcte doivent être **directement justifiables** par le cours donné.

**TÂCHES :**
1. Génère **{nb_questions} questions QCM** pour enrichir une base de données.
2. Le jeu de questions doit **couvrir tout le cours** de manière équilibrée : définitions, concepts, noms, dates, classifications.
3. Chaque question doit :
   - être courte et claire ;
   - avoir **4 choix plausibles** ;
   - contenir **une seule réponse correcte** ;
   - éviter les formulations ambiguës ou évidentes.
4. Les réponses doivent être précises.

TEXTE À ANALYSER :
<<<
{texte}
<<<
"""
class MCQ(BaseModel):
    question: str
    answers: List[str]
    correct_answer: str

class MCQList(BaseModel):
    questions: List[MCQ]

def _build_prompt(text: str, nb_questions: int) -> str:
    """build the prompt

    Args:
        text (str): markdown text
        nb_questions (int): number of questions to be generated

    Returns:
        str: prompt
    """
    return PROMPT.format(nb_questions=nb_questions, text=text)

def generate_mcq(text: str, nb_questions=10) -> List:
    """_summary_

    Args:
        text (str): Text to use as a base to the generate Multiple Choice Questions
        nb_questions (int, optional): Number of questions to generate. Defaults to 10.

    Returns:
        List: List of Multiple Choice Questions
    """
    prompt = _build_prompt(text=text, nb_questions=nb_questions)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt;
        generation_config = types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=MCQList
        )
    )

    try:
        quiz = MCQList.model_validate_json(response.text)
        return [item.model_dump() for item in quiz.questions]
    
    except Exception as e:
        print("JSON parsing error:", e)
        print(response.text[:200])
        return []





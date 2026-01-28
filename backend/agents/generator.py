"""
Generator Agent
Responsibility: Generate draft educational content for a given grade and topic.
"""

import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from config import OPENAI_API_KEY, MODEL_NAME


# ============== Structured Input/Output Models ==============

class GeneratorInput(BaseModel):
    grade: int
    topic: str
    feedback: Optional[List[str]] = None


class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: str


class GeneratorOutput(BaseModel):
    explanation: str
    mcqs: List[MCQ]


# ============== Generator Agent ==============

class GeneratorAgent:
    """
    Agent that generates educational content tailored to a specific grade level.
    """

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY is missing. Check your .env file.")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME

    def _build_prompt(self, input_data: GeneratorInput) -> str:
        base_prompt = f"""You are an expert educational content creator. 
Generate educational content for Grade {input_data.grade} students on the topic: "{input_data.topic}"

REQUIREMENTS:
1. Language MUST be appropriate for Grade {input_data.grade} students (age ~{input_data.grade + 5} years)
2. Use simple vocabulary and short sentences
3. Concepts must be factually correct
4. Create an engaging explanation (3-4 paragraphs)
5. Create exactly 3 multiple choice questions (MCQs)

OUTPUT FORMAT (strict JSON):
{{
    "explanation": "Your explanation here...",
    "mcqs": [
        {{
            "question": "Question text",
            "options": ["A) Option1", "B) Option2", "C) Option3", "D) Option4"],
            "answer": "A"
        }}
    ]
}}
"""

        if input_data.feedback:
            feedback_text = "\n".join(f"- {fb}" for fb in input_data.feedback)
            base_prompt += f"""

IMPORTANT - PREVIOUS FEEDBACK TO ADDRESS:
{feedback_text}

Please regenerate the content addressing ALL the feedback above.
"""

        return base_prompt

    def run(self, input_data: GeneratorInput) -> GeneratorOutput:
        prompt = self._build_prompt(input_data)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational content generator. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

        except Exception as e:
            print("\n🔥 OPENAI ERROR >>>", repr(e), "\n")
            raise

        # Parse response safely
        try:
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return GeneratorOutput(**parsed)

        except Exception as e:
            print("\n🔥 PARSING ERROR >>>", repr(e))
            print("RAW RESPONSE:", content, "\n")
            raise

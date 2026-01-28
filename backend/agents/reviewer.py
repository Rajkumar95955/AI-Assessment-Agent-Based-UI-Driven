"""
Reviewer Agent
Responsibility: Review educational content for age appropriateness, correctness, and clarity.
"""

import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Literal
from config import OPENAI_API_KEY, MODEL_NAME
from .generator import GeneratorOutput


# ============== Structured Input/Output Models ==============

class ReviewerInput(BaseModel):
    grade: int
    topic: str
    content: GeneratorOutput


class ReviewerOutput(BaseModel):
    status: Literal["pass", "fail"]
    feedback: List[str]
    scores: dict  # Optional: detailed scores


# ============== Reviewer Agent ==============

class ReviewerAgent:
    """
    Agent that reviews educational content for quality and appropriateness.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
    
    def _build_prompt(self, input_data: ReviewerInput) -> str:
        """Build the prompt for content review."""
        
        content_json = input_data.content.model_dump_json(indent=2)
        
        return f"""You are an expert educational content reviewer and child development specialist.

Review the following educational content created for Grade {input_data.grade} students (age ~{input_data.grade + 5} years) on the topic: "{input_data.topic}"

CONTENT TO REVIEW:
{content_json}

EVALUATION CRITERIA:
1. AGE APPROPRIATENESS (1-10):
   - Vocabulary suitable for grade level
   - Sentence complexity appropriate
   - Concepts not too advanced

2. CONCEPTUAL CORRECTNESS (1-10):
   - All facts are accurate
   - No misconceptions introduced
   - MCQ answers are correct

3. CLARITY (1-10):
   - Easy to understand
   - Well-organized
   - Examples are relatable

RULES:
- Status is "pass" if ALL scores are >= 7
- Status is "fail" if ANY score is < 7
- Provide specific, actionable feedback for improvements
- Be strict but fair

OUTPUT FORMAT (strict JSON):
{{
    "status": "pass" or "fail",
    "feedback": [
        "Specific feedback item 1",
        "Specific feedback item 2"
    ],
    "scores": {{
        "age_appropriateness": 8,
        "conceptual_correctness": 9,
        "clarity": 7
    }}
}}
"""
    
    def run(self, input_data: ReviewerInput) -> ReviewerOutput:
        """
        Execute the reviewer agent.
        
        Args:
            input_data: Structured input with grade, topic, and content to review
            
        Returns:
            ReviewerOutput: Structured output with status and feedback
        """
        prompt = self._build_prompt(input_data)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational content reviewer. Be thorough and critical. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for consistent evaluation
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        return ReviewerOutput(**parsed)
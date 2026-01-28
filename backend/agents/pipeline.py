"""
Agent Pipeline
Orchestrates the Generator → Reviewer → (Optional Refinement) flow.
"""

from pydantic import BaseModel
from typing import Optional
from .generator import GeneratorAgent, GeneratorInput, GeneratorOutput
from .reviewer import ReviewerAgent, ReviewerInput, ReviewerOutput


class PipelineInput(BaseModel):
    grade: int
    topic: str



class PipelineOutput(BaseModel):
    # Initial generation
    initial_output: GeneratorOutput
    initial_review: ReviewerOutput
    
    # Refinement (if applicable)
    was_refined: bool
    refined_output: Optional[GeneratorOutput] = None
    refined_review: Optional[ReviewerOutput] = None
    
    # Final result
    final_output: GeneratorOutput
    final_status: str


class AgentPipeline:
    """
    Orchestrates the full agent pipeline:
    1. Generate content
    2. Review content
    3. If review fails, refine once with feedback
    """
    
    def __init__(self):
        self.generator = GeneratorAgent()
        self.reviewer = ReviewerAgent()
        self.max_refinements = 1
    
    def run(self, input_data: PipelineInput) -> PipelineOutput:
        """
        Execute the full pipeline.
        
        Args:
            input_data: Grade and topic for content generation
            
        Returns:
            PipelineOutput: Complete pipeline results including any refinements
        """
        
        # ===== Step 1: Initial Generation =====
        print(f"[Pipeline] Generating content for Grade {input_data.grade}: {input_data.topic}")
        
        generator_input = GeneratorInput(
            grade=input_data.grade,
            topic=input_data.topic
        )
        initial_output = self.generator.run(generator_input)
        
        # ===== Step 2: Review =====
        print("[Pipeline] Reviewing generated content...")
        
        reviewer_input = ReviewerInput(
            grade=input_data.grade,
            topic=input_data.topic,
            content=initial_output
        )
        initial_review = self.reviewer.run(reviewer_input)
        
        # ===== Step 3: Refinement (if needed) =====
        refined_output = None
        refined_review = None
        was_refined = False
        
        if initial_review.status == "fail":
            print(f"[Pipeline] Review failed. Refining with feedback...")
            was_refined = True
            
            # Re-run generator with feedback
            generator_input_refined = GeneratorInput(
                grade=input_data.grade,
                topic=input_data.topic,
                feedback=initial_review.feedback
            )
            refined_output = self.generator.run(generator_input_refined)
            
            # Review refined content
            reviewer_input_refined = ReviewerInput(
                grade=input_data.grade,
                topic=input_data.topic,
                content=refined_output
            )
            refined_review = self.reviewer.run(reviewer_input_refined)
            
            final_output = refined_output
            final_status = refined_review.status
        else:
            print("[Pipeline] Review passed on first attempt!")
            final_output = initial_output
            final_status = initial_review.status
        
        return PipelineOutput(
            initial_output=initial_output,
            initial_review=initial_review,
            was_refined=was_refined,
            refined_output=refined_output,
            refined_review=refined_review,
            final_output=final_output,
            final_status=final_status
        )
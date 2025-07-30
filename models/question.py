from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Question(ABC):
    id: str
    text: str
    required_fields: List[str]
    
    def __post_init__(self):
        """Validate that required fields are provided."""
        if not self.required_fields:
            raise ValueError("At least one required field must be specified")
    
    @abstractmethod
    def is_valid_for(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        """Check if this question is valid for the given person."""
        return all(field in person for field in self.required_fields)
    
    @abstractmethod
    def get_question_text(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> str:
        """Render the question text with the given context."""
        pass
    
    @abstractmethod
    def get_correct_answer(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> Any:
        """Get the correct answer for this question."""
        pass
    
    @abstractmethod
    def get_choices(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> List[Any]:
        """Get possible answer choices for this question."""
        pass

class MultipleChoiceQuestion(Question):
    def __init__(self, id: str, text: str, required_fields: List[str], 
                 answer_expression: str, choices_expression: str):
        super().__init__(id, text, required_fields)
        self.answer_expression = answer_expression
        self.choices_expression = choices_expression
    
    def is_valid_for(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        if not super().is_valid_for(person, person_data):
            return False
        # Additional validation specific to multiple choice
        try:
            choices = self._evaluate_expression(self.choices_expression, person, person_data)
            return bool(choices)
        except:
            return False
    
    def get_question_text(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> str:
        return self.text.format(person=person, 
                              person_data=person_data,
                              get_parent=lambda p: person_data.get(person.get(p, ''), {}))
    
    def get_correct_answer(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> Any:
        return self._evaluate_expression(self.answer_expression, person, person_data)
    
    def get_choices(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> List[Any]:
        return self._evaluate_expression(self.choices_expression, person, person_data)
    
    def _evaluate_expression(self, expr: str, person: Dict, person_data: Dict) -> Any:
        # Safe evaluation context
        context = {
            'person': person,
            'person_data': person_data,
            'get_parent': lambda p: person_data.get(person.get(p, ''), {})
        }
        # Add utility functions
        from utils import (
            calculate_age, get_year, get_multiple_choices,
            get_age_choices, get_name_choices_by_gender,
            get_place_choices, compare_ages
        )
        context.update(locals())
        return eval(expr, {'__builtins__': {}}, context)

class QuestionFactory:
    @staticmethod
    def from_yaml(data: Dict[str, Any]) -> Question:
        question_type = data.get('type', 'multiple_choice')
        
        if question_type == 'multiple_choice':
            return MultipleChoiceQuestion(
                id=data['id'],
                text=data['question'],
                required_fields=data.get('required_fields', []),
                answer_expression=data['answer_function'],
                choices_expression=data['choices_function']
            )
        # Add more question types here as needed
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
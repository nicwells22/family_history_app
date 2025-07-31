from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from jinja2 import Environment, BaseLoader

@dataclass
class Question(ABC):
    id: str
    text: str
    required_fields: List[str] = field(default_factory=list)
    required_relationships: List[str] = field(default_factory=list)
    
    def is_valid_for(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        """
        Check if this question is valid for the given person.
        
        A question is valid if:
        1. All required fields exist in the person's data
        2. All required relationships exist and are valid
        3. The question-specific validation passes
        """
        # Check required fields
        if not self._has_required_fields(person):
            return False
            
        # Check required relationships
        if not self._has_required_relationships(person, person_data):
            return False
            
        # Let subclasses add their own validation
        return self._is_valid(person, person_data)
    
    def _has_required_fields(self, person: Dict[str, Any]) -> bool:
        """Check if person has all required fields with non-empty values."""
        for field in self.required_fields:
            if not person.get(field):
                return False
        return True
    
    def _has_required_relationships(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        """
        Check if all required relationships exist and are valid.
        Relationships are specified as 'parent.field' or 'relationship_name'.
        """
        for rel in self.required_relationships:
            # Handle parent.field syntax
            if '.' in rel:
                rel_type, field = rel.split('.', 1)
                parent_name = person.get(rel_type)
                if not parent_name or parent_name not in person_data:
                    return False
                if not person_data[parent_name].get(field):
                    return False
            # Handle direct relationship check
            elif rel not in person or not person[rel]:
                return False
        return True
    
    @abstractmethod
    def _is_valid(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        """Subclasses should implement their specific validation logic."""
        pass
    
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
    def __init__(self, id: str, text: str, 
                 required_fields: List[str] = None,
                 required_relationships: List[str] = None,
                 answer_expression: str = "",
                 choices_expression: str = ""):
        super().__init__(
            id=id,
            text=text,
            required_fields=required_fields or [],
            required_relationships=required_relationships or []
        )
        self.answer_expression = answer_expression
        self.choices_expression = choices_expression
    
    def _is_valid(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> bool:
        """Additional validation specific to multiple choice questions."""
        try:
            # Check if we can generate valid choices
            choices = self._evaluate_expression(self.choices_expression, person, person_data)
            return bool(choices)  # Must have at least one choice
        except Exception as e:
            print(f"Error validating question {self.id}: {e}")
            return False
    
    def get_question_text(self, person: Dict[str, Any], person_data: Dict[str, Dict]) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.text)
        return template.render(
            person=person,
            person_data=person_data,
            get_parent=lambda p: person_data.get(person.get(p, ''), {})
        )
    
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
            get_place_choices, compare_ages, get_year_choices
        )
        context.update(locals())
        return eval(expr, {'__builtins__': {}}, context)

class QuestionFactory:
    @staticmethod
    def from_yaml(data: Dict[str, Any]) -> Question:
        """
        Create a Question object from YAML data.
        
        Args:
            data: Dictionary containing question data from YAML
            
        Returns:
            Question: An instance of the appropriate question type
            
        Raises:
            ValueError: If the question type is not supported
        """
        question_type = data.get('type', 'multiple_choice')
        
        # Extract required fields and relationships
        required_fields = data.get('required_fields', [])
        required_relationships = []
        
        # Separate regular fields from relationship fields
        regular_fields = []
        for field in required_fields:
            if '.' in field and any(rel in field for rel in ['father', 'mother']):
                required_relationships.append(field)
            else:
                regular_fields.append(field)
        
        if question_type == 'multiple_choice':
            return MultipleChoiceQuestion(
                id=data['id'],
                text=data['question'],
                required_fields=regular_fields,
                required_relationships=required_relationships,
                answer_expression=data['answer_function'],
                choices_expression=data['choices_function']
            )
        # Add more question types here as needed
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
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
    
    def is_valid_for(self, person: 'Person', person_data: Dict[str, 'Person']) -> bool:
        """
        Check if this question is valid for the given person.
        
        A question is valid if:
        1. All required fields exist in the person's data
        2. All required relationships exist and are valid
        3. The question-specific validation passes
        """
        if not self._has_required_fields(person):
            # print(f"Question {self.id} is invalid for {person.name}: missing required fields")
            return False
            
        if not self._has_required_relationships(person, person_data):
            # print(f"Question {self.id} is invalid for {person.name}: missing required relationships")
            return False
            
        # Let subclasses add their own validation
        return self._is_valid(person, person_data)
    
    def _has_required_fields(self, person: 'Person') -> bool:
        """
        Check if person has all required fields with non-empty values.
        
        Args:
            person: The Person object to check
            
        Returns:
            bool: True if all required fields have non-empty values, False otherwise
        """
        for field in self.required_fields:
            # First try to get the attribute directly
            value = getattr(person, field, None)
            
            # If not found and the field is in additional_data, use that
            if not value and hasattr(person, 'additional_data') and field in person.additional_data:
                value = person.additional_data[field]
                
            # If still no value, check for common variations (e.g., birth_place vs birthplace)
            if not value and hasattr(person, 'additional_data'):
                # Try common variations of the field name
                variations = [
                    field.lower().replace('_', ''),  # birth_place -> birthplace
                    field.lower().replace('_', ' '),  # birth_place -> birth place
                    field.lower().replace('_', '') + 's',  # child -> children
                    field.lower() + 's' if not field.endswith('s') else field[:-1],  # child -> children, children -> child
                ]
                
                for variation in variations:
                    if variation in person.additional_data:
                        value = person.additional_data[variation]
                        break
            
            # If value is still empty, the field is missing
            if not value:
                return False
                
        return True
    
    def _has_required_relationships(self, person: 'Person', person_data: Dict[str, 'Person']) -> bool:
        """
        Check if all required relationships exist and are valid.
        Relationships are specified as 'parent.field' or 'relationship_name'.
        """
        for rel in self.required_relationships:
            # Handle parent.field syntax (e.g., 'father.birth_date')
            if '.' in rel:
                rel_type, field = rel.split('.', 1)
                # Get the parent ID (e.g., person.father_id)
                parent_id = getattr(person, f"{rel_type}_id", None)
                if not parent_id or parent_id not in person_data:
                    return False
                # Check if the parent has the required field
                parent = person_data[parent_id]
                field_value = getattr(parent, field, None)
                if not field_value and hasattr(parent, 'additional_data') and field in parent.additional_data:
                    field_value = parent.additional_data[field]
                if not field_value:
                    return False
            # Handle direct relationship check (e.g., 'father_id')
            else:
                # Check if the relationship ID exists
                rel_id = getattr(person, rel, None)
                if not rel_id or rel_id not in person_data:
                    return False
        return True
    
    @abstractmethod
    def _is_valid(self, person: 'Person', person_data: Dict[str, 'Person']) -> bool:
        """Subclasses should implement their specific validation logic."""
        pass
        
    @abstractmethod
    def get_question_text(self, person: 'Person', person_data: Dict[str, 'Person']) -> str:
        """Render the question text with the given context."""
        pass
        
    @abstractmethod
    def get_correct_answer(self, person: 'Person', person_data: Dict[str, 'Person']) -> Any:
        """Get the correct answer for this question."""
        pass
        
    @abstractmethod
    def get_choices(self, person: 'Person', person_data: Dict[str, 'Person']) -> List[Any]:
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
    
    def _is_valid(self, person: 'Person', person_data: Dict[str, 'Person']) -> bool:
        # For multiple choice, we need to be able to generate choices
        try:
            choices = self.get_choices(person, person_data)
            return bool(choices)  # Valid if we have at least one choice
        except (KeyError, AttributeError, IndexError) as e:
            print(f"Invalid question {self.id} for {getattr(person, 'name', 'unknown')}: {e}")
            return False
            
    def get_question_text(self, person: 'Person', person_data: Dict[str, 'Person']) -> str:
        # Simple template rendering with person data
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.text)
        
        # Create a context with the person and person_data directly
        # Jinja2 can access object attributes directly
        context = {
            'person': person,
            'person_data': person_data,
            # Also include person's attributes at the top level for backward compatibility
            'name': person.name,
            'gender': person.gender,
            'birth_date': person.birth_date,
            'birth_place': person.birth_place,
            'death_date': person.death_date,
            'death_place': person.death_place,
            'father_id': person.father_id,
            'mother_id': person.mother_id,
            'spouse_id': person.spouse_id,
            'children': person.children,
            **person.additional_data  # Include any additional fields
        }
        
        return template.render(**context)
        
    def get_correct_answer(self, person: 'Person', person_data: Dict[str, 'Person']) -> Any:
        if not self.answer_expression:
            return None
        return self._evaluate_expression(self.answer_expression, person, person_data)
        
    def get_choices(self, person: 'Person', person_data: Dict[str, 'Person']) -> List[Any]:
        if not self.choices_expression:
            return []
        return self._evaluate_expression(self.choices_expression, person, person_data)
        
    def _evaluate_expression(self, expr: str, person: 'Person', person_data: Dict[str, 'Person']) -> Any:
        """Safely evaluate an expression in the context of person data."""
        # Restrict builtins for security
        safe_builtins = {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'set': set,
            'range': range,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'any': any,
            'all': all,
            'bool': bool,
        }
        
        if not expr:
            return None
            
        # Import utility functions
        from utils import (
            calculate_age, get_year, get_multiple_choices,
            get_age_choices, get_name_choices_by_gender,
            get_place_choices, compare_ages, get_year_choices
        )
        
        # Create a safe evaluation context
        safe_globals = {
            '__builtins__': safe_builtins,
            'person': person,
            'person_data': person_data,
            'calculate_age': calculate_age,
            'get_year': get_year,
            'get_multiple_choices': get_multiple_choices,
            'get_age_choices': get_age_choices,
            'get_name_choices_by_gender': get_name_choices_by_gender,
            'get_place_choices': get_place_choices,
            'compare_ages': compare_ages,
            'get_year_choices': get_year_choices,
        }
        
        try:
            # Evaluate the expression in the safe context
            return eval(expr, {'__builtins__': {}}, safe_globals)
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            raise

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
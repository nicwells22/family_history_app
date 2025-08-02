# Adding New Question Types

This document explains how to add new question types to the family history quiz application.

## Table of Contents
- [Question Class Hierarchy](#question-class-hierarchy)
- [Creating a New Question Type](#creating-a-new-question-type)
- [Registering the Question Type](#registering-the-question-type)
- [Example: Multiple Choice with Images](#example-multiple-choice-with-images)
- [Question Validation](#question-validation)
- [Best Practices](#best-practices)

## Question Class Hierarchy

The question system uses a class hierarchy with a base `Question` class and specialized subclasses:

```
Question (ABC)
├── MultipleChoiceQuestion
├── TextQuestion
└── YourNewQuestionType
```

## Creating a New Question Type

1. Create a new class that inherits from `Question` or an existing question type
2. Implement the required abstract methods
3. Add any additional methods specific to your question type

### Required Methods to Implement

- `get_question_text()`: Returns the formatted question text
- `get_correct_answer()`: Returns the correct answer
- `get_choices()`: Returns possible answer choices (if applicable)
- `is_valid_for()`: Determines if the question is valid for a given person
- `to_dict()`: Serializes the question to a dictionary
- `from_dict()`: Creates a question from a dictionary (class method)

## Registering the Question Type

1. Add your new question type to the `QuestionFactory` class in `models/question.py`:

```python
@classmethod
def _get_question_class(cls, question_type: str) -> Type['Question']:
    """Get the appropriate question class based on type."""
    question_classes = {
        'multiple_choice': MultipleChoiceQuestion,
        'text': TextQuestion,
        'your_question_type': YourNewQuestionType,  # Add your new type here
    }
    return question_classes[question_type]
```

## Example: Multiple Choice with Images

Here's an example of a new question type that includes images in the choices:

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from models.question import Question

@dataclass
class ImageChoiceQuestion(Question):
    """A multiple choice question that includes images in the choices."""
    image_paths: Dict[str, str]  # Map of choice text to image path
    
    def get_question_text(self, person, person_data) -> str:
        """Return the formatted question text with image placeholders."""
        return f"Which image shows {person.name}'s {self.field}?"
    
    def get_choices(self, person, person_data) -> List[Dict[str, Any]]:
        """Return choices with image paths."""
        return [
            {
                'text': choice,
                'image': self.image_paths.get(choice, '')
            }
            for choice in super().get_choices(person, person_data)
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data['image_paths'] = self.image_paths
        data['type'] = 'image_choice'
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageChoiceQuestion':
        """Create from dictionary."""
        question = super().from_dict(data)
        question.image_paths = data.get('image_paths', {})
        return question
```

## Question Validation

Questions should validate their configuration:

1. In `__post_init__` for basic validation
2. In `is_valid_for()` for person-specific validation
3. Using the `@validate_question` decorator for common validations

Example:

```python
@validate_question
def is_valid_for(self, person: 'Person', person_data: Dict[str, 'Person']) -> bool:
    """Check if this question is valid for the given person."""
    # Check if the person has the required field
    if not hasattr(person, self.field):
        return False
        
    # Check if the field value is not empty
    value = getattr(person, self.field, None)
    if not value:
        return False
        
    # Add any additional validation specific to this question type
    if self.question_type == 'image_choice':
        if not self.image_paths:
            return False
            
    return True
```

## Best Practices

1. **Separation of Concerns**: Keep question logic separate from rendering logic
2. **Error Handling**: Provide clear error messages for invalid configurations
3. **Documentation**: Document all public methods and class attributes
4. **Testing**: Write unit tests for new question types
5. **Backward Compatibility**: Ensure existing questions continue to work
6. **Performance**: Be mindful of performance with large datasets
7. **Accessibility**: Ensure questions are accessible (alt text for images, etc.)

## Adding to questions.yaml

To use your new question type, add it to `questions.yaml`:

```yaml
- id: family_photo_quiz
  type: image_choice
  field: "family_photo"
  question: "Which photo shows {{person.name}}'s family?"
  image_paths:
    "Option 1": "images/family1.jpg"
    "Option 2": "images/family2.jpg"
    "Option 3": "images/family3.jpg"
  required_fields:
    - "family_photo"
```

## Testing Your Question Type

1. Create unit tests in `tests/test_questions.py`
2. Test edge cases (missing data, invalid configurations, etc.)
3. Test with different person data scenarios
4. Verify serialization/deserialization works correctly

# Extending the Person Class

This document explains how to extend the `Person` class to add new functionality and relationships.

## Table of Contents
- [Adding New Fields](#adding-new-fields)
- [Adding New Methods](#adding-new-methods)
- [Adding New Relationships](#adding-new-relationships)
- [Custom Serialization](#custom-serialization)
- [Example Extension](#example-extension)

## Adding New Fields

To add a new field to the `Person` class:

1. Add the field to the class definition in `models/person.py`
2. Update the `to_dict()` and `from_dict()` methods to handle the new field
3. Update the CSV headers in `data_manager.py` if needed

Example:
```python
@dataclass
class Person:
    # ... existing fields ...
    new_field: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            # ... existing fields ...
            'new_field': self.new_field,
        }
        return data
    
    @classmethod
    def from_dict(cls, person_id: str, data: Dict[str, Any]) -> 'Person':
        # ... existing code ...
        person.new_field = data.get('new_field', '')
        return person
```

## Adding New Methods

You can add new methods to the `Person` class to encapsulate behavior:

```python
def get_age_at_death(self) -> Optional[int]:
    """Calculate the person's age at death if deceased."""
    if not self.death_date or not self.birth_date:
        return None
    # Implementation here
    return age
```

## Adding New Relationships

To add a new relationship type (e.g., siblings, cousins):

1. Add the relationship field to the class
2. Update the loading/saving logic
3. Add helper methods to manage the relationship

Example:
```python
@dataclass
class Person:
    # ... existing fields ...
    sibling_ids: List[str] = field(default_factory=list)
    
    def add_sibling(self, sibling_id: str, person_data: Dict[str, 'Person']) -> None:
        """Add a sibling relationship."""
        if sibling_id not in self.sibling_ids:
            self.sibling_ids.append(sibling_id)
        # Add reciprocal relationship
        if sibling_id in person_data:
            sibling = person_data[sibling_id]
            if self.id not in sibling.sibling_ids:
                sibling.sibling_ids.append(self.id)
```

## Custom Serialization

If you add complex fields that need special serialization, update these methods:

- `to_dict()`: Convert the object to a dictionary for storage
- `from_dict()`: Create an object from a dictionary
- `__post_init__()`: Handle any initialization after object creation

## Example Extension: Adding Education History

Here's a complete example of adding education history to a person:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Education:
    degree: str
    institution: str
    year: int
    field: str = ""

@dataclass
class Person:
    # ... existing fields ...
    education_history: List[Education] = field(default_factory=list)
    
    def add_education(self, degree: str, institution: str, year: int, field: str = "") -> None:
        """Add an education record."""
        self.education_history.append(Education(
            degree=degree,
            institution=institution,
            year=year,
            field=field
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            # ... existing fields ...
            'education': [
                {
                    'degree': e.degree,
                    'institution': e.institution,
                    'year': e.year,
                    'field': e.field
                }
                for e in self.education_history
            ]
        }
        return data
    
    @classmethod
    def from_dict(cls, person_id: str, data: Dict[str, Any]) -> 'Person':
        # ... existing code ...
        person = cls(
            id=person_id,
            # ... other fields ...
        )
        
        # Handle education history
        for edu in data.get('education', []):
            person.add_education(
                degree=edu['degree'],
                institution=edu['institution'],
                year=edu['year'],
                field=edu.get('field', '')
            )
            
        return person
```

## Best Practices

1. **Encapsulation**: Keep data access through methods when possible
2. **Immutability**: Consider using `frozen=True` on the dataclass for thread safety
3. **Documentation**: Add docstrings for all public methods
4. **Validation**: Add input validation in `__post_init__` or setter methods
5. **Backward Compatibility**: Maintain compatibility with existing data when possible

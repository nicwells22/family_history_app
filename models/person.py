# models/person.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

@dataclass
class Person:
    id: str
    name: str
    gender: str
    birth_date: str = ""
    birth_place: str = ""
    death_date: str = ""
    death_place: str = ""
    father_id: str = ""
    mother_id: str = ""
    spouse_id: str = ""
    children: List[str] = field(default_factory=list)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Store any extra fields in additional_data
        self._original_init = True
        self._data = {}
        
    def __getattr__(self, name: str) -> Any:
        # Allow access to additional_data fields as attributes
        if name in self.additional_data:
            return self.additional_data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get_age(self, reference_date: Optional[datetime] = None) -> Optional[int]:
        """Calculate age based on birth date and optional reference date."""
        if not self.birth_date:
            return None
        # Implementation of age calculation
        pass
    
    def is_alive(self, reference_date: Optional[datetime] = None) -> bool:
        """Check if the person is alive at the given date (or now)."""
        if not self.death_date:
            return True
        # Implementation of alive check
        pass
    
    def get_relationship(self, other: 'Person', person_data: Dict[str, 'Person']) -> Optional[str]:
        """Determine the relationship between this person and another person."""
        # Implementation of relationship detection
        pass
    
    def get_ancestors(self, person_data: Dict[str, 'Person'], generations: int = -1) -> Set['Person']:
        """Get all ancestors up to the specified number of generations."""
        # Implementation of ancestor retrieval
        pass
    
    def get_descendants(self, person_data: Dict[str, 'Person'], generations: int = -1) -> Set['Person']:
        """Get all descendants up to the specified number of generations."""
        # Implementation of descendant retrieval
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Person object back to a dictionary."""
        data = {
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'birth_place': self.birth_place,
            'death_date': self.death_date,
            'death_place': self.death_place,
            'father': self.father_id,
            'mother': self.mother_id,
            'spouse': self.spouse_id,
            **self.additional_data
        }
        return {k: v for k, v in data.items() if v}  # Remove empty values
    
    @classmethod
    def from_dict(cls, person_id: str, data: Dict[str, Any]) -> 'Person':
        """Create a Person from a dictionary."""
        # Separate standard fields from additional data
        standard_fields = {
            'name', 'gender', 'birth_date', 'birth_place',
            'death_date', 'death_place', 'father', 'mother', 'spouse'
        }
        
        # Extract standard fields
        person_data = {k: data.get(k, '') for k in standard_fields}
        
        # Create person with standard fields
        person = cls(
            id=person_id,
            name=person_data['name'],
            gender=person_data['gender'],
            birth_date=person_data.get('birth_date', ''),
            birth_place=person_data.get('birth_place', ''),
            death_date=person_data.get('death_date', ''),
            death_place=person_data.get('death_place', ''),
            father_id=person_data.get('father', ''),
            mother_id=person_data.get('mother', ''),
            spouse_id=person_data.get('spouse', '')
        )
        
        # Store any additional fields
        person.additional_data = {
            k: v for k, v in data.items() 
            if k not in standard_fields and v
        }
        
        return person
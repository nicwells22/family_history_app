import csv
from typing import Dict, List, Optional, Union, Any
import os
from pathlib import Path
from models.person import Person
import uuid

# Define required and optional fields for a person
REQUIRED_FIELDS = ['name', 'gender']
OPTIONAL_FIELDS = [
    'birth_date', 'death_date', 'birth_place', 'death_place',
    'father_id', 'mother_id', 'spouse_id'
]
ALL_FIELDS = REQUIRED_FIELDS + [f for f in OPTIONAL_FIELDS if f not in REQUIRED_FIELDS]

def load_people(filename: Union[str, Path]) -> Dict[str, Person]:
    """
    Load people data from CSV file and return a dictionary of Person objects.
    
    Args:
        filename: Path to the CSV file containing people data
        
    Returns:
        Dictionary mapping person IDs to Person objects
    """
    if not os.path.exists(filename):
        return {}
        
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        people = {}
        
        # First pass: Create all person objects
        for row in reader:
            person_id = row.get('id', '')
            if not person_id:
                continue
                
            # Filter out empty values and create person data
            person_data = {k: v for k, v in row.items() if k and v and k != 'id'}
            people[person_id] = Person.from_dict(person_id, person_data)
            
        # Second pass: Update relationships
        for person_id, person in people.items():
            # Update children lists based on parent relationships
            if person.father_id and person.father_id in people:
                if person_id not in people[person.father_id].children:
                    people[person.father_id].children.append(person_id)
                    
            if person.mother_id and person.mother_id in people:
                if person_id not in people[person.mother_id].children:
                    people[person.mother_id].children.append(person_id)
                    
        return people

def save_people(filename: Union[str, Path], people: Dict[str, Person]) -> None:
    """
    Save people data to CSV file. Creates the directory if it doesn't exist.
    
    Args:
        filename: Path to save the CSV file
        people: Dictionary mapping person IDs to Person objects
    """
    if not people:
        # Create an empty file with just headers if no people
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id'] + ALL_FIELDS)
            writer.writeheader()
        return
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(str(filename))), exist_ok=True)
    
    # Convert Person objects to dictionaries
    people_data = []
    for person_id, person in people.items():
        person_dict = person.to_dict()
        person_dict['id'] = person_id
        people_data.append(person_dict)
    
    # Get all field names from the data
    fieldnames = set()
    for person in people_data:
        fieldnames.update(person.keys())
    
    # Ensure required fields are included
    fieldnames.update(ALL_FIELDS)
    fieldnames.add('id')  # Ensure id is included
    fieldnames.discard('')  # Remove empty field if present
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(people_data)

def _get_field_input(field: str, current_value: str = '', is_editing: bool = False) -> str:
    """Helper function to get and validate field input from the user."""
    field_hints = {
        'birth_date': ' (format: YYYY-MM-DD, e.g., 1980-05-15)',
        'death_date': ' (format: YYYY-MM-DD, e.g., 2020-10-22)',
        'gender': ' (enter Male or Female)'
    }
    
    while True:
        hint = field_hints.get(field, '')
        
        # Different prompts for editing vs adding
        if is_editing:
            prompt = f"{field.replace('_id', '').replace('_', ' ').title()}{hint} [{current_value}]: "
            value = input(prompt).strip()
            # If editing and user pressed Enter, keep the current value
            if not value:
                return current_value
        else:
            prompt = f"{field.replace('_id', '').replace('_', ' ').title()}{hint}: "
            value = input(prompt).strip()
            # If adding a required field, value can't be empty
            if field in REQUIRED_FIELDS and not value:
                print(f"⚠️  {field.replace('_id', '').replace('_', ' ').title()} is required.")
                continue
            # If optional field and empty, return empty string
            if not value:
                return ''
        
        # Validate gender input
        if field == 'gender' and value:
            value_lower = value.lower()
            if value_lower in ['male', 'female']:
                return value.capitalize()
            print("⚠️  Please enter 'Male' or 'Female' for gender.")
            continue
                
        # Validate date format if it's a date field
        if field in ['birth_date', 'death_date'] and value:
            if not is_valid_date(value):
                print(f"⚠️  Invalid date format. Please use YYYY-MM-DD format (e.g., 1990-01-15).")
                continue
        
        return value

def _handle_relationship_field(people: Dict[str, Person], field: str, value: str, current_person: Optional[Person] = None) -> Optional[str]:
    """
    Helper function to handle relationship field creation and validation.
    
    Args:
        people: Dictionary of Person objects
        field: Type of relationship ('father_id', 'mother_id', or 'spouse_id')
        value: The name of the related person
        current_person: The person being edited (used for spouse relationships)
        
    Returns:
        The ID of the related person, or None if no relationship was created
    """
    if not value:  # Skip if no value provided
        return None
        
    name = value.strip()
    
    # Determine relationship type and expected gender
    if field in ['father_id', 'mother_id']:
        gender = 'male' if field == 'father_id' else 'female'
        relationship_type = 'parent'
    elif field == 'spouse_id':
        # For spouse, we need to determine the opposite gender
        if current_person and current_person.gender.lower() == 'male':
            gender = 'female'
        else:
            gender = 'male'
        relationship_type = 'spouse'
    else:
        return None
    
    # Check if person already exists
    existing_person = next(
        (p for p in people.values() 
         if p.name.lower() == name.lower() and 
            (field == 'spouse_id' or p.gender == gender)),
        None
    )
    
    if not existing_person:
        # Generate a unique ID using UUID
        person_id = generate_person_id()

        # Create a new Person object
        new_person = Person(
            id=person_id,
            name=name,
            gender=gender
        )
        people[person_id] = new_person
        print(f"✅ Added {name} ({gender}) as a new person with ID {person_id}.")
        
        # If this is a spouse, set up the reciprocal relationship
        if field == 'spouse_id' and current_person:
            new_person.spouse_id = current_person.id
            
        return person_id
    
    # If this is a spouse and we have the current person, set up the reciprocal relationship
    if field == 'spouse_id' and current_person:
        existing_person.spouse_id = current_person.id
    
    # Return existing person's ID
    return existing_person.id

def add_person(people: Dict[str, Person]) -> None:
    """
    Interactively add a new person to the people dictionary with helpful input hints.
    """
    print("\n=== Add New Person ===")
    
    # Generate a new ID for the person
    person_id = generate_person_id()
    
    # Get required fields
    name = _get_field_input('name')
    gender = _get_field_input('gender')
    
    # Create the person with required fields
    person = Person(
        id=person_id,
        name=name,
        gender=gender
    )
    
    # Get optional fields
    for field in OPTIONAL_FIELDS:
        value = _get_field_input(field)
        if value:  # Only set if user provided a value
            if field == 'birth_date':
                person.birth_date = value
            elif field == 'death_date':
                person.death_date = value
            elif field == 'birth_place':
                person.birth_place = value
            elif field == 'death_place':
                person.death_place = value
            elif field in ['father_id', 'mother_id', 'spouse_id']:
                related_id = _handle_relationship_field(
                    people, 
                    field, 
                    value,
                    current_person=person if field == 'spouse_id' else None
                )
                if related_id:
                    if field == 'father_id':
                        person.father_id = related_id
                    elif field == 'mother_id':
                        person.mother_id = related_id
                    elif field == 'spouse_id':
                        person.spouse_id = related_id
            else:
                # Store any additional fields in additional_data
                person.additional_data[field] = value
    
    # Add the new person to the dictionary
    people[person_id] = person
    print(f"\n✅ Added {person.name} to the family tree with ID {person_id}!")
    

def is_valid_date(date_str: str) -> bool:
    """Check if a date string is in YYYY-MM-DD format."""
    import re
    return bool(re.match(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', date_str))
    
    # Add to the list
    people.append(person)
    print(f"\n✅ Added {person['name']} to the family tree!")

def edit_person(people: Dict[str, Person]) -> None:
    """Interactively edit an existing person's information."""
    if not people:
        print("No people in the database to edit.")
        return
        
    print("\n=== Edit Person ===")
    
    # List all people for selection
    print("\nSelect a person to edit:")
    people_list = list(people.values())
    for i, person in enumerate(people_list, 1):
        print(f"{i}. {person.name} (ID: {person.id})")
    
    # Get selection
    while True:
        try:
            choice = int(input("\nEnter number: ")) - 1
            if 0 <= choice < len(people_list):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    person = people_list[choice]
    print(f"\nEditing: {person.name} (ID: {person.id})")
    
    # Show current values and allow editing for each field
    for field in ALL_FIELDS:
        # Get current value based on field type
        current_value = getattr(person, field, '')
        if field in person.additional_data:
            current_value = person.additional_data[field]
            
        new_value = _get_field_input(field, str(current_value) if current_value else '', is_editing=True)
        
        # Only update if the value has changed and is not empty
        if new_value != str(current_value) and new_value:
            if field == 'name':
                person.name = new_value
            elif field == 'gender':
                person.gender = new_value
            elif field == 'birth_date':
                person.birth_date = new_value
            elif field == 'death_date':
                person.death_date = new_value
            elif field == 'birth_place':
                person.birth_place = new_value
            elif field == 'death_place':
                person.death_place = new_value
            elif field in ['father_id', 'mother_id', 'spouse_id']:
                related_id = _handle_relationship_field(
                    people, 
                    field, 
                    new_value,
                    current_person=person if field == 'spouse_id' else None
                )
                if related_id:
                    if field == 'father_id':
                        person.father_id = related_id
                    elif field == 'mother_id':
                        person.mother_id = related_id
                    elif field == 'spouse_id':
                        person.spouse_id = related_id
            else:
                # Store in additional_data for custom fields
                person.additional_data[field] = new_value
    
    print(f"\n✅ Updated {person.name}'s information!")

def find_person(people: Dict[str, Person], name: str) -> Optional[Person]:
    """
    Find a person by name (case-insensitive).
    
    Args:
        people: Dictionary of Person objects
        name: Name to search for
        
    Returns:
        Person object if found, None otherwise
    """
    name_lower = name.lower()
    for person in people.values():
        if person.name.lower() == name_lower:
            return person
    return None

def generate_person_id() -> str:
    # Generate a unique ID using UUID
    return f"p_{uuid.uuid4().hex[:8]}"  # Use first 8 chars of UUID
import csv
from typing import Dict, List, Optional
import os

# Define required and optional fields for a person
REQUIRED_FIELDS = ['name', 'gender']
OPTIONAL_FIELDS = [
    'birth_date', 'death_date', 'birth_place', 'death_place',
    'father', 'mother'
]
ALL_FIELDS = REQUIRED_FIELDS + [f for f in OPTIONAL_FIELDS if f not in REQUIRED_FIELDS]

def load_people(filename: str) -> List[Dict]:
    """Load people data from CSV file."""
    if not os.path.exists(filename):
        return []
        
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Filter out empty columns that might be present in the CSV
        return [
            {k: v for k, v in row.items() if k and v}
            for row in reader
        ]

def save_people(filename: str, people: List[Dict]) -> None:
    """Save people data to CSV file. Creates the directory if it doesn't exist."""
    if not people:
        # Create an empty file with just headers if no people
        people = [{}]
        
    # Get all unique field names from all people
    fieldnames = set()
    for person in people:
        fieldnames.update(person.keys())
    
    # Ensure required fields are included
    fieldnames = list(fieldnames.union(set(REQUIRED_FIELDS)))
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(filename)) or '.', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(people)

def add_person(people: List[Dict]) -> None:
    """
    Interactively add a new person to the people list with helpful input hints.
    """
    print("\n=== Add New Person ===")
    person = {}
    
    # Field-specific hints
    field_hints = {
        'birth_date': ' (format: YYYY-MM-DD, e.g., 1980-05-15)',
        'death_date': ' (format: YYYY-MM-DD, e.g., 2020-10-22)',
        'gender': ' (enter Male or Female)'
    }
    
    # Get required fields
    for field in REQUIRED_FIELDS:
        while True:
            hint = field_hints.get(field, '')
            value = input(f"{field.replace('_', ' ').title()}{hint}: ").strip()
            
            # Validate gender input
            if field == 'gender' and value:
                value_lower = value.lower()
                if value_lower in ['male', 'female']:
                    value = value.capitalize()
                else:
                    print("⚠️  Please enter 'Male' or 'Female' for gender.")
                    continue
                    
            if value:
                person[field] = value
                break
                
            print(f"⚠️  {field.replace('_', ' ').title()} is required.")
    
    # Get optional fields
    for field in OPTIONAL_FIELDS:
        if field in person:  # Skip if already set
            continue
            
        while True:
            hint = field_hints.get(field, '')
            value = input(f"{field.replace('_', ' ').title()}{hint} (press Enter to skip): ").strip()
            
            # If user pressed Enter, skip this field
            if not value:
                break
                
            # Validate date format if it's a date field
            if field in ['birth_date', 'death_date']:
                if not is_valid_date(value):
                    print(f"⚠️  Invalid date format. Please use YYYY-MM-DD format (e.g., 1990-01-15).")
                    continue  # This will repeat the current field's input
            
            # Handle parent fields (father/mother)
            if field in ['father', 'mother']:
                parent_name = value
                parent_gender = 'Male' if field == 'father' else 'Female'
                
                # Check if parent already exists
                parent_exists = any(p.get('name', '').lower() == parent_name.lower() for p in people)
                
                if not parent_exists:
                    # Create a new person record for the parent
                    parent = {
                        'name': parent_name,
                        'gender': parent_gender
                    }
                    people.append(parent)
                    print(f"✅ Added {parent_name} ({parent_gender}) as a new person.")
            
            # Set the field value (this will be the parent's name)
            person[field] = value
            break  # Move to next field
    
    # Add the new person to the list
    people.append(person)
    print(f"\n✅ Added {person['name']} to the family tree!")
    

def is_valid_date(date_str: str) -> bool:
    """Check if a date string is in YYYY-MM-DD format."""
    import re
    return bool(re.match(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', date_str))
    
    # Add to the list
    people.append(person)
    print(f"\n✅ Added {person['name']} to the family tree!")

def edit_person(people: List[Dict]) -> None:
    """Interactively edit an existing person's information."""
    if not people:
        print("No people in the database to edit.")
        return
        
    print("\n=== Edit Person ===")
    
    # List all people for selection
    print("\nSelect a person to edit:")
    for i, person in enumerate(people, 1):
        print(f"{i}. {person.get('name', 'Unnamed')}")
    
    # Get selection
    while True:
        try:
            choice = int(input("\nEnter number: ")) - 1
            if 0 <= choice < len(people):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    person = people[choice]
    print(f"\nEditing: {person.get('name')}")
    
    # Show current values and allow editing
    for field in ALL_FIELDS:
        current = person.get(field, "")
        new_value = input(f"{field.replace('_', ' ').title()} [{current}]: ").strip()
        if new_value:
            person[field] = new_value
    
    print(f"\n✅ Updated {person['name']}'s information!")

def find_person(people: List[Dict], name: str) -> Optional[Dict]:
    """Find a person by name (case-insensitive)."""
    name_lower = name.lower()
    for person in people:
        if person.get('name', '').lower() == name_lower:
            return person
    return None

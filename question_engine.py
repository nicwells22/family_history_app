# import yaml
# from jinja2 import Template

from typing import List, Dict, Any
import yaml
from models.question import Question, QuestionFactory

def load_questions(yaml_file: str) -> List[Question]:
    """Load questions from YAML file and return Question objects."""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        question_data = yaml.safe_load(f)
    
    questions = []
    for q_data in question_data:
        try:
            question = QuestionFactory.from_yaml(q_data)
            questions.append(question)
        except Exception as e:
            print(f"Error loading question {q_data.get('id', 'unknown')}: {e}")
    
    return questions

def get_valid_questions(person: Dict[str, Any], 
                       person_data: Dict[str, Dict], 
                       questions: List[Question]) -> List[Question]:
    """
    Get all questions that are valid for the given person.
    
    Args:
        person: The person to validate questions against
        person_data: Dictionary of all people
        questions: List of questions to validate
        
    Returns:
        List[Question]: List of valid questions for the person
    """
    return [q for q in questions if q.is_valid_for(person, person_data)]

# def load_questions(yaml_file):
#     with open(yaml_file, 'r', encoding='utf-8') as f:
#         return yaml.safe_load(f)

# def get_valid_questions(person, person_data, questions):
#     valid = []
#     for q in questions:
#         if not q.get("required_fields"):
#             continue
#         if all(field_is_available(person, person_data, f) for f in q["required_fields"]):
#             valid.append(q)
#     return valid


# def safe_get_parent(person, person_data, parent_type):
#     """Safely get parent data, returning a default dict if parent not found"""
#     parent_name = person.get(parent_type)
#     if not parent_name or parent_name not in person_data:
#         return {'name': parent_name or f'Unknown {parent_type.capitalize()}'}
#     return person_data[parent_name]

# def render_question(question_template, person, person_data):
#     context = {
#         'person': person,
#         'person_data': person_data,
#         'get_parent': lambda p_type: safe_get_parent(person, person_data, p_type)
#     }
#     template = Template(question_template)
#     return template.render(context)

# def resolve_field_path(person, person_data, path):
#     if '.' in path:
#         obj, field = path.split('.')
#         if obj == "parent":
#             return person_data.get(person['father'] or person['mother'], {}).get(field)
#         if obj == "person":
#             return person.get(field)
#         return None
#     return person.get(path)

# def field_is_available(person, person_data, field_path):
#     """
#     Returns True if the required field path exists and is non-empty.
#     Supports nested fields like person.birth_date or parent.birth_place.
#     """
#     try:
#         if '.' not in field_path:
#             return person.get(field_path) not in (None, "", "NA")

#         obj, attr = field_path.split('.')

#         if obj == "person":
#             return person.get(attr) not in (None, "", "NA")

#         if obj == "father" and person.get("father") in person_data:
#             return person_data[person["father"]].get(attr) not in (None, "", "NA")

#         if obj == "mother" and person.get("mother") in person_data:
#             return person_data[person["mother"]].get(attr) not in (None, "", "NA")

#         return False
#     except Exception:
#         return False

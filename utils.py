from datetime import datetime
import random

def calculate_age(birth_date, end_date):
    b = datetime.strptime(birth_date, "%Y-%m-%d")
    e = datetime.strptime(end_date, "%Y-%m-%d")
    return e.year - b.year - ((e.month, e.day) < (b.month, b.day))

def get_year(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").year

def safe_eval(expr, context):
    try:
        return eval(expr, {}, context)
    except Exception as e:
        print(f"Error evaluating expression: {expr} - {e}")
        return None

def get_multiple_choices(field, person_data, correct, transform=None):
    pool = []
    for p in person_data.values():
        val = p.get(field)
        if not val:
            continue
        val = transform(val) if transform else val
        if val != correct:
            pool.append(val)
    pool = list(set(pool))
    distractors = random.sample(pool, k=3) if len(pool) >= 3 else pool[:3]
    choices = [correct] + distractors
    random.shuffle(choices)
    return choices

def get_age_choices(birth, death):
    actual = calculate_age(birth, death)
    choices = list(set([
        actual,
        actual + random.randint(1, 5),
        actual - random.randint(1, 5),
        actual + random.randint(6, 10)
    ]))
    while len(choices) < 4:
        choices.append(random.randint(20, 90))
    choices = list(set(choices))
    random.shuffle(choices)
    return choices[:4]

def pick_random_people_with_lifespans(person_data, count=3, include=None):
    candidates = [p for p in person_data.values()
                  if p.get('birth_date') and p.get('death_date') and p != include]
    sample = random.sample(candidates, k=count)
    if include:
        sample.append(include)
    random.shuffle(sample)
    return [p['name'] for p in sample]

def longest_lived(people_list):
    def age(p): return calculate_age(p['birth_date'], p['death_date'])
    return max(people_list, key=age)['name']

def get_people_by_gender(person_data, gender):
    return [
        p for p in person_data.values()
        if p.get("gender", "").lower().startswith(gender[0])  # handles "male"/"m"
    ]

def get_place_choices(field, person_data, correct_place):
    """
    Generate multiple choice options for place-based questions.
    Returns a list of 4 unique place names including the correct one.
    """
    # Get all unique places from the specified field
    places = set()
    for person in person_data.values():
        place = person.get(field)
        if place and place != correct_place:  # Exclude the correct place
            places.add(place)
    
    places = list(places)
    
    # If we don't have enough places, add some generic ones
    while len(places) < 3:
        generic_places = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", 
                         "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA"]
        for place in generic_places:
            if place not in places and place != correct_place:
                places.append(place)
                if len(places) >= 3:
                    break
                    
    # Select 3 random places (or fewer if we don't have enough)
    selected = random.sample(places, min(3, len(places)))
    
    # Combine with correct answer and shuffle
    choices = [correct_place] + selected
    random.shuffle(choices)
    
    return choices[:4]  # Ensure we return exactly 4 choices

def get_name_choices_by_gender(person_data, correct_person, target_gender):
    """
    Return 4 total names (including the correct one), all matching the target gender.
    correct_person can be either a person dictionary or a name string.
    """
    # Handle case where correct_person is just a name string
    if isinstance(correct_person, str):
        correct_name = correct_person
    # Handle case where correct_person is a dictionary
    elif isinstance(correct_person, dict) and "name" in correct_person:
        correct_name = correct_person["name"]
    else:
        correct_name = "Unknown"
    
    # Get all names of the target gender (excluding the correct name)
    options = []
    for p in person_data.values():
        if p.get("gender", "").lower().startswith(target_gender[0].lower()) and p.get("name") != correct_name:
            options.append(p["name"])
    
    # Remove duplicates and ensure we have a list
    options = list(set(options))
    
    # If we don't have enough options, add some generic names based on gender
    if len(options) < 3:
        if target_gender.lower().startswith('f'):
            generic_names = ["Sarah Johnson", "Emily Davis", "Jessica Wilson", "Jennifer Brown"]
        else:
            generic_names = ["John Smith", "Michael Johnson", "David Williams", "Robert Brown"]
        
        for name in generic_names:
            if name != correct_name and name not in options:
                options.append(name)
                if len(options) >= 3:
                    break
    
    # If we still don't have enough options, use any available names
    if len(options) < 3:
        all_names = [p["name"] for p in person_data.values() if p.get("name") != correct_name]
        while len(options) < 3 and all_names:
            name = random.choice(all_names)
            if name not in options:
                options.append(name)
    
    # Ensure we have exactly 3 options (for a total of 4 with the correct answer)
    options = options[:3]
    
    # Combine with correct answer and shuffle
    choices = options + [correct_name]
    random.shuffle(choices)
    
    return choices

def get_parent(person, person_data, parent_type):
    """Safely get parent data, returning a default dict if parent not found"""
    parent_name = person.get(parent_type)
    if not parent_name or parent_name not in person_data:
        return {'name': parent_name or f'Unknown {parent_type.capitalize()}'}
    return person_data[parent_name]

def compare_ages(father_age, mother_age):
    if father_age > mother_age:
        return "Father"
    elif mother_age > father_age:
        return "Mother"
    elif father_age == mother_age:
        return "They were the same age"
    else:
        return "Unknown"

def get_year_choices(date_str, num_choices=4, year_range=10):
    """
    Generate multiple choice options for year-based questions.
    
    Args:
        date_str (str): The date string in 'YYYY-MM-DD' format
        num_choices (int): Number of choices to return (default: 4)
        year_range (int): Range of years to consider for incorrect choices (default: 10)
        
    Returns:
        list: List of year options including the correct year
    """
    try:
        # Extract the year from the date string
        correct_year = get_year(date_str)
        
        # Generate some incorrect choices
        years = {correct_year}
        
        # Add years within the specified range
        while len(years) < min(num_choices, year_range + 1):
            offset = random.randint(1, year_range)
            # Add both before and after the correct year
            for sign in [-1, 1]:
                if len(years) >= num_choices:
                    break
                years.add(correct_year + (offset * sign))
        
        # If we still don't have enough choices, add some random years
        while len(years) < num_choices:
            # Generate a random year within 100 years of the correct year
            years.add(correct_year + random.randint(-100, 100))
        
        # Convert to list, shuffle, and return
        years = list(years)
        random.shuffle(years)
        return years[:num_choices]
        
    except (ValueError, TypeError, AttributeError):
        # Fallback in case of invalid date string
        current_year = datetime.now().year
        return sorted([current_year - 30, current_year - 20, current_year - 10, current_year])
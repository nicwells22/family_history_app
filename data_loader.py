import csv

def load_ancestors(csv_file):
    people = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            person = {
                'name': row['name'],
                'birth_date': row.get('birth_date'),
                'death_date': row.get('death_date'),
                'birth_place': row.get('birth_place'),
                'death_place': row.get('death_place'),
                'father': row.get('father'),
                'mother': row.get('mother'),
                'gender': row.get('gender')
            }
            people[person['name']] = person
    return people

import random
from data_loader import load_ancestors
import yaml
import data_manager
from question_engine import (
    load_questions, render_question, 
    get_valid_questions
)
from utils import (
    calculate_age, get_year, safe_eval,
    get_multiple_choices, get_age_choices, 
    get_name_choices_by_gender, get_place_choices,
    compare_ages, get_parent
)

def show_menu():
    print("\n📜 Family History App")
    print("1. Take the Ancestor Quiz")
    print("2. Add a New Person")
    print("3. Edit Existing Person")
    print("4. View All People")
    print("5. Exit")
    while True:
        try:
            return int(input("\nSelect an option (1-5): "))
        except ValueError:
            print("Please enter a number between 1 and 5.")

def run_quiz():
    print("\n📜 Starting the Ancestor Quiz!")
    
    # Load data using data_manager
    people = data_manager.load_people("data.csv")
    
    # Check if we have at least one person with minimal required information
    if not people or not all(field in person for person in people for field in data_manager.REQUIRED_FIELDS):
        print("\n⚠️  No family members found or incomplete data. You need to add at least one person with name and gender before taking the quiz.")
        add_person = input("Would you like to add a family member now? (yes/no): ").strip().lower()
        if add_person in ['y', 'yes']:
            # Create a new empty list to collect the new person
            new_people = []
            data_manager.add_person(new_people)
            if new_people:  # If a person was successfully added
                # Save the new person to the file
                data_manager.save_people("data.csv", new_people)
                # Reload people after adding
                people = data_manager.load_people("data.csv")
                print(f"✅ Successfully added {new_people[0]['name']} to the family tree!")
            else:
                print("No person was added. Returning to main menu.")
                return
        else:
            print("Returning to main menu.")
            return
    
    person_data = {p['name']: p for p in people}  # Convert to dict for compatibility
    all_questions = load_questions("questions.yaml")
    score = 0
    rounds = 10

    # Pre-generate all possible valid questions with their associated people
    all_valid_questions = []
    for person in person_data.values():
        valid_qs = get_valid_questions(person, person_data, all_questions)
        for q in valid_qs:
            all_valid_questions.append((person, q))
    
    # Ensure we have enough questions
    if not all_valid_questions:
        print("Error: No valid questions could be generated from the data.")
        return
        
    # Select questions (with replacement if needed)
    selected_questions = random.choices(
        all_valid_questions,
        k=min(rounds, len(all_valid_questions))
    )
    
    for i, (person, q) in enumerate(selected_questions, 1):
        try:
            question_text = render_question(q['question'], person, person_data)
            print(f"\nQuestion {i}: {question_text}")

            context = {
                'person': person,
                'person_data': person_data,
                'calculate_age': calculate_age,
                'get_year': get_year,
                'get_multiple_choices': get_multiple_choices,
                'get_age_choices': get_age_choices,
                'get_name_choices_by_gender': get_name_choices_by_gender,
                'get_place_choices': get_place_choices,
                'compare_ages': compare_ages,
                'get_parent': lambda parent_type: get_parent(person, person_data, parent_type)
            }

            choices = safe_eval(q['choices_function'], context)
            correct = str(safe_eval(q['answer_function'], context))

            if not choices:
                print("Skipping question due to missing data.")
                continue

            # Display choices
            for idx, option in enumerate(choices, 1):
                print(f"{idx}. {option}")

            # Get user's answer
            while True:
                user_input = input(f"Your answer (1-{len(choices)}): ").strip()
                if user_input.isdigit() and 1 <= int(user_input) <= len(choices):
                    break
                print(f"Please enter a number between 1 and {len(choices)}")
            
            # Check answer
            selected = str(choices[int(user_input) - 1])
            if selected == correct:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Incorrect. The correct answer was: {correct}")
                
        except Exception as e:
            print(f"Error processing question: {e}")
            continue

    print(f"\n🏁 Final Score: {score}/{len(selected_questions)}")
    if score == len(selected_questions):
        print("🎉 Perfect score! You know your family well!")
    elif score >= len(selected_questions) / 2:
        print("👍 Good job! You know quite a bit about your family!")
    else:
        print("💡 Keep learning about your ancestors!")

def view_all_people():
    """Display all people in the database."""
    people = data_manager.load_people("data.csv")
    print("\n=== Family Members ===")
    for i, person in enumerate(people, 1):
        print(f"{i}. {person.get('name')} ({person.get('gender', 'unknown')})")
        if 'birth_date' in person or 'birth_place' in person:
            print(f"   Born: {person.get('birth_date', '?')} in {person.get('birth_place', '?')}")
        if 'death_date' in person or 'death_place' in person:
            print(f"   Died: {person.get('death_date', '?')} in {person.get('death_place', '?')}")
        print()

def check_initial_setup():
    """Check if we have the minimum required data to run the app."""
    people = data_manager.load_people("data.csv")
    if not people or not all(field in person for person in people for field in data_manager.REQUIRED_FIELDS):
        print("\n👋 Welcome to the Family History App!")
        print("It looks like this is your first time using the app or you don't have any family members added yet.")
        print("Let's get started by adding your first family member!")
        
        people = []
        while True:
            data_manager.add_person(people)
            data_manager.save_people("data.csv", people)
            
            add_another = input("\nWould you like to add another family member? (yes/no): ").strip().lower()
            if add_another not in ['y', 'yes']:
                break
        
        if not people:
            print("\n⚠️  You need to add at least one family member to use the app.")
            return False
    return True

def main():
    # Check if we need to do initial setup
    if not check_initial_setup():
        print("\nExiting the Family History App. Goodbye!")
        return
        
    print("\n📜 Welcome to the Family History App!")
    
    while True:
        choice = show_menu()
        
        if choice == 1:  # Run Quiz
            run_quiz()
        elif choice == 2:  # Add New Person
            people = data_manager.load_people("data.csv")
            data_manager.add_person(people)
            data_manager.save_people("data.csv", people)
        elif choice == 3:  # Edit Person
            people = data_manager.load_people("data.csv")
            data_manager.edit_person(people)
            data_manager.save_people("data.csv", people)
        elif choice == 4:  # View All People
            view_all_people()
        elif choice == 5:  # Exit
            print("\n👋 Thank you for using the Family History App!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

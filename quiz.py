import random
import sys
from typing import Dict, List, Any, Optional

from models.person import Person
import data_manager
from models.question import Question, QuestionFactory
import yaml

def show_menu() -> int:
    """
    Display the main menu and get user's choice.
    
    Returns:
        int: User's menu choice (1-5)
    """
    print("\n📜 Family History App")
    print("1. Take the Ancestor Quiz")
    print("2. Add a New Person")
    print("3. Edit Existing Person")
    print("4. View All People")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect an option (1-5): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 5:
                return int(choice)
            print("Please enter a number between 1 and 5.")
        except (ValueError, KeyboardInterrupt):
            print("\nPlease enter a valid number.")
        except EOFError:
            print("\nExiting...")
            sys.exit(0)

def run_quiz() -> None:
    """
    Run the family history quiz.
    
    Loads people data, generates questions, and administers the quiz.
    """
    print("\n📜 Starting the Ancestor Quiz!")
    
    # Load data using data_manager
    people = data_manager.load_people("data/people.csv")
    if not people:
        print("No family data found. Please add some family members first.")
        return
    
    # Load questions from YAML
    with open("questions.yaml", 'r') as f:
        questions_data = yaml.safe_load(f)
    
    # Create Question objects
    questions = [QuestionFactory.from_yaml(q) for q in questions_data]
    
    # Get valid questions for each person
    all_questions = []
    for person in people.values():
        valid_questions = [
            q for q in questions 
            if q.is_valid_for(person, people)
        ]
        all_questions.extend([(person, q) for q in valid_questions])
    
    if not all_questions:
        print("No valid questions found with the current family data.")
        return
    
    # Shuffle questions
    random.shuffle(all_questions)
    
    # Administer quiz
    score = 0
    total = min(10, len(all_questions))  # Limit to 10 questions
    
    print(f"\nYou'll be asked {total} questions. Let's begin!\n")
    
    for i, (person, question) in enumerate(all_questions[:total], 1):
        # Get question text and correct answer
        q_text = question.get_question_text(person, people)
        correct_answer = question.get_correct_answer(person, people)
        
        # Get choices (shuffled)
        choices = question.get_choices(person, people)
        random.shuffle(choices)
        
        # Display question
        print(f"\nQuestion {i}:")
        print(q_text)
        
        # Display choices
        for idx, choice in enumerate(choices, 1):
            print(f"{idx}. {choice}")
        
        # Get user's answer
        while True:
            try:
                user_choice = input("\nYour answer (1-4, or 'q' to quit): ").strip().lower()
                if user_choice == 'q':
                    print("\nQuiz aborted.")
                    return
                    
                user_choice = int(user_choice)
                if 1 <= user_choice <= len(choices):
                    break
                print(f"Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("Please enter a valid number or 'q' to quit.")
        
        # Check answer
        user_answer = choices[user_choice - 1]
        if user_answer == correct_answer:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Incorrect. The correct answer is: {correct_answer}")
    
    # Show results
    print(f"\nQuiz complete! Your score: {score}/{total} ({(score/total)*100:.1f}%)")
    if score == total:
        print("🎉 Perfect score! You know your family well!")
    elif score >= total * 0.7:
        print("👍 Great job! You know your family pretty well!")
    elif score >= total * 0.4:
        print("🤔 Not bad! Keep learning about your family history!")
    else:
        print("💡 Keep learning! You'll get better with time!")

def view_all_people() -> None:
    """Display all people in the database."""
    people = data_manager.load_people("data/people.csv")
    if not people:
        print("No people found in the database.")
        return
        
    print("\n=== People in Database ===")
    for i, (person_id, person) in enumerate(people.items(), 1):
        print(f"{i}. {person.name} (ID: {person_id})")
        print(f"   Gender: {person.gender}")
        print(f"   Birth: {person.birth_date or '?'} in {person.birth_place or '?'}")
        if person.father_id and person.father_id in people:
            print(f"   Father: {people[person.father_id].name} (ID: {person.father_id})")
        if person.mother_id and person.mother_id in people:
            print(f"   Mother: {people[person.mother_id].name} (ID: {person.mother_id})")
        if person.spouse_id and person.spouse_id in people:
            print(f"   Spouse: {people[person.spouse_id].name} (ID: {person.spouse_id})")
        if person.children:
            children_names = [
                f"{people[cid].name} (ID: {cid}" 
                for cid in person.children 
                if cid in people
            ]
            if children_names:
                print(f"   Children: {', '.join(children_names)}")
        print()

def check_initial_setup() -> None:
    """Check if we have the minimum required data to run the app."""
    import os
    from pathlib import Path
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Check if data file exists, create empty if not
    data_file = data_dir / "people.csv"
    if not data_file.exists():
        print("No data file found. Creating a new one.")
        with open(data_file, 'w', newline='', encoding='utf-8') as f:
            # Create a file with just headers
            import csv
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'gender', 'birth_date', 'birth_place', 'death_date', 'death_place', 'father_id', 'mother_id', 'spouse_id', 'children'])
            writer.writeheader()
    
    # Check if questions file exists
    questions_file = "questions.yaml"
    if not os.path.exists(questions_file):
        print("No questions file found. Please create one.")
        exit(1)

def main() -> None:
    """Main entry point for the application."""
    check_initial_setup()
    
    while True:
        try:
            choice = show_menu()
            
            if choice == 1:
                run_quiz()
            elif choice == 2:
                people = data_manager.load_people("data/people.csv")
                data_manager.add_person(people)
                data_manager.save_people("data/people.csv", people)
            elif choice == 3:
                people = data_manager.load_people("data/people.csv")
                data_manager.edit_person(people)
                data_manager.save_people("data/people.csv", people)
            elif choice == 4:
                view_all_people()
            elif choice == 5:
                print("\n👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️  An error occurred: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            print("Please try again or contact support if the problem persists.")
            continue

if __name__ == "__main__":
    main()

import random
import sys
from typing import Dict, List, Any

import data_manager
import question_engine
from models.question import Question

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
    people = data_manager.load_people("data.csv")
    if not people:
        print("No family data found. Please add some family members first.")
        return
        
    person_data = {p['name']: p for p in people}
    
    # Load questions
    try:
        all_questions = question_engine.load_questions("questions.yaml")
        if not all_questions:
            print("No questions found. Please check your questions.yaml file.")
            return
    except Exception as e:
        print(f"Error loading questions: {e}")
        return
    
    # Get valid questions
    valid_questions = []
    for person in person_data.values():
        person_questions = question_engine.get_valid_questions(person, person_data, all_questions)
        valid_questions.extend([(person, q) for q in person_questions])
    
    if not valid_questions:
        print("No valid questions found with the current family data.")
        print("Make sure you have enough family members with complete information.")
        return
    
    # Run quiz
    score = 0
    num_questions = min(10, len(valid_questions))
    selected_questions = random.sample(valid_questions, num_questions)
    
    print(f"\nYou'll be asked {num_questions} questions. Let's begin!\n")
    
    for i, (person, question) in enumerate(selected_questions, 1):
        try:
            # Display question
            print(f"\nQuestion {i}: {question.get_question_text(person, person_data)}")
            
            # Get and display choices
            choices = question.get_choices(person, person_data)
            if not choices:
                print("Skipping question - no valid choices generated.")
                continue
                
            for idx, choice in enumerate(choices, 1):
                print(f"{idx}. {choice}")
            
            # Get and validate user answer
            while True:
                try:
                    user_choice = input("\nYour answer (number, or 'q' to quit): ").strip().lower()
                    
                    if user_choice == 'q':
                        print("\nQuiz ended early.")
                        return
                        
                    if not user_choice.isdigit():
                        raise ValueError("Please enter a number")
                        
                    user_choice_idx = int(user_choice) - 1
                    if user_choice_idx < 0 or user_choice_idx >= len(choices):
                        raise ValueError(f"Please enter a number between 1 and {len(choices)}")
                        
                    break
                    
                except ValueError as e:
                    print(f"Invalid input: {e}")
                except (KeyboardInterrupt, EOFError):
                    print("\nQuiz ended early.")
                    return
            
            # Check answer
            try:
                correct_answer = question.get_correct_answer(person, person_data)
                user_answer = choices[user_choice_idx]
                
                if user_answer == correct_answer:
                    print("✅ Correct!")
                    score += 1
                else:
                    print(f"❌ Incorrect. The correct answer was: {correct_answer}")
                    
            except Exception as e:
                print(f"Error checking answer: {e}")
                
        except Exception as e:
            print(f"\nAn error occurred with this question: {e}")
            continue
    
    # Display final score
    print(f"\n{'🎉' * 3} Quiz Complete! {'🎉' * 3}")
    print(f"Your score: {score} out of {num_questions} ({(score/num_questions)*100:.1f}%)")
    
    # Add some encouragement based on score
    if score == num_questions:
        print("Perfect score! You know your family history well!")
    elif score / num_questions >= 0.8:
        print("Excellent job! You know your family history very well!")
    elif score / num_questions >= 0.5:
        print("Good job! You know quite a bit about your family.")
    else:
        print("Keep learning about your family history!")
    
    # input("\nPress Enter to return to the main menu...")

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

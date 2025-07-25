# Family History App

An interactive command-line application that helps users learn and test their knowledge about their family history through a quiz-based interface. The app stores family member information and generates personalized questions based on the data provided.

## Features

- **Interactive Quiz**: Test your knowledge about your family members with automatically generated questions
- **Family Tree Management**: Add and edit family member information with ease
- **Data Persistence**: All family data is saved to a CSV file for future use
- **Input Validation**: Ensures data integrity with proper validation for dates and required fields
- **First-Time User Friendly**: Guides new users through setting up their family tree

## Prerequisites

- Python 3.7 or higher
- Required Python packages (install via `pip install -r requirements.txt`):
  - PyYAML
  - Jinja2

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd family_history_app
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python quiz.py
   ```

2. Main Menu Options:
   - **1. Take the Ancestor Quiz**: Start a new quiz session
   - **2. Add a New Person**: Add a new family member to your tree
   - **3. Edit Existing Person**: Modify information for an existing family member
   - **4. View All People**: See a list of all family members in your tree
   - **5. Exit**: Close the application

## Data Format

Family member information is stored in `data.csv` with the following fields:
- **Required Fields**:
  - `name`: Full name of the family member
  - `gender`: Either "Male" or "Female"
- **Optional Fields**:
  - `birth_date`: Date of birth (format: YYYY-MM-DD)
  - `death_date`: Date of death (format: YYYY-MM-DD)
  - `birth_place`: Place of birth
  - `death_place`: Place of death
  - `father`: Name of father (must match exactly with another entry's name)
  - `mother`: Name of mother (must match exactly with another entry's name)

## Customizing Questions

Questions are stored in `questions.yaml` and use a template system with the following features:
- Use `{{ person.field }}` to reference the current person's data
- Use `{{ get_parent('father') }}` or `{{ get_parent('mother') }}` to reference parent information
- Each question can specify required fields that must be present in the data

## Example Usage

```
📜 Welcome to the Family History App!

=== Add New Person ===
Name: John Doe
Gender (enter Male or Female): Male
Birth Date (format: YYYY-MM-DD, e.g., 1980-05-15): 1985-07-20
Birth Place (press Enter to skip): New York

✅ Added John Doe to the family tree!
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

import pygame
from gpt import handle_prompt
from main import *
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QLabel, QComboBox, QSpinBox


# Initialize PyQt5 Application
app = QApplication(sys.argv)

def show_popup():
    # Create a dialog window
    dialog = QDialog()
    dialog.setWindowTitle("Quiz Setting")
    
    # Create a vertical layout for the popup
    layout = QVBoxLayout()
    
    # Create a label
    label = QLabel("Create quiz with AI")
    layout.addWidget(label)

    # Create a large text input (QTextEdit)
    text_input = QTextEdit()
    text_input.setPlaceholderText("Enter your content here...")
    layout.addWidget(text_input)

    # Create a ComboBox for difficulty level
    difficulty_label = QLabel("Select Difficulty Level:")
    layout.addWidget(difficulty_label)

    difficulty_combo = QComboBox()
    difficulty_combo.addItems(["Easy", "Medium", "Hard"])
    layout.addWidget(difficulty_combo)

     # Create a ComboBox for difficulty level
    language_label = QLabel("Choose language:")
    layout.addWidget(language_label)

    language_combo = QComboBox()
    language_combo.addItems(["thai", "english"])
    layout.addWidget(language_combo)

    # Create a label for number of questions
    num_questions_label = QLabel("Number of Questions (0-20):")
    layout.addWidget(num_questions_label)

    # Create a QSpinBox for number of questions with a range of 0 to 20
    num_questions_input = QSpinBox()
    num_questions_input.setRange(0, 20)  # Set the range from 0 to 20
    layout.addWidget(num_questions_input)

    # Create a button for selecting a file
    file_button = QPushButton("Select File")
    
    # Create a variable to store the selected file path
    file_path = ""

    # Function to open file dialog when the button is clicked
    def select_file():
        nonlocal file_path
        file_path, _ = QFileDialog.getOpenFileName(dialog, "Select a File", "", "All Files (*)")
        if file_path:
            print(f"Selected file: {file_path}")

    file_button.clicked.connect(select_file)
    layout.addWidget(file_button)

    # Create a submit button to return input text and file path
    submit_button = QPushButton("Submit")
    
    # Function to handle submit button click
    def submit():
        input_text = text_input.toPlainText()
        language_lavel = language_combo.currentText()
        difficulty_level = difficulty_combo.currentText()
        number_of_questions = num_questions_input.value()  # Get the value from QSpinBox

        if file_path == "":
            handle_prompt(input_text, number_of_questions, difficulty_level,language_lavel)


        # Pass the values to handle_prompt
        print(f"Selected language level: {language_lavel}")
        print(f"Input text: {input_text}")
        print(f"Selected difficulty level: {difficulty_level}")
        print(f"Number of questions: {number_of_questions}")
        print(f"Selected file path: {file_path}")
        dialog.accept()

    submit_button.clicked.connect(submit)
    layout.addWidget(submit_button)

    # Set layout to dialog
    dialog.setLayout(layout)
    
    # Show the popup dialog
    dialog.exec_()


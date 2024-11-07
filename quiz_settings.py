import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QFileDialog, QLabel, QComboBox, 
                            QSpinBox, QHBoxLayout, QFrame, QWidget)
from PyQt5.QtCore import Qt
from gpt import handle_prompt  # Make sure this import exists in your project

# Initialize the QApplication at the module level
if not QApplication.instance():
    app = QApplication(sys.argv)

class ModernDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Quiz Settings")
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
                min-width: 200px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
                min-width: 200px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#fileButton {
                background-color: #95a5a6;
            }
            QPushButton#fileButton:hover {
                background-color: #7f8c8d;
            }
            QFrame#settingsFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a frame for settings
        settings_frame = QFrame()
        settings_frame.setObjectName("settingsFrame")
        frame_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Create Quiz with AI")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        frame_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Content input section
        content_label = QLabel("Quiz Content")
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter your content here...")
        self.text_input.setMinimumHeight(120)
        frame_layout.addWidget(content_label)
        frame_layout.addWidget(self.text_input)
        
        # Create horizontal layout for difficulty and language
        settings_layout = QHBoxLayout()
        
        # Difficulty section
        difficulty_widget = QWidget()
        difficulty_layout = QVBoxLayout()
        difficulty_label = QLabel("Difficulty Level")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_combo)
        difficulty_widget.setLayout(difficulty_layout)
        settings_layout.addWidget(difficulty_widget)
        
        # Language section
        language_widget = QWidget()
        language_layout = QVBoxLayout()
        language_label = QLabel("Language")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["thai", "english"])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_widget.setLayout(language_layout)
        settings_layout.addWidget(language_widget)
        
        frame_layout.addLayout(settings_layout)
        
        # Questions settings
        questions_layout = QHBoxLayout()
        
        # Number of questions section
        num_questions_widget = QWidget()
        num_questions_layout = QVBoxLayout()
        num_questions_label = QLabel("Number of Questions")
        self.num_questions_input = QSpinBox()
        self.num_questions_input.setRange(1, 20)
        self.num_questions_input.setValue(5)  # Default value
        num_questions_layout.addWidget(num_questions_label)
        num_questions_layout.addWidget(self.num_questions_input)
        num_questions_widget.setLayout(num_questions_layout)
        questions_layout.addWidget(num_questions_widget)
        
        # Time per question section
        time_widget = QWidget()
        time_layout = QVBoxLayout()
        time_label = QLabel("Time per Question (seconds)")
        self.time_input = QSpinBox()
        self.time_input.setRange(5, 120)
        self.time_input.setValue(30)  # Default 30 seconds
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_input)
        time_widget.setLayout(time_layout)
        questions_layout.addWidget(time_widget)
        
        frame_layout.addLayout(questions_layout)
        
        # File selection
        self.file_path = ""
        file_button = QPushButton("Select File")
        file_button.setObjectName("fileButton")
        file_button.clicked.connect(self.select_file)
        frame_layout.addWidget(file_button)
        
        # Submit button
        submit_button = QPushButton("Create Quiz")
        submit_button.clicked.connect(self.submit)
        frame_layout.addWidget(submit_button)
        
        settings_frame.setLayout(frame_layout)
        main_layout.addWidget(settings_frame)
        self.setLayout(main_layout)
        
    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a File", "", "All Files (*)")
        if self.file_path:
            print(f"Selected file: {self.file_path}")
            
    def submit(self):
        input_text = self.text_input.toPlainText()
        language_level = self.language_combo.currentText()
        difficulty_level = self.difficulty_combo.currentText()
        number_of_questions = self.num_questions_input.value()
        countdown_time = self.time_input.value() * 1000  # Convert seconds to milliseconds
        
        # Save countdown time and other settings to a Python file
        with open('quiz_settings.py', 'w') as f:
            f.write('# Quiz Settings\n')
            f.write(f'COUNTDOWN_TIME = {countdown_time}  # Time in milliseconds\n')
            f.write(f'DIFFICULTY_LEVEL = "{difficulty_level}"\n')
            f.write(f'LANGUAGE_LEVEL = "{language_level}"\n')
            f.write(f'NUMBER_OF_QUESTIONS = {number_of_questions}\n')
        
        if self.file_path:
            handle_prompt(input_text, number_of_questions, 
                        difficulty_level, language_level)
        
        print(f"Settings saved to quiz_settings.py")
        self.accept()

def show_popup():
    dialog = ModernDialog()
    dialog.setFixedSize(600, 700)
    return dialog.exec_()

def initialize_qt():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    return QApplication.instance()

if __name__ == '__main__':
    app = initialize_qt()
    show_popup()
    sys.exit(app.exec_())
import os
import re
from flask import Flask, request, send_file

app = Flask(__name__)
# set upload folder to tmp
app.config['UPLOAD_FOLDER'] = '/tmp'

# Function to convert Aiken format to Blackboard tab-delimited format
def convert_aiken_to_blackboard(input_file, output_file):
  try:
    # Open the Aiken file for reading
    with open(input_file, 'r', encoding='utf-8') as aiken_file:
        aiken_text = aiken_file.read()
        
    # Initialize a list to store the Blackboard-formatted questions
    bb_questions = []
    
    # Split the Aiken text into lines
    lines = aiken_text.strip().split('\n')
    
    # Initialize variables to store question title and answer
    question_title = ""
    correct_answer_letter = ""
    choices = []
    questions = []

    # Process each line
    for line in lines:
        # Check for the "ANSWER:" marker
        if line.startswith("ANSWER:"):
          # Extract the answer letter
          correct_answer_letter = line.split(":")[1].strip()
          questions.append({
            "title": question_title,
            "answer": correct_answer_letter,
            "choices": choices
          })
          choices = []
        elif re.match(r'[A-Z]\)', line.strip()):
          choice = line.strip()
          choices.append(choice)
        else:
          question_title = line.strip()

    # Process the questions and format them into Blackboard tab-delimited lines
    bb_lines = []
    for question in questions:
      bb_question_type = 'MC'
      choices = []
      
      # Split the choices from the question stem
      for choice in question['choices']:
        choice_letter = choice[0]
        choice_text = choice[3:]
        correct_text = 'correct' if choice_letter == question['answer'] else 'incorrect'
        choices.append(f"{choice_text}\t{correct_text}")
      
      # Create the Blackboard tab-delimited line
      tab_escape_char = '\t'  # Replace with the desired escape character
      bb_line = f"{bb_question_type}\t{question['title']}\t{tab_escape_char.join(choices)}"
      
      bb_lines.append(bb_line)

    # Write the Blackboard-formatted questions to the output file
    with open(output_file, 'w', encoding='utf-8') as bb_file:
      for bb_line in bb_lines:
        bb_file.write(bb_line + '\n')

    print(f"Conversion complete. Results saved to {output_file}")
  except Exception as e:
    print(f"An error occurred: {str(e)}")

@app.route('/')
def home():
  return Flask.render_template('ui.html')

# API Endpoint Function
@app.route("/upload", methods=['POST'])
def get_file():
  # Get form submission file
  file = request.files['file']
  # Get form submission filename
  filename = file.filename
  # Get form submission file extension
  extension = filename.split('.')[1]
  # Check if file extension is .txt
  if extension == 'txt':
    # Save file to uploads folder
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Convert file to Blackboard format
    convert_aiken_to_blackboard(filename, filename + '_blackboard.txt')
    # Return file
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
  else:
    return 'File must be a .txt file'

def send_from_directory(upload_folder, filename):
  # Specify the path to the uploaded file
  file_path = os.path.join(upload_folder, filename)

  # Check if the file exists
  if os.path.exists(file_path):
    # Send the file as a response to the browser
    return send_file(file_path, as_attachment=True)
  else:
    return 'File not found'
  
if __name__ == '__main__':
  app.run()
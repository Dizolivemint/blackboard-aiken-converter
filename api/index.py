import os
import re
from flask import Flask, request, send_file, render_template

app = Flask(__name__)
# set upload folder to tmp
app.config['UPLOAD_FOLDER'] = '/tmp'

# Function to convert Aiken format to Blackboard tab-delimited format
def convert_aiken_to_blackboard(aiken_text, output_file):
  # try:
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
  # except Exception as e:
  #   print(f"An error occurred: {str(e)}")

@app.route('/')
def home():
  return render_template('ui.html')

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
    # Convert file to Blackboard format
    bb_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename[0:-4] + '_blackboard.txt')
    # Read file to text
    aiken_text = file.read().decode('utf-8')
    convert_aiken_to_blackboard(aiken_text, bb_filename)
    return 'Success'
  else:
    return 'File must be a .txt file'

@app.route('/download/<filename>')
def download_file(filename):
  filename = filename[0:-4] + '_blackboard.txt'

  # Specify the path to the uploaded file
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

  # Check if the file exists
  if os.path.exists(file_path):
    # Send the file as a response to the browser
    return send_file(file_path,
              download_name=filename, 
              mimetype='text/plain',
              as_attachment=True
            )
  else:
    return 'File not found'
  
if __name__ == '__main__':
  app.run()
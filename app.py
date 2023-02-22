import re
import yaml
import openai
from flask import Flask, render_template, request

# Load configuration from config.yml file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Set up OpenAI API credentials
openai.api_key = config['openai']['api_key']

# Set up Flask app
app = Flask(__name__)

# Define helper function to generate rewritten resume
def generate_resume(base_resume, job_description):
    # Call OpenAI API to generate rewritten resume
    response = openai.Completion.create(
        engine=config['openai']['model'],
        prompt=(f"Base-Resume: {base_resume}\n"
                "I want you to act as an experienced career adviser, I would like you to rewrite the Base-Resume provided above. Please tailor the Rewritten-Resume to the following Job-Description to maximize the chances of getting an interview. Include key words mentioned in the Job-Description."
                f"Job-Description: {job_description}\n\n"
                "Rewritten-Resume:"
        ),
        max_tokens=config['openai']['parameters']['max_tokens'],
        temperature=config['openai']['parameters']['temperature'],
        top_p=config['openai']['parameters']['top_p'],
        presence_penalty=config['openai']['parameters']['presence_penalty'],
        frequency_penalty=config['openai']['parameters']['frequency_penalty'],
        stop=config['openai']['parameters']['stop']
    )
    # Extract generated text from response and clean it up
    rewritten_resume = response.choices[0].text
    rewritten_resume = re.sub(r'[\n\r]+', '\n', rewritten_resume).strip()
    return rewritten_resume

# Define helper function to generate cover letter
def generate_cover_letter(rewritten_resume, job_description):
    # Call OpenAI API to generate cover letter
    response = openai.Completion.create(
        engine=config['openai']['model'],
        prompt=(f"I have a rewritten resume and a job description. I want to generate a cover letter that incorporates information from the rewritten resume. "
              f"Rewritten resume: {rewritten_resume}. "
              f"Job description: {job_description}. "
              "Please generate a cover letter."
        ),
        max_tokens=config['openai']['parameters']['max_tokens'],
        temperature=config['openai']['parameters']['temperature'],
        top_p=config['openai']['parameters']['top_p'],
        presence_penalty=config['openai']['parameters']['presence_penalty'],
        frequency_penalty=config['openai']['parameters']['frequency_penalty']
    )
    # Extract generated text from response and clean it up
    cover_letter = response.choices[0].text
    cover_letter = re.sub(r'[\n\r]+', '\n', cover_letter).strip()
    return cover_letter

# Define route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Define route for result page
@app.route('/result', methods=['POST'])
def result():
    # Get base resume and job description from request
    base_resume = request.form['base_resume']
    job_description = request.form['job_description']
    print(f"base_resume: {base_resume}")
    print(f"job_description: {job_description}")
    # Generate rewritten resume and cover letter
    rewritten_resume = generate_resume(base_resume, job_description)
    print(f"rewritten_resume: {rewritten_resume}")
    cover_letter = generate_cover_letter(rewritten_resume, job_description)
    print(f"cover_letter: {cover_letter}")
    # Render result page with rewritten resume and cover letter
    return render_template('result.html', rewritten_resume=rewritten_resume, cover_letter=cover_letter)

# Run the app
if __name__ == '__main__':
    app.run()

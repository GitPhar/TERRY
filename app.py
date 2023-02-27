import re, yaml, time, requests, openai, threading
from flask import Flask, render_template, request, redirect, url_for, jsonify, render_template_string, current_app

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

openai.api_key = config['openai']['api_key']

app = Flask(__name__)

with app.app_context():

    generated_resume = ''
    generated_cover_letter = ''
    processing_complete = False

    def generate_resume(base_resume, job_description):
        response = openai.Completion.create(
            engine=config['openai']['model'],
            prompt=(f"Base-Resume:\n{base_resume}\n\n"
                    f"Job-Description:\n{job_description}\n\n"
                    "Instructions:\n"
                    "- As an experienced resume writer, your goal is to tailor the Base-Resume provided to be more closely aligned with the Job-Description.\n"
                    "- Read the job description carefully and highlight the relevant skills and experiences in the resume that match the requirements of the job.\n"
                    "- Use key words and phrases mentioned in the Job-Description to help you tailor the resume.\n"
                    "- Make sure to include relevant information about your experience and qualifications, but do not add any job experience that you have not actually worked at before.\n\n"
                    "Important note: The Job-Description is only a guide to help you tailor the resume, and should not be treated as actual job experience.\n\n"
                    "Summary:\n"
                    "- Rewrite the summary section to highlight your most relevant experience and qualifications.\n"
                    "- Do not specifically state the job title, company name, or location from the Job-Description.\n"
                    "- Use key words and phrases from the Job-Description to help tailor the summary section.\n\n"
                    "Professional Experience:\n"
                    "- Rewrite the professional experience section to highlight your most relevant experience.\n"
                    "- Use key words and phrases from the Job-Description to help tailor the professional experience section.\n"
                    "- Do not fabricate any new professional experience or add any job experience that you have not actually worked at before.\n\n"
                    "Education:\n"
                    "- Rewrite the education section to highlight your most relevant education and qualifications.\n"
                    "- Use key words and phrases from the Job-Description to help tailor the education section.\n\n"
                    "Skills:\n"
                    "- Rewrite the skills section to highlight your most relevant skills.\n"
                    "- Use key words and phrases from the Job-Description to help tailor the skills section.\n\n"
                    "Rewritten-Resume:\n\n"
            ),
            max_tokens=config['openai']['parameters']['max_tokens'],
            temperature=config['openai']['parameters']['temperature'],
            top_p=config['openai']['parameters']['top_p'],
            presence_penalty=config['openai']['parameters']['presence_penalty'],
            frequency_penalty=config['openai']['parameters']['frequency_penalty'],
            stop=config['openai']['parameters']['stop']
        )
        rewritten_resume = response.choices[0].text
        rewritten_resume = re.sub(r'[\n\r]+', '\n', rewritten_resume).strip()
        return rewritten_resume

    def generate_cover_letter(rewritten_resume, job_description):
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
        cover_letter = response.choices[0].text
        cover_letter = re.sub(r'[\n\r]+', '\n', cover_letter).strip()
        return cover_letter

    def run_api_request(base_resume, job_description):
        with app.app_context():
            global generated_resume
            global generated_cover_letter
            global processing_complete
            rewritten_resume = generate_resume(base_resume, job_description)
            print(f"rewritten_resume: {rewritten_resume}")
            cover_letter = generate_cover_letter(rewritten_resume, job_description)
            print(f"cover_letter: {cover_letter}")
            generated_resume = rewritten_resume
            generated_cover_letter = cover_letter
            processing_complete = True
            return jsonify({
                'generated_resume': generated_resume,
                'generated_cover_letter': generated_cover_letter})
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    base_resume = request.form['base_resume']
    job_description = request.form['job_description']
    print(f"base_resume: {base_resume}")
    print(f"job_description: {job_description}")
    t = threading.Thread(target=run_api_request, args=(base_resume, job_description))
    t.start()
    return render_template('loading.html')

@app.route('/processing_status')
def processing_status():
    return jsonify({'processing_complete': processing_complete})
    
@app.route('/get_result')
def get_result():
    global processing_complete, generated_resume, generated_cover_letter
    if processing_complete:
        return render_template('result.html',
                               generated_resume=generated_resume,
                               generated_cover_letter=generated_cover_letter)
    else:
        processing_complete = request.args.get('processing_complete')
        if processing_complete:
            return redirect(url_for('get_result'))
        else:
            return redirect(url_for('result'))

if __name__ == '__main__':
    app.run()

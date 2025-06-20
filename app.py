from flask import Flask, render_template, request
from flask_cors import CORS
import subprocess, sys, os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins=["http://127.0.0.1:5500"])

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/choose-mode')
def choose_mode():
    return render_template('choose_mode.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    email = request.form['email']
    message = request.form['message']
    # You can save this to a database or send an email, etc.
    return redirect('/feedback')  # or render a thank you page

@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route('/community')
def community():
    return render_template('community.html')


@app.route('/quiz')
def quiz_home():
    return render_template('Quiz.html')

@app.route('/quiz/number')
def number_quiz():
    return render_template('numberQuiz.html')

@app.route('/quiz/alpha')
def alpha_quiz():
    return render_template('alphaQuiz.html')

@app.route('/quiz/phrase')
def phrase_quiz():
    return render_template('phraseQuiz.html')

@app.route('/phrases')
def phrases():
    return render_template('phrases.html')

@app.route('/Numerical')
def numerical():
    return render_template('Numerical.html')

@app.route('/alpha')
def alphabet_learning():
    return render_template('alpha.html')


def run_script(script_name):
    try:
        subprocess.Popen([sys.executable, script_name],
                         cwd=os.path.dirname(os.path.abspath(__file__)))
        return f"{script_name} started successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/start-alphabet', methods=['POST'])
def start_alphabet():
    return run_script('practiceAlphabet.py')

@app.route('/start-number', methods=['POST'])
def start_number():
    return run_script('practiceNumbers.py')

@app.route('/start-phrases', methods=['POST'])
def start_phrases():
    return run_script('practicePhrase.py')

if __name__ == '__main__':
    app.run(debug=True)

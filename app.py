from flask import Flask, render_template, request
import pickle
import pytesseract
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model & vectorizer
model = pickle.load(open('model/job_scam_model.pkl', 'rb'))
vectorizer = pickle.load(open('model/vectorizer.pkl', 'rb'))

# Common scam indicators
scam_keywords = ["earn", "no experience", "work from home", "click", "registration fee", "pay", "lottery", "easy money", "investment", "referral"]

def check_risky_keywords(text):
    found = [word for word in scam_keywords if word in text.lower()]
    return found

@app.route('/', methods=['GET', 'POST'])
def index():
    result = confidence = explanation = extracted_text = ""
    
    if request.method == 'POST':
        description = request.form.get('description', '')
        image = request.files.get('image')

        # If image uploaded, extract text
        if image and image.filename != '':
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)
            img = Image.open(path)
            extracted_text = pytesseract.image_to_string(img)
            description = extracted_text

        if description.strip() != "":
            input_vec = vectorizer.transform([description])
            prediction = model.predict(input_vec)[0]
            prob = model.predict_proba(input_vec)[0][prediction]
            risky = check_risky_keywords(description)

            result = "✅ Legit Job" if prediction == 0 else "❌ Possible Scam"
            confidence = round(prob * 100, 2)
            explanation = ", ".join(risky) if risky else "No obvious scam words found."

        return render_template('result.html', result=result, confidence=confidence, explanation=explanation, extracted=extracted_text)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

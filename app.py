from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pytesseract
from PIL import Image
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def redact_text_in_image(image_path, text_to_redact, filename):
    img = Image.open(image_path)
    
    extracted_text = pytesseract.image_to_string(img)

    text_to_redact_cleaned = list(text_to_redact.split(" "))

    img_cv = cv2.imread(image_path)
    
    boxes = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    n_boxes = len(boxes['text'])
    
    for i in range(n_boxes):
        word = boxes['text'][i].strip()
        
        word_cleaned = word.replace(' ', '')

        print(word_cleaned)
        
        if word_cleaned in text_to_redact_cleaned:
            x, y, w, h = boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i]
            img_cv = cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 0, 0), -1)
    
    redacted_image_path = './downloads/{}'.format(filename)
    cv2.imwrite(redacted_image_path, img_cv)
    print(f"Image redacted and saved to {redacted_image_path}")
    
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    text = request.form['text']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        redact_text_in_image(filepath, text, filename)
        return redirect(url_for('uploaded_file', filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):    
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

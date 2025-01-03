from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import qrcode
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory for uploaded images and generated QR codes
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file is in the request
        if 'image' not in request.files:
            return redirect(request.url)
        
        file = request.files['image']
        
        # Check for empty filename
        if file.filename == '':
            return redirect(request.url)
        
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"  # Ensure unique filenames
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Replace 'localhost' with your external IP address or the correct domain name
            img_url = f"http://10.0.14.142:5000/uploads/{unique_filename}"


            # Generate QR code linking to the uploaded image
            qr = qrcode.make(img_url)
            qr_filename = f"{uuid.uuid4()}_qr_code.png"
            qr_file_path = os.path.join(app.config['QR_FOLDER'], qr_filename)
            qr.save(qr_file_path)

            return render_template('index.html', filename=unique_filename, qr_code=qr_filename)

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/qr_codes/<filename>')
def qr_file(filename):
    return send_from_directory(app.config['QR_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

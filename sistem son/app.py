from flask import Flask, request, send_file, render_template
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "Hata: Dosya yüklenmemiş. Lütfen görsel yükleyiniz.", 400

    file = request.files['image']
    width = request.form.get('width')  # Kullanıcının belirttiği genişlik
    height = request.form.get('height')  # Kullanıcının belirttiği yükseklik
    keep_aspect_ratio = request.form.get('keep_aspect_ratio') == 'on'  # En-boy oranını koru seçeneği
    quality = int(request.form.get('quality', 90))  # Varsayılan kalite: 90

    if file.filename == '':
        return "Hata: Lütfen dosya seçiniz.", 400

    if not allowed_file(file.filename):
        return "Hata: Desteklenmeyen dosya tipi.", 400

    try:
        img = Image.open(file)
        original_width, original_height = img.size

        if keep_aspect_ratio:
            # En-boy oranını koruyarak genişlik veya yükseklik değerini hesapla
            if width:
                width = int(width)
                height = int(original_height * (width / original_width))
            elif height:
                height = int(height)
                width = int(original_width * (height / original_height))
        else:
            # En-boy oranını koruma seçeneği kapalıysa
            width = int(width) if width else original_width
            height = int(height) if height else original_height

        # Görüntüyü yeniden boyutlandır
        img = img.resize((width, height), Image.LANCZOS)

        # Görüntüyü sıkıştır ve kaydet
        output = BytesIO()
        img.save(output, format="JPEG", quality=quality)
        output.seek(0)

        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f"resized_{width}x{height}.jpg"
        )

    except Exception as e:
        return f"Hata: Bu görsel ile işlem yapılamıyor! Detaylar: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5001)

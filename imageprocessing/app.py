from flask import Flask, request, redirect, render_template, flash
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit max upload size to 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        flash('No file part')
        return redirect('/')
    
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect('/')
    
    if file and allowed_file(file.filename):
        try:
            # Save original image
            original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(original_image_path)

            # Open and get original image details
            img = Image.open(original_image_path)
            original_size = os.path.getsize(original_image_path)
            original_width, original_height = img.size
            
            # Compress the image
            compressed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{file.filename}")

            # Set the quality for compression
            quality_value = 85  # Adjust as needed to maintain quality
            img.save(compressed_image_path, format='JPEG', quality=quality_value, optimize=True)  # Adjust quality

            compressed_size = os.path.getsize(compressed_image_path)

            # Prepare statistics to send to the front end
            stats = {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'original_dimensions': (original_width, original_height),
                'compressed_dimensions': img.size  # Updated size after compression
            }
            
            # Render a template to display the images and statistics
            return render_template('stats.html', original_image=file.filename, compressed_image=f"compressed_{file.filename}", stats=stats)

        except Exception as e:
            flash(f'An error occurred: {str(e)}')
            return redirect('/')
    else:
        flash('Invalid file type')
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

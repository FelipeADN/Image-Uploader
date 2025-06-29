import os
import json
from flask import Flask, request, redirect, render_template, abort, url_for
from flask_limiter import Limiter
from werkzeug.utils import secure_filename

app = Flask(__name__)
limiter = Limiter(key_func=lambda: "global", app=app) # rate limiter

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_FOLDER_SIZE'] = 200 * 1024 * 1024  # 200 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
# Get whitelisted IPs from environment variable
try:
    app.config['WHITELISTED_IPS'] = json.loads(os.getenv("WHITELISTED_IPS", "[]"))
except json.JSONDecodeError:
    app.config['WHITELISTED_IPS'] = []


# upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check if the file extension is allowed
def allowed_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    return False

def check_folder_size():
    total_size = 0
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f)
        total_size += os.path.getsize(file_path)
    return total_size

def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        # take the original IP
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr

@app.before_request
def whitelist_ip():
    client_ip = get_client_ip()
    if client_ip not in app.config['WHITELISTED_IPS']:
        abort(403)

@app.route('/', methods=['POST', 'GET'])
@limiter.limit("50/hour")
def index():
    if request.method == "POST":
        if check_folder_size() >= app.config['MAX_FOLDER_SIZE']:
            return "Folder size limit exceeded, please delete some pictures", 507
        # check if post has a file
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file'] # get the file
        filename = secure_filename(file.filename) # secure the filename
        if filename != '' and allowed_extension(filename): # check if the file is allowed
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
        return redirect(request.url)

    # sends list of images to html
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Check if file is in the folder
    if filename not in os.listdir(app.config['UPLOAD_FOLDER']):
        abort(404)
    # Get secured file path
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('index'))

@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many requests. Please slow down.", 429

if __name__ == '__main__':
    app.run()
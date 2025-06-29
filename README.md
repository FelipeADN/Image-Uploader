# Image Uploader
Web application that allows uploading and deleting uploaded images.

Features:
- Upload .png, .jpg and .jpeg images
- Delete Images
- Sanitization of image name
- Whitelists IP
- Rate limits requests (100 / hour)
- Max folder size set to 200MB
- Max image size set to 2MB

dependencies:   
```
pip install Flask   
pip install Flask-Limiter
```

Developed with Python + Flask, HTML, and Bootstrap

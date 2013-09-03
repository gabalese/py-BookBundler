import sys
import os
from flask import Flask, request
from werkzeug.utils import secure_filename
import subprocess
from PIL import Image, ExifTags

from orientation import fix_orientation

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf',
                      'png',
                      'jpg',
                      'JPG',
                      'jpeg',
                      'gif',
                      'tif',
                      'tiff'}

app = Flask(__name__)
app.debug = False  # True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # else, return RequestEntityTooLarge


# logica di base del matching
def matches(file1, file2):
    lista1 = open(file1, "r").readlines()
    lista2 = open(file2, "r").readlines()

    for i in lista1:
        for v in lista2:
            if map(len, i.split(" ")) == map(len, v.split(" ")):
                if i == v:
                    return True
    else:
        return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    As http://flask.pocoo.org/docs/patterns/fileuploads/
    """
    if request.method == 'POST':
        sent_file = request.files['file']
        if sent_file and allowed_file(sent_file.filename):
            filename = secure_filename(sent_file.filename)

            sent_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            fix_orientation(os.path.join(app.config['UPLOAD_FOLDER'], filename), save_over=True)

            img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert('LA')

            img_name = os.tempnam("uploads/", "img_")+".png"
            img.save(img_name)

            temp = os.tempnam("uploads/", "tess_")

            command = ["tesseract", img_name, temp, "-l ita"]

            proc = subprocess.Popen(command)

            proc.wait()

            if matches("isola_target.txt", temp+".txt"):
                return "OOOOOK"
            else:
                return "NOOOOOO!!!"

    return '''
                <!doctype html>
                <title>Upload new File</title>
                <h1>Upload new File</h1>
                <form action="" method=post enctype=multipart/form-data>
                <p><input type=file name=file accept="image/*" capture="camera">
                <input type=submit value=Upload>
                </form>
                '''

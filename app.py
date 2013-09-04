import os
import subprocess
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

from PIL import Image

from matching import matches
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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # else, return RequestEntityTooLarge


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

            # escape malicious filename
            filename = secure_filename(os.tempnam()+sent_file.filename)

            # save image in upload folder
            sent_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # use PIL to fix orientation EXIF data for iPhone
            # TODO: is this valid for Android too?
            fix_orientation(os.path.join(app.config['UPLOAD_FOLDER'], filename), save_over=True)

            # open image and convert to BW
            img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert('LA')

            # save BW'd image on disk
            img_name = os.tempnam("uploads/", "img_")+".png"
            img.save(img_name)

            # temporary filename
            temp = os.tempnam("uploads/", "tess_")

            # prepare tesseract shell spawn
            command = ["tesseract", img_name, temp, "-l ita"]

            try:
                # spawn process, wait and intercept any non-zero exit status
                # mute stdin and stderr
                subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                return "Command unsuccessfull!"

            # temporary file context
            # replace with call to mongo
            with open("isola_target.txt") as f:
                source = f.readlines()

            # this one will last
            with open(temp+".txt") as g:
                destination = g.readlines()

            if matches(source, destination):  # the fixed file should be replaced with an array from dict
                # main OK response call
                return """
                        <!doctype html>
                        <html style="height: 100%">
                        <head>
                        <title>Success!</title>
                        </head>
                        <body style="height: 100%">
                        <p style="background-color: green; min-height: 100%;">&nbsp;</p>
                        </body>
                        </html>
                        """
            else:
                # main KO response call
                # render a fail template?
                return """
                        <!doctype html>
                        <html style="height: 100%">
                        <head>
                        <title>Fail!</title>
                        </head>
                        <body style="height: 100%">
                        <p style="background-color: red; min-height: 100%;">&nbsp;</p>
                        </body>
                        </html>
                        """
        else:
        # if not allowed_file ...
            return "NOPE."
            # I should throw a proper HTTP Status instead...

    if request.method == 'GET':
        return '''
                <!doctype html>
                <title>Upload new File</title>
                <h1>Upload new File</h1>
                <form action="" method=post enctype=multipart/form-data>
                <p><input type=file name=file accept="image/*" capture="camera">
                <input type=submit value=Upload>
                </form>
                '''

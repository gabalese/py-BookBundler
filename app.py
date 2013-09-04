import os
import subprocess
import urllib2
import json

from flask import Flask, request, render_template, Response
from werkzeug.utils import secure_filename

from PIL import Image

from matching import matches
from database import Database
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


def getremoteinfo(url):
    wget = urllib2.urlopen(url)
    result = json.JSONDecoder().decode(wget.read().encode("utf-8"))
    return result


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def cleanup(*args):
    map(os.remove, args)


@app.route("/", methods=['GET'])
def main():
    url = "http://www.edizionieo.it/jsonfeed.php?get=ebook&qt={qt}".format(qt=5)
    result = getremoteinfo(url)
    return render_template("list.html", list=result)


@app.route('/book/<int:isbn>', methods=['GET', 'POST'])
def upload_file(isbn):
    """
    As http://flask.pocoo.org/docs/patterns/fileuploads/
    """
    if request.method == 'POST':
        sent_file = request.files['file']
        if sent_file and allowed_file(sent_file.filename):

            # escape malicious filename, set random temporary filename [process-safer]
            filename = secure_filename(os.tempnam(None, "src_")+sent_file.filename)

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

            # result = mongo.books.findOne({"identifier":isbn})
            # source = result["identifier"]
            db = Database()
            destination = db.querydocument(isbn)["contents"]

            # this one will last
            with open(temp+".txt") as g:
                source = g.readlines()

            #return "LOL"
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
        try:
            url = "http://www.edizionieo.it/jsonfeed.php?search={isbn}".format(isbn=isbn)
            result = getremoteinfo(url)
        except urllib2.HTTPError:
            return Response("Nope.", 500)
        if not result:
            return Response("Nope.", 404)
        return render_template("single.html", book=result[0])

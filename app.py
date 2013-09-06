import os
import subprocess
import urllib2
import json

from flask import Flask, request, render_template, make_response
from werkzeug.utils import secure_filename

from PIL import Image, ImageFilter

from matching import matches
import database
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
    #url = "http://www.edizionieo.it/jsonfeed.php?get=ebook&qt={qt}".format(qt=5)
    baseurl = "http://www.edizionieo.it/jsonfeed.php?search={isbn}"
    db = database.Database()
    result = []
    for bid in db.availableidentifiers():
        info = getremoteinfo(baseurl.format(isbn=bid))
        result += info
    return render_template("list.html", list=result)


@app.route('/book/<int:isbn>', methods=['GET', 'POST'])
def upload_file(isbn):
    """
    Main program logic.
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
            try:
                fix_orientation(os.path.join(app.config['UPLOAD_FOLDER'], filename), save_over=True)
            except AttributeError:  # the picture does not have any EXIF. Move on, move on
                pass
            # open image and convert to BW
            img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert('LA')
            # enhance details
            img = img.filter(ImageFilter.DETAIL)
            # de-blurring
            img = img.filter(ImageFilter.SHARPEN)

            # save BW'd image on disk
            img_name = os.tempnam("uploads/", "img_")+".png"
            img.save(img_name)

            # temporary filename
            temp = os.tempnam("uploads/", "tess_")

            # prepare tesseract shell spawn
            command = ["tesseract", img_name, temp, "-l ita"]

            try:
                # spawn process and intercept any non-zero exit status
                # mute stdin and stderr
                ocr = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # the process continues
            except subprocess.CalledProcessError:
                return make_response(render_template("error.html"), 500)

            db = database.Database()
            try:
                destination = db.querydocument(isbn)["contents"]
            except database.EmptyResult:
                return make_response(render_template("error.html"), 404)

            # block while process terminates
            ocr.communicate()

            # this one will last
            with open(temp+".txt") as g:
                source = g.readlines()

            #return "LOL"
            print source
            if matches(source, destination):  # the fixed file should be replaced with an array from dict
                #cleanup(img_name, temp+".txt", os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # main OK response call
                return render_template("download.html")
            else:
                # main KO response call
                # render a fail template?
                #return source
                return render_template("nodownload.html")
        else:
            # if not allowed_file ...
            return make_response(render_template("error.html"), 500)

    if request.method == 'GET':
        try:
            url = "http://www.edizionieo.it/jsonfeed.php?search={isbn}".format(isbn=isbn)
            result = getremoteinfo(url)
        except urllib2.HTTPError:
            return make_response(render_template("error.html"), 500)
        if not result:
            return make_response(render_template("error.html"), 404)
        db = database.Database()
        pg = db.querydocument(isbn)["page"]
        return render_template("single.html", book=result[0], page=pg)

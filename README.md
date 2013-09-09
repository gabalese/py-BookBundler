py-BookBundler
=============

A python Flask webapp to enable publishers to bundle ebooks with paper books, providing that they can upload a picture of a page. The uploaded picture is ocr-ed with [tesseract-ocr](https://code.google.com/p/tesseract-ocr/) and if it matches the target page inserted by the operator a download page is shown. The algorithm in `matching.py` tries to guess if source and destination are similar enough, since a byte-perfect match is pure utopia.

API
---
The app exposes a RESTful API.

* `GET /`: returns a list of available publications.
* `GET /book/<isbn>`: presents the user with a form to upload a picture of the target page.
* `POST /book/<isbn>`: invoked by a form, takes the picture and spawns the ocr.
* `GET /new`:[basic-auth] presents the operator with a form to load data about a new publication.
* `POST /new/<isbn>` [basic-auth] creates the new publication.

Requirements
------------
* A working installation of [tesseract-ocr](https://code.google.com/p/tesseract-ocr/);
* tesseract-ocr Italian language files (or change the `app.py:91` and `app.py:181` language setting with `-l eng`).
* A mongodb instance running on the same server as py-BookBundler
* See `requirements.txt` for python dependencies.

License
-------
The py-BookBundler project is © 2013 by Gabriele Alese (gabriele@alese.it) / [http://www.alese.it](http://www.alese.it)
Released under a MIT license (see `LICENSE.txt` for details).
tesseract-ocr (not included) is available under Apache License 2.0 (see [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)).

Usage
-----

Unsurprisingly,
```bash
$ python server.py
```
will execute the flask app behind a basic http server on port 80 (requires root privileges; otherwise, change `server.py:7`). The test server is in NO WAY meant to be put in production, and you should wrap `app.py` in a real wsgi wrapper like gunicorn, gevent or tornado. YMMV.

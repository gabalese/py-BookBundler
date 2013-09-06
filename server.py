from app import app
# basic test server. Change with something more efficient like Tornado or Gunicorn in production

if __name__ == "__main__":
    app.debug = True  # lotta stuff on your stdout
    app.run(threaded=True, port=80, host='0.0.0.0')  # public reachable

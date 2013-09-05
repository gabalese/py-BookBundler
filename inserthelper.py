import database
import os

DIRECTORY = "pages/"

# main logic

if __name__ == "__main__":
    # test script
    db = database.Database()
    for path, dirs, files in os.walk(os.path.abspath(DIRECTORY)):
        for singular in files:
            if singular.endswith("txt"):
                filepath = os.path.abspath(os.path.join(path, singular))
                print db.inserttxt(filepath)
        else:
            print "DONE."

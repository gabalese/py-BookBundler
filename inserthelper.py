import database
import os

DIRECTORY = "pages/"

# helper script to add target contents to db
# could be refactored to accept a list of files via shell expansion

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

import database

# main logic

if __name__ == "__main__":
    # test script
    db = database.Database()

    print db.inserttxt("isola_target.txt")

    print db.querydocument("9788866322399")

import pymongo


class EmptyResult(Exception):
    pass


class DatabaseError(Exception):
    pass


class Database():
    """
    database class wrapper around MongoClient
    """
    def __init__(self, dbname="bookbundler", collection="books"):
        self.client = pymongo.MongoClient()
        self.db = self.client[dbname]
        self.collection = self.db[collection]

    def querydocument(self, param):
        query = {u"identifier": unicode(param)}
        result = self.collection.find_one(query)
        if result:
            return result
        else:
            raise EmptyResult

    def availableidentifiers(self, limit=None):
        query = {u"identifier": 1, u"_id": 0}
        result = self.collection.find({}, query)
        return [i["identifier"].encode("utf-8") for i in result]

    def inserttxt(self, txtfile):
        """
        Helper function to insert target contents in db via list of files
        Each file must have publication identifier in first line, target page number on second line,
        then

        :param txtfile: file
        :return: object_id
        """
        with open(txtfile) as f:
            try:
                txt = f.readlines()
            except Exception:
                raise RuntimeError
            identifier = txt[0].rstrip()
            page = txt[1].rstrip()
            contents = txt[2:]

            insert = {"identifier": identifier, "page": page, "contents": contents}

            return self.collection.save(insert)

    def insertreferencepage(self, identifier, page, contents):
        return self.collection.save({"identifier": identifier, "page": page, "contents": contents})

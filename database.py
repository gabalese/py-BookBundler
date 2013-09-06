import pymongo


class EmptyResult(Exception):
    pass


class DatabaseError(Exception):
    pass


class Database():
    def __init__(self, dbname="default", collection="books"):
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
        with open(txtfile) as f:
            txt = f.readlines()
            identifier = txt[0].rstrip()
            page = txt[1].rstrip()
            contents = txt[2:]

            insert = {"identifier": identifier, "page": page, "contents": contents}

            return self.collection.save(insert)

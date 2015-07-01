# Pseudo session-store aiming at sharing authentication and
# identification between the Django app and external apps.
import pymongo

CONFIG = {
    'database': 'cocosession',
}

ATTRIBUTES = ('cookie', 'username', 'userid')
class SessionGateway(object):
    def __init__(self):
        self.connection = pymongo.MongoClient("localhost", 27017)
        self.db = self.connection[CONFIG['database']]
        self.collection = self.db['session']

    def get_session(self, **kwargs):
        """Get session data for a given cookie/username/userid.

        Pass either parameter as named parameter.
        """
        return self.collection.find_one({ k: v
                                          for k, v in kwargs.iteritems()
                                          if v and k in ATTRIBUTES })

    def store_session(self, info):
        if all(info.get(k) for k in ATTRIBUTES):
            self.collection.save(info)
        else:
            raise Exception("Invalid session data")

    def delete_session(self, cookie):
        self.collection.remove({ 'cookie': cookie })


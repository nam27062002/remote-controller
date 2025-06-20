import firebase_admin
from firebase_admin import credentials, db, initialize_app

class FirebaseController:
    def __init__(self,
                 db_url = "https://remote-controller-356c1-default-rtdb.asia-southeast1.firebasedatabase.app/",
                 cred_path="../Firebase/service-account-key.json"):
        self.cred_path = cred_path
        self.db_url = db_url
        self._initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.cred_path)
            initialize_app(cred, {
                'databaseURL': self.db_url
            })
            self._initialized = True

    @staticmethod
    def set_url(url: str):
        db.reference("server_url").set(url)

    @staticmethod
    def get_url() -> object:
        return db.reference("server_url").get()


# if __name__ == "__main__":
#     print(FirebaseController().get_url())
import firebase_admin
from firebase_admin import credentials, db
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://remote-controller-356c1-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ref = db.reference('/users')  # đường dẫn gốc
# ref.set({
#     'user1': {
#         'name': 'Alice',
#         'age': 25
#     },
#     'user2': {
#         'name': 'Bob',
#         'age': 30
#     }
# })

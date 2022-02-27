from google.cloud import firestore


# Useful class for dropping all data about collections and documents on Firestore
#
# USAGE:
# ref = db.collection('users').document(f'{email}').get()
# if ref.exists:
#     DeleteAllFirestore().delete_document(db.collection('users').document(f'{email}'))
#
class DeleteAllFirestore(object):
    def __init__(self, verbose=False):
        # Attention! 'GOOGLE_APPILCATION_CREDENTIALS' env variable must be setted.
        self.db = firestore.Client()
        self.verbose = verbose

    # Deletes collection and its content in a recursive way
    def delete_collection(self, coll_ref):
        docs = coll_ref.stream()
        deleted = 0
        for doc in docs:
            for collection in doc.reference.collections():
                self.delete_collection(collection)
            if self.verbose is True:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
            doc.reference.delete()
            deleted = deleted + 1
        if self.verbose is True:
            print("Total of documents deleted: ", deleted)

    # Deletes document and all its content
    def delete_document(self, doc):
        for collection in doc.collections():
            self.delete_collection(collection)
        doc.delete()


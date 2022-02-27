from flask_login import UserMixin
from api import Api

api = Api(verbose=True)


class User(UserMixin):
    def __init__(self, provider, email, name=None, image=None):
        self.provider = provider
        self.email = email
        self.name = name
        self.image = image

    # ATTENTION! If the user is not in Firestore DB, we create a new one.
    def get(self):
        user = api.get_user(email=self.email)
        if not user:
            print(f'Impossible to find user with EMAIL {self.email}. Creating a new one in Firestore DB ...')
            api.post_user(email=self.email, provider=self.provider, name=self.name, image=self.image)
            return api.get_user(email=self.email)
        else:
            # ATTENTION! We cannot allow to have different accounts with same email:
            #            it can be related only to one registered account.
            if self.provider == user['provider']:
                return user
            else:
                return None

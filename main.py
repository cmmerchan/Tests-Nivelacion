from models.user_credentials import User
from db.mongodb import MongoDB
from bson import ObjectId
from resources.multiple_users_handler import MultipleUsersHandler


def main():


    users_handler = MultipleUsersHandler(2, "errores.log")
    users_handler.run()
    #class="input question-input question-input-is-active

if __name__ == "__main__":
    main()

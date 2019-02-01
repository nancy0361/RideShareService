from models import Account


# input dict format:
# {
#     "name" : "Bob",
#     "password" : "1234",
#     "email" : "bob@duke.edu"
# }
def createAccount(info):
    newAccount = Account(user_name=info["name"], password=info["password"], email=info["email"])
    newAccount.save()


if __name__ == "__main__":
    info = {}
    info["name"] = "Bob"
    info["password"] = "1234"
    info["email"] = "bob@duke.edu"
    createAccount(info)
    pass

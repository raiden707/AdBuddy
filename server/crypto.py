from os import environ
import bcrypt

def encrypt(target):
    """
    Encrypts password
    """
    password = target.encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_password

def password_check(password, hashed_password):
    """
    Checks if password is correct
    """
    if bcrypt.checkpw(password, hashed_password):
        print("It matches")
    else:
        print("No match :(")
        
def test_crypto(password):
    
    hashed = encrypt(password)
    return password_check(password.encode('utf-8'),hashed)


    
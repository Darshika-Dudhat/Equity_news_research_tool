import os
from dotenv import load_dotenv

load_dotenv()

# Read from .env
usernames = os.getenv("USERNAMES","").split(',')
passwords = os.getenv("PASSWORDS","").split(',')

# Make sure both are equal length
if len(usernames) != len(passwords):
    raise ValueError("USERNAMES and PASSWORDS count do not match in .env")

# Create a dictionary for authorizatiom
# VALID_USERS = dict(zip(usernames, passwords))

USER_CREDENTIALS = dict(zip(usernames, passwords))

# print(VALID_USERS)
# print(USER_CREDENTIALS)
import os
from dotenv import load_dotenv

load_dotenv("./env")
github_token = os.getenv("GITHUB_TOKEN")
print(github_token)
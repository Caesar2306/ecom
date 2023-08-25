
import os
from dotenv import load_dotenv

# Load the dotenv file
load_dotenv()

def get_chat_gpt_api_key():
    return os.getenv('CHATGPT_API_KEY')

def get_backend_username():
    return os.getenv('BACKEND_USERNAME')

def get_rapid_api_key():
    return os.getenv('RAPID_API_KEY')

def get_rapid_api_host():
    return os.getenv('RAPID_API_HOST')

def get_testsystem_api():
    return os.getenv('TESTSYSTEM_API')

def get_testsystem_url():
    return os.getenv('TESTSYSTEM_URL')

def get_localsystem_api():
    return os.getenv('LOCALSYSTEM_API')

def get_localsystem_url():
    return os.getenv('LOCALSYSTEM_URL')
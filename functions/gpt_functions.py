import openai
import time
from datetime import datetime

MAX_RETRIES = 15
SLEEP_TIME = 5
ERROR_LOG = f"error_log_{datetime.now().strftime('%Y%m%d')}.txt"

class ChatGPT:
    def __init__(self, api_key):
        openai.api_key = api_key

    def make_response(self, system_message, user_message):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        retries = MAX_RETRIES
        while retries > 0:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.75,
                    max_tokens=250,
                    top_p=1,
                    frequency_penalty=0.3,
                    presence_penalty=0
                )
                response_message = response.choices[0].message['content'].strip()
                return response_message
            except openai.error.RateLimitError:
                print(f"Rate limit error. Retrying in {SLEEP_TIME} seconds...")
                retries -= 1
                time.sleep(SLEEP_TIME)
            except openai.error.APIError as e:
                print(f"API error: {e}.")
                return str(e)
            except Exception as e:
                print(f"Unexpected error: {e}.")
                self._save_to_error_log(str(e))
                return str(e)

    @staticmethod
    def _save_to_error_log(error):
        with open(ERROR_LOG, 'a') as error_log_file:
            error_log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : {error}\n")

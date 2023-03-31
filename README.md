# SOPHIE

Sophie is a chatbot that you can speak with and she will speak back using several APIs and some custom prompting to GPT. It is also possible for this chatbot to speak with varying tones and emotions.

## How to run

1. Clone this repository <br>
    ```git clone https://github.com/caelanhadley/sophie-gpt.git```

2. Install the requirements <br>
    ```pip install -r requirements.txt```

3. Create OpenAI and Microsoft Azure accounts
   - OpenAI account should be straight forward.
   - The Azure account is more complicated, after creating an account you will needs to create a speech resource.
   - After creating a speech resource go to you overview to access your API key and region.<br>
4. After you have created your accounts you need to put your API keys into these three files:<br>
    ```key_azure``` your Microsoft Azure API key.<br>
    ```key_region``` the region your azure service is located. (example: "eastus")<br>
    ```key_openai``` your OpenAI API key.<br>
5. Run the program (Use command prompt to excute)<br>
    ```python main.py```<br>
6. To begin the conversation say "hey sophie" after that the conversation will not require you to say this phrase. The conversation in its current state will run until you terminate the program.

## Common Problems

- Audio is not recording
  - Check to make sure that your microphone is the default microphone through your computer's settings.
  - Make sure your microphone is not muted and the recording volume is turned up.
- API is not working / Requests not working
  - if the requests to the API are not working make sure that your api keys are correct in the ```key_azure```, ```key_region```, and ```key_openai``` files.

- Having other issues?
  - Open a ticket on the github and I'll try to help you toubleshoot any issues and bugs you encounter.

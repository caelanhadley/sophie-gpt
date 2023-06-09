# SOPHIE

&nbsp;&nbsp;&nbsp;&nbsp;Sophie is a chatbot that you can speak with! Using several APIs and through some custom prompting, this chatbot can speak audibly with varying tones and emotions. Sophie can sound happy, mad, sad, and more within the same response. If you want to see an example, ask Sophie to tell you a story that starts sad, becomes angering, and ends happily. I hope this program makes AI more accessible and engaging for you! You're free to modify, copy, and redistribute this code, so please tinker with it and see what you can create!

## How to run

1. Clone this repository. <br>
    ```git clone https://github.com/caelanhadley/sophie-gpt.git```

2. Install the requirements.<br>
    ```pip install -r requirements.txt```

3. Create OpenAI and Microsoft Azure accounts.
   - OpenAI account should be straightforward.
   - The Azure account is more complicated, after creating an account you will need to create a speech service.
   - This should create a resource group with a speech service in it.
   - Go to the overview in your newly created speech service to access your API key and region.<br>
4. After you have created your accounts you need to put your API keys into these three files:<br>
    ```key_azure``` your Microsoft Azure API key.<br>
    ```key_region``` the region your azure service is located. (example: "eastus")<br>
    ```key_openai``` your OpenAI API key.<br>
5. Run the program.<br>
    ```python main.py```<br>
6. To begin the conversation say "hey sophie" after that the conversation will not require you to say this phrase. The conversation in its current state will run until you terminate the program.

## Common Problems

- Audio is not recording
  - Check to make sure that your microphone is the default microphone through your computer's settings.
  - Make sure your microphone is not muted and the recording volume is turned up.
- API is not working / Requests not working
  - if the requests to the API are not working make sure that your api keys are correct in the ```key_azure```, ```key_region```, and ```key_openai``` files.

- Having other issues?
  - Open a ticket on github and I'll try to help you toubleshoot any issues and bugs you encounter.
  - If you are having an issue with the API keys remember **NEVER** publicly post or share your API keys!

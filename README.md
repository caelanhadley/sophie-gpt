# SOPHIE

Sophie is a chatbot that you can speak with and she will speak back using several APIs and some custom prompting to GPT it is also possible for this chatbot to speak with varying tones.

## How to run

1. Clone this repository <br>
    ```git clone https://github.com/caelanhadley/sophie-gpt.git```

2. Install the requirements <br>
    ```pip install -r requirements.txt```

3. Create OpenAI and Microsoft Azure accounts
   - OpenAI account should be straight forward.
   - The Azure account is more complicated, after creating an account you will needs to create a speech resource.
   - After creating a speech resource go to your overview to access your API key and region.<br>
4. After you have created your accounts you need to put your API keys into these three files:<br>
    ```key_azure``` your Microsoft Azure API key.<br>
    ```key_region``` the region your azure service is located. (example: "eastus")<br>
    ```key_openai``` your OpenAI API key.<br>
5. Run the program (Use command prompt to excute)<br>
    ```python main.py```


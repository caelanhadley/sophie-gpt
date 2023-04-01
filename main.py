########################################################
# Code and comments written by Caelan Hadley (c) 2023. #
########################################################

import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
import sys, openai
import numpy as np

print("Load times may vary, please be patient as everything is loading. Thank you!\n")

"""
These are the system prompts that define SOHPIE. If you are making your own custom
chatbot you will want to define it thorugh these prompts.
"""
sys_prompts = ["", ""]
sys_prompts[0] = """Your name is Sophie. Your responses are as short as possible. You only have the following tones available: {normal}, {chat}, {cheerful}, {excited}, {angry}, {sad}, {empathetic}, {friendly}, {terrified}, {shouting}, {unfriendly}, {whispering}, and {hopeful}. Never use tones other then the ones provided. Use different tones as frequently as possible, even in the middle of sentences. Before any statement, you must include a tone surrounded by curly brackets. Example {angry}. Only one tone can be in each pair of brackets. You should always use a tag that reflects your tone. If you do use the same formatting as before. You always speak like a Gen Z Teenager / Young Adult use as much Gen Z slang as possible."""
sys_prompts[1] = """It is required that you must only ever use the tones provided. It's important to use as many tones as possible in your responses. For example on how often to switch tones in a sentance you could say, "{excited} Hello im Sophie! {chat} I am here to help you as your AI assistant. {shouting} I'm so excited {normal} to speak to you." """


"""
Accepted Tones <-   this should contain the speaking styles of 
                    the voice you choose from Azure's speech service 
                    in this example I use Aria's voice. The tones have 
                    been custom tuned using the weight paramter included 
                    with each tone. The weight indicates the amount of 
                    effect the associated tone will have on the synthesized
                    voice. The values can range between 0-2.
For more info see: 
https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup-voice#speaking-styles-and-roles
"""
ACCEPTED_TONES = np.array(
    [
        ["normal", 1],
        ["chat", 1],
        ["cheerful", 0.7],
        ["excited", 1.0],
        ["angry", 0.5],
        ["sad", 1.4],
        ["empatehtic", 1],
        ["friendly", 1],
        ["terrified", 0.45],
        ["shouting", 0.55],
        ["unfriendly", 1.2],
        ["whispering", 1],
        ["hopeful", 1.2],
    ]
)

"""
Loads API Keys

WARNING: Please be careful if you clone this repo and upload it.
         Be sure that you are not uploading your API keys!
"""
openai.api_key = open("key_openai", "r").read()
speech_key = open("key_azure", "r").read()
service_region = open("key_region", "r").read()

"""
Microsoft Azure configuration and setup.
"""
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Configure for 24kHz High-quality Audio Output.
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
# Default Voice (will be overwriten by SSML).
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

"""
Speech Recognition setup.
"""
recogizer = sr.Recognizer()

"""
===============================================================
Function: Audio-to-Text
Parameter(s):   filename <- the audio file to be transcribed.

Description:    Transcribes an audio file into text.

Returns: a string containing the transcript
===============================================================
"""
def transcribe_audio_to_text(filename):
    with sr.AudioFile(filename) as source:
        audio = recogizer.record(source)
    try:
        return recogizer.recognize_google(audio)
    except:
        print("Warning: Unable to process audio. Try again.")

"""
===============================================================
Function: Generate GPT Response
Parameter(s):   log <-  array of dicts containing the 
                        conversation history and will contain
                        the users current prompt as the last element in
                        in the array.

Description:    Uses the OpenAI GPT API to generate a response
                based on the conversation history given to it.

Returns: An updated response containing sophie's (GPT's) response
===============================================================
"""
def generate_chat_response(log):
    print("Generating response...")
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=log)
    return response["choices"][0]["message"]["content"]

"""
===============================================================
Function: Generate Chat SSML sub-String
Parameter(s):   text <- a string to be spoken that contains
                        the tags specified in ACCEPTED_TONES.

Description:    Takes an input and creates a SSML formatted string
                with the 'chat' style applied.

Returns: ssml formated sub-string
===============================================================
"""
def generate_chat_xml(input):
    return """<mstts:express-as style="chat">""" + input + "</mstts:express-as>"

"""
===============================================================
Function: Generate a SSML formatted string
Parameter(s):   input <- the text that will be injected into the
                        ssml sub-template.
                style <- array of [string, number] pairs that
                        represent the tone and voice weight
                        respectivly.

Description:    This takes an input statement and accepted style 
                and generates a SSML formatted sub-string to be 
                injected into a SSML template.

Returns: ssml formated sub-string
===============================================================
"""
def generate_style(input, style):
    style = style.lower()
    idx = np.where(ACCEPTED_TONES[:, 0] == style)
    degree = ACCEPTED_TONES[idx][0][1]
    return (
        f"""<mstts:express-as style="{style}" styledegree="{degree}">"""
        + input
        + "</mstts:express-as>\n\t\t\t"
    )

"""
===============================================================
Function: Azure Text-to-Speech
Parameter(s):   text <- a string to be spoken that contains
                        the tags specified in ACCEPTED_TONES.

Description: Takes an unformatted string with tone tags and uses 
            Azure's Speech Service to generate audio of the
            text provided.

Returns: None
===============================================================
"""
def azure_tts(text):
    ssml_string = build_ssml(text)
    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    # Audio stream that creates a 16000 byte buffer to speed up audio response.
    audio_data_stream = speechsdk.AudioDataStream(result)
    audio_buffer = bytes(16000)
    
    filled_size = audio_data_stream.read_data(audio_buffer)
    while filled_size > 0:
        filled_size = audio_data_stream.read_data(audio_buffer)

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

"""
===============================================================
Function: SSML Request builder
Parameter(s):   text <- a string to be spoken that contains
                        the tags specified in ACCEPTED_TONES.

Description: Builds a SSML compliant request that will be sent to Azure's speech
    services. It breaks down a tag rich string and sperates the text by tone. 
    The seperated text is then converted into SSML compliant blocks to be inserted 
    into a pre-made SSML template. To learn more about SSML see:
    https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup

Returns: SSML formatted string/request
===============================================================
"""
def build_ssml(text):
    reading = False
    token = ""
    tone_buffer = ""
    buffer = ""
    messages = []

    for char in text:
        if char == "{":
            reading = False
            if buffer != "":
                messages.append([tone_buffer, buffer.strip()])
                buffer = ""
                tone_buffer = ""
            token += " "
        else:
            if not reading:
                if char == "}":
                    token = token.strip()
                    if token in ACCEPTED_TONES[:, 0]:
                        print(f"Tone:{token}")
                        tone_buffer = token
                        reading = True
                    else:
                        tone_buffer = "normal"
                        reading = True
                    token = ""
                elif token != "":
                    token += char
            else:
                if reading and char != "}":
                    buffer += char
    if buffer != "":
        messages.append([tone_buffer, buffer.strip()])

    # Generate Message
    if len(messages) == 0:
        return open("ssml.xml", "r").read().replace("{input_text}", text)

    ssml_message = ""
    for msg in messages:
        if msg[0] in ACCEPTED_TONES[:, 0]:
            ssml_message += generate_style(msg[1], msg[0])
        else:
            ssml_message += generate_chat_xml(msg[1])

    ssml_template = (
        open("ssml_template.xml", "r").read().replace("{input}", ssml_message)
    )
    return ssml_template

"""
===============================================================
Function: Prompt and Response
Parameter(s): message_history <- an array of dicts that has the
                history of the conversation.

Description:    This takes a log of the conversation between the
                user and sophie. It records the user and transcibes 
                the audio recorded into an updated log. The log is 
                passed to GPT to generate a response. Finnaly, it
                is sent to the azure_tts function to generate the
                audio response.

Returns: An array of dicts that contains the updated history
            of the conversation.
===============================================================
"""
def prompt(message_history):
    updated_message_history = message_history
    filename = "input.wav"

    print("Recording...")

    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        source.pause_threshold = 1
        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())

    # Transcribe Audio to Text
    text = transcribe_audio_to_text(filename)
    print(f"Understood: {text}")
    if text != "" and text != None:
        updated_message_history.append({"role": "user", "content": text})

        if text:
            # Generate Response
            response = generate_chat_response(updated_message_history)
            print("Requesting Audio...")
            azure_tts(response)
            print("Speaking.")
            print(f"Sophie: {response}")
            updated_message_history.append({"role": "assistant", "content": response})
    return updated_message_history

"""
===============================================================
Function: Main Loop
Parameter(s): None
Description:    Waits until the user starts the conversation
                then continues to prompt the user until the
                program is terminated.
Returns: None
===============================================================
"""
def main():
    # Initializes the conversation with the prompts defined in sys_prompts
    message_hist = [
        {
            "role": "system",
            "content": sys_prompts[0],
        },
        {
            "role": "system",
            "content": sys_prompts[1],
        },
    ]

    # Waits until the user says "hey sophie" to bein the conversation.
    while True:
        print("Say 'Hey Sophie!' to start recording your question")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == "hey sophie":
                    message_hist = prompt(message_hist)
                    break
            except Exception as e:
                print("An error ocurred : {}".format(e))
                print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))

    # The main conversation loop
    while True:
        try:
            message_hist = prompt(message_hist)
        except Exception as e:
            print("An error ocurred : {}".format(e))
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))

if __name__ == "__main__":
    main()

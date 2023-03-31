########################################################
# Code and comments written by Caelan Hadley (c) 2023. #
########################################################
# NOTE: For this program to work you must include 3
#   files.
#   > Azure API key containing your API key,
#   > Region key that is the region where your service
#   is being hosted.
#   > OpenAI API key.
# The files that should be included respectivly are:
#   > key_azure
#   > key_region
#   > key_openai
########################################################
print("Load times may vary, please be patient as everything is loading. Thank you!\n")

sys_prompts = ["", ""]
sys_prompts[0] = """Your name is Sophie. Your responses are as short as possible. You only have the following tones available: normal, chat, cheerful, excited, angry, sad, empathetic, friendly, terrified, shouting, unfriendly, whispering, and hopeful. Never use tones other then the ones provided. Always use as many emotions , even in between sentences. Before any statement, you must include a tone surrounded by curly brackets. Example {angry}. You must change the tone at any point in your response and it is expected to use more than one tone but not necessary. You should always use a tag that reflects your tone. If you do use the same formatting as before. You always speak like a Gen Z Teenager / Young Adult."""
sys_prompts[0] = """Your name is Sophie. Your responses are as short as possible. You only have the following tones available: {normal}, {chat}, {cheerful}, {excited}, {angry}, {sad}, {empathetic}, {friendly}, {terrified}, {shouting}, {unfriendly}, {whispering}, and {hopeful}. Never use tones other then the ones provided. Use different tones as frequently as possible, even in the middle of sentences. Before any statement, you must include a tone surrounded by curly brackets. Example {angry}. Only one tone can be in each pair of brackets. You should always use a tag that reflects your tone. If you do use the same formatting as before. You always speak like a Gen Z Teenager / Young Adult use as much Gen Z slang as possible."""
sys_prompts[1] = """It is required that you must only ever use the tones provided. It's important to use as many tones as possible in your responses. For example on how often to switch tones in a sentance you could say, "{excited} Hello im Sophie! {chat} I am here to help you as your AI assistant. {shouting} I'm so excited {normal} to speak to you." """
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
import sys, openai
import numpy as np

# Accepted tone tokens - this should contain the
#       speaking styles of the voice you choose
#       in this example I use Aria's voice on Azure.
#       The tones have been fine tuned using the
#       weight paramter included with each tone.
#
# See for more info: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup-voice#speaking-styles-and-roles
ACCEPTED_TOKENS = np.array(
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

# OpenAI API Key
openai.api_key = open("key_openai", "r").read()

# Azure API Key and Region
speech_key = open("key_azure", "r").read()
service_region = open("key_region", "r").read()

# Azure Set-Up
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# 24kHz High-quality Audio Output
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
)

# Voice Config (will be overwriten by ssml)
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

# Speech Recognition Recognizer Object
recogizer = sr.Recognizer()

# Audio file to text
def transcribe_audio_to_text(filename):
    with sr.AudioFile(filename) as source:
        audio = recogizer.record(source)
    try:
        return recogizer.recognize_google(audio)
    except:
        print("Warning: Unable to process audio. Try again.")


# Gpt-3 Prompt Request
def generate_chat_response(log):
    print("Generating response...")
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=log)
    return response["choices"][0]["message"]["content"]


# Text Completion (deprecated)
def generate_response(prompt):
    repsonse = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return repsonse["choices"][0]["text"]


# SSML Formating -> Angry (deprecated)
def generate_angry_xml(input):
    return (
        """<mstts:express-as style="angry" styledegree="0.45">"""
        + input
        + "</mstts:express-as>"
    )


# SSML Formating -> Chat (deprecated)
def generate_chat_xml(input):
    return """<mstts:express-as style="chat">""" + input + "</mstts:express-as>"


# SSML Formating -> Sad (deprecated)
def generate_sad_xml(input):
    return generate_style(input, style="sad")


# SSML Formating, takes an input statemnt and accepted style and
# generates XML query code to be injected into an SSML template.
# I have added enough functionality to control the voice style
# and voice weights. If you would like to add further functionality
# see the SSML formating page for Azure voices.
def generate_style(input, style):
    style = style.lower()
    idx = np.where(ACCEPTED_TOKENS[:, 0] == style)
    degree = ACCEPTED_TOKENS[idx][0][1]
    return (
        f"""<mstts:express-as style="{style}" styledegree="{degree}">"""
        + input
        + "</mstts:express-as>\n\t\t\t"
    )


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


# SSML Query builder
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
                    if token in ACCEPTED_TOKENS[:, 0]:
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
        if msg[0] in ACCEPTED_TOKENS[:, 0]:
            ssml_message += generate_style(msg[1], msg[0])
        else:
            ssml_message += generate_chat_xml(msg[1])

    ssml_template = (
        open("ssml_template.xml", "r").read().replace("{input}", ssml_message)
    )
    return ssml_template


def prompt(message_history):
    log = message_history
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
        log.append({"role": "user", "content": text})

        if text:
            # Generate Response
            response = generate_chat_response(log)
            print("Requesting Audio...")
            azure_tts(response)
            print("Speaking.")
            print(f"Sophie: {response}")
            log.append({"role": "assistant", "content": response})
    return log


def main():
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
    while True:
        try:
            message_hist = prompt(message_hist)
        except Exception as e:
            print("An error ocurred : {}".format(e))
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


if __name__ == "__main__":
    main()

import os
import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclib as m
from dotenv import load_dotenv
import requests
from google import genai
from google.genai import types

load_dotenv()
news = os.getenv("news")
gemini_client = genai.Client(api_key=os.getenv("gemini"))   # .env key named "gemini"

recogniser = sr.Recognizer()


def speak(text):
    """Fresh engine each call — fixes macOS pyttsx3 speaking only one line."""
    print("Joker:", text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def aiProcess(command):
    """Send any general question to Gemini and return a short answer."""
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=command,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a virtual assistant named Joker, skilled in general "
                    "tasks like Alexa and Google. Answer in 2-3 short sentences."
                ),
            ),
        )
        return response.text.strip()
    except Exception as e:
        print("AI error:", e)
        return "Sorry, I couldn't reach my brain right now."


def process_command(command):
    command = command.lower()

    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open facebook" in command:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")

    elif "open twitter" in command:
        speak("Opening Twitter")
        webbrowser.open("https://www.twitter.com")

    elif "open instagram" in command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com")

    elif "open gmail" in command:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")

    elif command.startswith("play "):
        song = command.split("play ", 1)[1].strip()
        if song in m.music:
            speak(f"Playing {song}")
            webbrowser.open(m.music[song])
        else:
            speak(f"Sorry, I don't have {song} in my music library.")

    elif "news" in command:
        speak("Fetching the latest news headlines...")
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            if not articles:
                speak("I couldn't find any news right now.")
            else:
                for i, article in enumerate(articles[:5], 1):
                    speak(f"Headline {i}: {article['title']}")
        else:
            speak("Sorry, the news service returned an error.")
            print(data)

    else:
        # Any other command → ask Gemini
        answer = aiProcess(command)
        speak(answer)


def joker_mode():
    """
    Joker stays active and continuously listens for commands.
    Saying 'stop' exits Joker mode and returns to wake-word listening.
    """
    speak("Yes, how can I help you?")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n🎤 Joker Listening...")
                audio = recogniser.listen(source, timeout=5, phrase_time_limit=5)

            command = recogniser.recognize_google(audio)
            print("You:", command)

            if "stop" in command.lower():
                speak("Okay, going back to sleep.")
                break

            process_command(command)

        except sr.WaitTimeoutError:
            print("No command heard...")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
        except sr.RequestError as e:
            print("Speech recognition error:", e)


if __name__ == "__main__":
    speak("Initializing speech recognition")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n👂 Listening for 'Joker'...")
                audio = recogniser.listen(source, timeout=5, phrase_time_limit=3)

            word = recogniser.recognize_google(audio)
            print("Heard:", word)

            if "joker" in word.lower():
                joker_mode()

        except sr.WaitTimeoutError:
            print("No wake word detected...")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print("Speech recognition error:", e)
        except KeyboardInterrupt:
            print("\nJoker shutting down...")
            break
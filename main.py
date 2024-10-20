from flask import Flask, jsonify, render_template, request
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import openai
import pyautogui
import subprocess
import pygame
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import requests
import time
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import face_recognition
import cv2
import numpy as np
import os
import cv2
import face_recognition
import numpy as np
import datetime
import time
import pyautogui
import subprocess
from pytesseract import image_to_string
from PIL import ImageGrab

app = Flask(__name__)


# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set to a female voice (optional)

# Initialize pygame mixer
pygame.mixer.init()

SPOTIFY_CLIENT_ID = '8386f0e6c2604b09965ed6d753546159'
SPOTIFY_CLIENT_SECRET = 'a914794fc9004b5cb6f7857fc083bac6'
REDIRECT_URI = 'http://localhost:8888/callback'

# Scope to control playback and access user library
scope = 'user-read-playback-state,user-modify-playback-state'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Replace with your SerpAPI key and OpenAI API key if needed
SERPAPI_KEY = '5cd840ab0d4e6acca61c1382f9a51b2bab80a6ba6b8ae17c80f4266a78a608c2'  # Replace with your actual SerpAPI key
OPENAI_API_KEY = 'pwcMlXZbbrKdkjrMqE2hhjDxqXXy2H9PAsjRpyxC9Zn45YVSCkNYFI77YfaFwUq105HHmoC9NWT3BlbkFJYNUIiE9tlfHBoK8iaDOoBLl7NdLioTtlqvhNQ8JkloSkgPphK3xmUkIzByzKRzTJKagDlTV1cA'  # Replace with your actual OpenAI API key
openai.api_key = OPENAI_API_KEY

# File to store user data
data_file = 'user_data.json'
stored_face_encoding = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_command', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data.get('command', '')
    response_text = ''
    if command:
        response_text = handle_command(command)  # type: ignore # You can call your existing command processing function here

    return jsonify({'response': response_text})



# Load user data from JSON file
def load_user_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    return {"name": "", "nickname": "", "dob": ""}

# Save user data to JSON file
def save_user_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

# Function to convert text to speech
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Function to play sound
def play_sound():
    pygame.mixer.music.load('v1.mp3')  # Update with the correct path to your beep.mp3 file
    pygame.mixer.music.play()
    

# Function to capture voice commands
def take_command():
    command = ""  # Initialize command variable
    try:
        with sr.Microphone() as source:
            print('Listening...')
            play_sound()  # Call the sound function here
            listener.adjust_for_ambient_noise(source)  # Optional: reduce noise interference
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alexa' in command:
                command = command.replace('alexa', '')
            print(f"Command recognized: {command}")  # Debugging output to see what is captured
    except sr.UnknownValueError:
        talk("Sorry, I didn't catch that. Could you say it again?")
    except sr.RequestError:
        talk("I'm having trouble connecting to the recognition service.")
    except Exception as e:
        print(f"Error: {e}")  # Print the exception for troubleshooting
    return command
# Function to play a song on Spotify (for free accounts, return link instead)
def play_on_spotify(song):
    results = sp.search(q=song, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        track_link = track['external_urls']['spotify']
        talk(f"I found {track_name} by {artist_name}. You can listen to it on Spotify here: {track_link}")
    else:
        talk("Couldn't find the song on Spotify.")


"""def capture_and_encode_face():
    # Capture video from the webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        raise Exception("Could not open video device")

    # Read a single frame from the video capture
    ret, frame = video_capture.read()

    if not ret:
        raise Exception("Failed to capture frame from webcam")

    # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
    rgb_frame = frame[:, :, ::-1]

    # Detect the location of faces in the image
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) == 0:
        print("No face detected. Please capture your face again.")
        video_capture.release()
        return None

    # Get face encodings for the detected faces
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)

    # Release the capture device
    video_capture.release()

    # Return the first encoding if found
    if face_encodings:
        return face_encodings[0]
    else:
        print("No face encodings found. Please try again.")
        return None

def verify_face(known_face_encoding):
    Capture a face and verify it against the known encoding.
    video_capture = cv2.VideoCapture(0)
    while True:
        # Capture a single frame of video
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        print(f"Detected {len(face_locations)} face(s)")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)

        # Check if any face matches the known face
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
            if True in matches:
                print("Face verified successfully!")
                video_capture.release()
                cv2.destroyAllWindows()
                return True

        # Display the resulting frame
        cv2.imshow('Video - Press "q" to exit', frame)

        # Press 'q' to quit without verifying
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            return False

def main():
    # Check if we already have a saved face encoding
    known_face_file = "known_face.npy"

    if os.path.exists(known_face_file):
        known_face_encoding = np.load(known_face_file)
        print("Known face loaded.")
    else:
        print("No known face found. Please capture your face.")
        known_face_encoding = capture_and_encode_face()
        if known_face_encoding is not None:
            np.save(known_face_file, known_face_encoding)
            print("Face captured and saved for future verifications.")
        else:
            print("No face detected. Exiting.")
            return

    # Perform face verification before starting the assistant
    print("Verifying your face...")
    if verify_face(known_face_encoding):
        print("Welcome! Starting the voice assistant...")
        # Call your assistant's main function here
        # run_alexa() or any other start function
    else:
        print("Face not recognized. Exiting the program.")

if __name__ == "__main__":
    main()"""
# Google search function using SerpAPI
def google_search(query, location="us", language="en", safe_search="active"):
    try:
        search_params = {
            "engine": "google",
            "q": query,
            "location": location,
            "gl": location,  # Country code
            "hl": language,  # Language
            "safe": safe_search,
            "num": 1,  # Retrieve one result
            "api_key": SERPAPI_KEY  # Your SerpAPI key
        }
        search = GoogleSearch(search_params)
        results = search.get_dict()
        print(f"Search Parameters: {search_params}")  # Debugging output


        # Check if the response contains organic results
        if 'organic_results' in results and results['organic_results']:
            top_result = results['organic_results'][0]
            return top_result['link']  # Return the URL of the first result
        else:
            print("No relevant information found.") 
            print(f"Results: {results}")  # Debugging output
# Debug output
            return "No relevant information found."
    except Exception as e:
        print(f"Error: {e}")
        return "I encountered an issue while searching."

# Web scraping function to extract content from the first search result
def scrape_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs[:3]])  # Get the first 3 paragraphs
        return content if content else "Couldn't extract meaningful information from the page."
    except Exception as e:
        print(f"Error: {e}")
        return "Couldn't retrieve information from the web."

# Function to open applications
def open_application(app_name):
    app_dict = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
        "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
        "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
        "whatsapp": "start whatsapp:"  # Use 'start' command for WhatsApp
    }

    if app_name in app_dict:
        subprocess.Popen(app_dict[app_name], shell=True)  # Open the application using shell=True
        talk(f"Opening {app_name}.")
    else:
        talk("Sorry, I can't open that application.")

# Function to send a WhatsApp message
def send_whatsapp_message(contact, message):
    try:
        # Open WhatsApp
        open_application("whatsapp")
        time.sleep(10)  # Wait for WhatsApp to open

        # Type the contact name
        pyautogui.hotkey('ctrl', 'f')  # Open search
        time.sleep(1)
        pyautogui.typewrite(contact)  # Type the contact name
        time.sleep(2)  # Wait for the contact to appear
        
        # Use the arrow keys to navigate to the contact
        time.sleep(1)  # Extra wait time
        pyautogui.press('down')  # Move down to select the first contact
        time.sleep(1)  # Wait for selection
        pyautogui.press('enter')  # Select the contact
        time.sleep(1)

        # Ensure the message input box is focused
        time.sleep(1)  # Wait for the message box to be ready

        # Type the message
        pyautogui.typewrite(message)  # Type the message
        pyautogui.press('enter')
        time.sleep(2)  # Send the message
        talk(f"Message sent to {contact}.")
    except Exception as e:
        talk("I couldn't send the message. Please check the contact name.")
        print(f"Error: {e}")
    
def read_last_two_messages_from(contact):
    try:
        # Open WhatsApp
        open_application("whatsapp")
        time.sleep(10)  # Wait for WhatsApp to open

        # Search for the contact
        pyautogui.hotkey('ctrl', 'f')  # Open search
        time.sleep(1)
        pyautogui.typewrite(contact)  # Type the contact name
        time.sleep(2)  # Wait for the contact to appear

        # Select the contact
        pyautogui.press('down')
        time.sleep(1)
        pyautogui.press('enter')  # Open the contact chat
        time.sleep(2)  # Wait for the chat to load

        # Scroll up to ensure we can see previous messages
        for _ in range(5):
            pyautogui.scroll(100)  # Adjust scroll amount if needed
            time.sleep(0.5)

        # Capture the screen
        time.sleep(1)  # Give time for scrolling
        screen = ImageGrab.grab()
        screen.save("screenshot.png")  # Save screenshot for debugging

        # Use OCR to read text from the screenshot
        text = image_to_string(screen)
        lines = text.split('\n')
        
        # Filter out empty lines and get the last two messages
        messages = [line for line in lines if line.strip()]
        last_two_messages = messages[-2:]  # Get the last two non-empty messages

        # Read the messages
        for message in last_two_messages:
            talk(f"Last message from {contact}: {message.strip()}")

    except Exception as e:
        talk("I couldn't read the messages. Please check the contact name.")
        print(f"Error: {e}")

# Function to change user name
def change_name(new_name):
    user_data = load_user_data()
    user_data['name'] = new_name
    save_user_data(user_data)
    talk(f"Your name has been updated to {new_name}.")

# Function to handle user information
def handle_user_info(command):
    user_data = load_user_data()
    
    if 'my name is' in command:
        name = command.replace('my name is', '').strip()
        change_name(name)
    
    elif 'my nickname is' in command:
        nickname = command.replace('my nickname is', '').strip()
        user_data['nickname'] = nickname
        save_user_data(user_data)
        talk(f"Your nickname has been set to {nickname}.")
    
    elif 'my birthday is' in command:
        dob = command.replace('my birthday is', '').strip()
        user_data['dob'] = dob
        save_user_data(user_data)
        talk(f"Your birthday has been set to {dob}.")
    
    elif 'what is my name' or 'whats my name' in command:
        name = user_data.get('name', 'not set')
        talk(f"Your name is {name}.")
    
    elif 'say my nickname' or 'whats my nickname' in command:
        nickname = user_data.get('nickname', 'not set')
        talk(f"Your nickname is {nickname}.")
    
    elif 'when is my birthday' in command:
        dob = user_data.get('dob', 'not set')
        talk(f"Your birthday is {dob}.")

# Main function to handle different commands and interactions
def run_alexa():
    command = take_command()
    print(command)
 

    if command == "":
        talk('I didn’t hear anything. Please say the command again.')
    elif 'youtube' in command:
        song = command.replace('youtube', '').strip()
        talk('Playing ' + song)
        pywhatkit.playonyt(song)
    elif 'spotify' in command:
        song = command.replace('spotify', '').strip()
        play_on_spotify(song)
        
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + current_time)
    elif 'define' in command:
        person = command.replace('define', '' ).strip()
        info = wikipedia.summary(person, 1)
        print(info)
        talk(info)
    elif 'date' in command:
        current_date = datetime.datetime.now().strftime('%B %d, %Y') 
        talk('Current date is ' + current_date)
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    elif 'ask' in command:
        
        query = command.replace('ask', '').strip()
        talk('Searching for information on the internet...')
        first_result = google_search(query)
        print(f"First result: {first_result}")  # Debug: Print the first URL found
        if "No relevant information found." not in first_result:
            content = scrape_webpage(first_result)
            print(f"Extracted content: {content}")
            talk(content)
        else:
            talk("I couldn't find relevant information.")
    elif 'open' in command:  # Check if the command is to open an application
        app_name = command.replace('open', '').strip()
        open_application(app_name)
        if 'open' in command:  # Check if the command is to open an application
            app_name = command.replace('open', '').strip()
            open_application(app_name)  # Open the application

    elif 'read last two messages from' in command:  # Command to read the last two messages from a contact
            contact = command.replace('read last two messages from', '').strip()  # Get the contact name
            read_last_two_messages_from(contact) 
    
    elif 'send message' in command:  # Command to send a WhatsApp message
        # Extract contact and message from the command
        parts = command.split("to")
        if len(parts) > 1:
            contact = parts[1].strip().split()[0]  # Get the contact name/number
            message = parts[1].strip().split(maxsplit=1)[1]  # Get the message part
            send_whatsapp_message(contact, message)
        else:
            talk("Please specify the contact and the message.")
    elif 'stop' in command or 'exit' in command:
        talk('Goodbye!')
        return False  # Return False to break the loop
    else:
        # Handle user information commands
        handle_user_info(command)
    return True  # Return True to keep running


# Main loop to keep the assistant running
if __name__ == "__main__":
    app.run(debug=True)
    while running:
        running = run_alexa()


import speech_recognition as sr
import spacy

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

def interpret_command(command):
    doc = nlp(command)
    start_square = None
    end_square = None
    piece_type = None
    action = "move"

    for token in doc:
        # Identify piece types
        if token.text.lower() in ["pawn", "knight", "bishop", "rook", "queen", "king"]:
            piece_type = token.text.lower()

        # Identify action (move, capture, etc.)
        if token.lemma_ in ["move", "capture", "take"]:
            action = token.lemma_

        # Identify squares using pattern recognition (e.g., "e2", "a7")
        if len(token.text) == 2 and token.text[0].isalpha() and token.text[1].isdigit():
            if start_square is None:
                start_square = token.text.lower()
            else:
                end_square = token.text.lower()

    # Validate recognized squares
    if start_square and end_square:
        return start_square, end_square, piece_type, action
    return None, None, piece_type, action

def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for your command...")

        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing speech...")
            command = recognizer.recognize_google(audio)
            print(f"Recognized command: {command}")
            return command
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")
            return None

if __name__ == "__main__":
    # Initialize your chess game or integrate with existing chess game setup
    # Replace this part with your actual chess game initialization logic
    print("Initializing chess game...")
    print("Chess game ready!")

    # Main loop for interacting with the game via voice commands
    while True:
        command = recognize_speech()

        if command:
            start, end, piece, action = interpret_command(command)
            if start and end:
                # Replace with logic to move piece in your chess game
                print(f"Interpreted command: {action.capitalize()} {piece.capitalize()} from {start} to {end}.")
                # Implement logic to move piece in chess game here
                # Example: game.move_piece(piece, start, end)
            else:
                print("Could not interpret the chess move command from speech.")
        else:
            print("No valid command received.")

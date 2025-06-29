import spacy

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


import pygame
import speech_recognition as sr
import spacy
from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from move import Move
from popup import Popup

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

class Game:
    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.popup = Popup(WIDTH, HEIGHT)

        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def interpret_command(self, command):
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
            start_pos = Square.parse_square(start_square)
            end_pos = Square.parse_square(end_square)
            if start_pos and end_pos:
                return start_pos, end_pos, piece_type, action
        return None, None, piece_type, action

    def recognize_speech(self):
        with self.microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for your command...")

            try:
                audio = self.recognizer.listen(source, timeout=5)
                print("Recognizing speech...")
                command = self.recognizer.recognize_google(audio)
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

    def handle_voice_command(self, screen):
        command = self.recognize_speech()
        if command:
            start, end, piece, action = self.interpret_command(command)
            if start and end:
                initial_square = Square(*start)
                final_square = Square(*end)
                move = Move(initial_square, final_square)
                print(f"Interpreted command: {action.capitalize()} {piece.capitalize()} from {start} to {end}.")
                print(f"Move: {move}")

                # Implement logic to move chess piece or update game state based on command
                # For example, update self.board based on start, end, piece, action
                self.popup.show_message(screen, f"{action.capitalize()} {piece.capitalize()} from {initial_square.alphacol}{8-initial_square.row} to {final_square.alphacol}{8-final_square.row}.")
            else:
                self.popup.show_message(screen, "Could not interpret the chess move command from speech.")
        else:
            self.popup.show_message(screen, "No valid command received.")

    def handle_mouse_drag(self, screen):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.dragger.update_mouse(event.pos)
                clicked_row = event.pos[1] // SQSIZE
                clicked_col = event.pos[0] // SQSIZE
                if self.board.squares[clicked_row][clicked_col].has_piece():
                    piece = self.board.squares[clicked_row][clicked_col].piece
                    if piece.color == self.next_player:
                        self.dragger.save_initial(event.pos)
                        self.dragger.drag_piece(piece)
                        self.board.squares[clicked_row][clicked_col].piece = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragger.is_dragging():
                    self.dragger.update_mouse(event.pos)
                    self.show_bg(screen)
                    self.show_pieces(screen)
                    self.dragger.update_blit(screen)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragger.is_dragging():
                    self.dragger.update_mouse(event.pos)
                    released_row = event.pos[1] // SQSIZE
                    released_col = event.pos[0] // SQSIZE
                    initial = Square(self.dragger.initial_row, self.dragger.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final)
                    self.board.squares[initial.row][initial.col].piece = self.dragger.piece
                    self.dragger.undrag_piece()
                    print(f"Move: {move}")

    def run_game(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Handle space bar press for voice command
                        self.handle_voice_command(screen)

            # Handle mouse drag interactions
            self.handle_mouse_drag(screen)

            screen.fill((255, 255, 255))  # White background
            self.show_bg(screen)
            self.show_pieces(screen)
            # Other show methods for displaying game elements

            # Update the popups
            self.popup.update(screen)

            pygame.display.flip()
            clock.tick(30)  # Frame rate

        pygame.quit()

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    # Implement other methods for displaying game elements

if __name__ == "__main__":
    game = Game()
    game.run_game()


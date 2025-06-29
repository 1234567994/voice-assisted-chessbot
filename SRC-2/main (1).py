import sys
import pygame
import speech_recognition as sr
from const import *
from game import Game
from square import Square
from move import Move
from ai import AI
from popup import Popup

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.ai = AI('black')
        self.popup = Popup(WIDTH, HEIGHT)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def recognize_speech(self):
        try:
            with self.microphone as source:
                print("Say your move:")
                audio = self.recognizer.listen(source)
                move = self.recognizer.recognize_google(audio)
                print(f"You said: {move}")
                return move
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

    def parse_move(self, move_str):
        # Example move format: "e2 to e4"
        move_str = move_str.lower().replace(" to ", "")
        if len(move_str) == 4:
            try:
                initial_col = ord(move_str[0]) - ord('a')
                initial_row = 8 - int(move_str[1])
                final_col = ord(move_str[2]) - ord('a')
                final_row = 8 - int(move_str[3])
                return (initial_row, initial_col, final_row, final_col)
            except ValueError:
                return None
        return None

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            game.show_check(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.next_player == 'white':  
                        dragger.update_mouse(event.pos)
                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)

                elif event.type == pygame.MOUSEMOTION:
                    if game.next_player == 'white':
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE
                        game.set_hover(motion_row, motion_col)
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if game.next_player == 'white':
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)
                                game.play_sound(captured)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                game.next_turn()

                                if game.next_player == 'black':
                                    ai_move = self.ai.get_move(board)
                                    if ai_move:
                                        board.move(ai_move.piece, ai_move)
                                        game.play_sound(ai_move.captured_piece is not None)
                                        game.show_bg(screen)
                                        game.show_last_move(screen)
                                        game.show_pieces(screen)
                                        game.next_turn()
                            else:
                                self.popup.show_message(screen, "Invalid Move!")
                                game.handle_invalid_move(screen)
                        dragger.undrag_piece()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        game.change_theme()
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger()

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if game.next_player == 'white':
                move_str = self.recognize_speech()
                if move_str:
                    move_coords = self.parse_move(move_str)
                    if move_coords:
                        initial_row, initial_col, final_row, final_col = move_coords
                        piece = board.squares[initial_row][initial_col].piece
                        if piece and piece.color == game.next_player:
                            move = Move(Square(initial_row, initial_col), Square(final_row, final_col))
                            if board.valid_move(piece, move):
                                board.move(piece, move)
                                board.set_true_en_passant(piece)
                                game.play_sound(False)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                game.next_turn()

                                if game.next_player == 'black':
                                    ai_move = self.ai.get_move(board)
                                    if ai_move:
                                        board.move(ai_move.piece, ai_move)
                                        game.play_sound(ai_move.captured_piece is not None)
                                        game.show_bg(screen)
                                        game.show_last_move(screen)
                                        game.show_pieces(screen)
                                        game.next_turn()
                            else:
                                self.popup.show_message(screen, "Invalid Move!")
                                game.handle_invalid_move(screen)

            game.handle_checkmate(screen)
            self.popup.update(screen)
            pygame.display.update()

if __name__ == "__main__":
    main = Main()
    main.mainloop()

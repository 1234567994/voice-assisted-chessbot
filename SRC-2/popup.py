import pygame
import time

class Popup:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 48)
        self.popup_duration = 2  # duration in seconds
        self.message_queue = []

    def show_message(self, surface, message):
        # Add the message to the queue with the current time
        self.message_queue.append((message, time.time()))

    def update(self, surface):
        current_time = time.time()

        # Remove old messages
        self.message_queue = [(msg, msg_time) for msg, msg_time in self.message_queue if current_time - msg_time < self.popup_duration]

        # Display all messages in the queue
        for message, msg_time in self.message_queue:
            text = self.font.render(message, True, (255, 255, 255))
            rect = text.get_rect(center=(self.width // 2, self.height // 2))
            surface.blit(text, rect)

from typing import Tuple
from pygame import Vector2, Color
import pygame
from ...bot import Bot
from ...linear_math import Transform
import socket
import json
from ...track import Track


class DaBullet(Bot):
    @property
    def name(self):
        return "DaBullet"

    @property
    def contributor(self):
        return "MeltedPianoMan"

    @property
    def color(self) -> Color:
        r = 50
        g = 205
        b = 50
        return Color(r, g, b)

    def __init__(self, track: Track):
        super().__init__(track)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', 12345)

    def __del__(self):
        self.sock.close()

    def send_plotjuggler_data(self):

        data = {
            "x": self.position.p.x,
            "y": self.position.p.y,
        }
        self.sock.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def compute_commands(self, next_waypoint: int, position: Transform, velocity: Vector2) -> Tuple:
        self.position = position

        target = self.track.lines[next_waypoint]
        # calculate the target in the frame of the robot
        target = position.inverse() * target
        # calculate the angle to the target
        angle = target.as_polar()[1]

        # calculate the throttle
        target_velocity = 150
        if velocity.length() < target_velocity:
            throttle = 1
        else:
            throttle = -1

        # calculate the steering
        if angle > 0:
            steer = 1
        else:
            steer = -1

        self.send_plotjuggler_data()
        return throttle, steer

    def draw(self, map_scaled, zoom):
        return
        # Draw the simulation on the scaled map
        # print(f'Simulation: {[p.p for p in self.simulation]}')
        # pygame.draw.circle(map_scaled, (0, 0, 0), self.position.p * zoom, 10)
        debugText = "Some Debug Text"
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(debugText, False, (0, 0, 0))
        map_scaled.blit(text_surface, (0, 0))

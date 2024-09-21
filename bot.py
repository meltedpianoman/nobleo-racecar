import math
from typing import Tuple
from pygame import Vector2, Color
import pygame
from ...bot import Bot
from ...linear_math import Transform
import socket
import json
from ...track import Track


def calculate_angle(v1: Vector2, v2: Vector2):
    dot_product = v1.dot(v2)
    magnitude_v1 = v1.length()
    magnitude_v2 = v2.length()
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
    angle_radians = math.acos(cos_theta)
    return math.degrees(angle_radians)


def calculate_lenth(p1: Vector2, p2: Vector2):
    return p1.distance_to(p2)


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

        self.CURVE_ANGLE = 15
        self.MIN_VELOCITY = 150
        self.MAX_VELOCITY = 300
        self.BRAKE_DISTANCE = 200

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', 12345)

        self.calculate_waypoints()
        self.target_velocity = 0

    def calculate_waypoints(self):
        self.waypoints = []
        self.nof_waypoints = len(self.track.lines)
        for i in range(len(self.track.lines)):
            p0 = self.track.lines[i - 1]
            p1 = self.track.lines[i]
            p2 = self.track.lines[(i + 1) % self.nof_waypoints]

            v1 = p1 - p0
            v2 = p2 - p1

            waypoint = {
                "angle": calculate_angle(v1, v2),
                "length": calculate_lenth(p0, p1),
            }
            self.waypoints.append(waypoint)

        def __del__(self):
            self.sock.close()

    def send_plotjuggler_data(self):
        data = {
            "waypoints": self.waypoints,
            "status": {
                "velocity": self.velocity.length(),
                "angle": self.angle,
                "x": self.position.p.x,
                "y": self.position.p.y,
                "next_waypoint": self.next_waypoint,
                "length_to_next_waypoint": self.target.length(),
                "throttle": self.throttle,
                "steer": self.steer,
                "target_velocity": self.target_velocity,
            },
        }
        self.sock.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def next_segment_is_curve(self):
        length = 0.0
        curve = False
        waypoint = self.next_waypoint
        while not curve and length < self.BRAKE_DISTANCE:
            if self.waypoints[waypoint]["angle"] > self.CURVE_ANGLE:
                curve = True
                break
            length = length + self.waypoints[waypoint]["length"]
            waypoint = (waypoint + 1) % self.nof_waypoints
        return curve, length

    def determine_target_velocity(self):
        self.target_velocity = self.MAX_VELOCITY
        (is_curve, length_to_curve) = self.next_segment_is_curve()
        if is_curve:
            if self.target.length() <= (self.BRAKE_DISTANCE - length_to_curve):
                self.target_velocity = self.MIN_VELOCITY

    def compute_commands(self, next_waypoint: int, position: Transform, velocity: Vector2) -> Tuple:
        self.next_waypoint = next_waypoint
        self.position = position
        self.velocity = velocity

        self.target = self.track.lines[next_waypoint]
        # calculate the target in the frame of the robot
        self.target = position.inverse() * self.target
        # calculate the angle to the target
        self.angle = self.target.as_polar()[1]

        # calculate the throttle
        self.determine_target_velocity()
        if self.velocity.length() < self.target_velocity:
            self.throttle = 1
        else:
            self.throttle = -1

        # calculate the steering
        if self.angle > 0:
            self.steer = 1
        else:
            self.steer = -1

        self.send_plotjuggler_data()
        return self.throttle, self.steer

    def draw(self, map_scaled, zoom):
        return
        # Draw the simulation on the scaled map
        # print(f'Simulation: {[p.p for p in self.simulation]}')
        # pygame.draw.circle(map_scaled, (0, 0, 0), self.position.p * zoom, 10)
        debugText = "Some Debug Text"
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(debugText, False, (0, 0, 0))
        map_scaled.blit(text_surface, (0, 0))

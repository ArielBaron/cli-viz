# visualizers/stick_figure.py
import curses
import random
import math
from visualizer_base import VisualizerBase

class StickFigureVisualizer(VisualizerBase):
    def __init__(self):
        super().__init__(name="Dancing Stick Figure")
        self.dance_mode = 0  # Different dance styles
        self.speed = 0.5

    def setup(self):
        self.phase = 0
        
    def draw(self, stdscr, spectrum, height, width, energy, hue_offset):
        # Centers for stick figure
        center_x = width // 2
        center_y = height // 2
        
        # Clear figure area
        for y in range(center_y - 10, center_y + 10):
            if 0 <= y < height:
                for x in range(center_x - 15, center_x + 15):
                    if 0 <= x < width:
                        stdscr.addstr(y, x, " ")
        
        # Animate based on audio energy and current phase
        self.phase += energy * self.speed
        
        # Calculate limb positions based on phase and dance mode
        if self.dance_mode == 0:
            # Regular dancing
            head_x = center_x
            head_y = center_y - 6
            
            # Body
            body_bottom_x = center_x
            body_bottom_y = center_y + 1
            
            # Arms
            left_arm_x = center_x - 4 * math.cos(self.phase)
            left_arm_y = center_y - 3 - math.sin(self.phase)
            
            right_arm_x = center_x + 4 * math.cos(self.phase + math.pi)
            right_arm_y = center_y - 3 - math.sin(self.phase + math.pi)
            
            # Legs
            left_leg_x = center_x - 3 * math.cos(self.phase * 0.7)
            left_leg_y = center_y + 5 + math.sin(self.phase * 0.7)
            
            right_leg_x = center_x + 3 * math.cos(self.phase * 0.7 + math.pi)
            right_leg_y = center_y + 5 + math.sin(self.phase * 0.7 + math.pi)
            
        elif self.dance_mode == 1:
            # Breakdance mode
            head_x = center_x + 4 * math.cos(self.phase)
            head_y = center_y - 2 - 2 * math.sin(self.phase)
            
            # Body
            body_bottom_x = center_x
            body_bottom_y = center_y + 1
            
            # Arms
            left_arm_x = center_x - 5 * math.cos(self.phase * 2)
            left_arm_y = center_y - 1 - 2 * math.sin(self.phase * 2)
            
            right_arm_x = center_x + 5 * math.cos(self.phase * 2 + math.pi/2)
            right_arm_y = center_y - 1 - 2 * math.sin(self.phase * 2 + math.pi/2)
            
            # Legs
            left_leg_x = center_x - 5 * math.cos(self.phase * 1.5)
            left_leg_y = center_y + 3 + 3 * math.sin(self.phase * 1.5)
            
            right_leg_x = center_x + 5 * math.cos(self.phase * 1.5 + math.pi/3)
            right_leg_y = center_y + 3 + 3 * math.sin(self.phase * 1.5 + math.pi/3)
            
        else:
            # Robot dance
            head_x = center_x + (energy > 0.5) * random.randint(-1, 1)
            head_y = center_y - 6 + (energy > 0.7) * random.randint(-1, 1)
            
            # Body
            body_bottom_x = center_x
            body_bottom_y = center_y + 1
            
            # Arms - robotic movements
            arm_phase = int(self.phase * 4) % 4
            
            if arm_phase == 0:
                left_arm_x, left_arm_y = center_x - 4, center_y - 3
                right_arm_x, right_arm_y = center_x + 4, center_y - 3
            elif arm_phase == 1:
                left_arm_x, left_arm_y = center_x - 4, center_y - 5
                right_arm_x, right_arm_y = center_x + 4, center_y - 3
            elif arm_phase == 2:
                left_arm_x, left_arm_y = center_x - 4, center_y - 5
                right_arm_x, right_arm_y = center_x + 4, center_y - 5
            else:
                left_arm_x, left_arm_y = center_x - 4, center_y - 3
                right_arm_x, right_arm_y = center_x + 4, center_y - 5
                
            # Legs - robot dance
            leg_phase = int(self.phase * 2) % 2
            
            if leg_phase == 0:
                left_leg_x, left_leg_y = center_x - 3, center_y + 5
                right_leg_x, right_leg_y = center_x + 3, center_y + 5
            else:
                left_leg_x, left_leg_y = center_x - 2, center_y + 5 
                right_leg_x, right_leg_y = center_x + 2, center_y + 5
        
        # Calculate color based on energy and hue_offset
        hue = (hue_offset + energy) % 1.0
        sat = 0.8
        val = 0.7 + 0.3 * energy
        
        color_attr = self.hsv_to_color_pair(stdscr, hue, sat, val)
        
        # Draw stick figure
        # Head
        stdscr.addstr(int(head_y), int(head_x), "O", color_attr | curses.A_BOLD)
        
        # Body
        for i in range(1, 6):
            body_y = head_y + i
            if 0 <= int(body_y) < height and 0 <= int(center_x) < width:
                stdscr.addstr(int(body_y), int(center_x), "|", color_attr)
        
        # Arms
        self.draw_line(stdscr, center_x, head_y + 2, left_arm_x, left_arm_y, "/", color_attr)
        self.draw_line(stdscr, center_x, head_y + 2, right_arm_x, right_arm_y, "\\", color_attr)
        
        # Legs
        self.draw_line(stdscr, center_x, body_bottom_y, left_leg_x, left_leg_y, "/", color_attr)
        self.draw_line(stdscr, center_x, body_bottom_y, right_leg_x, right_leg_y, "\\", color_attr)
        
        # Add a dancing floor that reacts to the music
        floor_y = body_bottom_y + 6
        floor_width = int(15 + 10 * energy)
        
        for x in range(center_x - floor_width, center_x + floor_width + 1):
            if 0 <= x < width and 0 <= floor_y < height:
                floor_hue = (hue_offset + (x - center_x) / floor_width / 2) % 1.0
                floor_color = self.hsv_to_color_pair(stdscr, floor_hue, 0.7, 0.8)
                stdscr.addstr(floor_y, x, "_", floor_color)
    
    def draw_line(self, stdscr, x1, y1, x2, y2, char, attr):
        """Draw a line between two points using Bresenham's algorithm"""
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        height, width = stdscr.getmaxyx()
        
        while True:
            if 0 <= y1 < height and 0 <= x1 < width:
                stdscr.addstr(y1, x1, char, attr)
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    def handle_keypress(self, key):
        if key == 'd':  # Change dance mode
            self.dance_mode = (self.dance_mode + 1) % 3
            return True
        elif key == 's':  # Speed up
            self.speed = min(1.5, self.speed + 0.1)
            return True
        elif key == 'S':  # Slow down
            self.speed = max(0.1, self.speed - 0.1)
            return True
        return False
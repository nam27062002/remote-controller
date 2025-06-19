import pygame
import sys
import math
from settings import *


class PS5ControllerTester:
    def __init__(self, width=1000, height=664):
        pygame.init()
        pygame.joystick.init()

        self.base_width = 1000
        self.base_height = 664
        self.width = width
        self.height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("PS5 Controller Tester")

        # Controller detection
        self.joystick = None
        self.controller_connected = False
        self.check_controller()

        # Button states
        self.button_states = {}
        self.axis_values = {}
        self.hat_values = {}

        # Visual feedback colors
        self.normal_color = (255, 255, 255)
        self.pressed_color = (100, 200, 255)
        self.highlight_color = (255, 255, 0)

        # Joystick positions (for visual feedback)
        self.left_stick_pos = [0, 0]
        self.right_stick_pos = [0, 0]

        # Load assets and define positions
        self.load_assets()
        self.define_positions()

        # Font for text display
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.clock = pygame.time.Clock()

    def check_controller(self):
        """Check for connected controllers"""
        pygame.joystick.quit()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.controller_connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
            print(f"Buttons: {self.joystick.get_numbuttons()}")
            print(f"Axes: {self.joystick.get_numaxes()}")
            print(f"Hats: {self.joystick.get_numhats()}")
        else:
            self.controller_connected = False
            self.joystick = None
            print("No controller connected")

    def load_assets(self):
        """Load all image assets"""
        asset_files = {
            'icon': 'assets/icon.png',
            'center_pad': 'assets/center-pad.png',
            'highlight': 'assets/highlight.png',
            'speaker': 'assets/speaker.png',
            'ps_logo_under': 'assets/ps_logo_under.png',
            'ps_logo_upper': 'assets/ps_logo_upper.png',
            'ps_logo_under_layout': 'assets/ps_logo_under_layout.png',
            'ps_logo_upper_layout': 'assets/ps_logo_upper_layout.png',
            'voice_button': 'assets/voice_button.png',
            'voice_button_highlight': 'assets/voice_button_highlight.png',
            'icon_mute': 'assets/icon-mute.png',
            'loudspeaker': 'assets/loudspeaker.png',
            'right_button': 'assets/right_button.png',
            'button_circle': 'assets/button-circle.png',
            'button_cross': 'assets/button-cross.png',
            'button_square': 'assets/button-square.png',
            'button_triangle': 'assets/button-triangle.png',
            'right_side': 'assets/right_side.png',
            'left_side': 'assets/left-side.png',
            'blue_highlight_right': 'assets/blue_highlight_right.png',
            'blue_highlight_left': 'assets/blue_highlight_left.png',
            'black_right': 'assets/black_right.png',
            'black_left': 'assets/black_left.png',
            'white_right': 'assets/white_right_highlight.png',
            'white_left': 'assets/white_left_highlight.png',
            'right_analog_stick': 'assets/right_analog_stick.png',
            'dpad_up': 'assets/dpad_up.png',
            'dpad_down': 'assets/dpad_down.png',
            'dpad_left': 'assets/dpad_left.png',
            'dpad_right': 'assets/dpad_right.png',
            'r1': 'assets/R1.png',
            'l1': 'assets/L1.png',
            'joystick': 'assets/joystick.png',
            'left_icon': 'assets/left_icon.png',
            'right_icon': 'assets/right_icon.png',
            'share_button': 'assets/share_button.png',
            'option_button': 'assets/option_button.png'
        }

        self.assets = {}
        for name, path in asset_files.items():
            try:
                self.assets[name] = pygame.image.load(path)
            except pygame.error as e:
                print(f"Could not load {path}: {e}")
                # Create a placeholder surface
                self.assets[name] = pygame.Surface((50, 50))
                self.assets[name].fill((255, 0, 255))  # Magenta placeholder

        # Set icon
        if 'icon' in self.assets:
            pygame.display.set_icon(self.assets['icon'])

    def define_positions(self):
        """Define all element positions relative to base resolution"""
        self.positions = {
            # Right side elements
            'r1': (735.17, 11.29),
            'white_right': (709.53, 408),
            'black_right': (500, 18.07),
            'right_side': (676.97, 33.09),
            'blue_highlight_right': (500, 44),

            # Right buttons (Cross, Square, Circle, Triangle)
            'right_button_cross': (768, 232.97),
            'right_button_square': (697.38, 161.89),
            'right_button_circle': (838.93, 161.89),
            'right_button_triangle': (768, 91),

            # Button symbols
            'button_cross': (773.57, 238.54),
            'button_square': (702.94, 167.46),
            'button_circle': (844.5, 167.46),
            'button_triangle': (773.57, 96.57),

            'right_joystick': (591.47, 264),
            'right_icon': (723, 49),
            'option_button': (708.73, 64),

            # Left side elements
            'l1': (134.84, 11.29),
            'white_left': (143.99, 408),
            'black_left': (88, 18.07),
            'left_side': (17.58, 33.09),
            'blue_highlight_left': (298.64, 44),

            # D-pad
            'dpad_up': (170, 111),
            'dpad_down': (170, 204),
            'dpad_left': (114, 163),
            'dpad_right': (214, 163),

            'left_joystick': (238, 264),
            'left_icon': (262.58, 49.25),
            'share_button': (258.68, 64),

            # Center elements
            'center_pad': (308.09, 17.89),
            'highlight': (464, 226),
            'speaker': (461, 250),
            'ps_logo_under': (470.6, 320.85),
            'ps_logo_upper': (492.74, 295),
            'ps_logo_under_layout': (470.6, 320.85),
            'ps_logo_upper_layout': (492.74, 295),
            'voice_button_highlight': (475.6, 371),
            'voice_button': (477.6, 373),
            'icon_mute': (495.04, 397.61),
            'loudspeaker': (491.5, 418.27)
        }

        # Button mapping for PS5 controller
        self.button_mapping = {
            0: 'cross',  # X button
            1: 'circle',  # Circle button
            2: 'square',  # Square button
            3: 'triangle',  # Triangle button
            4: 'share',  # Share button
            5: 'ps',  # PS button
            6: 'option',  # Options button
            7: 'l3',  # Left stick press
            8: 'r3',  # Right stick press
            9: 'l1',  # L1
            10: 'r1',  # R1
            11: 'dpad_up',  # D-pad up
            12: 'dpad_down',  # D-pad down
            13: 'dpad_left',  # D-pad left
            14: 'dpad_right',  # D-pad right
        }

        # Axis mapping
        self.axis_mapping = {
            0: 'left_stick_x',
            1: 'left_stick_y',
            2: 'right_stick_x',
            3: 'right_stick_y',
            4: 'l2',  # Left trigger
            5: 'r2',  # Right trigger
        }

    def update_controller_input(self):
        """Update controller input states"""
        if not self.controller_connected or not self.joystick:
            return

        # Update button states
        for i in range(self.joystick.get_numbuttons()):
            button_name = self.button_mapping.get(i, f'button_{i}')
            self.button_states[button_name] = self.joystick.get_button(i)

        # Update axis values
        for i in range(self.joystick.get_numaxes()):
            axis_name = self.axis_mapping.get(i, f'axis_{i}')
            value = self.joystick.get_axis(i)
            self.axis_values[axis_name] = value

            # Update joystick positions for visual feedback
            if axis_name == 'left_stick_x':
                self.left_stick_pos[0] = value * 20  # Scale for visual movement
            elif axis_name == 'left_stick_y':
                self.left_stick_pos[1] = value * 20
            elif axis_name == 'right_stick_x':
                self.right_stick_pos[0] = value * 20
            elif axis_name == 'right_stick_y':
                self.right_stick_pos[1] = value * 20

        # Update hat (D-pad) values
        for i in range(self.joystick.get_numhats()):
            self.hat_values[f'hat_{i}'] = self.joystick.get_hat(i)

    def scale_position(self, pos):
        """Scale position based on current resolution"""
        return (int(pos[0] * self.scale_x), int(pos[1] * self.scale_y))

    def scale_surface(self, surface, scale_factor=1.0):
        """Scale surface based on current resolution"""
        if surface is None:
            return None

        original_size = surface.get_size()
        new_size = (
            int(original_size[0] * self.scale_x * scale_factor),
            int(original_size[1] * self.scale_y * scale_factor)
        )

        if new_size[0] <= 0 or new_size[1] <= 0:
            return surface

        return pygame.transform.scale(surface, new_size)

    def blit_scaled(self, asset_name, position_key, scale_factor=1.0, color_tint=None):
        """Blit an asset at a scaled position with scaled size and optional color tint"""
        if asset_name in self.assets and position_key in self.positions:
            scaled_surface = self.scale_surface(self.assets[asset_name], scale_factor)
            scaled_pos = self.scale_position(self.positions[position_key])

            # Apply color tint if specified
            if color_tint:
                tinted_surface = scaled_surface.copy()
                tinted_surface.fill(color_tint, special_flags=pygame.BLEND_ADD)
                self.screen.blit(tinted_surface, scaled_pos)
            else:
                self.screen.blit(scaled_surface, scaled_pos)

    def draw_button_with_state(self, button_asset, symbol_asset, button_pos, symbol_pos, button_name):
        """Draw button with visual feedback based on state"""
        is_pressed = self.button_states.get(button_name, False)
        color_tint = self.pressed_color if is_pressed else None

        # Draw button background
        self.blit_scaled(button_asset, button_pos, color_tint=color_tint)
        # Draw button symbol
        self.blit_scaled(symbol_asset, symbol_pos, color_tint=color_tint)

    def draw_dpad_with_state(self):
        """Draw D-pad with visual feedback"""
        dpad_buttons = [
            ('dpad_up', 'dpad_up', 'dpad_up'),
            ('dpad_down', 'dpad_down', 'dpad_down'),
            ('dpad_left', 'dpad_left', 'dpad_left'),
            ('dpad_right', 'dpad_right', 'dpad_right')
        ]

        for asset_name, pos_key, button_name in dpad_buttons:
            is_pressed = self.button_states.get(button_name, False)
            color_tint = self.pressed_color if is_pressed else None
            self.blit_scaled(asset_name, pos_key, color_tint=color_tint)

    def draw_joystick_with_movement(self, asset_name, base_pos_key, stick_offset):
        """Draw joystick with movement based on input"""
        base_pos = self.scale_position(self.positions[base_pos_key])
        offset_x = int(stick_offset[0] * self.scale_x)
        offset_y = int(stick_offset[1] * self.scale_y)

        moved_pos = (base_pos[0] + offset_x, base_pos[1] + offset_y)

        scaled_surface = self.scale_surface(self.assets[asset_name])
        self.screen.blit(scaled_surface, moved_pos)

    def draw_controller(self):
        """Draw the complete PS5 controller with input feedback"""
        # Right side elements
        self.blit_scaled('r1', 'r1', color_tint=self.pressed_color if self.button_states.get('r1', False) else None)
        self.blit_scaled('white_right', 'white_right')
        self.blit_scaled('black_right', 'black_right')
        self.blit_scaled('right_side', 'right_side')
        self.blit_scaled('blue_highlight_right', 'blue_highlight_right')

        # Right buttons with state feedback
        self.draw_button_with_state('right_button', 'button_cross', 'right_button_cross', 'button_cross', 'cross')
        self.draw_button_with_state('right_button', 'button_square', 'right_button_square', 'button_square', 'square')
        self.draw_button_with_state('right_button', 'button_circle', 'right_button_circle', 'button_circle', 'circle')
        self.draw_button_with_state('right_button', 'button_triangle', 'right_button_triangle', 'button_triangle',
                                    'triangle')

        # Right side controls
        self.draw_joystick_with_movement('joystick', 'right_joystick', self.right_stick_pos)
        self.blit_scaled('right_icon', 'right_icon')
        self.blit_scaled('option_button', 'option_button',
                         color_tint=self.pressed_color if self.button_states.get('option', False) else None)

        # Left side elements
        self.blit_scaled('l1', 'l1', color_tint=self.pressed_color if self.button_states.get('l1', False) else None)
        self.blit_scaled('white_left', 'white_left')
        self.blit_scaled('black_left', 'black_left')
        self.blit_scaled('left_side', 'left_side')
        self.blit_scaled('blue_highlight_left', 'blue_highlight_left')

        # D-pad with state feedback
        self.draw_dpad_with_state()

        # Left side controls
        self.draw_joystick_with_movement('joystick', 'left_joystick', self.left_stick_pos)
        self.blit_scaled('left_icon', 'left_icon')
        self.blit_scaled('share_button', 'share_button',
                         color_tint=self.pressed_color if self.button_states.get('share', False) else None)

        # Center elements
        self.blit_scaled('center_pad', 'center_pad')
        self.blit_scaled('highlight', 'highlight')
        self.blit_scaled('speaker', 'speaker')
        self.blit_scaled('ps_logo_under', 'ps_logo_under')
        self.blit_scaled('ps_logo_upper', 'ps_logo_upper',
                         color_tint=self.pressed_color if self.button_states.get('ps', False) else None)
        self.blit_scaled('ps_logo_under_layout', 'ps_logo_under_layout')
        self.blit_scaled('ps_logo_upper_layout', 'ps_logo_upper_layout')
        self.blit_scaled('voice_button_highlight', 'voice_button_highlight')
        self.blit_scaled('voice_button', 'voice_button')
        self.blit_scaled('icon_mute', 'icon_mute')
        self.blit_scaled('loudspeaker', 'loudspeaker')

    def draw_controller_info(self):
        """Draw controller connection status and input values"""
        y_offset = 10

        # Connection status
        if self.controller_connected:
            status_text = f"Controller: {self.joystick.get_name()}"
            color = (0, 255, 0)
        else:
            status_text = "No Controller Connected (Press R to refresh)"
            color = (255, 0, 0)

        text_surface = self.font.render(status_text, True, color)
        self.screen.blit(text_surface, (10, y_offset))
        y_offset += 30

        if not self.controller_connected:
            return

        # Display active buttons
        active_buttons = [name for name, pressed in self.button_states.items() if pressed]
        if active_buttons:
            buttons_text = f"Active Buttons: {', '.join(active_buttons)}"
            text_surface = self.small_font.render(buttons_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

        # Display axis values
        for axis_name, value in self.axis_values.items():
            if abs(value) > 0.1:  # Only show significant values
                axis_text = f"{axis_name}: {value:.2f}"
                text_surface = self.small_font.render(axis_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 20

        # Display trigger values as bars
        l2_value = self.axis_values.get('l2', 0)
        r2_value = self.axis_values.get('r2', 0)

        if abs(l2_value) > 0.1:
            self.draw_trigger_bar("L2", l2_value, 10, self.height - 60)
        if abs(r2_value) > 0.1:
            self.draw_trigger_bar("R2", r2_value, 10, self.height - 30)

    def draw_trigger_bar(self, label, value, x, y):
        """Draw trigger pressure as a progress bar"""
        # Normalize value from [-1, 1] to [0, 1] for triggers
        normalized_value = (value + 1) / 2

        bar_width = 200
        bar_height = 20

        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x + 30, y, bar_width, bar_height))
        # Fill
        fill_width = int(bar_width * normalized_value)
        pygame.draw.rect(self.screen, (0, 255, 0), (x + 30, y, fill_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (x + 30, y, bar_width, bar_height), 2)

        # Label
        label_surface = self.small_font.render(f"{label}:", True, (255, 255, 255))
        self.screen.blit(label_surface, (x, y + 3))

    def handle_resize(self, new_width, new_height):
        """Handle window resize"""
        self.width = new_width
        self.height = new_height
        self.scale_x = new_width / self.base_width
        self.scale_y = new_height / self.base_height
        self.screen = pygame.display.set_mode((new_width, new_height))

    def run(self):
        """Main game loop"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Press R to refresh controller
                        self.check_controller()
                elif event.type == pygame.JOYBUTTONDOWN:
                    print(f"Button {event.button} pressed")
                elif event.type == pygame.JOYBUTTONUP:
                    print(f"Button {event.button} released")
                elif event.type == pygame.JOYAXISMOTION:
                    print(f"Axis {event.axis}: {event.value:.2f}")

            # Update controller input
            self.update_controller_input()

            # Clear screen
            self.screen.fill(GRAY)

            # Draw controller
            self.draw_controller()

            # Draw info overlay
            self.draw_controller_info()

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        sys.exit()


# Usage
if __name__ == "__main__":
    # Initialize controller tester
    tester = PS5ControllerTester(1000, 664)
    tester.run()
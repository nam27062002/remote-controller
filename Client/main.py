import pygame
import sys
import math
from Client.client import RemoteClient
import time
class PS5ControllerTester:
    def __init__(self, width=1000, height=664):
        pygame.init()
        pygame.joystick.init()

        self.base_width = 1000
        self.base_height = 664
        self.width = width
        self.height = height

        # Scale controller while maintaining quality
        self.controller_scale = 0.8
        self.scale_x = (width / self.base_width) * self.controller_scale
        self.scale_y = (height / self.base_height) * self.controller_scale

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
        self.pressed_color = (0, 150, 255)
        self.trigger_color = (100, 255, 100)
        self.joystick_pressed_color = (255, 100, 100)
        self.circle_color = (100, 200, 255, 100)

        # Joystick positions
        self.left_stick_pos = [0, 0]
        self.right_stick_pos = [0, 0]
        self.left_stick_moved = False
        self.right_stick_moved = False
        self.left_stick_move_timer = 0
        self.right_stick_move_timer = 0
        self.joystick_move_threshold = 0.2

        # Joystick properties
        self.joystick_size = 161
        self.joystick_radius = self.joystick_size / 2

        # Store centers for trigonometric circles
        self.left_joystick_center = None
        self.right_joystick_center = None

        # L1/R1 dimensions
        self.l1_size = (131, 47)
        self.r1_size = (131, 47)

        # Load assets and define positions
        self.load_assets()
        self.define_positions()

        # Fonts for text display
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.clock = pygame.time.Clock()

        # Initialize RemoteClient
        self.remote_client = RemoteClient()
        self.last_send_time = 0
        self.send_interval = 0.1 # Send data every 0.1 seconds

        # Calculate controller offset to center it
        self.controller_offset_x = (width - (self.base_width * self.controller_scale)) // 2
        self.controller_offset_y = (height - (self.base_height * self.controller_scale)) // 2

    def check_controller(self):
        """Check for connected controllers"""
        try:
            pygame.joystick.quit()
            pygame.joystick.init()

            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.controller_connected = True
                print(f"Controller connected: {self.joystick.get_name()}")
                print(f"Total buttons: {self.joystick.get_numbuttons()}")
                print(f"Total axes: {self.joystick.get_numaxes()}")
            else:
                self.controller_connected = False
                self.joystick = None
                print("No controller connected")
        except Exception as e:
            print(f"Error checking controller: {e}")
            self.controller_connected = False
            self.joystick = None

    def load_assets(self):
        """Load all image assets with quality handling"""
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
            'option_button': 'assets/option_button.png',
            'l2': 'assets/L2.png',
            'r2': 'assets/R2.png',
        }

        self.assets = {}
        for name, path in asset_files.items():
            try:
                original_surface = pygame.image.load(path)
                self.assets[name] = original_surface.convert_alpha()
            except pygame.error as e:
                print(f"Could not load {path}: {e}")
                # Create a placeholder surface
                self.assets[name] = pygame.Surface((50, 50), pygame.SRCALPHA)
                self.assets[name].fill((255, 0, 255, 128))

        # Set icon
        if 'icon' in self.assets:
            pygame.display.set_icon(self.assets['icon'])

    def define_positions(self):
        """Define all element positions relative to base resolution"""
        self.positions = {
            'r1': (735.17, 11.29),
            'white_right': (709.53, 408),
            'black_right': (500, 18.07),
            'right_side': (676.97, 33.09),
            'blue_highlight_right': (500, 44),
            'button_cross': (768, 232.97),
            'button_square': (697.38, 161.89),
            'button_circle': (838.93, 161.89),
            'button_triangle': (768, 91),
            'right_joystick': (591.47, 264),
            'right_icon': (723, 49),
            'option_button': (708.73, 64),
            'l1': (134.84, 11.29),
            'white_left': (143.99, 408),
            'black_left': (88, 18.07),
            'left_side': (17.58, 33.09),
            'blue_highlight_left': (298.64, 44),
            'dpad_up': (170, 111),
            'dpad_down': (170, 204),
            'dpad_left': (114, 163),
            'dpad_right': (214, 163),
            'left_joystick': (238, 264),
            'left_icon': (262.58, 49.25),
            'share_button': (258.68, 64),
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
            'loudspeaker': (491.5, 418.27),
        }

        # Calculate trigger positions based on R1/L1 positions and sizes
        r1_center_x = self.positions['r1'][0] + self.r1_size[0] / 2
        l1_center_x = self.positions['l1'][0] + self.l1_size[0] / 2

        # Position triggers above the shoulder buttons
        self.positions['r2'] = (r1_center_x - 50, -50)
        self.positions['l2'] = (l1_center_x - 50, -50)

        # Button mapping for PS5 controller
        self.button_mapping = {
            0: 'cross',
            1: 'circle',
            2: 'square',
            3: 'triangle',
            4: 'share',
            5: 'ps',
            6: 'option',
            7: 'l3',
            8: 'r3',
            9: 'l1',
            10: 'r1',
            11: 'dpad_up',
            12: 'dpad_down',
            13: 'dpad_left',
            14: 'dpad_right',
            15: 'touchpad',
        }

        # Axis mapping
        self.axis_mapping = {
            0: 'left_stick_x',
            1: 'left_stick_y',
            2: 'right_stick_x',
            3: 'right_stick_y',
            4: 'l2',
            5: 'r2',
        }

    def update_controller_input(self):
        """Update controller input states with error handling"""
        if not self.controller_connected or not self.joystick:
            return

        try:
            # Track joystick movement
            prev_left_stick = self.left_stick_pos.copy()
            prev_right_stick = self.right_stick_pos.copy()

            # Update button states
            for i in range(self.joystick.get_numbuttons()):
                button_name = self.button_mapping.get(i, f'button_{i}')
                self.button_states[button_name] = self.joystick.get_button(i)

            # Update axis values
            for i in range(self.joystick.get_numaxes()):
                axis_name = self.axis_mapping.get(i, f'axis_{i}')
                value = self.joystick.get_axis(i)
                self.axis_values[axis_name] = value

                # Update joystick positions
                if axis_name == 'left_stick_x':
                    self.left_stick_pos[0] = value * 40
                elif axis_name == 'left_stick_y':
                    self.left_stick_pos[1] = value * 40
                elif axis_name == 'right_stick_x':
                    self.right_stick_pos[0] = value * 40
                elif axis_name == 'right_stick_y':
                    self.right_stick_pos[1] = value * 40

            # Only activate circles when movement exceeds threshold
            left_moved = (abs(self.left_stick_pos[0] - prev_left_stick[0]) > self.joystick_move_threshold * 40 or
                          abs(self.left_stick_pos[1] - prev_left_stick[1]) > self.joystick_move_threshold * 40)
            right_moved = (abs(self.right_stick_pos[0] - prev_right_stick[0]) > self.joystick_move_threshold * 40 or
                           abs(self.right_stick_pos[1] - prev_right_stick[1]) > self.joystick_move_threshold * 40)

            if left_moved:
                self.left_stick_moved = True
                self.left_stick_move_timer = 10
            if right_moved:
                self.right_stick_moved = True
                self.right_stick_move_timer = 10

            # Update hat (D-pad) values
            for i in range(self.joystick.get_numhats()):
                self.hat_values[f'hat_{i}'] = self.joystick.get_hat(i)

        except pygame.error as e:
            print(f"Controller error: {e}")
            self.controller_connected = False
            self.joystick = None
            self.check_controller()  # Try to reconnect

    def scale_position(self, pos):
        """Scale position based on current resolution and add offset for centering"""
        scaled_x = int(pos[0] * self.scale_x) + self.controller_offset_x
        scaled_y = int(pos[1] * self.scale_y) + self.controller_offset_y
        return (scaled_x, scaled_y)

    def scale_surface(self, surface, scale_factor=1.0):
        """Scale surface based on current resolution with better quality"""
        if surface is None:
            return None

        original_size = surface.get_size()
        new_size = (
            int(original_size[0] * self.scale_x * scale_factor),
            int(original_size[1] * self.scale_y * scale_factor)
        )

        if new_size[0] <= 0 or new_size[1] <= 0:
            return surface

        return pygame.transform.smoothscale(surface, new_size)

    def blit_scaled(self, asset_name, position_key, scale_factor=1.0, color_tint=None):
        """Blit an asset at a scaled position with scaled size and optional color tint"""
        if asset_name in self.assets and position_key in self.positions:
            scaled_surface = self.scale_surface(self.assets[asset_name], scale_factor)
            scaled_pos = self.scale_position(self.positions[position_key])

            if color_tint:
                tinted_surface = scaled_surface.copy()
                overlay = pygame.Surface(tinted_surface.get_size())
                overlay.fill(color_tint)
                overlay.set_alpha(128)
                tinted_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
                self.screen.blit(tinted_surface, scaled_pos)
            else:
                self.screen.blit(scaled_surface, scaled_pos)

    def draw_symbol_button(self, asset_name, position_key, button_name):
        """Draw a symbol button with visual feedback based on state"""
        is_pressed = self.button_states.get(button_name, False)
        color_tint = self.pressed_color if is_pressed else None
        self.blit_scaled(asset_name, position_key, color_tint=color_tint)

    def draw_dpad_with_state(self):
        """Draw D-pad with visual feedback"""
        self.draw_symbol_button('dpad_up', 'dpad_up', 'dpad_up')
        self.draw_symbol_button('dpad_down', 'dpad_down', 'dpad_down')
        self.draw_symbol_button('dpad_left', 'dpad_left', 'dpad_left')
        self.draw_symbol_button('dpad_right', 'dpad_right', 'dpad_right')

    def draw_right_buttons(self):
        """Draw right buttons (cross, circle, square, triangle) with visual feedback"""
        self.draw_symbol_button('button_cross', 'button_cross', 'cross')
        self.draw_symbol_button('button_square', 'button_square', 'square')
        self.draw_symbol_button('button_circle', 'button_circle', 'circle')
        self.draw_symbol_button('button_triangle', 'button_triangle', 'triangle')

    def draw_joystick_with_movement(self, asset_name, base_pos_key, stick_offset, stick_button, is_left=False):
        """Draw joystick with movement and press feedback"""
        base_pos = self.scale_position(self.positions[base_pos_key])
        offset_x = int(stick_offset[0] * self.scale_x)
        offset_y = int(stick_offset[1] * self.scale_y)

        # Calculate the actual center of the joystick base
        center_x = base_pos[0] + int(self.joystick_radius * self.scale_x)
        center_y = base_pos[1] + int(self.joystick_radius * self.scale_y)

        # Store center for later use in trigonometric circle
        if is_left:
            self.left_joystick_center = (center_x, center_y)
        else:
            self.right_joystick_center = (center_x, center_y)

        # Calculate the moved position relative to the center
        moved_pos = (center_x + offset_x - int(self.joystick_radius * self.scale_x),
                     center_y + offset_y - int(self.joystick_radius * self.scale_y))

        # Draw joystick
        scaled_surface = self.scale_surface(self.assets[asset_name])

        # Check if joystick is pressed (L3 or R3)
        is_pressed = self.button_states.get(stick_button, False)

        if is_pressed:
            tinted_surface = scaled_surface.copy()
            overlay = pygame.Surface(tinted_surface.get_size())
            overlay.fill(self.joystick_pressed_color)
            overlay.set_alpha(128)
            tinted_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.screen.blit(tinted_surface, moved_pos)
        else:
            self.screen.blit(scaled_surface, moved_pos)

        # Draw connection line and center point only when movement exceeds threshold
        distance = math.hypot(offset_x, offset_y)
        threshold_pixels = self.joystick_move_threshold * 40 * self.scale_x

        if distance > threshold_pixels:
            # Draw center point
            pygame.draw.circle(self.screen, (100, 200, 255), (center_x, center_y), 5)

            # Calculate line end point
            angle = math.atan2(offset_y, offset_x)
            line_length = min(40, distance * 1.5)
            end_x = center_x + int(line_length * math.cos(angle))
            end_y = center_y + int(line_length * math.sin(angle))

            # Draw connection line with color gradient
            pygame.draw.line(self.screen, (100, 200, 255), (center_x, center_y), (end_x, end_y), 3)

    def draw_trigonometric_circle(self, center, offset, is_left):
        """Draw trigonometric circle for joystick movement"""
        if center is None:
            return

        offset_x, offset_y = offset

        circle_radius = int(self.joystick_radius * min(self.scale_x, self.scale_y))
        circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)

        # Draw circle with transparency
        pygame.draw.circle(circle_surface, (*self.circle_color[:3], 150),
                           (circle_radius, circle_radius), circle_radius, 2)

        # Draw axes
        pygame.draw.line(circle_surface, self.circle_color,
                         (circle_radius, 0), (circle_radius, circle_radius * 2), 1)
        pygame.draw.line(circle_surface, self.circle_color,
                         (0, circle_radius), (circle_radius * 2, circle_radius), 1)

        # Draw current position if threshold is exceeded
        distance = math.hypot(offset_x, offset_y)
        if distance > self.joystick_move_threshold * 40:
            angle = math.atan2(offset_y, offset_x)
            indicator_x = circle_radius + int(circle_radius * 0.8 * math.cos(angle))
            indicator_y = circle_radius + int(circle_radius * 0.8 * math.sin(angle))
            pygame.draw.circle(circle_surface, (255, 100, 100, 200), (indicator_x, indicator_y), 5)

        circle_pos = (center[0] - circle_radius, center[1] - circle_radius)
        self.screen.blit(circle_surface, circle_pos)

    def draw_trigger(self, position_key, trigger_name):
        """Draw trigger using L2/R2 image with visual feedback"""
        base_pos = self.scale_position(self.positions[position_key])

        # Get trigger value (normalize from [-1, 1] to [0, 1])
        trigger_value = self.axis_values.get(trigger_name, 0)
        normalized_value = (trigger_value + 1) / 2

        # Determine asset name
        asset_name = 'l2' if 'l2' in trigger_name else 'r2'

        # Scale and position the trigger image
        scaled_surface = self.scale_surface(self.assets[asset_name])
        self.screen.blit(scaled_surface, base_pos)

        # Create a semi-transparent overlay for visual feedback
        overlay = pygame.Surface((100, int(100 * normalized_value)), pygame.SRCALPHA)

        # Color gradient based on pressure
        if normalized_value < 0.5:
            r = int(255 * (normalized_value * 2))
            g = 255
        else:
            r = 255
            g = int(255 * ((1 - normalized_value) * 2))
        b = 0

        # Create gradient overlay
        for i in range(overlay.get_height()):
            row_intensity = i / overlay.get_height()
            row_color = (r, g, b, int(150 * row_intensity))
            pygame.draw.line(overlay, row_color, (0, i), (overlay.get_width(), i))

        # Position overlay at the bottom of the trigger image
        overlay_pos = (base_pos[0], base_pos[1] + 100 - overlay.get_height())
        self.screen.blit(overlay, overlay_pos)

    def draw_controller(self):
        """Draw the complete PS5 controller with input feedback"""
        if self.left_stick_move_timer > 0:
            self.left_stick_move_timer -= 1
        if self.right_stick_move_timer > 0:
            self.right_stick_move_timer -= 1

        # Draw background gradient
        self.draw_gradient_background()

        # Draw L2/R2 triggers first
        self.draw_trigger('l2', 'l2')
        self.draw_trigger('r2', 'r2')

        # Right side elements
        r1_pressed = self.button_states.get('r1', False)
        self.blit_scaled('r1', 'r1', color_tint=self.pressed_color if r1_pressed else None)

        self.blit_scaled('white_right', 'white_right')
        self.blit_scaled('black_right', 'black_right')
        self.blit_scaled('right_side', 'right_side')
        self.blit_scaled('blue_highlight_right', 'blue_highlight_right')

        # Right buttons with state feedback
        self.draw_right_buttons()

        # Right side controls
        self.draw_joystick_with_movement('joystick', 'right_joystick', self.right_stick_pos, 'r3', is_left=False)
        self.blit_scaled('right_icon', 'right_icon')

        option_pressed = self.button_states.get('option', False)
        self.blit_scaled('option_button', 'option_button', color_tint=self.pressed_color if option_pressed else None)

        # Left side elements
        l1_pressed = self.button_states.get('l1', False)
        self.blit_scaled('l1', 'l1', color_tint=self.pressed_color if l1_pressed else None)

        self.blit_scaled('white_left', 'white_left')
        self.blit_scaled('black_left', 'black_left')
        self.blit_scaled('left_side', 'left_side')
        self.blit_scaled('blue_highlight_left', 'blue_highlight_left')

        # D-pad with state feedback
        self.draw_dpad_with_state()

        # Left side controls
        self.draw_joystick_with_movement('joystick', 'left_joystick', self.left_stick_pos, 'l3', is_left=True)
        self.blit_scaled('left_icon', 'left_icon')

        share_pressed = self.button_states.get('share', False)
        self.blit_scaled('share_button', 'share_button', color_tint=self.pressed_color if share_pressed else None)

        # Center elements
        touchpad_pressed = self.button_states.get('touchpad', False)
        self.blit_scaled('center_pad', 'center_pad', color_tint=self.pressed_color if touchpad_pressed else None)

        self.blit_scaled('highlight', 'highlight')
        self.blit_scaled('speaker', 'speaker')

        # Highlight all PS logo parts when PS button is pressed
        ps_pressed = self.button_states.get('ps', False)
        self.blit_scaled('ps_logo_under', 'ps_logo_under', color_tint=self.pressed_color if ps_pressed else None)
        self.blit_scaled('ps_logo_upper', 'ps_logo_upper', color_tint=self.pressed_color if ps_pressed else None)
        self.blit_scaled('ps_logo_under_layout', 'ps_logo_under_layout',
                         color_tint=self.pressed_color if ps_pressed else None)
        self.blit_scaled('ps_logo_upper_layout', 'ps_logo_upper_layout',
                         color_tint=self.pressed_color if ps_pressed else None)

        self.blit_scaled('voice_button_highlight', 'voice_button_highlight')
        self.blit_scaled('voice_button', 'voice_button')
        self.blit_scaled('icon_mute', 'icon_mute')
        self.blit_scaled('loudspeaker', 'loudspeaker')

        # Draw trigonometric circles only if movement exceeds threshold
        if self.left_joystick_center and self.left_stick_move_timer > 0:
            # Only show if movement exceeds threshold
            if (abs(self.left_stick_pos[0]) > self.joystick_move_threshold * 40 or
                    abs(self.left_stick_pos[1]) > self.joystick_move_threshold * 40):
                self.draw_trigonometric_circle(self.left_joystick_center, self.left_stick_pos, True)

        if self.right_joystick_center and self.right_stick_move_timer > 0:
            # Only show if movement exceeds threshold
            if (abs(self.right_stick_pos[0]) > self.joystick_move_threshold * 40 or
                    abs(self.right_stick_pos[1]) > self.joystick_move_threshold * 40):
                self.draw_trigonometric_circle(self.right_joystick_center, self.right_stick_pos, False)

    def draw_gradient_background(self):
        """Draw a gradient background for better visual appeal"""
        for y in range(self.height):
            # Calculate gradient color (darker at top, lighter at bottom)
            color_value = 20 + int(30 * (y / self.height))
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 10),
                             (0, y), (self.width, y))

    def draw_no_controller_screen(self):
        """Draw screen when no controller is connected"""
        # Draw gradient background
        self.draw_gradient_background()

        # Draw title
        title = self.title_font.render("PS5 Controller Tester", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Draw warning message
        warning = self.font.render("No controller detected!", True, (255, 100, 100))
        self.screen.blit(warning, (self.width // 2 - warning.get_width() // 2, 150))

        # Draw instructions
        instruction1 = self.font.render("Please connect a PS5 controller to your computer", True, (200, 200, 200))
        instruction2 = self.font.render("Press 'R' to rescan for controllers", True, (200, 200, 200))
        instruction3 = self.font.render("Press ESC to exit", True, (200, 200, 200))

        self.screen.blit(instruction1, (self.width // 2 - instruction1.get_width() // 2, 220))
        self.screen.blit(instruction2, (self.width // 2 - instruction2.get_width() // 2, 260))
        self.screen.blit(instruction3, (self.width // 2 - instruction3.get_width() // 2, 300))

        # Draw controller icon
        if 'icon' in self.assets:
            icon = pygame.transform.scale(self.assets['icon'], (200, 200))
            self.screen.blit(icon, (self.width // 2 - 100, 350))

    def handle_resize(self, new_width, new_height):
        """Handle window resize"""
        self.width = new_width
        self.height = new_height
        self.scale_x = (new_width / self.base_width) * self.controller_scale
        self.scale_y = (new_height / self.base_height) * self.controller_scale
        self.screen = pygame.display.set_mode((new_width, new_height))

        self.controller_offset_x = (new_width - (self.base_width * self.scale_x)) // 2
        self.controller_offset_y = (new_height - (self.base_height * self.scale_y)) // 2

    def run(self):
        """Main game loop with robust error handling"""
        running = True

        while running:
            # Handle events with robust error handling
            try:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self.handle_resize(event.w, event.h)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.check_controller()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
            except Exception as e:
                print(f"Error processing events: {e}")
                # Reset controller state on error
                self.controller_connected = False
                self.joystick = None
                self.check_controller()

            # Update controller input
            try:
                if self.controller_connected:
                    self.update_controller_input()
            except Exception as e:
                print(f"Error updating controller: {e}")
                self.controller_connected = False
                self.joystick = None

            # Clear screen
            self.screen.fill((20, 20, 30))

            # Draw appropriate screen based on connection status
            if self.controller_connected:
                try:
                    self.draw_controller()
                except Exception as e:
                    print(f"Error drawing controller: {e}")
            else:
                self.draw_no_controller_screen()

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    tester = PS5ControllerTester(1000, 664)
    tester.run()
import arcade

class InputHandler:
    """Component that handles keyboard input and maps to actions"""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.keys_pressed = set()
    
    def process_key_press(self, key, modifiers):
        """Process a key press event"""
        self.keys_pressed.add(key)
        
        if key == arcade.key.SPACE:
            self.simulator.robot.stop()
            self.simulator.add_serial_message("STP command", "tx")
        elif key == arcade.key.A:
            # Toggle autopilot
            self.simulator.autopilot = not self.simulator.autopilot
            self.simulator.add_serial_message(f"Autopilot {'ON' if self.simulator.autopilot else 'OFF'}", "tx")
        elif key == arcade.key.R:
            # Reset robot position
            self.simulator.robot.x = self.simulator.width // 2
            self.simulator.robot.y = self.simulator.height // 2
            self.simulator.robot.direction = 0
        elif key == arcade.key.S:
            # Toggle serial monitor
            self.simulator.show_serial_monitor = not self.simulator.show_serial_monitor
        elif key == arcade.key.D:
            # Toggle dashboard
            self.simulator.show_dashboard = not self.simulator.show_dashboard
        elif key == arcade.key.V:
            # Toggle voice panel
            self.simulator.show_voice_panel = not self.simulator.show_voice_panel
        elif key == arcade.key.H:
            # Toggle help/controls panel
            self.simulator.controls_panel.toggle()
        elif key == arcade.key.W:
            # Simulate wake word
            if self.simulator.show_voice_panel:
                self.simulator.voice_panel.activate_wake_word()
        elif key == arcade.key.C:
            # Execute the selected test command
            if self.simulator.show_voice_panel:
                command = self.simulator.voice_panel.get_selected_command()
                self.simulator._handle_voice_command(command)
                self.simulator.voice_panel.show_command_feedback(command)
        elif key == arcade.key.LEFT:
            if self.simulator.show_voice_panel and modifiers & arcade.key.MOD_SHIFT:
                # Previous test command
                self.simulator.voice_panel.select_prev_command()
            else:
                # Turn robot left
                self.simulator.robot.turn_left(0.5)
                self.simulator.add_serial_message("LFT command", "tx")
        elif key == arcade.key.RIGHT:
            if self.simulator.show_voice_panel and modifiers & arcade.key.MOD_SHIFT:
                # Next test command
                self.simulator.voice_panel.select_next_command()
            else:
                # Turn robot right
                self.simulator.robot.turn_right(0.5)
                self.simulator.add_serial_message("RGT command", "tx")
        elif key == arcade.key.Q or key == arcade.key.ESCAPE:
            print("Exit key pressed - closing window")
            self.simulator.close()
            arcade.exit()
    
    def process_key_release(self, key, modifiers):
        """Process a key release event"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def process_update(self):
        """Process ongoing key presses during update cycle"""
        if arcade.key.UP in self.keys_pressed:
            self.simulator.robot.move_forward(0.5)
            self.simulator.add_serial_message("FWD command", "tx")
        elif arcade.key.DOWN in self.keys_pressed:
            self.simulator.robot.move_backward(0.5)
            self.simulator.add_serial_message("BCK command", "tx")
        elif arcade.key.LEFT in self.keys_pressed:
            self.simulator.robot.turn_left(0.5)
        elif arcade.key.RIGHT in self.keys_pressed:
            self.simulator.robot.turn_right(0.5)

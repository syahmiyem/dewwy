import arcade

class ControlsPanel:
    """Panel for displaying keyboard controls"""
    
    def __init__(self):
        # Control groups
        self.control_groups = {
            "Movement": [
                {"key": "↑", "action": "Forward"},
                {"key": "↓", "action": "Backward"},
                {"key": "←", "action": "Turn Left"},
                {"key": "→", "action": "Turn Right"},
                {"key": "Space", "action": "Stop"}
            ],
            "Display": [
                {"key": "D", "action": "Dashboard"},
                {"key": "S", "action": "Serial"},
                {"key": "V", "action": "Voice Panel"}
            ],
            "Voice": [
                {"key": "W", "action": "Wake Word"},
                {"key": "C", "action": "Command"}
            ],
            "System": [
                {"key": "A", "action": "Autopilot"},
                {"key": "R", "action": "Reset Position"},
                {"key": "Q/ESC", "action": "Quit"}
            ]
        }
        
        self.show_panel = False  # Default hidden
        
    def toggle(self):
        """Toggle panel visibility"""
        self.show_panel = not self.show_panel
    
    def draw(self, x, y, width=200, height=300):
        """Draw the controls panel"""
        if not self.show_panel:
            # Just draw a small help button when hidden
            arcade.draw_rectangle_filled(
                x, y, 30, 30,
                (40, 44, 52, 200)
            )
            
            arcade.draw_text(
                "?",
                x - 5, y - 12,
                arcade.color.WHITE,
                18,
                bold=True
            )
            return
            
        # Background panel
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (40, 44, 52, 230)  # Dark semi-transparent background
        )
        
        # Panel border
        arcade.draw_rectangle_outline(
            x, y, width, height,
            (80, 90, 100),
            2
        )
        
        # Title
        arcade.draw_text(
            "KEYBOARD CONTROLS",
            x - width/2 + 10, y + height/2 - 25,
            arcade.color.WHITE,
            16,
            bold=True
        )
        
        # Horizontal separator
        arcade.draw_line(
            x - width/2 + 10, y + height/2 - 35,
            x + width/2 - 10, y + height/2 - 35,
            arcade.color.GRAY,
            1
        )
        
        # Draw each control group
        y_offset = y + height/2 - 55
        for group_name, controls in self.control_groups.items():
            # Group header
            arcade.draw_text(
                group_name,
                x - width/2 + 15, y_offset,
                arcade.color.LIGHT_BLUE,
                14,
                bold=True
            )
            
            y_offset -= 20
            
            # Controls in this group
            for control in controls:
                # Key in bold
                arcade.draw_text(
                    control["key"],
                    x - width/2 + 20, y_offset,
                    arcade.color.YELLOW,
                    12,
                    bold=True
                )
                
                # Description
                arcade.draw_text(
                    control["action"],
                    x - width/2 + 50, y_offset,
                    arcade.color.WHITE,
                    12
                )
                
                y_offset -= 18
            
            # Space between groups
            y_offset -= 5

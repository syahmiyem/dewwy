import time
import random

class RobotState:
    IDLE = "idle"
    ROAMING = "roaming"
    AVOIDING = "avoiding"
    INTERACTING = "interacting"
    SEARCHING = "searching"
    SLEEPING = "sleeping"

class RobotStateMachine:
    def __init__(self, sensor, motors, personality=None):
        self.current_state = RobotState.IDLE
        self.sensor = sensor  # Ultrasonic sensor interface
        self.motors = motors  # Motor control interface
        self.personality = personality  # Robot personality traits
        
        # State configuration
        self.min_obstacle_distance = 20  # cm
        self.last_state_change = time.time()
        self.state_duration = {
            RobotState.IDLE: (5, 15),      # 5-15 seconds
            RobotState.ROAMING: (20, 60),   # 20-60 seconds
            RobotState.SLEEPING: (10, 30),  # 10-30 seconds
        }
        
        # Initialize state handlers
        self.state_handlers = {
            RobotState.IDLE: self._handle_idle,
            RobotState.ROAMING: self._handle_roaming,
            RobotState.AVOIDING: self._handle_avoiding,
            RobotState.INTERACTING: self._handle_interacting,
            RobotState.SEARCHING: self._handle_searching,
            RobotState.SLEEPING: self._handle_sleeping
        }
    
    def update(self):
        """Main update method to be called in the robot's main loop"""
        # Check for obstacles regardless of state
        distance = self.sensor.measure_distance()
        
        # Override current state if obstacle detected (except if already avoiding)
        if distance < self.min_obstacle_distance and self.current_state != RobotState.AVOIDING:
            if self.current_state != RobotState.AVOIDING:
                self.transition_to(RobotState.AVOIDING)
        
        # Check if we should transition based on time
        current_time = time.time()
        if self.current_state in self.state_duration:
            min_time, max_time = self.state_duration[self.current_state]
            if (current_time - self.last_state_change) > random.uniform(min_time, max_time):
                self._choose_next_state()
        
        # Execute current state handler
        if self.current_state in self.state_handlers:
            self.state_handlers[self.current_state]()
    
    def transition_to(self, new_state):
        """Transition to a new state"""
        print(f"State transition: {self.current_state} -> {new_state}")
        self.current_state = new_state
        self.last_state_change = time.time()
        
        # Update personality/emotion if available
        if self.personality:
            self.personality.on_state_change(new_state)
    
    def _choose_next_state(self):
        """Choose next state based on current state and personality"""
        if self.current_state == RobotState.IDLE:
            # After being idle, either roam or sleep
            choices = [RobotState.ROAMING, RobotState.SEARCHING, RobotState.SLEEPING]
            self.transition_to(random.choice(choices))
        
        elif self.current_state == RobotState.ROAMING or self.current_state == RobotState.SEARCHING:
            # After roaming, become idle
            self.transition_to(RobotState.IDLE)
        
        elif self.current_state == RobotState.SLEEPING:
            # After sleeping, become idle
            self.transition_to(RobotState.IDLE)
    
    # State handlers
    def _handle_idle(self):
        """Idle state behavior"""
        self.motors.stop()
    
    def _handle_roaming(self):
        """Roaming state behavior"""
        # Randomly change direction occasionally
        if random.random() < 0.05:  # 5% chance per update
            choice = random.choice(['left', 'right', 'forward'])
            if choice == 'left':
                self.motors.turn_left(0.5)
                time.sleep(0.5)
            elif choice == 'right':
                self.motors.turn_right(0.5)
                time.sleep(0.5)
        else:
            self.motors.move_forward(0.7)
    
    def _handle_avoiding(self):
        """Obstacle avoidance behavior"""
        self.motors.stop()
        time.sleep(0.5)
        
        # Decide whether to turn left or right
        if random.choice([True, False]):
            self.motors.turn_left(0.8)
        else:
            self.motors.turn_right(0.8)
        
        time.sleep(1.0)  # Turn for a second
        
        # Check if obstacle is still there
        distance = self.sensor.measure_distance()
        if distance > self.min_obstacle_distance:
            self.transition_to(RobotState.ROAMING)
    
    def _handle_interacting(self):
        """Interacting with human behavior"""
        self.motors.stop()
        # In real implementation, this would include more complex interaction logic
    
    def _handle_searching(self):
        """Searching behavior - looking for something or someone"""
        # Move forward slowly while turning head
        self.motors.move_forward(0.4)
        # In hardware implementation, would move a servo for "head" movement
    
    def _handle_sleeping(self):
        """Sleeping behavior"""
        self.motors.stop()
        # In real implementation, this might include dimming displays, etc.

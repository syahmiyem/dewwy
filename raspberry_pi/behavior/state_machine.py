import time
import random

class RobotState:
    IDLE = "idle"
    ROAMING = "roaming"
    AVOIDING = "avoiding"
    INTERACTING = "interacting"
    SEARCHING = "searching"
    SLEEPING = "sleeping"
    PLAYING = "playing"     # New playful state
    STARTLED = "startled"   # New startled reaction state
    CURIOUS = "curious"     # Curiosity-driven behavior

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
            RobotState.IDLE: (3, 15),       # 3-15 seconds of idling
            RobotState.ROAMING: (10, 30),   # 10-30 seconds of roaming
            RobotState.SLEEPING: (10, 40),  # 10-40 seconds of sleeping
            RobotState.PLAYING: (5, 15),    # 5-15 seconds of playing
            RobotState.STARTLED: (1, 3),    # Brief startled reactions
            RobotState.CURIOUS: (5, 15),    # 5-15 seconds of curious investigation
        }
        
        # Pet-like behavior variables
        self.boredom_level = 0          # Increases over time, triggers playful behavior
        self.curiosity_level = 0        # Increases during idle, triggers exploration
        self.tiredness_level = 0        # Increases during activity, triggers sleeping
        self.interest_points = []       # Things the robot finds interesting
        self.attention_span = random.randint(5, 15)  # How long it focuses on one thing
        
        # Movement patterns for different states
        self.idle_fidget_chance = 0.05  # Chance to fidget while idle
        
        # Initialize state handlers
        self.state_handlers = {
            RobotState.IDLE: self._handle_idle,
            RobotState.ROAMING: self._handle_roaming,
            RobotState.AVOIDING: self._handle_avoiding,
            RobotState.INTERACTING: self._handle_interacting,
            RobotState.SEARCHING: self._handle_searching,
            RobotState.SLEEPING: self._handle_sleeping,
            RobotState.PLAYING: self._handle_playing,
            RobotState.STARTLED: self._handle_startled,
            RobotState.CURIOUS: self._handle_curious
        }
    
    def update(self):
        """Main update method to be called in the robot's main loop"""
        # Update pet-like behavior metrics
        self._update_behavior_metrics()
        
        # Check for obstacles regardless of state
        distance = self.sensor.measure_distance()
        
        # Potentially get startled by sudden obstacle appearance
        if (distance < self.min_obstacle_distance * 2 and 
            distance < self.last_distance * 0.7 and  # Sudden drop in distance
            self.current_state != RobotState.AVOIDING and
            self.current_state != RobotState.STARTLED and
            random.random() < 0.3):  # 30% chance to startle
            self.transition_to(RobotState.STARTLED)
        
        # Override current state if obstacle is too close and we're not already avoiding
        elif distance < self.min_obstacle_distance and self.current_state != RobotState.AVOIDING:
            self.transition_to(RobotState.AVOIDING)
        
        # Save last distance reading
        self.last_distance = distance
        
        # Check if we should transition based on time
        current_time = time.time()
        if self.current_state in self.state_duration:
            min_time, max_time = self.state_duration[self.current_state]
            if (current_time - self.last_state_change) > random.uniform(min_time, max_time):
                self._choose_next_state()
        
        # Pet-like behavior triggers
        if self.boredom_level > 70 and self.current_state not in [RobotState.PLAYING, RobotState.STARTLED, RobotState.AVOIDING]:
            # When bored, start playing
            self.transition_to(RobotState.PLAYING)
            self.boredom_level = 0
        
        elif self.tiredness_level > 80 and self.current_state not in [RobotState.SLEEPING, RobotState.AVOIDING]:
            # When tired, go to sleep
            self.transition_to(RobotState.SLEEPING)
            self.tiredness_level = 0
        
        elif self.curiosity_level > 90 and self.current_state == RobotState.IDLE:
            # When curious while idle, start investigating
            self.transition_to(RobotState.CURIOUS)
            self.curiosity_level = 0
        
        # Execute current state handler
        if self.current_state in self.state_handlers:
            self.state_handlers[self.current_state]()
    
    def _update_behavior_metrics(self):
        """Update pet-like behavior metrics based on time and state"""
        # Boredom increases faster during idle states
        if self.current_state == RobotState.IDLE:
            self.boredom_level = min(100, self.boredom_level + random.uniform(0.2, 0.5))
            self.curiosity_level = min(100, self.curiosity_level + random.uniform(0.3, 0.8))
            self.tiredness_level = max(0, self.tiredness_level - random.uniform(0.1, 0.3))
        
        # Tiredness increases during active states
        elif self.current_state in [RobotState.ROAMING, RobotState.PLAYING, RobotState.AVOIDING]:
            self.tiredness_level = min(100, self.tiredness_level + random.uniform(0.1, 0.4))
            self.boredom_level = max(0, self.boredom_level - random.uniform(0.2, 0.6))
        
        # Sleeping decreases tiredness
        elif self.current_state == RobotState.SLEEPING:
            self.tiredness_level = max(0, self.tiredness_level - random.uniform(0.5, 1.0))
            self.boredom_level = min(100, self.boredom_level + random.uniform(0.1, 0.2))
    
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
        weights = {}
        
        if self.current_state == RobotState.IDLE:
            # After being idle, consider multiple states based on current metrics
            weights = {
                RobotState.ROAMING: 30 + self.boredom_level * 0.3,
                RobotState.SLEEPING: max(5, self.tiredness_level * 0.7),
                RobotState.CURIOUS: self.curiosity_level * 0.5,
                RobotState.PLAYING: self.boredom_level * 0.2
            }
        
        elif self.current_state == RobotState.ROAMING:
            # After roaming, likely to become idle, sometimes curious
            weights = {
                RobotState.IDLE: 60,
                RobotState.CURIOUS: 20,
                RobotState.PLAYING: 10 + self.boredom_level * 0.1,
                RobotState.SLEEPING: max(5, self.tiredness_level * 0.3)
            }
        
        elif self.current_state == RobotState.SLEEPING:
            # After sleeping, become idle
            weights = {
                RobotState.IDLE: 80,
                RobotState.ROAMING: 20
            }
        
        elif self.current_state == RobotState.PLAYING:
            # After playing, either idle or roam
            weights = {
                RobotState.IDLE: 60,
                RobotState.ROAMING: 30,
                RobotState.SLEEPING: max(5, self.tiredness_level * 0.2)
            }
        
        elif self.current_state == RobotState.STARTLED:
            # After being startled, calm down to idle or run away (roam)
            weights = {
                RobotState.IDLE: 40,
                RobotState.ROAMING: 60
            }
        
        elif self.current_state == RobotState.AVOIDING:
            # After avoiding, resume previous activity or idle
            weights = {
                RobotState.IDLE: 70,
                RobotState.ROAMING: 30
            }
        
        elif self.current_state == RobotState.CURIOUS:
            # After being curious, either idle or continue roaming
            weights = {
                RobotState.IDLE: 60,
                RobotState.ROAMING: 40
            }
        
        else:
            # Default behavior for any other states
            weights = {
                RobotState.IDLE: 100
            }
            
        # Choose next state based on weights
        choices, weights_list = zip(*weights.items())
        next_state = random.choices(choices, weights=weights_list, k=1)[0]
        self.transition_to(next_state)
    
    # State handlers
    def _handle_idle(self):
        """Idle state behavior"""
        self.motors.stop()
        
        # Occasionally fidget while idle
        if random.random() < self.idle_fidget_chance:
            # Small random movements to look alive
            if random.random() < 0.5:
                self.motors.turn_left(0.1)
                time.sleep(0.1)
            else:
                self.motors.turn_right(0.1)
                time.sleep(0.1)
            self.motors.stop()
    
    def _handle_roaming(self):
        """Roaming state behavior"""
        # Random movement patterns that seem pet-like
        decision = random.random()
        
        if decision < 0.7:  # 70% chance to just move forward
            self.motors.move_forward(random.uniform(0.3, 0.7))
        elif decision < 0.85:  # 15% chance to turn left while moving
            self.motors.turn_left(random.uniform(0.2, 0.6))
            self.motors.move_forward(0.4)
        else:  # 15% chance to turn right while moving
            self.motors.turn_right(random.uniform(0.2, 0.6))
            self.motors.move_forward(0.4)
    
    def _handle_avoiding(self):
        """Obstacle avoidance behavior"""
        # Existing avoidance logic...
        self.motors.stop()
        time.sleep(0.2)
        
        # Decide whether to turn left or right
        if random.choice([True, False]):
            self.motors.turn_left(0.8)
        else:
            self.motors.turn_right(0.8)
        
        time.sleep(random.uniform(0.5, 1.0))  # Variable turning time
        
        # Check if obstacle is still there
        distance = self.sensor.measure_distance()
        if distance > self.min_obstacle_distance * 1.5:  # Make sure we have enough clearance
            self.transition_to(RobotState.ROAMING)
    
    def _handle_playing(self):
        """Playful behavior with quick, random movements"""
        # Choose a random playful behavior
        play_behavior = random.randint(0, 3)
        
        if play_behavior == 0:
            # Quick spin
            turn_direction = random.choice([self.motors.turn_left, self.motors.turn_right])
            turn_direction(0.7)
            time.sleep(random.uniform(0.3, 0.7))
            self.motors.stop()
            
        elif play_behavior == 1:
            # Short dash forward
            self.motors.move_forward(0.8)
            time.sleep(random.uniform(0.2, 0.5))
            self.motors.stop()
            
        elif play_behavior == 2:
            # Wiggle (alternate left-right quickly)
            for _ in range(random.randint(2, 5)):
                self.motors.turn_left(0.5)
                time.sleep(0.1)
                self.motors.turn_right(0.5)
                time.sleep(0.1)
            self.motors.stop()
            
        elif play_behavior == 3:
            # Reverse and turn
            self.motors.move_backward(0.6)
            time.sleep(0.2)
            turn_direction = random.choice([self.motors.turn_left, self.motors.turn_right])
            turn_direction(0.6)
            time.sleep(0.3)
            self.motors.stop()
    
    def _handle_startled(self):
        """Reaction when startled"""
        # Quick reverse motion
        self.motors.move_backward(1.0)
        time.sleep(random.uniform(0.3, 0.6))
        
        # Quick turn in random direction
        if random.choice([True, False]):
            self.motors.turn_left(1.0)
        else:
            self.motors.turn_right(1.0)
        
        time.sleep(random.uniform(0.3, 0.7))
        self.motors.stop()
    
    def _handle_curious(self):
        """Curious investigation behavior"""
        # Slower, more deliberate movements with pauses
        
        # Move a bit
        self.motors.move_forward(0.3)
        time.sleep(random.uniform(0.3, 0.7))
        
        # Stop and look around (turn slightly left or right)
        self.motors.stop()
        time.sleep(0.5)  # Pause to "observe"
        
        if random.random() < 0.5:
            self.motors.turn_left(0.2)
        else:
            self.motors.turn_right(0.2)
            
        time.sleep(random.uniform(0.2, 0.5))
        self.motors.stop()
    
    def _handle_interacting(self):
        """Interacting with human behavior"""
        # Stop movement
        self.motors.stop()
        
        # Show attentiveness by tracking (simulated here with small turns)
        if random.random() < 0.3:
            if random.random() < 0.5:
                self.motors.turn_left(0.1)
            else:
                self.motors.turn_right(0.1)
            time.sleep(0.1)
            self.motors.stop()
    
    def _handle_searching(self):
        """Searching behavior - looking for something or someone"""
        # Move forward slowly while turning head
        self.motors.move_forward(0.3)
        time.sleep(0.3)
        
        # Stop and look around
        self.motors.stop()
        
        if random.random() < 0.6:  # 60% chance to turn and look
            turn_func = self.motors.turn_left if random.random() < 0.5 else self.motors.turn_right
            turn_func(0.2)
            time.sleep(random.uniform(0.2, 0.5))
            self.motors.stop()
    
    def _handle_sleeping(self):
        """Sleeping behavior"""
        # Just stop and occasionally "breathe" (small movements)
        self.motors.stop()
        
        # Occasionally make small movement like breathing
        if random.random() < 0.05:  # 5% chance per update
            if random.random() < 0.5:
                self.motors.turn_left(0.05)  # Very slight turn
            else:
                self.motors.turn_right(0.05)  # Very slight turn
            time.sleep(0.1)
            self.motors.stop()

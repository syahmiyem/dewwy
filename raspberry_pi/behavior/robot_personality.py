import random
import time
import sqlite3
from pathlib import Path

class Emotion:
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    NEUTRAL = "neutral"
    SLEEPY = "sleepy"
    CURIOUS = "curious"
    SCARED = "scared"
    PLAYFUL = "playful"  # New playful emotion
    GRUMPY = "grumpy"    # New grumpy emotion

class RobotPersonality:
    def __init__(self, db_path="robot_memory.db", display=None):
        self.current_emotion = Emotion.NEUTRAL
        self.display = display  # OLED display interface
        self.last_emotion_change = time.time()
        
        # Personality traits (1-10 scale)
        self.traits = {
            "openness": 7,       # Curiosity and openness to experience
            "friendliness": 8,   # How friendly the robot acts
            "activeness": 6,     # How much the robot likes to move around
            "expressiveness": 7, # How strongly the robot shows emotions
            "patience": 5        # How patient the robot is
        }
        
        # Initialize memory database
        self._init_memory_db(db_path)
        
        # Add mood tracking
        self.mood_duration = {
            Emotion.HAPPY: (30, 120),     # 30-120 seconds
            Emotion.SAD: (30, 90),        # 30-90 seconds
            Emotion.EXCITED: (20, 60),    # 20-60 seconds
            Emotion.NEUTRAL: (60, 180),   # 60-180 seconds
            Emotion.SLEEPY: (40, 120),    # 40-120 seconds
            Emotion.CURIOUS: (30, 60),    # 30-60 seconds
            Emotion.SCARED: (10, 30),     # 10-30 seconds
            Emotion.PLAYFUL: (30, 90),    # 30-90 seconds
            Emotion.GRUMPY: (30, 60)      # 30-60 seconds
        }
        
        # Chance of random emotion changes
        self.random_emotion_chance = 0.01  # 1% chance per update
        
        # New emotional reactive multipliers
        self.emotional_reactivity = random.uniform(0.8, 1.2)  # Personality trait
        
        # Timestamps for mood changes
        self.last_random_mood_check = time.time()
        self.mood_check_interval = 5  # Check for random mood changes every 5 seconds
    
    def _init_memory_db(self, db_path):
        """Initialize the SQLite database for robot memory"""
        self.db_path = db_path
        db = Path(db_path)
        
        # Create parent directory if it doesn't exist
        db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create tables if they don't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                interaction_type TEXT,
                details TEXT,
                emotion TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS learning (
                id INTEGER PRIMARY KEY,
                keyword TEXT,
                response TEXT,
                confidence REAL,
                times_used INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def on_state_change(self, new_state):
        """React emotionally to state changes"""
        from raspberry_pi.behavior.state_machine import RobotState
        
        # Store current state for reference
        self._current_robot_state = new_state
        
        # React more strongly based on emotional reactivity
        react_chance = 0.7 * self.emotional_reactivity  # Base 70% chance to react
        
        if new_state == RobotState.IDLE:
            if random.random() < react_chance:
                self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.ROAMING:
            # More active personality types get more excited about roaming
            if self.traits["activeness"] > 7:
                if random.random() < react_chance:
                    self.set_emotion(Emotion.EXCITED)
            else:
                if random.random() < react_chance:
                    self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.AVOIDING:
            # Less patient robots get scared easier
            if self.traits["patience"] < 4:
                if random.random() < react_chance:
                    self.set_emotion(Emotion.SCARED)
            else:
                # More patient ones just get grumpy or neutral
                if random.random() < react_chance:
                    self.set_emotion(random.choice([Emotion.GRUMPY, Emotion.NEUTRAL]))
        
        elif new_state == RobotState.INTERACTING:
            # Friendly robots get happier during interactions
            if self.traits["friendliness"] > 6:
                if random.random() < react_chance:
                    self.set_emotion(Emotion.HAPPY)
            else:
                if random.random() < react_chance:
                    self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.SEARCHING:
            if random.random() < react_chance:
                self.set_emotion(Emotion.CURIOUS)
        
        elif new_state == RobotState.SLEEPING:
            if random.random() < react_chance:
                self.set_emotion(Emotion.SLEEPY)
        
        elif new_state == RobotState.PLAYING:
            if random.random() < react_chance:
                self.set_emotion(random.choice([Emotion.PLAYFUL, Emotion.EXCITED, Emotion.HAPPY]))
        
        elif new_state == RobotState.STARTLED:
            if random.random() < react_chance:
                self.set_emotion(Emotion.SCARED)
        
        elif new_state == RobotState.CURIOUS:
            if random.random() < react_chance:
                self.set_emotion(Emotion.CURIOUS)
    
    def set_emotion(self, emotion):
        """Set the robot's current emotional state"""
        self.current_emotion = emotion
        
        # Update display if available
        if self.display:
            self.display.set_emotion(emotion)
            
        self.last_emotion_change = time.time()
        
        # Log the emotion change
        self._log_interaction("emotion_change", f"Changed to {emotion}")
    
    def get_emotion(self):
        """Get the current emotion"""
        return self.current_emotion
    
    def _log_interaction(self, interaction_type, details):
        """Log an interaction to the memory database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            c.execute(
                "INSERT INTO interactions (timestamp, interaction_type, details, emotion) VALUES (?, ?, ?, ?)",
                (timestamp, interaction_type, details, self.current_emotion)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log interaction: {e}")
    
    def learn_response(self, keyword, response):
        """Learn a response to a keyword"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if we already know this keyword
            c.execute("SELECT id, confidence, times_used FROM learning WHERE keyword=?", (keyword,))
            result = c.fetchone()
            
            if result:
                # Update existing response with increased confidence
                entry_id, confidence, times_used = result
                new_confidence = min(confidence + 0.1, 1.0)
                c.execute("UPDATE learning SET response=?, confidence=?, times_used=? WHERE id=?", 
                         (response, new_confidence, times_used+1, entry_id))
            else:
                # Add new response
                c.execute("INSERT INTO learning (keyword, response, confidence, times_used) VALUES (?, ?, ?, ?)",
                         (keyword, response, 0.5, 1))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to learn response: {e}")
    
    def get_learned_response(self, keyword):
        """Get a learned response for a keyword"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("SELECT response, confidence FROM learning WHERE keyword=?", (keyword,))
            result = c.fetchone()
            
            conn.close()
            
            if result and result[1] > 0.4:  # Only return if confidence is high enough
                return result[0]
            return None
        except Exception as e:
            print(f"Failed to retrieve response: {e}")
            return None
    
    def update(self):
        """Update emotions periodically based on personality"""
        current_time = time.time()
        
        # Check if it's time for a possible random emotion change
        if current_time - self.last_random_mood_check > self.mood_check_interval:
            self.last_random_mood_check = current_time
            
            # Small chance of random emotion change
            if random.random() < self.random_emotion_chance:
                self._trigger_random_emotion()
            
            # Check if current emotion has lasted its duration
            if current_time - self.last_emotion_change > self._get_emotion_duration():
                # Transition back to neutral after other emotions wear off
                if self.current_emotion != Emotion.NEUTRAL:
                    self.set_emotion(Emotion.NEUTRAL)
    
    def _trigger_random_emotion(self):
        """Trigger a random emotion based on personality traits"""
        # Weight emotions based on personality traits
        weights = {
            Emotion.HAPPY: 10 * self.traits["friendliness"],
            Emotion.SAD: 10 * (10 - self.traits["friendliness"]),
            Emotion.EXCITED: 10 * self.traits["expressiveness"],
            Emotion.SLEEPY: 5 * (10 - self.traits["activeness"]),
            Emotion.CURIOUS: 10 * self.traits["openness"],
            Emotion.PLAYFUL: 10 * self.traits["activeness"],
            Emotion.GRUMPY: 10 * (10 - self.traits["patience"]),
        }
        
        # Skip certain emotions in certain states
        from raspberry_pi.behavior.state_machine import RobotState
        
        # Exclude emotions that don't make sense in certain states
        excluded_emotions = []
        
        # Map a list of emotions to exclude for each state
        state_exclusions = {
            RobotState.SLEEPING: [Emotion.EXCITED, Emotion.PLAYFUL, Emotion.CURIOUS],
            RobotState.PLAYING: [Emotion.SLEEPY, Emotion.SAD],
            RobotState.AVOIDING: [Emotion.SLEEPY],
            # Add more exclusions as needed
        }
        
        # Get current robot state (access via a cache or other mechanism)
        current_state = getattr(self, '_current_robot_state', None)
        if current_state in state_exclusions:
            excluded_emotions.extend(state_exclusions[current_state])
        
        # Remove excluded emotions from the weights
        for emotion in excluded_emotions:
            if emotion in weights:
                del weights[emotion]
        
        # Choose a random emotion
        emotions = list(weights.keys())
        emotion_weights = list(weights.values())
        
        if emotions and emotion_weights:
            new_emotion = random.choices(emotions, weights=emotion_weights, k=1)[0]
            self.set_emotion(new_emotion)
    
    def _get_emotion_duration(self):
        """Get the duration for the current emotion"""
        if self.current_emotion in self.mood_duration:
            min_time, max_time = self.mood_duration[self.current_emotion]
            return random.uniform(min_time, max_time)
        return 60  # Default duration

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
        
        if new_state == RobotState.IDLE:
            self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.ROAMING:
            # More active personality types get more excited about roaming
            if self.traits["activeness"] > 7:
                self.set_emotion(Emotion.EXCITED)
            else:
                self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.AVOIDING:
            # Less patient robots get scared easier
            if self.traits["patience"] < 4:
                self.set_emotion(Emotion.SCARED)
            else:
                self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.INTERACTING:
            # Friendly robots get happier during interactions
            if self.traits["friendliness"] > 6:
                self.set_emotion(Emotion.HAPPY)
            else:
                self.set_emotion(Emotion.NEUTRAL)
        
        elif new_state == RobotState.SEARCHING:
            self.set_emotion(Emotion.CURIOUS)
        
        elif new_state == RobotState.SLEEPING:
            self.set_emotion(Emotion.SLEEPY)
    
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

class Settings:
    """A class to store all settings for Alien Invasion."""
    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 1100
        self.screen_height = 700
        self.bg_color = (255, 255, 255)
        
        # Ship settings
        self.ship_speed = .5
        self.ship_limit = 3
        
        # Ships Bullets settings
        self.bullet_speed = 0.3
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255,255,255)
        self.bullets_allowed = 3
        
         # Aliens bombs settings
        self.bomb_speed = .3
        self.bomb_width = 3
        self.bomb_height = 15
        self.bomb_color = (255,0,0)
        self.bomb_allowed = 5
        # Time between bombs in miliseconds
        self.bomb_dealy = 300
        
        # Alien settings
        self.alien_speed = 0.2
        self.fleet_drop_speed = 10
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        # flee aliens rows
        self.fleet_rows = 5
        
        
        
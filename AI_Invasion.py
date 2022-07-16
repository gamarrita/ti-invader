from random import randint
import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet_ship import Bullet
from alien import Alien
from button import Button
from bomb import Bomb


class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the game, create game resourcess."""
        pygame.init()
        self.settings = Settings()
                        
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
       
        """self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height"""
        
         # Originalmente usaba un BMP, 
        self.bg_img = pygame.image.load('images/background.bmp')
        self.bg_img = pygame.transform.scale(self.bg_img,
            (self.settings.screen_width, self.settings.screen_height))
        
        pygame.display.set_caption("Artificial Intelligence Invader")
        
        # Create a instance to store game staticstics.
        self.stats = GameStats(self)
        self.stats.game_active = False
        
        # Create a instances
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self._create_fleet ()
        
        # Make the Play button.
        self.play_button = Button(self, "Play")
        
        #
        time_to_bomb = 100 # 0.5 seconds
        self.timer_event_bomb = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_event_bomb , time_to_bomb)
        
        
    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_bombs()
            
            self._update_screen()
            
    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)                
            elif event.type == pygame.KEYUP:
                self._chek_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_playbutton(mouse_pos)
            elif event.type == self.timer_event_bomb:
                if len(self.aliens):
                    if randint(1,5) == 1:
                        self._alien_drop_bomb()
                
    
    
    def _check_playbutton(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:            
            # Reset the game statictics.
            self.stats.reset_stats()
            self.stats.game_active = True
            
            # Get rid of any remaning aliens ond bullets
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
              
    def _update_screen(self):
        """"Update images on the screen, and flip to the new screen"""
        self.screen.blit(self.bg_img,(0,0))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        for bomb in self.bombs.sprites():
            bomb.draw_bomb()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            
        pygame.display.flip()
        
    
    def _create_fleet(self):
        """Create the flee of the aliens."""
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Dtermin the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_sapace_y = (self.settings.screen_height - 3 * alien_height - ship_height)
        number_rows = available_sapace_y // (2 * alien_height)
        
        # Verify is number of rows greate than standart set value
        if number_rows > self.settings.fleet_rows:
            number_rows = self.settings.fleet_rows


        # Create the first row of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
        
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height *row_number
        
        self.aliens.add(alien) 
        
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
   
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _update_bombs(self):
        """Update position of bombs, detec colisions, and get rid of old bombs"""
    # Update bullets position
        self.bombs.update()
        
        # Get rid of bullets that have disappeared.
        for bomb in self.bombs.copy():
            if bomb.rect.bottom > self.settings.screen_height - 5:
                self.bombs.remove(bomb)
        
        self._check_bomb_ship_collisions()
    
    def _check_bomb_ship_collisions(self):
        """ """
        # Rempve any bullets and aliens that have collided.
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.bombs):
            self._ship_hit()
        

    
    def _alien_drop_bomb(self):
        """Select a bomber in the last line to drop bombs."""
        aliens_qty = len(self.aliens) - 1
        alien_attacker = randint(0, aliens_qty)
        new_bomb = Bomb(self, self.aliens.sprites()[alien_attacker])
        self.bombs.add(new_bomb)
        
                    
    def _update_aliens(self):
        """Update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
        
        
                    
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            # Start movint ship to the right.
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            # Start movint ship to the right.
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
          self.new_bullet = self._fire_bullet()
                    
    def _chek_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            # Stop moving ship to the left.
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            # Stop moving ship to the left.
            self.ship.moving_left = False
    
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets"""
        # Update bullets position
        self.bullets.update()
        
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_allien_collisions()
            
    def _check_bullet_allien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Rempve any bullets and aliens that have collided.
        collision = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
        
    def _ship_hit(self):
        """Rspond to the ship being hit by an alien."""
        if self.stats.ship_left > 0:
            # Decrement ships_left
            self.stats.ship_left -= 1
            # Get rid of any ramaning aliens and bullets.
            self.aliens.empty()
            self.ship.center_ship()
            self.bombs.empty()       
            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
        
if __name__ == '__main__':
    # Make a game isntance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
    
    
            
        
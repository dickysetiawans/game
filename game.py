import pygame
import os
import time
import random


pygame.font.init()

WIDTH, HEIGHT = 700,700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shoter")

#load image

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "enemy1.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "enemy4.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "enemy2.png"))

# player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship.png"))

#laser 
RED_LASER = pygame.image.load(os.path.join("assets", "laser7.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "laser8.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "laser9.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "laser_ship.png"))
#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT))

pygame.mixer.init()
hit_sound = pygame.mixer.Sound("235968__tommccann__explosion-01.wav")
enemy_hit_sound = pygame.mixer.Sound("Shotgun_Blast-Jim_Rogers-1914772763.wav")
shoot_sound = pygame.mixer.Sound("sf_laser_15.mp3")


hit_sound.set_volume(0.05)
enemy_hit_sound.set_volume(0.50)
shoot_sound.set_volume(0.50)

pygame.mixer.music.load("l.ogg")
pygame.mixer.music.play(-1, 0.1)
pygame.mixer.music.set_volume(1.00)


class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 1)

	def collision(self, obj):
		return collide(self, obj)	


class Ship:
	COOLDOWN = 10

	def __init__(self, x, y,  health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0 
		if self.cool_down_counter > 0:
			self.cool_down_counter +=1	

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			shoot_sound.play()
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def get_width(self):
		return self.ship_img.get_width()
	def get_height(self):
		return self.ship_img.get_height()
			

class Player(Ship):
	def __init__(self, x, y, health=200):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health


	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			shoot_sound.play()
			self.lasers.append(laser)
			self.cool_down_counter = 1		
		
	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			for obj in objs: 
				if laser.collision(obj):
					if objs.remove(obj):
					enemy_hit_sound.play()	

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 11))
		pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 11))


class Enemy(Ship):
	COLOR_MAP = {
				"red": (RED_SPACE_SHIP, RED_LASER),
				"green": (GREEN_SPACE_SHIP, GREEN_LASER),
				"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
				}

	def __init__(self, x, y, color, health=100):
		super().__init__(x,y, health)
		self.ship_img, self.laser_img =self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x+20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 3


	def move(self, vel):
		self.y += vel 

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) !=None


	
def main():
	run = True
	FPS = 60
	level = 0
	lives = 5
	score = 0
	main_font = pygame.font.SysFont("comicsans", 50)
	lost_font = pygame.font.SysFont("comicsans", 60)
	score_font = pygame.font.SysFont("comicsans", 35)


	enemies = []
	wave_length = 5
	enemy_vel = 2
	
	player_vel = 6
	laser_vel = 9
	
	
	player = Player(300, 600)

	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

	def draw_score():
		score +=1

	def redraw_window():
		WIN.blit(BG, (0,0))
		#draw text
		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
		score_label = score_font.render(f"score: {score}", 1, (255,255,255))
		level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

		WIN.blit(lives_label, (10, 10))
		WIN.blit(score_label, (10, 50))

		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("Game Over", 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

			

		pygame.display.update()
		
	while run:
		clock.tick(FPS)
		redraw_window()
		

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		if len(enemies) <= 0:
			level += 1
			if level > 1:
				score += 15
			wave_length += 10
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH - 80), random.randrange(-1000, -90), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)
			


		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x - player_vel > 0: # left
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
			player.x += player_vel
		if keys[pygame.K_w] and player.y - player_vel > 0: # up
			player.y -= player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # down
			player.y += player_vel 
		if keys[pygame.K_SPACE]:
		 	if player.shoot():
		 		score += 1

		

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*40) == 1:
				enemy.shoot()				

			if collide(enemy, player):
				player.health -= 2
				enemies.remove(enemy)
			elif  enemy.y + enemy.get_height() > HEIGHT:
				score -= 4
				enemies.remove(enemy)
	
	

		player.move_lasers(-laser_vel, enemies)
			

main()		

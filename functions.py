import pygame
import random
from constants import *
import sqlite3
from sqlite3 import Error
from datetime import datetime


# MENU
# Menu title text
def draw_menu_text(text, y_menu_text):
    draw_text = titlefont.render(text, 1, WHITE)
    screen.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, y_menu_text))
def draw_text(text, y_menu_text):
    draw_text = font.render(text, 1, WHITE)
    screen.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, y_menu_text))

# Draws the menu
def draw_menu():
        screen.fill(BLACK)
        start_button.draw_button(screen)
        scoreboard_button.draw_button(screen)
        controls_button.draw_button(screen)
        draw_menu_text("Dungeon of the Forsaken", 60)

def draw_controls():
    screen.fill(BLACK)
    return_to_menu.draw_button(screen)
    draw_menu_text("How to Play:", 60)
    draw_text("WASD: To Move.", 180)
    draw_text("K: To attack.", 240)
    draw_text("(Careful, some enemies wont die in one hit.)", 300)
    draw_text("K: To exit dungeon level.", 360)
    
def draw_scores(top_scores):
    screen.fill(BLACK)
    return_to_menu.draw_button(screen)
    i = 1
    draw_menu_text("High Scores:", 60)
    for date_added, score in top_scores:
        i +=1
        menu_score = (f"Date: {date_added}, Score: {score}")
        draw_text(menu_score, i*60)

# GAME
def draw_game(player, enemies, room, camera_x, camera_y, player_health, score, attack_x):
    screen.fill(BLACK)
    screen.blit(background_image, (0 -camera_x, 0 - camera_y))
    map_loading(room, camera_x, camera_y)
    screen.blit(player_image, (player.x - camera_x, player.y - camera_y))
    # Attack
    if attack_x == 0:
        pass
    else:
        screen.blit(player_attack_image, (player.x - player_size // 2 - camera_x, player.y - player_size // 2 - camera_y))
    #draw enemies
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

    # Health UI
    health_text = font.render("Health: " + str(player_health), 1, WHITE)
    screen.blit(health_text, (10, 10))
    score_text = font.render("Score: " + str(score), 1, WHITE)
    screen.blit(score_text, (10, 50))


# PLAYER
def player_movement(keys_pressed, player, room):
    global player_image

    # Calculate the future position based on the current keys pressed
    future_x = player.x
    future_y = player.y

    # Elif makes it so the player can only move 1 direction at a time
    if keys_pressed[pygame.K_a]:  # Left
        future_x -= VEL
        player_image = player_left_image
    elif keys_pressed[pygame.K_d]:  # Right
        future_x += VEL
        player_image = player_right_image
    elif keys_pressed[pygame.K_w]:  # Up
        future_y -= VEL
        player_image = player_up_image
    elif keys_pressed[pygame.K_s]:  # Down
        future_y += VEL
        player_image = player_down_image

    # Calculate player's future tile
    future_tile_left = int((future_x - VEL) // TILE_SIZE)
    future_tile_right = int((future_x + player.width + VEL) // TILE_SIZE)
    future_tile_top = int((future_y - VEL) // TILE_SIZE)
    future_tile_bottom = int((future_y + player.height + VEL) // TILE_SIZE)

    # Check for collisions
    for y in range(future_tile_top, future_tile_bottom + 1):
        for x in range(future_tile_left, future_tile_right + 1):
            if room[y][x] == "w":
                # If collision is detected, do not update the player's position
                return
    # Update the player's position if there is no collision
    player.x = future_x
    player.y = future_y

# Enemy
def collides_walls(rect, room):
    # Calculate the future tile
    future_tile_left = int(rect.left // TILE_SIZE)
    future_tile_right = int(rect.right // TILE_SIZE)
    future_tile_top = int(rect.top // TILE_SIZE)
    future_tile_bottom = int(rect.bottom // TILE_SIZE)

    # Check for collisions with walls
    for y in range(future_tile_top, future_tile_bottom + 1):
        for x in range(future_tile_left, future_tile_right + 1):
            if room[y][x] == "w":
                return True  # Collision with wall

    return False  # No collision

def choose_room(room):
    random_room = random.choice(game_maps)
    reset_room(random_room)
    choose_exit(random_room)
    return random_room

# Resets map to remove enemy and exit spots
def reset_room(room):
    # Tests all cells and checks if they are not a wall
    available = [(i, j) for i, row in enumerate(room) for j, cell in enumerate(row) if cell == "e"]
    for i, j in available:
        room[i][j] = " "
    # Tests all cells and checks if they are not a wall
    available = [(i, j) for i, row in enumerate(room) for j, cell in enumerate(row) if cell == "x"]
    for i, j in available:
        room[i][j] = " "   

def choose_exit(room):
    # Tests all cells and checks if they are not a wall
    available = [(i, j) for i, row in enumerate(room) for j, cell in enumerate(row) if cell == " "]
    if available:
        # Chooses one of the cells that is not a wall
        random_available = random.choice(available)
        i, j = random_available
        # Sets chosen cell to be "e" for exit
        room[i][j] = "e"

def choose_enemy(room):
    available = [(i, j) for i, row in enumerate(room) for j, cell in enumerate(row) if cell == " "]
    if available:
        # Chooses one of the cells that is not a wall
        random_available = random.choice(available)
        i, j = random_available
        # Sets chosen cell to be "x" for enemy to prevent doubles
        room[i][j] = "x"
        r_enemy = random.randint(1,4)
        # GHOUL
        if r_enemy == 1:
            enemy_list_item = Enemy(j * TILE_SIZE, i * TILE_SIZE, player_size, player_size, "img_ghoul.png", "ghoul", 2.5, 2, 1, 0, 5)
        # SKELETON
        elif r_enemy == 2:
            enemy_list_item = Enemy(j * TILE_SIZE, i * TILE_SIZE, player_size, player_size, "img_skeleton.png", "skeleton", 3.5, 1, 1, 0, 5)
        # DEMON
        elif r_enemy == 3:
            enemy_list_item = Enemy(j * TILE_SIZE, i * TILE_SIZE, player_size, player_size, "img_demon.png", "demon", 3, 2, 2, 0, 15)
        # golem
        elif r_enemy == 4:
            enemy_list_item = Enemy(j * TILE_SIZE, i * TILE_SIZE, player_size, player_size, "img_golem.png", "golem", 2, 3, 1, 0, 10)
        return enemy_list_item

# MAP
def map_loading(room, camera_x, camera_y):
    # Draw the map
    for y, row in enumerate(room):
        for x, cell in enumerate(row):
            if cell == "w":
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))
            if cell == "e":
                pygame.draw.rect(screen, GREEN, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE))

# SQL
def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    return conn

def create_scores_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            date_added TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    print("Table 'scores' created successfully")

def add_score(conn, addscore):
    sql = ''' INSERT INTO scores(date_added, score)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, addscore)
    conn.commit()
    return cur.lastrowid

def add(conn, score):
    with conn:
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        addscore = (date_added, score)
        add_score(conn, addscore)

def get_top_scores(conn):
        sql = "SELECT date_added, score FROM scores ORDER BY score DESC LIMIT 10"
        cursor = conn.cursor()
        cursor.execute(sql)
        top_scores = cursor.fetchall()
        return top_scores
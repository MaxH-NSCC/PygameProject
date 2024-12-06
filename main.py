import pygame
import random
pygame.init()
import functions as f
from constants import *

# MAIN FUNCTION
def main():
    # Updates the game running it at 60 fps until the exit button is pressed which will shut down the game
    pygame.display.set_caption("Dungeon of the Forsaken")
    clock = pygame.time.Clock()
    database = r"database.db"
    run = True
    mode = "menu"
    room = ""
    layer = 10
    attack_x = 0
    attack_y = 0
    attack = pygame.Rect(attack_x, attack_y, player_size*2, player_size*2)
    enemies = []
    starting_game = "start"


    # Set camera position
    camera_x = 0
    camera_y = 0

    while run:
        clock.tick(FPS)
        # Exit the main loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Menu Button Functions
            if mode == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if f.start_button.is_clicked(mouse_pos):
                    print("STARTING")
                    mode = "play"
                if f.scoreboard_button.is_clicked(mouse_pos):
                    print("SCORES")
                    mode = "scores"
                    db_conn = f.create_conn(database)
                    top_scores = f.get_top_scores(db_conn)
                    if top_scores:
                        print("Top 10 Scores:")
                        for date_added, score in top_scores:
                            print(f"Date: {date_added}, Score: {score}")
                    if db_conn is not None:
                        db_conn.close()
                if f.controls_button.is_clicked(mouse_pos):
                    print("HOW TO PLAY")
                    mode = "controls"

            if mode == "scores" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if f.return_to_menu.is_clicked(mouse_pos):
                    mode = "menu"
            if mode == "controls" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if f.return_to_menu.is_clicked(mouse_pos):
                    mode = "menu"
        # Draw Menu
        if mode == "menu":
            f.draw_menu()
        elif mode == "scores":
            f.draw_scores(top_scores)
        elif mode == "controls":
            f.draw_controls()
        # Test if game starts
        elif mode == "play":

            # Set up game properly
            if starting_game == "start":
                player_health = 3
                score = 0
                starting_game = "run"
                map_level = "new"

            # Loads a new instance of the map
            if map_level == "new":
                enemies.clear()
                player = pygame.Rect(TILE_SIZE * 2, TILE_SIZE * 21, player_size, player_size)
                room = f.choose_room(room)
                numb_of_enemies = random.randint(4,layer)
                for i in range(numb_of_enemies):
                    enemies.append(f.choose_enemy(room))
                map_level = "old"

            # Player movement and attacks
            keys_pressed = pygame.key.get_pressed()
            f.player_movement(keys_pressed, player, room)

            # Update the camera
            camera_x = player.x - WIDTH // 2
            camera_y = player.y - HEIGHT // 2

            # Handle attacks
            if keys_pressed[pygame.K_SPACE]:
                attack_x = player.x - player_size // 2
                attack_y = player.y - player_size // 2
                attack = pygame.Rect(attack_x, attack_y, player_size*2, player_size*2)
            else:
                attack_x = 0
                attack_y = 0
                attack = pygame.Rect(attack_x, attack_y, player_size*2, player_size*2)


            tile_left = int((player.x - VEL) // TILE_SIZE)
            tile_right = int((player.x + player.width + VEL) // TILE_SIZE)
            tile_top = int((player.y - VEL) // TILE_SIZE)
            tile_bottom = int((player.y + player.height + VEL) // TILE_SIZE)

            for y in range(tile_top, tile_bottom + 1):
                for x in range(tile_left, tile_right + 1):
                    if room[y][x] == "e":
                        if keys_pressed[pygame.K_SPACE]:
                            pygame.mixer.Sound(EXIT).play()
                            map_level = "new"

            # Enemy movement
            for enemy in enemies:
                enemy.move(player, enemies, room, attack, attack_x)
                # Check if enemy should be dead and remove them from the game.
                if enemy.health == 0:
                    enemies.remove(enemy)
                    score += enemy.score
                # Check if player should take damage and calculate player health
                if enemy.damage == 1:
                    player_health -= enemy.attack
                    pygame.mixer.Sound(HURT).play()
                    enemy.damage = 0
                    # Test if player should die and end game
                    if player_health <= 0:
                        pygame.mixer.Sound(DEATH).play()
                        db_conn = f.create_conn(database)
                        if db_conn is not None:
                            f.create_scores_table(db_conn)
                            f.add(db_conn, score)
                        if db_conn is not None:
                            db_conn.close()
                        mode = "menu"
                        starting_game = "start"
                        map_level = "new"


            f.draw_game(player, enemies, room, camera_x, camera_y, player_health, score, attack_x)

        pygame.display.flip()
        pygame.display.update()

    # Quit the game when the main loop exits
    pygame.quit()

# RUN PROGRAM
if __name__ == '__main__':
    main()
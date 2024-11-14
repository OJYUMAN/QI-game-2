



if __name__ == '__main__':
    from welcome import welcome_screen
    welcome_screen()

    from login import run_login
    game_started, firebase, players = run_login()
    if game_started:
        print("Starting game with players:", players)

    from quizgame import quiz_game
    quiz_game()
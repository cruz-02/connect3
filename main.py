from games import Connect3M

if __name__ == '__main__':
    while True:
        try:
            model = str(input("Choose your model 'mm', 'mmD': "))
            choice = int(input("Choose your player: 0 (White, moves first) or 1 (Black, moves second): "))
            if choice in [0, 1]:
                human = choice
                break
            else:
                print("Invalid choice. Please enter 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    game = Connect3M(model= model, human_player=human)
    game.play()
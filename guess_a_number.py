from random import randint
computer_number = randint(1, 100)
guess = 0
while guess != 6:
    player = input()
    if not player.isdigit():
        print('Invalid input. Try again!')
        continue
    player = int(player)
    if player == computer_number:
        print('You guess it!')
        if guess == 1:
            print('You win with excellent score of 100!')
        elif guess == 2:
            print('You win with perfect score of 80!')
        elif guess == 3:
            print('You win with good score of 60!')
        elif guess == 4:
            print('You win with satisfying of score 40!')
        elif guess == 5:
            print('You win with average score of 20!')
        elif guess == 4:
            print('You win with score of 10!')
        print('Play another game [y] for YES or [n] for NO?')
        again = input()
        if again == 'y':
            guess = 0
        else:
            break
    elif player > computer_number:
        print('Your number is too high!')
    else:
        print('Your number is too low!')
    guess += 1
else:
    print('You\'ve passed your limits.')
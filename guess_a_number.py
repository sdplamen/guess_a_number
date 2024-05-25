from random import randint
computer_number = randint(1, 100)
guess = 0
while guess != 6:
    player = input('Guess a number from 1 to 100: ')
    if not player.isdigit():
        print('Invalid input. Try again!')
        continue
    player = int(player)
    if player == computer_number:
        print('You guess it!')
        break
    elif player > computer_number:
        print('Your number is too high!')
    else:
        print('Your number is too low!')
    guess += 1
else:
    print('You\'ve passed your limits.')
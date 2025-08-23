from random import randint
from django.shortcuts import render, redirect
from django.views import View
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from game.forms import GuessForm
from game.serializers import GameStateSerializer, PlayAgainSerializer, GuessInputSerializer


# Create your views here.
class GameView(View):
    template_name = 'index.html'

    def get(self, request):
        if 'computer_number' not in request.session:
            request.session['computer_number'] = randint(1, 100)
            request.session['guess_count'] = 0
            request.session['message'] = "Welcome! Try to guess the number."
            request.session['score_message'] = None
            request.session['game_over'] = False

        form = GuessForm()
        context = {
            'form': form,
            'message': request.session.get('message'),
            'score_message': request.session.get('score_message'),
            'guess_count': request.session.get('guess_count'),
            'game_over': request.session.get('game_over'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = GuessForm(request.POST)
        computer_number = request.session.get('computer_number')
        guess_count = request.session.get('guess_count', 0)

        if form.is_valid():
            player_guess = form.cleaned_data['player_guess']
            play_again = form.cleaned_data.get('play_again')

            if play_again:
                if play_again == 'y':
                    request.session['computer_number'] = randint(1, 100)
                    request.session['guess_count'] = 0
                    request.session['message'] = 'Welcome! Try to guess the number.'
                    request.session['score_message'] = None
                    request.session['game_over'] = False
                else:
                    request.session.flush()
                    request.session['game_over'] = True
                return redirect('play')

            if not request.session.get('game_over'):
                guess_count += 1
                request.session['guess_count'] = guess_count
                message = ''
                score_message = None

                if player_guess == computer_number:
                    request.session['game_over'] = True
                    message = f'You guessed it! The number was {computer_number}.'
                    if guess_count == 1:
                        score_message = 'You win with an excellent score of 100!'
                    elif guess_count == 2:
                        score_message = 'You win with a perfect score of 80!'
                    elif guess_count == 3:
                        score_message = 'You win with a good score of 60!'
                    elif guess_count == 4:
                        score_message = 'You win with a satisfying score of 40!'
                    elif guess_count == 5:
                        score_message = 'You win with an average score of 20!'
                    else:
                        score_message = 'You win with a score of 10!'
                elif player_guess > computer_number:
                    message = 'Your number is too high!'
                else:
                    message = 'Your number is too low!'

                if guess_count >= 6 and not request.session.get('game_over'):
                    message = f"You've passed your limits. The number was {computer_number}."
                    request.session['game_over'] = True
                    request.session['score_message'] = None

                request.session['message'] = message
                request.session['score_message'] = score_message
        else:
            request.session['message'] = 'Invalid input. Please enter a number between 1 and 100.'

        context = {
            'form': form,
            'message': request.session.get('message'),
            'score_message': request.session.get('score_message'),
            'guess_count': request.session.get('guess_count'),
            'game_over': request.session.get('game_over'),
        }
        return render(request, self.template_name, context)



class GameAPIView(APIView) :
    @extend_schema(
        summary="Get Current Game State",
        description="Retrieves the current state of the number guessing game.",
        responses={200 :GameStateSerializer},
        examples=[
            OpenApiExample(
                'Initial Game State',
                value={
                    'message' :'Welcome! Try to guess the number.',
                    'score_message' :None,
                    'guess_count' :0,
                    'game_over' :False
                },
                response_only=True
            ),
            OpenApiExample(
                'Game State - In Progress',
                value={
                    'message' :'Your number is too high!',
                    'score_message' :None,
                    'guess_count' :2,
                    'game_over' :False
                },
                response_only=True
            ),
            OpenApiExample(
                'Game State - Game Over (Win)',
                value={
                    'message' :'You guessed it! The number was 50.',
                    'score_message' :'You win with a perfect score of 80!',
                    'guess_count' :2,
                    'game_over' :True
                },
                response_only=True
            ),
        ]
    )
    def get(self, request) :
        if 'computer_number' not in request.session :
            request.session['computer_number'] = randint(1, 100)
            request.session['guess_count'] = 0
            request.session['message'] = "Welcome! Try to guess the number."
            request.session['score_message'] = None
            request.session['game_over'] = False

        game_state = {
            'message' :request.session.get('message'),
            'score_message' :request.session.get('score_message'),
            'guess_count' :request.session.get('guess_count'),
            'game_over' :request.session.get('game_over'),
        }
        serializer = GameStateSerializer(game_state)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Submit a Guess or Play Again",
        description="Allows the player to submit a number guess or choose to play again after a game is over.",
        request={
            'application/json' :GuessInputSerializer,
            'application/json' :PlayAgainSerializer
        },
        responses={
            200: GameStateSerializer,
            400: {'description' :'Invalid input'},
        },
        examples=[
            OpenApiExample(
                'Submit a Guess',
                value={'player_guess' :50},
                request_only=True,
                description='Submit a number guess while the game is active.'
            ),
            OpenApiExample(
                'Play Again (Yes)',
                value={'play_again' :'y'},
                request_only=True,
                description='Choose to play again after the game is over.'
            ),
            OpenApiExample(
                'Play Again (No)',
                value={'play_again' :'n'},
                request_only=True,
                description='Choose not to play again after the game is over. This will clear the session.'
            ),
            OpenApiExample(
                'Invalid Guess Input',
                value={'player_guess' :101},
                request_only=True,
                description='Example of an invalid guess input (out of range).'
            )
        ]
    )
    def post(self, request) :
        guess_serializer = GuessInputSerializer(data=request.data)
        play_again_serializer = PlayAgainSerializer(data=request.data)

        computer_number = request.session.get('computer_number')
        guess_count = request.session.get('guess_count', 0)
        game_over = request.session.get('game_over', False)

        if play_again_serializer.is_valid() and 'play_again' in play_again_serializer.validated_data:
            play_again = play_again_serializer.validated_data['play_again']
            if play_again == 'y' :
                request.session['computer_number'] = randint(1, 100)
                request.session['guess_count'] = 0
                request.session['message'] = 'Welcome! Try to guess the number.'
                request.session['score_message'] = None
                request.session['game_over'] = False
            else:
                request.session.flush()
                request.session['game_over'] = True
                request.session['message'] = "Game ended. Session cleared. See you next time!"
                request.session['score_message'] = None

            game_state = {
                'message' :request.session.get('message'),
                'score_message' :request.session.get('score_message'),
                'guess_count' :request.session.get('guess_count'),
                'game_over' :request.session.get('game_over'),
            }
            return Response(GameStateSerializer(game_state).data, status=status.HTTP_200_OK)

        if not game_over:
            if guess_serializer.is_valid() and 'player_guess' in guess_serializer.validated_data :
                player_guess = guess_serializer.validated_data['player_guess']

                guess_count += 1
                request.session['guess_count'] = guess_count
                message = ''
                score_message = None

                if player_guess == computer_number:
                    request.session['game_over'] = True
                    message = f'You guessed it! The number was {computer_number}.'
                    if guess_count == 1 :
                        score_message = 'You win with an excellent score of 100!'
                    elif guess_count == 2 :
                        score_message = 'You win with a perfect score of 80!'
                    elif guess_count == 3 :
                        score_message = 'You win with a good score of 60!'
                    elif guess_count == 4 :
                        score_message = 'You win with a satisfying score of 40!'
                    elif guess_count == 5 :
                        score_message = 'You win with an average score of 20!'
                    else:
                        score_message = 'You win with a score of 10!'
                elif player_guess > computer_number:
                    message = 'Your number is too high!'
                else:
                    message = 'Your number is too low!'

                if guess_count >= 6 and not request.session.get('game_over') :
                    message = f"You've passed your limits. The number was {computer_number}."
                    request.session['game_over'] = True
                    request.session['score_message'] = None

                request.session['message'] = message
                request.session['score_message'] = score_message

                game_state = {
                    'message' :request.session.get('message'),
                    'score_message' :request.session.get('score_message'),
                    'guess_count' :request.session.get('guess_count'),
                    'game_over' :request.session.get('game_over'),
                }
                return Response(GameStateSerializer(game_state).data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'detail' :'Invalid input. Please provide a number between 1 and 100, or a play_again choice.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            game_state = {
                'message' :request.session.get('message', "Game over. Please choose to play again or restart."),
                'score_message' :request.session.get('score_message'),
                'guess_count' :request.session.get('guess_count'),
                'game_over' :request.session.get('game_over'),
            }
            return Response(GameStateSerializer(game_state).data, status=status.HTTP_200_OK)
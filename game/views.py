from random import randint
from django.shortcuts import render, redirect
from django.views import View
from game.forms import GuessForm


# Create your views here.
class GameView(View):
    template_name = 'index.html'

    def get(self, request):
        if 'computer_number' not in request.session or request.GET.get('reset'):
            request.session['computer_number'] = randint(1, 100)
            request.session['guess_count'] = 0
            request.session['message'] = "Welcome! Try to guess the number."
            request.session['score_message'] = None

        form = GuessForm()
        context = {
            'form': form,
            'message': request.session.get('message'),
            'score_message': request.session.get('score_message'),
            'guess_count': request.session.get('guess_count'),
            'player_won': request.session.get('score_message') is not None
        }
        return render(request, self.template_name, context)

    def post(self, request) :
        form = GuessForm(request.POST)
        computer_number = request.session.get('computer_number')
        guess_count = request.session.get('guess_count')

        if form.is_valid() :
            player = form.cleaned_data['player_guess']
            guess_count += 1
            request.session['guess_count'] = guess_count
            message = ''
            score_message = None
            player_won = False

            if player == computer_number :
                player_won = True
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
                elif guess_count >= 6 :
                    score_message = 'You win with a score of 10!'
                del request.session['computer_number']
            elif player > computer_number :
                message = 'Your number is too high!'
            else :
                message = 'Your number is too low!'

            request.session['message'] = message
            request.session['score_message'] = score_message

            if guess_count >= 6 and not player_won :
                message = f"You've passed your limits. The number was {computer_number}."
                request.session['message'] = message
                del request.session['computer_number']

        else :
            request.session['message'] = 'Invalid input. Please enter a number between 1 and 100.'

        return redirect('play')
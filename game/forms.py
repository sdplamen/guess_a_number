from django import forms

class GuessForm(forms.Form):
    player_guess = forms.IntegerField(
        label='Guess a number from 1 to 100',
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your guess'}),
        required=False,
    )
    play_again = forms.ChoiceField(
        choices=[('y', 'Yes'), ('n', 'No')],
        required=False,
        widget=forms.RadioSelect,
    )
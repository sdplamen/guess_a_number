from rest_framework import serializers

class GuessInputSerializer(serializers.Serializer):
    player_guess = serializers.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        help_text='Enter your guess (a number from 1 to 100).'
    )

class PlayAgainSerializer(serializers.Serializer):
    play_again = serializers.ChoiceField(
        choices=[('y', 'Yes'), ('n', 'No')],
        required=False,
        help_text='Do you want to play again? ("y" or "n")'
    )

class GameStateSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='Current game message.')
    score_message = serializers.CharField(allow_null=True, required=False, help_text='Message indicating score if game is over.')
    guess_count = serializers.IntegerField(help_text='Number of guesses made.')
    game_over = serializers.BooleanField(help_text='Indicates if the game is over.')
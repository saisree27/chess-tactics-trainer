from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    piece_set = models.CharField(verbose_name="Piece set", max_length=100, default="lichess")
    rating = models.FloatField(verbose_name="Tactics rating", default=1500)
    darkmode = models.BooleanField(verbose_name="Dark mode", default=False)

    total_tactics_correct = models.IntegerField(verbose_name="Total Tactics Correct", default=10)
    total_tactics_incorrect = models.IntegerField(verbose_name="Total Tactics Incorrect", default=10)


    # will add more fields to this later

class Tactic(models.Model):
    position = models.CharField(verbose_name="FEN string", max_length=200)
    evaluation_before = models.IntegerField(verbose_name="Evaluation before")
    evaluation_after = models.IntegerField(verbose_name="Evaluation after")
    best_move = models.CharField(verbose_name="Best Move", max_length=200)
    variation = models.TextField(verbose_name="Variation (JSON-serialized)")
    classifications = models.TextField(verbose_name="Classifications (JSON-serialized)")
    rating = models.FloatField(verbose_name="Difficulty rating", default=1500)
    side_to_move = models.IntegerField(verbose_name="Side to move")

    def set_variation(self, variation):
        self.variation = json.dumps(variation)
    
    def get_variation(self):
        return json.loads(self.variation)

    def set_classifications(self, classifications):
        self.classifications = json.dumps(classifications)
    
    def get_classifications(self):
        return json.loads(self.classifications)
    
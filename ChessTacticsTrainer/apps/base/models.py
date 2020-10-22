from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    piece_set = models.CharField(verbose_name="Piece set", max_length=100, default="lichess")
    rating = models.FloatField(verbose_name="Tactics rating", default=1500)
    darkmode = models.BooleanField(verbose_name="Dark mode", default=False)

    total_tactics_correct = models.IntegerField(verbose_name="Total Tactics Correct", default=10)
    total_tactics_incorrect = models.IntegerField(verbose_name="Total Tactics Incorrect", default=10)


    # will add more fields to this later
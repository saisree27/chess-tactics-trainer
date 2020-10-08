from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    piece_set = models.CharField(verbose_name="Piece set", max_length=100, default="lichess")
    rating = models.FloatField(verbose_name="Tactics rating", default=1500)

    # will add more fields to this later
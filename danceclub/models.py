from django.db import models
from django.contrib.auth.models import User

LEVELS = ('F', 'E', 'D', 'C', 'B', 'A')

class Member(models.Model):
    user = models.ForeignKey(User)
    
class Dancer(Member):
    license = models.CharField(max_length=20)
    level = models.CharField(max_length=1, choices=LEVELS)
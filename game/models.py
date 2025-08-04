from django.db import models
from django.contrib.auth.models import User



class Question(models.Model):
    LEVEL_CHOICES = [(i, f"Level {i}") for i in range(1, 6)]
    level = models.IntegerField(choices=LEVEL_CHOICES)
    question_text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Level {self.level}: {self.question_text}"

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_level = models.IntegerField(default=1)
    earned_reward = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet - ₹{self.balance}"


class PayoutRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_id = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} to {self.upi_id}"


class PlayWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Play Wallet - ₹{self.balance}"


# In models.py


class KYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    pan_number = models.CharField(max_length=10)
    aadhaar_number = models.CharField(max_length=12)
    is_verified = models.BooleanField(default=False)  # Optional: For admin verification

    def __str__(self):
        return f"KYC for {self.user.username}"

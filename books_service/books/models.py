from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=63)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(default=0)
    monthly_annual_fee = models.DecimalField("Monthly annual fee in $USD", max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.title} - {self.author}"


from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    batch_year = models.IntegerField()
    roll_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    edition = models.CharField(max_length=20)
    quantity = models.IntegerField()
    available_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_due_date = models.DateField()
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)
    return_requested = models.BooleanField(default=False)
    return_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', blank=True)

    def __str__(self):
        return f"{self.student} borrowed {self.book}"
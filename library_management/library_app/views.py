from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, Book, BorrowRecord
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.is_staff:
        students = Student.objects.all()
        books = Book.objects.all()
        borrowed_books = BorrowRecord.objects.filter(returned=False)
        pending_returns = BorrowRecord.objects.filter(return_requested=True, return_status='pending')
        return render(request, 'admin_dashboard.html', {
            'students': students,
            'books': books,
            'borrowed_books': borrowed_books,
            'pending_returns': pending_returns,
        })
    else:
        student = get_object_or_404(Student, user=request.user)
        borrowed_books = BorrowRecord.objects.filter(student=student)
        return render(request, 'student_dashboard.html', {
            'student': student,
            'borrowed_books': borrowed_books,
        })

@login_required
def add_student(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        batch_year = request.POST['batch_year']
        roll_number = request.POST['roll_number']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(username=username, password=password)
            Student.objects.create(user=user, batch_year=batch_year, roll_number=roll_number)
            messages.success(request, 'Student added successfully')
            return redirect('dashboard')
    return render(request, 'add_student.html')

@login_required
def add_book(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        category = request.POST['category']
        edition = request.POST['edition']
        quantity = int(request.POST['quantity'])
        Book.objects.create(
            title=title,
            author=author,
            category=category,
            edition=edition,
            quantity=quantity,
            available_quantity=quantity
        )
        messages.success(request, 'Book added successfully')
        return redirect('dashboard')
    return render(request, 'add_book.html')

@login_required
def edit_student(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        student.user.username = request.POST['username']
        student.batch_year = request.POST['batch_year']
        student.roll_number = request.POST['roll_number']
        if request.POST['password']:
            student.user.set_password(request.POST['password'])
        student.user.save()
        student.save()
        messages.success(request, 'Student updated successfully')
        return redirect('dashboard')
    return render(request, 'add_student.html', {'student': student})

@login_required
def delete_student(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
    student = get_object_or_404(Student, id=id)
    student.user.delete()
    messages.success(request, 'Student deleted successfully')
    return redirect('dashboard')

@login_required
def edit_book(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.category = request.POST['category']
        book.edition = request.POST['edition']
        quantity = int(request.POST['quantity'])
        diff = quantity - book.quantity
        book.quantity = quantity
        book.available_quantity += diff
        book.save()
        messages.success(request, 'Book updated successfully')
        return redirect('dashboard')
    return render(request, 'add_book.html', {'book': book})

@login_required
def delete_book(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
    book = get_object_or_404(Book, id=id)
    book.delete()
    messages.success(request, 'Book deleted successfully')
    return redirect('dashboard')

@login_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query)
    ).filter(available_quantity__gt=0)
    return render(request, 'book_list.html', {'books': books, 'query': query})

@login_required
def borrow_book(request, book_id):
    student = get_object_or_404(Student, user=request.user)
    book = get_object_or_404(Book, id=book_id)
    if book.available_quantity > 0:
        BorrowRecord.objects.create(
            student=student,
            book=book,
            return_due_date=datetime.now().date() + timedelta(days=14)
        )
        book.available_quantity -= 1
        book.save()
        messages.success(request, 'Book borrowed successfully')
    else:
        messages.error(request, 'Book not available')
    return redirect('book_list')

@login_required
def borrowed_books(request):
    student = get_object_or_404(Student, user=request.user)
    borrowed_books = BorrowRecord.objects.filter(student=student)
    return render(request, 'borrowed_books.html', {'borrowed_books': borrowed_books})

@login_required
def profile(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        student.user.username = request.POST['username']
        if request.POST['password']:
            student.user.set_password(request.POST['password'])
        student.user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('dashboard')
    return render(request, 'profile.html', {'student': student})

@login_required
def request_return(request, record_id):
    if request.user.is_staff:
        return redirect('dashboard')
    record = get_object_or_404(BorrowRecord, id=record_id, student__user=request.user, returned=False)
    if not record.return_requested:
        record.return_requested = True
        record.save()
        messages.success(request, 'Return request submitted successfully')
    else:
        messages.info(request, 'Return request already submitted')
    return redirect('borrowed_books')

@login_required
def approve_return(request, record_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    record = get_object_or_404(BorrowRecord, id=record_id, return_requested=True, return_status='pending')
    record.return_status = 'approved'
    record.returned = True
    record.return_date = datetime.now().date()
    record.book.available_quantity += 1
    record.book.save()
    record.save()
    messages.success(request, 'Return approved successfully')
    return redirect('dashboard')

@login_required
def reject_return(request, record_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    record = get_object_or_404(BorrowRecord, id=record_id, return_requested=True, return_status='pending')
    record.return_status = 'rejected'
    record.return_requested = False
    record.save()
    messages.success(request, 'Return request rejected')
    return redirect('dashboard')
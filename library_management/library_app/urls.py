from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('library/admin/students/add/', views.add_student, name='add_student'),
    path('library/admin/books/add/', views.add_book, name='add_book'),
    path('library/admin/students/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('library/admin/students/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('library/admin/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('library/admin/books/delete/<int:id>/', views.delete_book, name='delete_book'),
    path('books/', views.book_list, name='book_list'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('borrowed/', views.borrowed_books, name='borrowed_books'),
    path('profile/', views.profile, name='profile'),
    path('return/request/<int:record_id>/', views.request_return, name='request_return'),
    path('return/approve/<int:record_id>/', views.approve_return, name='approve_return'),
    path('return/reject/<int:record_id>/', views.reject_return, name='reject_return'),
]
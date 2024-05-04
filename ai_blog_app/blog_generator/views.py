from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def generate_blog(request):
    pass

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_nessage': error_message})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def user_signup(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        if password == confirmPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating an account'
        else:
            error_message = 'Passwords do not match!'
            return render(request, 'register.html', {'error_message': error_message})
        
    return render(request, 'register.html')
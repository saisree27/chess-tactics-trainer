from django import forms
# from .forms import UploadFileForm
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return render(request=request, template_name="home.html")
    else:
        return render(request=request, template_name="landing.html")

def submit_login(request):
    print("here")
    error = ""
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        print("here2")
        print(request.POST)
        print(form)
        # if form.is_valid():
            # print("here3")
        try:
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print("Logged in")
                return redirect("/")
            else:
                print("Invalid username or password")
                error = "Invalid username or password!"
        except Exception as e:
            print(e)
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"form": form, "error": error})

def register(request):
    error = ""
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        print("Form: ", form.errors, form.cleaned_data.get('username'), form.cleaned_data.get('email'))
        if form.is_valid():
            username, password, email = form.cleaned_data.get('username'), form.cleaned_data.get('password'), form.cleaned_data.get('email')
            print(username, password, email, "yooooo")
            User = get_user_model()
            try:
                match = User.objects.get(email=email)
                messages.error(request, "An account with that email already exists!", extra_tags="danger")
                error = "An account with that email already exists!"
                return redirect("/")
            except User.DoesNotExist:
                form.save()
                user = authenticate(username=username, password=password, email=email)
                return redirect("/login")
        else:
            error = form.errors
    else:
        form = UserCreationForm()
    if error.__contains__("password2"):
        error = str(error).replace("password2", "<strong>Password: </strong>")
    if error.__contains__("username"):
        error = str(error).replace("username", "<strong>Username: </strong>")
    return render(request = request,
                    template_name = "register.html",
                    context={"form":form, "error": error})

def submit_logout(request):
    logout(request)
    return redirect("/login")

def start_training(request):
    return render(request=request, template_name="training.html")

def progress(request):
    return render(request=request, template_name="progress.html")

def preferences(request):
    return render(request=request, template_name="preferences.html")
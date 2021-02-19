from django import forms
from .models import Player, Tactic
from django.http import JsonResponse
from django.core import serializers
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from stockfish import Stockfish
import json
import chess
import pickle
import random

def update_tactics():
    tactics_dict = {}
    with open('ChessTacticsTrainer/static/assets/JULY 2019 FINAL WITH CLASSIFICATIONS.obj', 'rb') as f:
        tactics_dict = pickle.load(f)

    for num in tactics_dict:
        print(num, end="\r")
        tactic = tactics_dict[num]
        try:
            new_tactic = Tactic.objects.get(position=tactic[1])
            print("Tactic position exists. Updating values.")
            if new_tactic.evaluation_before != tactic[2]:
                print("Updating evaluation before.")
                new_tactic.evaluation_before = tactic[2]
            if new_tactic.evaluation_after != tactic[3]:
                print("Updating evaluation after.")
                new_tactic.evaluation_after = tactic[3]
            if new_tactic.best_move != tactic[4]:
                print("Updating best move.")
            if new_tactic.variation != json.dumps(tactic[5]):
                print("Updating variation.")
            if new_tactic.classifications != json.dumps(list(tactic[6])):
                print("Updating classifications.")
        except Tactic.DoesNotExist:
            print("Creating new tactic")
            print(list(tactic[6]))
            new_tactic = Tactic(position=tactic[1], side_to_move=tactic[0].turn, evaluation_before=tactic[2], evaluation_after=tactic[3],
                                best_move=tactic[4], variation=json.dumps(tactic[5]), classifications=json.dumps(list(tactic[6])))
            # new_tactic.side_to_move = tactic[0].turn
            # new_tactic.evaluation_before = tactic[2] 
            # new_tactic.evaluation_after = tactic[3]
            # new_tactic.best_move = tactic[4]
            # new_tactic.variation = json.dumps(tactic[5])
            # new_tactic.classifications = json.dumps(list(tactic[6]))
            new_tactic.save()


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        player, _ = Player.objects.get_or_create(user=request.user)

        context = {
            "darkmode": player.darkmode
        }
        return render(request=request, template_name="home.html", context=context)
    else:
        return render(request=request, template_name="landing.html")

def no_auth_home(request):
    return render(request=request, template_name="no_auth_home/home.html")

def stockfish_reply(request):
    # change to Linux binary if on Linux OS
    stockfish = Stockfish('ChessTacticsTrainer/static/assets/stockfish/stockfish_20090216_x64_bmi2')
    stockfish.set_depth(20)

    if request.is_ajax and request.method == "POST":
        position = request.POST.get('position')
        print(position)
        stockfish.set_fen_position(position)
        
        board = chess.Board(position)

        uci_move = stockfish.get_best_move()
        board.push_uci(uci_move)

        data = {
            'new_position': board.fen(),
            'move': uci_move
        }
        return JsonResponse(data)
    else:
        print("incorrect request")
        return JsonResponse({})
        
def send_tactic(request):
    if request.is_ajax and request.method == "POST":
        tactic = random.choice(Tactic.objects.all())
        data = {
            'tactic': {
                'turn': tactic.side_to_move,
                'fen': tactic.position,
                'bestmove': tactic.best_move,
                'variation': tactic.get_variation(),
                'classifications': tactic.get_classifications()
            }
        }
        print("sent tactic")
        return JsonResponse(data)
    else:
        print("incorrect request")
        return JsonResponse({})

def play_engine(request):
    player, _ = Player.objects.get_or_create(user=request.user)
    piece_path = ""

    print(player.piece_set)
    if player.piece_set == "lichess":
        piece_path = "/cburnett/{piece}.svg"
        print(piece_path)
    if player.piece_set == "merida":
        piece_path = "/merida/{piece}.svg"
        print(piece_path)
    if player.piece_set == 'alpha':
        piece_path = "/alpha/{piece}.svg"

    context = {
        "pieces": piece_path,
        "darkmode": player.darkmode
    }

    return render(request=request, template_name="play_engine.html", context=context)

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

    player, _ = Player.objects.get_or_create(user=request.user)
    piece_path = ""

    print(player.piece_set)
    if player.piece_set == "lichess":
        piece_path = "/cburnett/{piece}.svg"
        print(piece_path)
    if player.piece_set == "merida":
        piece_path = "/merida/{piece}.svg"
        print(piece_path)
    if player.piece_set == 'alpha':
        piece_path = "/alpha/{piece}.svg"

    context = {
        "pieces": piece_path,
        "darkmode": player.darkmode
    }

    return render(request=request, template_name="training.html", context=context)

def start_training_no_auth(request):

    context = {
        "pieces": "/merida/{piece}.svg"
    }

    return render(request=request, template_name="no_auth_home/training.html", context=context)


def progress(request):
    player, _ = Player.objects.get_or_create(user=request.user)

    context = {
        "rating": player.rating,
        "darkmode": player.darkmode,
        "tactics_correct": player.total_tactics_correct,
        "tactics_incorrect": player.total_tactics_incorrect
    }

    return render(request=request, template_name="progress.html", context=context)

def settings(request):
    player, _ = Player.objects.get_or_create(user=request.user)
    context = {
        "piece_change_error": "", 
        "change_password_error": "", 
        "darkmode": player.darkmode,

        "piece_option": player.piece_set 
    }
    if request.method == "POST":
        print(request.POST)
        if request.POST.__contains__("pieces"):
            print(player)
            player.piece_set = request.POST.get("pieces")
            print(player.piece_set)
            context["piece_change_error"] = "Piece set succesfully updated!"
            context["piece_option"] = request.POST.get("pieces")
        elif request.POST.__contains__("oldpass"):
            # changing password
            print(player)
            if player.user.check_password(request.POST.get("oldpass")):
                if request.POST.get("newpass1") == request.POST.get("newpass2"):
                    # add check for whether password is good later
                    try:
                        validate_password(request.POST.get("newpass1"))
                        context["change_password_error"] = "Changed password!"
                        print("Changed password!")
                        player.user.set_password(request.POST.get("newpass1"))
                        player.user.save()
                    except ValidationError as e:
                        print(e)
                        print(e.error_list[0])
                        context["change_password_error"] = e.error_list[0]
                else:
                    print("Your second confirmation is incorrect!")
                    context["change_password_error"] = "Your confirmed password does not match your first one!"
            else:
                context["change_password_error"] = "Wrong old password!"
                print("Wrong old password!")
        elif 'darkmode' in request.POST:
            player.darkmode = True
            print(player.darkmode)
            player.save()
            return redirect('/settings')
        else:
            # if there is no parameter, assume it's turning off dark mode
            player.darkmode = False
            player.save()
            return redirect('/settings')
    player.save()
    return render(request=request, template_name="settings.html", context=context)

def update(request):
    if request.method == "POST":
        if "changeRating" in request.POST:
            rating_diff = int(request.POST.get("changeRating"))
            player, _ = Player.objects.get_or_create(user=request.user)
            player.rating += rating_diff
            player.save()
        if "changeTacticsCorrect" in request.POST:
            tactic_diff = int(request.POST.get("changeTacticsCorrect"))
            player, _ = Player.objects.get_or_create(user=request.user)
            if tactic_diff > 0:
                player.total_tactics_correct += 1
            else:
                player.total_tactics_incorrect += 1
            player.save()
    return JsonResponse({})

# update_tactics()
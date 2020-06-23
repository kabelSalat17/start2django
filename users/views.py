from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

def register(request):
    # when click on button
    if request.method == 'POST':
        # create a form with request from post request
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # get the name from form
            username= form.cleaned_data.get('username')
            messages.success(request, f"Welcome, {username}. Now you can log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request, id):
    return render(request, 'users/profile.html', {'id':id})




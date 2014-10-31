from django.shortcuts import render,redirect
from app.models.file import File
from django.contrib.auth import authenticate,login
from django.contrib import messages

# see
# https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.login
def index(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page. Currently just our "index.html" site
                #TODO direct to the correct success page (does no exist yet)
                return redirect('/')
        else:
            messages.error(request,'Email/password incorrect')
    return render(request, 'login.html')

from django.shortcuts import render,redirect
from app.models.file import File
from django.contrib.auth import authenticate,login
from django.contrib import messages

# see
# https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.login

##  Default handler for login requests by the client that sends the client the login page. If correct login details were sent with the request (over POST data), the user will be redirected to a success page. Otherwise an error message will be inserted into the django messages queue. 
#   @param request The HttpRequest Object
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
            #else:
                #Some handling because the user is banned/email was not verified yet?
                
               
        else:
            messages.error(request,'Email/password incorrect')
    return render(request, 'login.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomLoginForm


@csrf_exempt

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)  # Pass `request` to support AuthenticationForm's features
        if form.is_valid():
            user = form.get_user()  # AuthenticationForm provides the user if valid
            login(request, user)
            
            # Check user groups for redirection
            if user.groups.filter(name='secretarias').exists():
                return redirect('crearCliente')
            elif user.groups.filter(name='mecanicos').exists():
                return redirect('mecanico')
            elif user.groups.filter(name='jefe').exists():
                return redirect('informe')
            else:
                return redirect('/')
        else:
            print("Form errors:", form.errors)  # Debugging output to show errors in console
    else:
        form = CustomLoginForm()

    return render(request, 'login/login.html', {'form': form})

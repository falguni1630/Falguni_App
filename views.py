from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader

from .models import Customer, Account
from .models import Check
from django.contrib import messages
import time
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login


# Create your views here.

def dashboard(request):
    return render(request, 'bankingApp/index.html')


def signup(request):
    if request.method == 'POST':

        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password']
        confirm_password = request.POST['confirmpassword']

        if User.objects.filter(username=username):
            messages.error(request, 'Username already exists!')
            return redirect('signup')

        if password1 == confirm_password:

            customer = Customer(
                firstname=firstname,
                lastname=lastname,
                email=email,
                username=username,
                password=password1)

            customer.save()

            user = User.objects.create_user(username=username, password=password1)
            user.email = email
            user.first_name = firstname
            user.last_name = lastname

            user.save()

            messages.success(request, "Account created successfully! Login to continue.")

            time.sleep(2)

            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'bankingApp/signup.html')

    return render(request, 'bankingApp/signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            first_name = user.first_name

            return render(request, 'bankingApp/ViewAccounts.html', {'first_name': first_name})

        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('dashboard')

    return render(request, 'bankingApp/login.html')


def signout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('dashboard')


def account_details(request):
    var_customer = Customer.objects.filter(username='arhat1').values()
    var_cust_id=var_customer[0]['customer_id']
    var_account = Account.objects.filter(customer_id_id=var_cust_id).values()
    var_acc_num = var_account[0]['account_number']
    var_transaction = Check.objects.filter(account_number=var_acc_num).values()
    template = loader.get_template('bankingApp/ChequingAcct.html')
    context = {
        'mycustomer': var_customer,
        'myaccount': var_account,
        'mytransaction':var_transaction
            }
    return HttpResponse(template.render(context, request))

# Cust_Id =""
# account = Check.objects.get(account_number=account_number)
# return render(request, 'bankingApp/ChequingAcct.html', {'account': account})

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator
from bankingApp.models import Account, Check, Customer, Saving, CreditCard
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
        request.session['username'] = username
        if user is not None:
            auth_login(request, user)
            first_name = user.first_name

            # Chequing Account Details
            c_account = Account.objects.get(account_type="Chequing",
                                            customer_id=(
                                                Customer.objects.get(username=request.session['username'])).customer_id)
            c_accNum = c_account.account_number
            transactions = Check.objects.filter(account_number=c_accNum)

            # set the account balance to the sum of all transactions and the initial balance

            var_balance = 0
            for transaction in transactions:
                if transaction.transaction_type == 'Credit':
                    var_balance += transaction.transaction_amount
                elif transaction.transaction_type == 'Debit':
                    var_balance -= transaction.transaction_amount

            c_account.balance = var_balance

            # Saving Account Details
            s_account = Account.objects.get(account_type="Saving",
                                            customer_id=(
                                                Customer.objects.get(username=request.session['username'])).customer_id)
            s_accNum = s_account.account_number
            transactions = Saving.objects.filter(account_number=s_accNum)

            # set the account balance to the sum of all transactions and the initial balance

            balance = s_account.balance
            var_balance = 0
            for transaction in transactions:
                if transaction.transaction_type == 'Credit':
                    var_balance += transaction.transaction_amount
                elif transaction.transaction_type == 'Debit':
                    var_balance -= transaction.transaction_amount

            s_account.balance = var_balance

            return render(request, 'bankingApp/ViewAccounts.html',
                          {'first_name': first_name,
                           'checking_account_num': c_accNum,
                           'checking_account_balance': c_account.balance,
                           'saving_account_num': s_accNum,
                           'saving_account_balance': s_account.balance})

        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')

    return render(request, 'bankingApp/login.html')


def signout(request):
    logout(request)
    request.session['username'] = ""
    messages.success(request, 'Logged out successfully!')
    return redirect('dashboard')


def account_details(request):
    # Chequing Account Details

    c_account = Account.objects.get(account_type="Chequing",
                                    customer_id=(
                                        Customer.objects.get(username=request.session['username'])).customer_id)
    c_accNum = c_account.account_number
    transactions = Check.objects.filter(account_number=c_accNum)

    # set the account balance to the sum of all transactions and the initial balance

    balance = c_account.balance
    var_balance = 0
    for transaction in transactions:
        if transaction.transaction_type == 'Credit':
            var_balance += transaction.transaction_amount
        elif transaction.transaction_type == 'Debit':
            var_balance -= transaction.transaction_amount

    c_account.balance = var_balance

    # Saving Account Details
    s_account = Account.objects.get(account_type="Saving",
                                    customer_id=(
                                        Customer.objects.get(username=request.session['username'])).customer_id)
    s_accNum = s_account.account_number
    transactions = Saving.objects.filter(account_number=s_accNum)

    # set the account balance to the sum of all transactions and the initial balance

    balance = s_account.balance
    var_balance = 0
    for transaction in transactions:
        if transaction.transaction_type == 'Credit':
            var_balance += transaction.transaction_amount
        elif transaction.transaction_type == 'Debit':
            var_balance -= transaction.transaction_amount

    s_account.balance = var_balance
    """
            saving_acc = Account.objects.get(account_type="Saving", customer_id=(
                Customer.objects.get(username=request.session['username'])).customer_id)
            saving_account_num = saving_acc.account_number
            saving_account_balance = saving_acc.balance

            saving_transactions = Saving.objects.filter(account_number=saving_account_num)
            for transaction in saving_transactions:
                if transaction.transaction_type == 'credit':
                    saving_account_balance += transaction.transaction_amount
                elif transaction.transaction_type == 'debit':
                    saving_account_balance -= transaction.transaction_amount
            """
    return render(request, 'bankingApp/ViewAccounts.html',
                  {
                      'checking_account_num': c_accNum,
                      'checking_account_balance': c_account.balance,
                      'saving_account_num': s_accNum,
                      'saving_account_balance': s_account.balance})


# Chequing Account Transaction  Details

# New transaction - Credit Amount
def credit_money(request):
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        description = request.POST['description']
        date = request.POST['date']
        account = Account.objects.get(account_type="Chequing",
                                      customer_id=(
                                          Customer.objects.get(username=request.session['username'])).customer_id)
        account.balance += amount
        account.save()
        new_trans = Check(account_number=account, transaction_amount=amount,
                          transaction_type='Credit', transaction_desc='description',
                          transaction_date='date')
        new_trans.save()
      
        return redirect('bankingApp/SampleChequing.html')

    return render(request, 'bankingApp/SampleChequing.html')
 

def checkingaccount(request):
    account = Account.objects.get(account_type="Chequing",
                                  customer_id=(Customer.objects.get(username=request.session['username'])).customer_id)
    accNum = account.account_number
    if request.method == "POST":
        fromdate = request.POST.get('fromDate')
        todate = request.POST.get('toDate')
        searchResult = Check.objects.filter(transaction_date__gte=fromdate, transaction_date__lte=todate,
                                            account_number=accNum)
        return render(request, 'bankingApp/SampleChequing.html', {'account': account, 'var_trans': searchResult})
    else:
        transactions = Check.objects.filter(account_number=accNum)

        # var_tran_id = transactions.transaction_id
        # set the account balance to the sum of all transactions and the initial balance

        balance = account.balance
        var_balance = 0
        for transaction in transactions:
            if transaction.transaction_type == 'Credit':
                var_balance += transaction.transaction_amount
            elif transaction.transaction_type == 'Debit':
                var_balance -= transaction.transaction_amount

        account.balance = var_balance
        account.save()

        # SET PAGINATION

        p = Paginator(transactions, 5)
        page = request.GET.get('page')
        var_trans = p.get_page(page)

        return render(request, 'bankingApp/SampleChequing.html',
                      {'account': account, 'transactions': transactions, 'var_trans': var_trans})


# Saving Account Transaction Details
def savingsaccount(request):
    account = Account.objects.get(account_type="Saving",
                                  customer_id=(Customer.objects.get(username=request.session['username'])).customer_id)
    accNum = account.account_number
    accInterest = account.interest_rate / 12
    monthly_interest = (account.balance * accInterest) / 100
    if request.method == "POST":
        fromdate = request.POST.get('fromDate')
        todate = request.POST.get('toDate')
        searchResult = Saving.objects.filter(transaction_date__gte=fromdate, transaction_date__lte=todate,
                                             account_number=accNum)
        return render(request, 'bankingApp/Saving.html', {'account': account, 'transactions': searchResult})
    else:
        transactions = Saving.objects.filter(account_number=accNum)

        # set the account balance to the sum of all transactions and the initial balance

        balance = account.balance
        var_balance = 0
        for transaction in transactions:
            if transaction.transaction_type == 'Credit':
                var_balance += transaction.transaction_amount
            elif transaction.transaction_type == 'Debit':
                var_balance -= transaction.transaction_amount

        account.balance = var_balance
        account.save()

        # Calculate Interest on monthly basis

        return render(request, 'bankingApp/Saving.html',
                      {'account': account, 'transactions': transactions, 'monthly_interest': monthly_interest})

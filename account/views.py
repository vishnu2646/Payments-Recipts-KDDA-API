from datetime import datetime, date
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.models import Expense, ExpenseType, Income, IncomeType, Opening
from account.serializers import (
    ExpenseTypeSerializer,
    IncomeTypeSerializer,
    SendPasswordResetEmailSerializer,
    UserChangePasswordSerializer,
    UserLoginSerializer,
    UserPasswordResetSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    GetIncomeSerializer,
    GetExpenseSerializer,
    BarChartDataSerializer,
    OpeningSerializer
)
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.db.models import Sum, DateField
from django.db.models.functions import TruncMonth, Cast
from account.renderers import UserRenderer
from django.db import models

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # If using JWT authentication
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklists the token so it can no longer be used

            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(
        data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def apiOverView(request):
    api_urls = {
        'income_list': '/income/list',
        'income_details': '/income/details/:id/'
    }
    return JsonResponse(api_urls)

@api_view(['GET'])
def IncomeList(request):
    if(request.user.is_authenticated):
        incomes = Income.objects.all()
        serializer = GetIncomeSerializer(incomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('User is not authenticated', status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def IncomeDetail(request, pk):
    if(request.user.is_authenticated):
        income = Income.objects.get(id=pk)
        serializer = GetIncomeSerializer(income, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response("User is not authenticated", status=status.HTTP_401_UNAUTHORIZED)

class AddIncome(APIView):
    def post(self, request):
        if(request.user.is_authenticated):
            serializer = GetIncomeSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response("Income saved successfully", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("User is not authorized to create a new income", status=status.HTTP_401_UNAUTHORIZED)

class UpdateIncome(APIView):
    def post(self, request, pk):
        income = Income.objects.get(id=pk)
        serializer = GetIncomeSerializer(instance=income,data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response("Income Updated successfully", status=status.HTTP_200_OK)

@api_view(['DELETE'])
def DeleteIncome(request, pk):
    income = Income.objects.get(id=pk)
    income.delete()
    return Response("Income Deleted successfully", status=status.HTTP_200_OK)

@api_view(['GET'])
def ExpenseList(requet):
    if(requet.user.is_authenticated):
        expenses = Expense.objects.all()
        serializer = GetExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('User is Not Authenticated', status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def ExpenseDetail(request, pk):
    if(request.user.is_authenticated):
        expense = Expense.objects.get(expid=pk)
        serializer = GetExpenseSerializer(expense, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response("User is not authenticated", status=status.HTTP_401_UNAUTHORIZED)

class AddExpense(APIView):
    def post(self, request):
        if(request.user.is_authenticated):
            serializer = GetExpenseSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response("Expense saved successfully", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("User is not authorized to create a new expense", status=status.HTTP_401_UNAUTHORIZED)

class UpdateExpense(APIView):
    def post(self, request, pk):
        try:
            expense = Expense.objects.get(expid=pk)
        except Expense.DoesNotExist:
            return Response("Expense not found", status=status.HTTP_404_NOT_FOUND)
        serializer = GetExpenseSerializer(instance=expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Expense updated successfully", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def DeleteExpense(request, pk):
    expense = Expense.objects.get(expid=pk)
    expense.delete()
    return Response("Expense Deleted successfully", status=status.HTTP_200_OK)

@api_view(['GET'])
def ExpenseTypeList(requet):
    if(requet.user.is_authenticated):
        expenses = ExpenseType.objects.all()
        serializer = ExpenseTypeSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('User is Not Authenticated', status=status.HTTP_401_UNAUTHORIZED)

class AddExpenseType(APIView):
    def post(self, request):
        if(request.user.is_authenticated):
            serializer = ExpenseTypeSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save()
            return Response("Expense Type saved successfully", status=status.HTTP_200_OK)
        return Response("User is not authorized to create a new expense type", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def IncomeTypeList(requet):
    if(requet.user.is_authenticated):
        income = IncomeType.objects.all()
        serializer = IncomeTypeSerializer(income, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('User is Not Authenticated', status=status.HTTP_401_UNAUTHORIZED)

class AddIncomeType(APIView):
    def post(self, request):
        if(request.user.is_authenticated):
            serializer = IncomeTypeSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save()
            return Response("Income Type saved successfully", status=status.HTTP_200_OK)
        return Response("User is not authorized to create a new income type", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def getOpeningDetails(request):
    if (request.user.is_authenticated):
        openings = Opening.objects.all()
        serializer = OpeningSerializer(openings, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response("User is not authenticated",status=status.HTTP_400_BAD_REQUEST)

class UpdateOpening(APIView):
    def post(self, request, id):
        opening = Opening.objects.get(id=id)
        serializer = OpeningSerializer(instance=opening, data = request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response("Opening updated successfully", status=status.HTTP_200_OK)

class AddOpening(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            serializer = OpeningSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response("Opening added successfully", status=status.HTTP_200_OK)
            return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)
        return Response("User is not authenticated", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
def deleteOpeningDetails(request, id):
    if (request.user.is_authenticated):
        opening = Opening.objects.get(id=id)
        opening.delete()
        return Response("Deleted Successfully", status=status.HTTP_200_OK)
    return Response("User is not authenticated",status=status.HTTP_400_BAD_REQUEST)

class ReportView(APIView):
    def get(self, request):
        if(request.user.is_authenticated):
            incomes = Income.objects.all()
            expenses = Expense.objects.all()
            openings = Opening.objects.all()

            incomeSerializer = GetIncomeSerializer(incomes, many=True)
            expenseSerializer = GetExpenseSerializer(expenses, many=True)
            openingSerializer = OpeningSerializer(openings, many=True)

            incomeData = incomeSerializer.data
            expenseData = expenseSerializer.data
            openingData = openingSerializer.data

            tot = sum(income['amount'] for income in incomeData)

            lastYearIncomeTotal = 0

            for opening in openingData:
                lastYearIncomeTotal = opening['cashinhand'] + opening['cashatbank']

            finalIncome = lastYearIncomeTotal + tot

            amt = sum(expense['amount'] for expense in expenseData)

            fin = finalIncome

            current_date = datetime.today()

            extot = sum(expense['amount'] for expense in expenseData)
            a = fin - sum(expense['amount'] for expense in expenseData)

            b = 0
            for opening in openingData:
                b = opening['cashatbankexp'] - a
                print(opening, "opening")

            finexp = extot + a

            result = Income.objects.values('income_name').annotate(total_amt=Sum('amount'))
            expx = Expense.objects.values('expense_name').annotate(exp_tot=Sum('amount'))

            response_data = {
                "result": result,
                "tot": tot,
                "extot": extot,
                "openings": openingSerializer.data,
                "fin": fin,
                "b": b,
                "finexp": finexp,
                "expx": expx,
                "date": current_date,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response("User is not authorized", status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def tilesList(request):
    incomes = Income.objects.all()
    incomeSerializer = GetIncomeSerializer(incomes, many=True)

    expenses = Expense.objects.all()
    expenseSerializer = GetExpenseSerializer(expenses, many=True)

    incomeData = incomeSerializer.data
    expenseData = expenseSerializer.data

    incomeTotal = sum(income['amount'] for income in incomeData)
    expenseTotal = sum(expense['amount'] for expense in expenseData)

    data = {
        "incomeTotal": incomeTotal,
        "expenseData": expenseTotal,
    }
    return Response(data, status=status.HTTP_200_OK)

class ExpenseBarChartView(APIView):
    def get(self, request):
        # Group by 'mode' and sum the 'amount' for each mode
        expense_data = (
            Expense.objects
            .values('expense_name')  # Group by the 'mode' field
            .annotate(total_amount=Sum('amount'))  # Sum the 'amount' for each mode
            .order_by('expense_name')  # Optionally, order by mode
        )

        # Prepare the data for the bar chart
        chart_data = {
            'labels': [],
            'data': []
        }

        # Populate the labels and data lists for the chart
        for item in expense_data:
            chart_data['labels'].append(item['expense_name'])
            chart_data['data'].append(item['total_amount'])

        return Response(chart_data)

class IncomeBarChartView(APIView):
    def get(self, request):
        # Group by 'mode' and sum the 'amount' for each mode
        income_data = (
            Income.objects
            .values('income_name')  # Group by the 'mode' field
            .annotate(total_amount=Sum('amount'))  # Sum the 'amount' for each mode
            .order_by('income_name')  # Optionally, order by mode
        )

        # Prepare the data for the bar chart
        chart_data = {
            'labels': [],
            'data': []
        }

        # Populate the labels and data lists for the chart
        for item in income_data:
            chart_data['labels'].append(item['income_name'])
            chart_data['data'].append(item['total_amount'])

        return Response(chart_data)
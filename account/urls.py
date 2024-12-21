from django.urls import path
from account.views import (
    AddExpense,
    AddExpenseType,
    AddIncomeType,
    DeleteExpense,
    DeleteIncome,
    ExpenseDetail,
    ExpenseList,
    IncomeList,
    ExpenseTypeList,
    IncomeDetail,
    IncomeTypeList,
    tilesList,
    UpdateExpense,
    UpdateIncome,
    AddIncome,
    SendPasswordResetEmailView,
    UserChangePasswordView,
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
    UserPasswordResetView,
    apiOverView,
    ReportView,
    getOpeningDetails,
    deleteOpeningDetails,
    UpdateOpening,
    AddOpening,
    ExpenseBarChartView,
    IncomeBarChartView,
    LogoutView
)
urlpatterns = [
    path('', apiOverView, name='api-overview'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('income/list/', IncomeList, name='income-list'),
    path('income/detail/<str:pk>/',IncomeDetail, name='income-detail'),
    path('income/create/', AddIncome.as_view(), name='income-create'),
    path('income/update/<str:pk>/', UpdateIncome.as_view(), name='income-update'),
    path('income/delete/<str:pk>/', DeleteIncome, name='income-delete'),

    path('expense/list/', ExpenseList, name='expense-list'),
    path('expense/detail/<str:pk>/',ExpenseDetail, name='expense-detail'),
    path('expense/create/', AddExpense.as_view(), name='expense-create'),
    path('expense/update/<str:pk>/', UpdateExpense.as_view(), name='expense-update'),
    path('expense/delete/<str:pk>/', DeleteExpense, name='expense-delete'),

    path('expensetype/list/', ExpenseTypeList, name='expense-type-list'),
    path('expensetype/create/', AddExpenseType.as_view(), name='expense-type-create'),

    path('incometype/list/', IncomeTypeList, name='income-type-list'),
    path('incometype/create/', AddIncomeType.as_view(), name='income-type-create'),

    path('openings/', getOpeningDetails, name='openings'),
    path('openings/delete/<str:id>/', deleteOpeningDetails, name='delete-openings'),
    path('openings/update/<str:id>/', UpdateOpening.as_view(), name='update-openings'),
    path('openings/create', AddOpening.as_view(), name='create-openings'),

    path("report/", ReportView.as_view(), name='report-view'),

    path('tiles/', tilesList, name='tile-data'),
    path('expense/bar/', ExpenseBarChartView.as_view(), name='income-bar-chart'),
    path('income/bar/', IncomeBarChartView.as_view(), name='income-bar-chart'),
]
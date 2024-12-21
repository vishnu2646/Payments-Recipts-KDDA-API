from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

#  Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#  Custom User Model
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

PAYMENT_TYPE = (
    ('CASH','cash'),
    ('CHEQUE','cheque'),
    ('DEMAND DRAFT','demand draft'),
    ('Transfer', 'transfer')
)

class Income(models.Model):
    incid = models.IntegerField()
    income_name = models.CharField(null=True,blank=True,max_length=255)
    amount = models.IntegerField(default=0, null=True,blank=True,)
    date = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=15,choices=PAYMENT_TYPE, null=True,blank=True,)
    reason = models.TextField(max_length=300,null=True,blank=True,)
    income_by = models.CharField(max_length=100,blank=True, null=True)
    bankname = models.CharField(max_length=50,null=True,blank=True,default=None)
    chequeordd = models.IntegerField(null=True,blank=True)
    dateinbank = models.CharField(null=True,blank=True,default=None,max_length=50)
    details = models.TextField(null=True,max_length=255,blank=True)

    def __str__(self):
        return self.income_name

class Expense(models.Model):
    expid = models.IntegerField()
    expense_name = models.CharField(max_length=255, null=True,blank=True,)
    amount = models.IntegerField(default=0,null=True,blank=True)
    date = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=15,choices=PAYMENT_TYPE,null=True,blank=True)
    reason = models.TextField(max_length=300,null=True,blank=True,)
    expense_by = models.CharField(max_length=100, blank=True, null=True)
    bankname = models.CharField(max_length=50,null=True,blank=True,default=None)
    chequeordd = models.IntegerField(default=None,null=True,blank=True)
    dateinbank = models.CharField(null=True,blank=True,default=None,max_length=50)
    details = models.TextField(null=True,max_length=255,blank=True)

    def __str__(self):
        return self.expense_name

class IncomeType(models.Model):
    typeid = models.IntegerField()
    typename = models.CharField(max_length=50)

    def __str__(self):
        return self.typename

class ExpenseType(models.Model):
    etypeid = models.IntegerField()
    etypename = models.CharField(max_length=50)

    def __str__(self):
        return self.etypename

class Opening(models.Model):
    cashinhand = models.IntegerField(blank=True,null=True)
    cashatbank = models.IntegerField(blank=True,null=True)
    cashatbankexp = models.IntegerField(blank=True,null=True)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('kdda/admin/', admin.site.urls),
    path('kdda/api/user/', include('account.urls'))
]

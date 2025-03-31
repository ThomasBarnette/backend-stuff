from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ClassViewSet, UserViewSet

router = DefaultRouter()
router.register(r'classes', ClassViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]


print("Registered URLs:")
for url in router.urls:
    print(url)

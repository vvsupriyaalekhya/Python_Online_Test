# from django.urls import path
# from .views import login_view, exam_view, test_view

# urlpatterns = [
#     path('login/', login_view, name='login'),
#     path('exam/', exam_view, name='exam'),
#     path('test/', test_view, name='test'),
#     path('', login_view),  # Redirect to login by default
# ]
from django.urls import path,include
from django.contrib import admin
from .views import (
    test_view, 
    login_view, 
    exam_view, 
    submit_assessment,
    thank_you_view,
    generate_pdf,
    logout_view,
    capture_view,\
    detect_objects_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/login/', include('django.contrib.auth.urls')),
    path('', login_view, name='login'),
    path('test/', test_view, name='test'),
    path('exam/', exam_view, name='exam'),  # Ensure this matches
    path('submit_assessment/', submit_assessment, name='submit_assessment'),
    path('result/', thank_you_view, name='result'),
    path('logout/', logout_view, name='logout'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
    path('capture/', capture_view, name='capture'),
    path('detect_objects/', detect_objects_view, name='detect_objects'),
]


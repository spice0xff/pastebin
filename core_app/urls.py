from django.urls import path, re_path
from . import views


app_name = 'core_app'
urlpatterns = [
    path('', views.home, name='home'),
    path('add_paste', views.add_paste, name='add_paste'),
    path('paste/<str:hash>', views.paste, name='paste'),
    path('oops', views.oops, name='oops'),

    path('registration', views.registration, name='registration'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('my_paste_list', views.my_paste_list, name='my_paste_list'),
    path('access_denied', views.access_denied, name='access_denied'),
    path('find', views.find, name='find'),
]

# # Для раздачи статики в режиме разработки.
# if settings.DEBUG:
#     urlpatterns += [
#         re_path(r'^static/(?P<path>.*)$', static_views.serve),
#     ]

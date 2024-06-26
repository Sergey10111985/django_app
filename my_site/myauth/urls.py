from django.contrib.auth.views import LoginView
from django.urls import path
from myauth.views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    # MyLogoutView,
    logout_view,
    AboutMeView,
    RegisterView,
    JsonTestView,
    UsersListView,
    UserInfoView,
    HelloView,
)

app_name = 'myauth'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name='login'),
    path("hello/", HelloView.as_view(), name="hello"),
    path("logout/", logout_view, name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about_me"),
    path("users/", UsersListView.as_view(), name="users_list"),
    path("user-info/<int:pk>", UserInfoView.as_view(), name="user_info"),
    path("register/", RegisterView.as_view(), name="register"),
    path("cookie/get/", get_cookie_view, name="get_cookie"),
    path("cookie/set/", set_cookie_view, name="set_cookie"),
    path("session/get/", get_session_view, name="get_session"),
    path("session/set/", set_session_view, name="set_session"),
    path("json-view/", JsonTestView.as_view(), name="json_view"),
]

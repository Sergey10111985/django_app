from random import random

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from .forms import AboutMeForm
from .models import Profile


class HelloView(View):
    welcome_message = _('welcome hello world')

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            "One product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class UsersListView(ListView):
    model = Profile
    template_name = 'myauth/users-list.html'
    context_object_name = 'users'


class UserInfoView(UserPassesTestMixin, UpdateView):
    form_class = AboutMeForm
    template_name = 'myauth/user-info.html'
    success_url = reverse_lazy('myauth:users_list')

    def get_object(self, queryset=None):
        # не нашёл лучшего способа как взять нужный профиль
        prof = Profile.objects.get(id=int(self.request.get_full_path()[-1]))
        return prof

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return self.request.user.is_staff or self.request.user == self.get_object().user


class AboutMeView(UpdateView):
    template_name = "myauth/about-me.html"

    form_class = AboutMeForm
    success_url = reverse_lazy('myauth:about-me')

    def get_object(self, queryset=None):
        prof = Profile.objects.get(user_id=self.request.user)
        return prof


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')
    return render(request, 'myauth/login.html', {'error': 'Invalid username or password.'})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    template_name = 'myauth/logout.html'
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookies set")
    response.set_cookie("test_cookie", "test_cookie_value", max_age=3600)
    return response

@cache_page(10)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("test_cookie", "default_value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["test_session"] = "test_session_value"
    return HttpResponse("Session set")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("test_session", "default_value")
    return HttpResponse(f"Session value: {value!r}")


class JsonTestView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"test": "test", "test2": "test2"})

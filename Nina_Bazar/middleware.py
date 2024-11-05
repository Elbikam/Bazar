from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip login check if user is authenticated
        if request.user.is_authenticated:
            return self.get_response(request)

        # Define URLs that should be accessible without login
        exempt_urls = [settings.LOGIN_URL, '/signup/', '/login/']
        if resolve(request.path_info).url_name not in [url.strip('/') for url in exempt_urls]:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware для требования авторизации на всех страницах,
    кроме явно разрешенных.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Список URL, доступных без авторизации
        self.public_paths = [
            reverse('login'),  # страница входа
            '/admin/login/',   # вход в админку
            '/static/',        # статические файлы
            '/media/',         # медиа файлы
        ]
    
    def __call__(self, request):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            # Проверяем, находится ли запрашиваемый путь в списке публичных
            path = request.path_info
            if not any(path.startswith(public_path) for public_path in self.public_paths):
                return redirect(f"{reverse('login')}?next={path}")
        
        response = self.get_response(request)
        return response
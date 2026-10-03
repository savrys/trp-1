from django.http import HttpResponse


def page(title, content):
    """Единый каркас для всех веб-страниц приложения с Bootstrap 5.3"""
    bootstrap = (
        "https://jsdelivr.net"
        "bootstrap@5.3.3/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="navbar navbar-expand navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">BikeRent</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Главная</a>
                <a class="nav-link" href="/bikes/">Велосипеды и Станции</a>
                <a class="nav-link" href="/rentals/">Журнал аренды</a>
            </div>
        </div>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    """Отображение главной страницы проекта"""
    content = """
    <div class="p-5 mb-4 bg-light rounded-3 mt-3">
        <div class="container-fluid py-5">
            <h1 class="display-5 fw-bold">BikeRent</h1>
            <p class="col-md-8 fs-4">
                Добро пожаловать в веб-интерфейс системы
                автоматизированного проката велосипедов.
            </p>
            <hr class="my-4">
            <p>
                Используйте панель навигации выше или кнопки ниже
                для просмотра текущего состояния системы.
            </p>
            <a href="/bikes/" class="btn btn-primary btn-lg me-2">
                Каталог велосипедов
            </a>
            <a href="/rentals/" class="btn btn-secondary btn-lg">
                Журнал аренды
            </a>
        </div>
    </div>
    """
    return HttpResponse(page("Главная – BikeRent", content))

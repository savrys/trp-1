from django.http import HttpResponse


def page(title, content):
    bootstrap = (
        "https://jsdelivr.net"
        "/dist/css/bootstrap.min.css"
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
    <nav class="nav container my-3">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/bikes/">Велосипеды</a>
        <a class="nav-link" href="/rentals/">Аренды</a>
    </nav>
    <nav class="container">{content}</nav>
</body>
</html>"""


def index(request):
    content = """
    <h1 class="display-4">Bikely</h1>
    <p class="lead">Система управления шерингом велосипедов.</p>
    <a href="/bikes/" class="btn btn-primary me-2">Просмотр велосипедов</a>
    <a href="/rentals/" class="btn btn-secondary">Просмотр аренд</a>
    """
    return HttpResponse(page("Bikely – Главная", content))

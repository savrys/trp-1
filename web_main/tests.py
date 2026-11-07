"""Тесты главной страницы и кастомной страницы ошибки 404."""

from django.test import TestCase, override_settings
from django.urls import reverse


class IndexViewTests(TestCase):
    """Проверка главной страницы."""

    def test_index_page_renders(self):
        response = self.client.get(reverse("web_main:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_main/index.html")
        self.assertContains(response, "Bikely")


class Custom404Tests(TestCase):
    """Проверка кастомной страницы ошибки 404."""

    def test_unknown_url_returns_custom_page(self):
        response = self.client.get("/net-takoy-stranicy/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(
            response,
            "Страница не найдена",
            status_code=404,
        )
        self.assertContains(response, "На главную", status_code=404)

    def test_unknown_bike_returns_custom_page(self):
        response = self.client.get(
            reverse("web_bikes:detail", args=[9999])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_unknown_rental_returns_custom_page(self):
        response = self.client.get(
            reverse("web_rentals:detail", args=[9999])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    @override_settings(DEBUG=True)
    def test_custom_page_is_shown_when_debug_enabled(self):
        response = self.client.get("/net-takoy-stranicy/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(
            response,
            "Страница не найдена",
            status_code=404,
        )
        self.assertNotContains(
            response,
            "You're seeing this error because you have",
            status_code=404,
        )


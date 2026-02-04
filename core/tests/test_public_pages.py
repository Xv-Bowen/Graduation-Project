from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Article, Category


class PublicPagesTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="情绪管理")
        Article.objects.create(
            category=category,
            title="示例文章",
            summary="示例摘要",
            content="示例内容",
            is_published=True,
        )
        Article.objects.create(
            category=category,
            title="睡眠建议",
            summary="与睡眠相关",
            content="睡眠",
            is_published=True,
        )
        Article.objects.create(
            category=category,
            title="焦虑应对",
            summary="与焦虑相关",
            content="焦虑",
            is_published=True,
        )

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_knowledge_list_redirects_to_login_when_logged_out(self):
        response = self.client.get(reverse("knowledge_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_knowledge_list_requires_login(self):
        user = User.objects.create_user(username="tester", password="pass12345")
        self.client.login(username="tester", password="pass12345")
        response = self.client.get(reverse("knowledge_list"))
        self.assertEqual(response.status_code, 200)

    def test_knowledge_search_splits_tokens(self):
        user = User.objects.create_user(username="tester", password="pass12345")
        self.client.login(username="tester", password="pass12345")
        response = self.client.get(reverse("knowledge_list"), {"query": "睡眠、焦虑"})
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn("睡眠建议", html)
        self.assertIn("焦虑应对", html)

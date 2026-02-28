from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from blog.models import Category, Comment, Post


class PostModelTests(TestCase):
    def test_auto_slug_and_suffix(self):
        user = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        category = Category.objects.create(name="Python", slug="python")

        first = Post.objects.create(
            title="Привет Django",
            content="content",
            author=user,
            category=category,
            is_published=True,
        )
        second = Post.objects.create(
            title="Привет Django",
            content="content2",
            author=user,
            category=category,
            is_published=True,
        )

        self.assertTrue(first.slug)
        self.assertTrue(second.slug.endswith("-2"))

    def test_slug_max_length_respected_with_suffix(self):
        user = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        category = Category.objects.create(name="Backend", slug="backend")
        long_title = "a" * 260

        first = Post.objects.create(title=long_title, content="c1", author=user, category=category, is_published=True)
        second = Post.objects.create(title=long_title, content="c2", author=user, category=category, is_published=True)

        self.assertLessEqual(len(first.slug), 200)
        self.assertLessEqual(len(second.slug), 200)


class CommentFormTests(TestCase):
    def test_comment_too_short(self):
        from blog.forms import CommentForm

        form = CommentForm(data={"text": "a"})
        self.assertFalse(form.is_valid())

    def test_comment_valid(self):
        from blog.forms import CommentForm

        form = CommentForm(data={"text": "Это валидный комментарий"})
        self.assertTrue(form.is_valid())


class PostPermissionsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        self.other_user = User.objects.create_user(username="other", email="other@example.com", password="pass12345")
        self.category = Category.objects.create(name="Python", slug="python")
        self.post = Post.objects.create(
            title="Auth Post",
            content="Body",
            author=self.author,
            category=self.category,
            is_published=True,
        )

    def test_anonymous_redirected_from_create_edit_delete(self):
        create_response = self.client.get(reverse("blog:post_create"))
        edit_response = self.client.get(reverse("blog:post_edit", kwargs={"slug": self.post.slug}))
        delete_response = self.client.get(reverse("blog:post_delete", kwargs={"slug": self.post.slug}))

        self.assertEqual(create_response.status_code, 302)
        self.assertEqual(edit_response.status_code, 302)
        self.assertEqual(delete_response.status_code, 302)

    def test_authenticated_non_author_gets_403(self):
        self.client.login(username="other", password="pass12345")

        edit_response = self.client.get(reverse("blog:post_edit", kwargs={"slug": self.post.slug}))
        delete_response = self.client.get(reverse("blog:post_delete", kwargs={"slug": self.post.slug}))

        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)


class PostListAndSearchTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        self.category = Category.objects.create(name="Django", slug="django")

    def test_only_published_in_list_and_category(self):
        Post.objects.create(
            title="Published",
            content="Visible",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        Post.objects.create(
            title="Draft",
            content="Hidden",
            author=self.author,
            category=self.category,
            is_published=False,
        )

        list_response = self.client.get(reverse("blog:post_list"))
        category_response = self.client.get(reverse("blog:category_posts", kwargs={"slug": self.category.slug}))

        self.assertContains(list_response, "Published")
        self.assertNotContains(list_response, "Draft")
        self.assertContains(category_response, "Published")
        self.assertNotContains(category_response, "Draft")

    def test_search_works_only_on_non_empty_query(self):
        Post.objects.create(
            title="Django search",
            content="special keyword",
            author=self.author,
            category=self.category,
            is_published=True,
        )

        empty_query = self.client.get(reverse("blog:post_list"), {"q": "   "})
        active_query = self.client.get(reverse("blog:post_list"), {"q": "keyword"})

        self.assertEqual(empty_query.status_code, 200)
        self.assertContains(active_query, "Django search")

    def test_pagination_10_per_page(self):
        for index in range(11):
            Post.objects.create(
                title=f"Post {index}",
                content="content",
                author=self.author,
                category=self.category,
                is_published=True,
            )

        first_page = self.client.get(reverse("blog:post_list"))
        second_page = self.client.get(reverse("blog:post_list"), {"page": 2})

        self.assertEqual(len(first_page.context["posts"]), 10)
        self.assertEqual(len(second_page.context["posts"]), 1)


class CommentsModerationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        self.commenter = User.objects.create_user(username="reader", email="reader@example.com", password="pass12345")
        self.category = Category.objects.create(name="Python", slug="python")
        self.post = Post.objects.create(
            title="Post",
            content="Body",
            author=self.author,
            category=self.category,
            is_published=True,
        )

    def test_new_comment_goes_to_moderation(self):
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("blog:comment_create", kwargs={"slug": self.post.slug}), {"text": "Новый комментарий"})

        comment = Comment.objects.get(post=self.post, author=self.commenter)
        self.assertFalse(comment.is_approved)

    def test_post_detail_shows_only_approved_comments(self):
        Comment.objects.create(post=self.post, author=self.commenter, text="Approved", is_approved=True)
        Comment.objects.create(post=self.post, author=self.commenter, text="Hidden", is_approved=False)

        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": self.post.slug}))

        self.assertContains(response, "Approved")
        self.assertNotContains(response, "Hidden")


class AdminActionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass12345")
        self.author = User.objects.create_user(username="author", email="author@example.com", password="pass12345")
        self.category = Category.objects.create(name="Ops", slug="ops")
        self.post = Post.objects.create(
            title="Admin Post",
            content="Body",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        self.comment = Comment.objects.create(post=self.post, author=self.author, text="to approve", is_approved=False)

    def test_bulk_approve_action_marks_comments_approved(self):
        self.client.force_login(self.admin)
        changelist_url = reverse("admin:blog_comment_changelist")

        response = self.client.post(
            changelist_url,
            {
                "action": "approve_comments",
                "_selected_action": [self.comment.pk],
                "index": 0,
            },
            follow=True,
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.comment.is_approved)

    def test_post_admin_change_form_loads_with_inline(self):
        self.client.force_login(self.admin)
        change_url = reverse("admin:blog_post_change", args=[self.post.pk])

        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "comments")


class CategoryCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="writer", email="writer@example.com", password="pass12345")

    def test_authenticated_user_can_create_category_with_auto_slug(self):
        self.client.login(username="writer", password="pass12345")
        response = self.client.post(reverse("blog:category_create"), {"name": "Data Science", "slug": ""})

        self.assertRedirects(response, reverse("blog:category_list"))
        category = Category.objects.get(name="Data Science")
        self.assertEqual(category.slug, "data-science")


class PostCategoryTests(TestCase):
    def test_post_form_shows_hint_when_no_categories(self):
        user = User.objects.create_user(username="writer2", email="writer2@example.com", password="pass12345")
        self.client.login(username="writer2", password="pass12345")

        response = self.client.get(reverse("blog:post_create"))

        self.assertContains(response, "Сначала создайте хотя бы одну категорию")
        self.assertContains(response, reverse("blog:category_create"))

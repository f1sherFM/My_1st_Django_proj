from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from blog.models import Category, Comment, Post


class ApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", email="author@example.com", password="pass12345"
        )
        self.other = User.objects.create_user(
            username="other", email="other@example.com", password="pass12345"
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="pass12345",
            is_staff=True,
        )
        self.category = Category.objects.create(name="Python", slug="python")

        self.published_post = Post.objects.create(
            title="Published post",
            content="Visible content",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        self.draft_post = Post.objects.create(
            title="Draft post",
            content="Hidden content",
            author=self.author,
            category=self.category,
            is_published=False,
        )

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_jwt_token_obtain(self):
        response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": "author", "password": "pass12345"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_anonymous_cannot_create_post(self):
        response = self.client.post(
            reverse("api:post_list_create"),
            {
                "title": "API post",
                "content": "Body",
                "category": self.category.pk,
                "is_published": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_patch_and_delete_own_post(self):
        self.auth(self.author)

        patch_response = self.client.patch(
            reverse("api:post_detail", kwargs={"slug": self.published_post.slug}),
            {"title": "Updated by author"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(
            reverse("api:post_detail", kwargs={"slug": self.published_post.slug})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_author_gets_403_for_patch_delete(self):
        self.auth(self.other)

        patch_response = self.client.patch(
            reverse("api:post_detail", kwargs={"slug": self.published_post.slug}),
            {"title": "Updated by other"},
            format="json",
        )
        delete_response = self.client.delete(
            reverse("api:post_detail", kwargs={"slug": self.published_post.slug})
        )

        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_create_returns_201(self):
        self.auth(self.author)
        response = self.client.post(
            reverse("api:post_list_create"),
            {
                "title": "Created via API",
                "content": "Body",
                "category": self.category.pk,
                "is_published": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_posts_list_returns_only_published_in_results(self):
        response = self.client.get(reverse("api:post_list_create"))
        slugs = [item["slug"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.published_post.slug, slugs)
        self.assertNotIn(self.draft_post.slug, slugs)

    def test_posts_list_with_empty_search_returns_all_published(self):
        another_published = Post.objects.create(
            title="Another published",
            content="More visible content",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        response = self.client.get(reverse("api:post_list_create"), {"search": ""})
        slugs = [item["slug"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.published_post.slug, slugs)
        self.assertIn(another_published.slug, slugs)
        self.assertNotIn(self.draft_post.slug, slugs)

    def test_posts_list_ordering_is_desc_by_created_at(self):
        older = Post.objects.create(
            title="Older published",
            content="Older content",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        newer = Post.objects.create(
            title="Newer published",
            content="Newer content",
            author=self.author,
            category=self.category,
            is_published=True,
        )
        response = self.client.get(reverse("api:post_list_create"))
        slugs = [item["slug"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(slugs.index(newer.slug), slugs.index(older.slug))

    def test_post_comment_creates_unapproved(self):
        self.auth(self.other)
        response = self.client.post(
            reverse("api:post_comments", kwargs={"slug": self.published_post.slug}),
            {"text": "Новый комментарий"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(post=self.published_post, author=self.other)
        self.assertFalse(comment.is_approved)

    def test_comments_list_returns_only_approved(self):
        Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="Approved",
            is_approved=True,
        )
        Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="Hidden",
            is_approved=False,
        )

        response = self.client.get(
            reverse("api:post_comments", kwargs={"slug": self.published_post.slug})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = [item["text"] for item in response.data["results"]]
        self.assertIn("Approved", payload)
        self.assertNotIn("Hidden", payload)

    def test_comments_list_ordering_is_asc_by_created_at(self):
        first = Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="A first",
            is_approved=True,
        )
        second = Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="B second",
            is_approved=True,
        )

        response = self.client.get(
            reverse("api:post_comments", kwargs={"slug": self.published_post.slug})
        )
        comment_ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(comment_ids.index(first.id), comment_ids.index(second.id))

    def test_non_staff_cannot_approve_comment(self):
        comment = Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="Need approve",
            is_approved=False,
        )
        self.auth(self.other)

        response = self.client.patch(
            reverse("api:comment_approve", kwargs={"pk": comment.pk}), {}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unpublished_visibility_for_detail_and_comments(self):
        anon_detail = self.client.get(
            reverse("api:post_detail", kwargs={"slug": self.draft_post.slug})
        )
        anon_comments = self.client.get(
            reverse("api:post_comments", kwargs={"slug": self.draft_post.slug})
        )

        self.assertEqual(anon_detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anon_comments.status_code, status.HTTP_404_NOT_FOUND)

        self.auth(self.author)
        author_detail = self.client.get(
            reverse("api:post_detail", kwargs={"slug": self.draft_post.slug})
        )
        author_comments = self.client.get(
            reverse("api:post_comments", kwargs={"slug": self.draft_post.slug})
        )
        self.assertEqual(author_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(author_comments.status_code, status.HTTP_200_OK)

        self.auth(self.staff)
        staff_detail = self.client.get(
            reverse("api:post_detail", kwargs={"slug": self.draft_post.slug})
        )
        staff_comments = self.client.get(
            reverse("api:post_comments", kwargs={"slug": self.draft_post.slug})
        )
        self.assertEqual(staff_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(staff_comments.status_code, status.HTTP_200_OK)

    def test_staff_can_approve_comment_and_non_staff_cannot(self):
        comment = Comment.objects.create(
            post=self.published_post,
            author=self.other,
            text="Need approve",
            is_approved=False,
        )

        self.auth(self.other)
        forbidden_response = self.client.patch(
            reverse("api:comment_approve", kwargs={"pk": comment.pk}), {}, format="json"
        )
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

        self.auth(self.staff)
        ok_response = self.client.patch(
            reverse("api:comment_approve", kwargs={"pk": comment.pk}), {}, format="json"
        )
        self.assertEqual(ok_response.status_code, status.HTTP_200_OK)

        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)

    def test_me_endpoint_requires_auth_and_returns_expected_fields(self):
        anonymous_response = self.client.get(reverse("api:me"))
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth(self.author)
        response = self.client.get(reverse("api:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.author.username)
        self.assertEqual(response.data["email"], self.author.email)
        self.assertIn("is_staff", response.data)
        self.assertIn("bio", response.data)
        self.assertIn("avatar", response.data)
        self.assertIsNone(response.data["avatar"])

    def test_health_endpoint_available_for_anonymous(self):
        response = self.client.get(reverse("api:health"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertIn("django", response.data)

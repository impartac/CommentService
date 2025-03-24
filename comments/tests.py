from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Post, Comment, Like
import uuid

class BaseTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', 
            password='testpass123',
            email='test1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            password='testpass123',
            email='test2@example.com'
        )
        
        self.post1 = Post.objects.create(
            title='Test Post 1',
            content='Content for test post 1',
            author=self.user1
        )
        
        self.comment1 = Comment.objects.create(
            content='Test comment 1',
            author=self.user1,
            post=self.post1
        )
        
        self.like1 = Like.objects.create(
            author=self.user1,
            post=self.post1
        )
        
        self.posts_url = reverse('post-list')
        self.post_detail_url = reverse('post-detail', args=[self.post1.id])
        self.comments_url = reverse('comment-list')
        self.likes_url = reverse('like-list')
        self.users_url = reverse('user-list')
        
        self.client_user1 = APIClient()
        self.client_user1.force_authenticate(user=self.user1)
        
        self.client_user2 = APIClient()
        self.client_user2.force_authenticate(user=self.user2)

class PostTests(BaseTestCase):
    def test_create_post_authenticated(self):
        data = {
            'title': 'New Post',
            'content': 'New post content'
        }
        response = self.client_user1.post(self.posts_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.last().author, self.user1)

    def test_create_post_unauthenticated(self):
        data = {
            'title': 'New Post',
            'content': 'New post content'
        }
        response = self.client.post(self.posts_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post_author(self):
        data = {
            'title': 'Updated Post',
            'content': 'Updated content'
        }
        url = reverse('post-detail', args=[self.post1.id])
        response = self.client_user1.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Updated Post')

    def test_update_post_non_author(self):
        data = {
            'title': 'Updated Post',
            'content': 'Updated content'
        }
        url = reverse('post-detail', args=[self.post1.id])
        response = self.client_user2.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_author(self):
        url = reverse('post-detail', args=[self.post1.id])
        response = self.client_user1.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_non_author(self):
        url = reverse('post-detail', args=[self.post1.id])
        response = self.client_user2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_get_post_comments(self):
        url = reverse('post-comments', args=[self.post1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_like_post(self):
        url = reverse('post-like', args=[self.post1.id])
        

        response = self.client_user2.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post1.like_set.count(), 2)
        

        response = self.client_user2.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

        response = self.client_user2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.post1.like_set.count(), 1)

class CommentTests(BaseTestCase):
    def test_create_comment_authenticated(self):
        data = {
            'content': 'New comment',
            'post': self.post1.id
        }
        response = self.client_user2.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().author, self.user2)

    def test_create_comment_unauthenticated(self):
        data = {
            'content': 'New comment',
            'post': self.post1.id
        }
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_author(self):
        data = {
            'content': 'Updated comment',
            'post': self.post1.id
        }
        url = reverse('comment-detail', args=[self.comment1.id])
        response = self.client_user1.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.content, 'Updated comment')

    def test_update_comment_non_author(self):
        data = {
            'content': 'Updated comment',
            'post': self.post1.id
        }
        url = reverse('comment-detail', args=[self.comment1.id])
        response = self.client_user2.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_comments_by_post(self):
        url = f"{self.comments_url}?post_id={self.post1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class LikeTests(BaseTestCase):
    def test_list_likes_authenticated(self):
        response = self.client_user1.get(self.likes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_likes_unauthenticated(self):
        response = self.client.get(self.likes_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_likes_by_post(self):
        url = f"{self.likes_url}?post_id={self.post1.id}"
        response = self.client_user1.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_likes_by_user(self):
        url = f"{self.likes_url}?user_id={self.user1.id}"
        response = self.client_user1.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class UserTests(BaseTestCase):
    def test_list_users_authenticated(self):
        response = self.client_user1.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_users_unauthenticated(self):
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user(self):
        url = reverse('user-detail', args=[self.user1.id])
        response = self.client_user1.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser1')
        
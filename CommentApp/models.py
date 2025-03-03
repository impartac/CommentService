from django.db import models
import uuid

from django.contrib.auth.models import User

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    count_likes = models.IntegerField()
    comments_list = models.UUIDField(list, )

    def __str__(self):
        return self.title
    
    @property
    def comments_list(self):
        return self.comments.all() 

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

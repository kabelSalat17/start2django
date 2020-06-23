from django.db import models
from django.utils import timezone
from blog.utils import sendTransaction
import hashlib
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    hash = models.CharField(max_length=32, default=None,blank=True ,null=True)
    txId = models.CharField(max_length=66, default=None, blank=True,null=True)

    def writeOnChain(self):
        self.hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        self.txId = sendTransaction(self.hash)
        self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        #return full url as a string
        #redirect in new detail view
        return reverse('post-detail', kwargs={'pk': self.pk})
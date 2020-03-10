import six
from django.db import models

class BlogPost(models.Model):
    """Simple blog post model for demo purposes."""
    
    title = models.CharField('Title', max_length=255)
    text = models.TextField('Text')
    
    class Meta:
        verbose_name='Blog post'
        verbose_name_plural='Blog posts'

    def __unicode__(self):        
        return self.title

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf-8')
        return self.__unicode__()

        
    def serialize_fields(self):
        """Only these fields will be included in API responses."""
        
        return [
            'id',
            'title',
            'text'
        ]

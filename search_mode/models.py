from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ('created_date',)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Request(models.Model):

    author = models.ForeignKey(User)
    text = models.TextField(blank=True, null=True)
    search_timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(_("user-agent"), blank=True, null=True)
    ip_address = models.GenericIPAddressField(_("ip address"), protocol='both', blank=True, null=True)

    class Meta:
        verbose_name = _("Search request")
        verbose_name_plural = _("Search requests")
        ordering = ('search_timestamp',)

    def __str__(self):
        return self.text

    def __unicode__(self):
        return self.text


class Result(models.Model):

    search_text = models.TextField(blank=True, null=True)
    category_id = models.BigIntegerField()
    price_type = models.TextField(blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    search_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Search result")
        verbose_name_plural = _("Search results")
        ordering = ('search_timestamp',)

    def __str__(self):
        return self.search_text

    def __unicode__(self):
        return self.search_text


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Post, Request


class RequestAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'get_ip_address', 'search_timestamp')
    list_filter = ('search_timestamp',)
    readonly_fields = ('author', 'text', 'ip_address', 'user_agent', 'search_timestamp')
    search_fields = ('author', 'text', 'ip_address', 'user_agent')

    def get_actions(self, request):
    	actions = super(RequestAdmin, self).get_actions(request)
    	if 'delete_selected' in actions:
        	del actions['delete_selected']
    	return actions

    def get_ip_address(self, instance):
        return '<a href="?ip_address=%(ip)s">%(ip)s</a>' % {'ip': instance.ip_address}
    get_ip_address.short_description = _('IP Address')
    get_ip_address.allow_tags = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Post)

admin.site.register(Request, RequestAdmin)
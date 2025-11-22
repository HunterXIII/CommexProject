from django.contrib.auth.mixins import PermissionRequiredMixin

class ChatAccessMixin(PermissionRequiredMixin):

    def has_permission(self):
        return self.get_object().user1 == self.request.user or self.get_object().user2 == self.request.user 
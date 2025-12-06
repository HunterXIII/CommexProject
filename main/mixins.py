from django.contrib.auth.mixins import PermissionRequiredMixin

class ChatAccessMixin(PermissionRequiredMixin):

    def has_permission(self):
        chat = self.get_object()
        return chat.has_participant(self.request.user)
from django.core.exceptions import PermissionDenied
from django.template.response import SimpleTemplateResponse
from django.views.generic.base import View

from lib.viewbase import BaseMixin, BaseTemplateView
from .models import UserProfile
from rest_framework.authtoken.models import Token


class ACCESS(object):
    ANONYMOUS = 0
    ENROLL = 1
    STUDENT = 3
    ASSISTANT = 5
    GRADING = 6
    TEACHER = 10


class UserProfileMixin(BaseMixin):
    access_mode = ACCESS.STUDENT
    login_redirect = True

    def get_resource_objects(self):
        super().get_resource_objects()
        if self.request.user.is_authenticated():
            self.profile = UserProfile.get_by_request(self.request)

            # Get user's API key
            self.token = Token.objects.get(user=self.profile)
        else:
            self.profile = None
        # Add available for template
        self.note("profile")
        self.note("token")

    def access_control(self):
        super().access_control()
        if self.access_mode > ACCESS.ANONYMOUS \
                and not self.request.user.is_authenticated():
            raise PermissionDenied


class UserProfileView(UserProfileMixin, BaseTemplateView):
    pass

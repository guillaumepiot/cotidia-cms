from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from cms.settings import ADMIN_LOGIN_URL

#
# Allow permission checking for class based views
#

class UserCheckMixin(object):

    def check_user(self, user):
        return True

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            if request.user.is_authenticated():
                raise PermissionDenied
            else:
                return redirect(ADMIN_LOGIN_URL)
        return super(UserCheckMixin, self).dispatch(request, *args, **kwargs)


class StaffPermissionRequiredMixin(UserCheckMixin):
    permission_required = None

    #
    # The user must be staff and have the required permissions
    #
    def check_user(self, user):
        return user.is_staff and user.has_perm(self.permission_required)
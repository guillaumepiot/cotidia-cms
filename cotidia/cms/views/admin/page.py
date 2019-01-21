import django_filters

from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from cotidia.account.conf import settings
from cotidia.admin.views import AdminListView
from cotidia.admin.views import (
    AdminDetailView,
    AdminCreateView,
    AdminUpdateView,
    AdminDeleteView,
)
from cotidia.cms.models import Page
from cotidia.cms.forms.admin.page import PageAddForm, PageUpdateForm


########
# Page #
########


class PageFilter(django_filters.FilterSet):
    display_title = django_filters.CharFilter(lookup_expr="icontains", label="Search")

    class Meta:
        model = Page
        fields = ["display_title"]


class PageList(AdminListView):
    model = Page
    columns = (
        ("Title", "display_title"),
        ("URL", "get_absolute_url"),
        ("Status", "status"),
        ("Show in menu", "hide_from_nav"),
        ("Template", "template_label"),
        ("Order", "order"),
    )
    template_type = "fluid"
    filterset = PageFilter
    actions = ["approve"]
    row_click_action = "detail"
    row_actions = ["view"]

    def get_queryset(self):
        queryset = Page.objects.get_originals()

        if self.filterset:
            self.filter = self.filterset(self.request.GET, queryset=queryset)
            queryset = self.filter.qs

        return queryset

    def approve(self, object):
        if object.get_translations():
            object.approval_needed = False
            object.published = True
            object.save()
            object.publish_version()
            object.publish_translations()

    approve.action_name = "Approve & Publish"


class PageDetail(AdminDetailView):
    model = Page
    fieldsets = [
        {"legend": "Content", "template_name": "admin/cms/page/content.html"},
        {
            "legend": "Settings",
            "fields": [
                [
                    {"label": "Display title", "field": "display_title"},
                    {"label": "Template", "field": "template"},
                ],
                [
                    {"label": "Home", "field": "home"},
                    {"label": "Hide from navigation", "field": "hide_from_nav"},
                ],
                {"label": "Unique page identifier", "field": "slug"},
            ],
        },
        {
            "legend": "Redirect",
            "fields": [
                [
                    {"label": "Redirect to an internal page", "field": "redirect_to"},
                    {"label": "Redirect to a URL", "field": "redirect_to_url"},
                ]
            ],
        },
    ]

    def get_fieldsets(self):
        fieldsets = self.fieldsets.copy()

        if settings.CMS_ENABLE_META_DATA:
            fieldsets.insert(
                1,
                {
                    "legend": "Meta data",
                    "template_name": "admin/cms/page/metadata.html",
                },
            )

        return fieldsets


class PageCreate(AdminCreateView):
    model = Page
    form_class = PageAddForm


class PageUpdate(AdminUpdateView):
    model = Page
    form_class = PageUpdateForm

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.get_translations:
            self.object.approval_needed = True
            self.object.save()
        return response

    def get_success_url(self):
        messages.success(self.request, _("The page has been updated."))
        return reverse("cms-admin:page-detail", kwargs={"pk": self.object.id})


class PageDelete(AdminDeleteView):
    model = Page


##############
# Publishing #
##############


@permission_required("cms.publish_page", settings.ACCOUNT_ADMIN_LOGIN_URL)
def PagePublish(request, page_id):

    page = get_object_or_404(Page, id=page_id)

    if request.method == "POST":
        if page.get_translations():

            page.approval_needed = False
            page.published = True
            page.save()
            page.publish_version()
            page.publish_translations()

            messages.success(request, _("The page has been published."))

        return HttpResponseRedirect(
            reverse("cms-admin:page-detail", kwargs={"pk": page.id})
        )

    template = "admin/cms/page/publish.html"

    return render(
        request, template, {"object": page, "app_label": "cms", "model_name": "page"}
    )


@permission_required("cms.publish_page", settings.ACCOUNT_ADMIN_LOGIN_URL)
def PageUnpublish(request, page_id):

    page = get_object_or_404(Page, id=page_id)

    if request.method == "POST":
        if page.get_translations():

            page.approval_needed = False
            page.published = False
            page.save()
            page.unpublish_version()

            messages.success(request, _("The page has been unpublished."))

        return HttpResponseRedirect(
            reverse("cms-admin:page-detail", kwargs={"pk": page.id})
        )

    template = "admin/cms/page/unpublish.html"

    return render(
        request, template, {"object": page, "app_label": "cms", "model_name": "page"}
    )

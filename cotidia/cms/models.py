import json
import reversion

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from cotidia.cms.conf import settings
from cotidia.core.models import BaseModel

TARGET_CHOICES = (("_self", "the same window"), ("_blank", "a new window"))


class BasePageManager(TreeManager):
    def get_published_live(self):
        return self.model.objects.filter(published=True).exclude(published_from=None)

    def get_published_translation_live(self, language_code=False):
        translation_model = self.model.CMSMeta.translation_class
        if language_code:
            return translation_model.objects.filter(
                parent__published=True, language_code=language_code
            ).exclude(parent__published_from=None)
        else:
            return translation_model.objects.filter(parent__published=True).exclude(
                parent__published_from=None
            )

    def get_published_originals(self):
        return self.model.objects.filter(published=True, published_from=None)

    def get_originals(self):
        return self.model.objects.filter(published_from=None)


class BasePage(MPTTModel):
    home = models.BooleanField(default=False)
    published = models.BooleanField(_("Active"), default=False)
    approval_needed = models.BooleanField(default=False)
    template = models.CharField(max_length=250, choices=[], default="cms/page.html")

    # Display title
    display_title = models.CharField(max_length=250, verbose_name="Display title")

    # MPTT parent
    parent = TreeForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    # Publish version key
    published_from = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )

    # A unique identifier
    slug = models.SlugField(
        max_length=60, verbose_name="Unique Page Identifier", blank=True, null=True
    )

    # Publishing
    publish = models.BooleanField(
        _("Publish this page. The page will also be set to Active."), default=False
    )

    approve = models.BooleanField(_("Submit for approval"), default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Optional redirect
    redirect_to = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="redirect_to_page",
        on_delete=models.SET_NULL,
    )

    redirect_to_url = models.URLField(
        _("Redirect to URL"),
        blank=True,
        help_text=_("Redirect this page to a given URL"),
    )

    target = models.CharField(
        _("Open page in"), max_length=50, choices=TARGET_CHOICES, default="_self"
    )

    # Navigation
    hide_from_nav = models.BooleanField(_("Hide from navigation"), default=False)

    # Related pages / can be used for reading more about the same subject
    related_pages = models.ManyToManyField("self", blank=True)

    objects = BasePageManager()

    class Meta:
        # Make this class a reference only with no database, all models must be subclass from this
        abstract = True

    class CMSMeta:
        templates = settings.CMS_PAGE_TEMPLATES
        # Must be provided on model extension
        # translation_class = PageTranslation
        model_url_name = "cms:page"

    def __str__(self):
        return self.display_title

    def get_content_type(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return content_type

    @property
    def title(self):
        return self.display_title

    @property
    def status(self):
        if self.approval_needed:
            return "APPROVAL_NEEDED"
        elif self.published:
            return "PUBLISHED"
        else:
            return "DRAFT"

    @property
    def status_verbal(self):
        if self.approval_needed:
            return _("Approval needed")
        elif self.published:
            return _("Published")
        else:
            return _("Draft")

    def get_published(self):
        cls = self.__class__
        published = cls.objects.filter(published_from=self)
        if published.count() > 0:
            return published[0]
        else:
            return None

    def orderable_queryset(self):
        return self.get_siblings(include_self=True)

    def set_dynamic_attributes(self, translation):
        # Go through each fieldset
        if hasattr(self, "dataset") and self.dataset:
            for fieldset in self.dataset.get_fields():
                fieldset_id = slugify(fieldset["fieldset"]).replace("-", "_")
                for field in fieldset["fields"]:

                    # Get the name of the field
                    field_name = "%s_%s" % (fieldset_id, field["name"])
                    # Assign the value of the field to the translation object
                    setattr(translation, field_name, translation.get_attr(field_name))

    def translated(self):
        from django.utils.translation import get_language

        try:
            translation = self.CMSMeta.translation_class.objects.get(
                language_code=get_language(), parent=self
            )
        except:
            #
            # Check if we want to return the default language translation
            # if the current language one is not available
            #
            if settings.CMS_DEFAULT_LANGUAGE_FALLBACK:
                translation = self.CMSMeta.translation_class.objects.get(
                    language_code=settings.LANGUAGE_CODE, parent=self
                )
            else:
                return None

        self.set_dynamic_attributes(translation)

        try:
            translation.regions = json.loads(translation.regions)
        except:
            pass

        try:
            translation.content = json.loads(translation.content)
        except:
            pass

        return translation

    def get_translations(self):
        return self.CMSMeta.translation_class.objects.filter(parent=self)

    def publish_translations(self):
        # Get translations
        for translation in self.CMSMeta.translation_class.objects.filter(parent=self):
            translation.publish_version()

    # Publish method
    # Create a clone of the current page state or update the current clone

    def publish_version(self):

        cls = self.__class__

        # Fields to ignore in duplication
        ignore_fields = [
            "id",
            "approval_needed",
            "parent_id",
            "published_from_id",
            "order_id",
            "publish",
            "approve",
            "lft",
            "rght",
            "tree_id",
            "level",
            "page_ptr_id",
        ]

        # Check if the page exist already
        try:
            obj = cls.objects.get(published_from=self)
        except:
            obj = cls()

        # Update fields which are not ignored
        for field in cls._meta.fields:
            if field.attname not in ignore_fields:
                obj.__dict__[field.attname] = self.__dict__[field.attname]

        # Override fields that are part of the publishing process
        obj.parent = None
        obj.published_from = self
        obj.order_id = 0

        obj.save()

        return obj

    def unpublish_version(self):

        cls = self.__class__

        # Check if the page exist already
        try:
            obj = cls.objects.get(published_from=self)
        except:
            obj = None

        if obj:
            # Update data
            obj.published = False
            obj.save()

        return obj

    def duplicate(self):

        cls = self.__class__

        # Fields to ignore in duplication
        ignore_fields = [
            "id",
            "published",
            "approval_needed",
            "published_from_id",
            "order_id",
            "publish",
            "approve",
            "lft",
            "rght",
            "tree_id",
            "level",
            "page_ptr_id",
        ]

        obj = cls()

        # Update fields which are not ignored
        for field in cls._meta.fields:
            if field.attname not in ignore_fields:
                if field.attname == "slug":
                    obj.__dict__[field.attname] = self.__dict__[field.attname] + "-copy"
                elif field.attname == "display_title":
                    obj.__dict__[field.attname] = self.__dict__[field.attname] + " Copy"
                else:
                    obj.__dict__[field.attname] = self.__dict__[field.attname]

        obj.save()

        # Duplicate translations
        for translation in self.CMSMeta.translation_class.objects.filter(parent=self):
            translation.duplicate(obj)

        return obj

    def get_absolute_url(
        self, current_language=False, urlargs=False, preview=False, parent_only=False
    ):

        from django.utils.translation import get_language

        if not current_language:
            current_language = get_language()

        if settings.CMS_PREFIX and settings.CMS_PREFIX.get(current_language, False):
            prefix = settings.CMS_prefix[current_language]
        else:
            prefix = False

        if prefix and not prefix[len(prefix) - 1] == "/":
            prefix = prefix + "/"

        if self.home:
            if prefix:
                url = reverse("cms-public:home", prefix=prefix)
            else:
                url = reverse("cms-public:home")
        else:
            slug = ""
            # Get ancestor from original
            if self.get_published():
                ancestors = self.get_ancestors()
            elif self.published_from:
                ancestors = self.published_from.get_ancestors()
            else:
                ancestors = []

            # Go through the ancestor to get slugs
            for ancestor in ancestors:
                # Get the ancestor's slugs
                translation = self.CMSMeta.translation_class.objects.filter(
                    parent=ancestor.id, language_code=current_language
                )

                # If no translation available in the current language
                if translation.count() > 0:
                    translation = translation[0]
                else:
                    translation = self.CMSMeta.translation_class.objects.get(
                        parent=ancestor.id,
                        language_code=settings.CMS_DEFAULT_LANGUAGE[0],
                    )

                # Only add slug if the ansector is not home
                if not ancestor.home:
                    slug = "%s%s/" % (slug, translation.slug)

            translation = self.CMSMeta.translation_class.objects.filter(
                parent=self.id, language_code=current_language
            )

            if translation.count() > 0:
                translation = translation[0]
            else:
                translation = self.CMSMeta.translation_class.objects.filter(
                    parent=self.id, language_code=settings.CMS_DEFAULT_LANGUAGE[0]
                ).first()

            if not translation:
                return None

            slug = "%s%s" % (slug, translation.slug)

            # Add extra prefixes if required
            default_args = {"slug": slug}
            if urlargs:
                reverse_args = default_args.update(urlargs)

            reverse_args = default_args

            # Create the full url based on the pattern
            if prefix:
                url = reverse(
                    self.CMSMeta.model_url_name, kwargs=reverse_args, prefix=prefix
                )
            else:
                url = reverse(self.CMSMeta.model_url_name, kwargs=reverse_args)

        #
        # Replace URL prefix by the right language
        #
        if current_language:
            available_languages = [lang[0] for lang in settings.CMS_LANGUAGES]
            if url.split("/")[1] in available_languages:
                slugs = url.split("/")
                slugs[1] = current_language
                url = "/".join(slugs)

        return url

    def get_admin_url(self):
        return reverse(self.CMSMeta.admin_url_name, kwargs={"pk": self.id})

    def get_breadcrumbs(self):
        if self.home:
            breadcrumbs = []
        else:
            # if self.parent:
            #   slug = "%s/%s" % (self.parent.slug, self.slug)
            breadcrumbs = []

            # If is original
            if self.get_published():
                for ancestor in self.get_ancestors():
                    breadcrumbs.append(ancestor.get_published())
            # Else if it is the published version
            else:
                # if self.published_from != None:
                if self.published_from:
                    for ancestor in self.published_from.get_ancestors():
                        breadcrumbs.append(ancestor.get_published())
                else:
                    for ancestor in self.get_ancestors():
                        breadcrumbs.append(ancestor.get_published())
        return breadcrumbs

    def get_child_pages(self, include_self=False):
        if self.published_from:
            children = []
            for child in self.published_from.get_descendants(include_self=include_self):
                if child.published is True:
                    children.append(child)
            return children
        else:
            return self.get_descendants(include_self=include_self)

    def get_root_page(self):
        # TODO: improve
        if self.get_published():
            return self.get_root()
        else:
            if self.published_from:
                return self.published_from.get_root()
            else:
                return self.get_root()

    @property
    def has_published_version(self):
        try:
            return bool(self.__class__.objects.get(published_from=self, published=True))
        except:
            return False

    #
    # Return a list of all the languages available
    # If a translation doesn't exist for a language, we create a dummy one
    #
    def languages(self):

        languages = []

        for lang in settings.CMS_LANGUAGES:

            try:
                page = self.CMSMeta.translation_class.objects.get(
                    parent=self, language_code=lang[0]
                )
            except self.CMSMeta.translation_class.DoesNotExist:
                page = self.CMSMeta.translation_class(language_code=lang[0])

            languages.append(page)

        return languages

    @property
    def template_label(self):
        if self.template:
            return dict(settings.CMS_PAGE_TEMPLATES).get(self.template)

    @property
    def previous_sibling(self):
        return self.get_previous_sibling(published_from=None)

    @property
    def next_sibling(self):
        return self.get_next_sibling(published_from=None)

    def move_up(self):
        self.move_to(self.previous_sibling, position="left")

    def move_down(self):
        self.move_to(self.next_sibling, position="right")


class PublishTranslation(object):
    """Handle the publising workflow of a translation model."""

    def save(self):
        try:
            if self.parent.publish_inlines:
                self.publish_version()
        except:
            pass
        super().save()

    def publish_version(self):

        parent_cls = self.parent.__class__
        cls = self.__class__

        # Fields to ignore in duplication
        ignore_fields = ["id", "parent_id", "uuid"]

        published_page = parent_cls.objects.filter(published_from=self.parent)
        if len(published_page) > 0:
            published_page = published_page[0]
            try:
                obj = cls.objects.get(
                    language_code=self.language_code, parent=published_page
                )
            except:
                obj = cls()

            # Update fields which are not ignored
            for field in cls._meta.fields:
                if field.attname not in ignore_fields:
                    setattr(obj, field.attname, getattr(self, field.attname))

            obj.parent = published_page
            obj.save()

    def duplicate(self, parent):
        # We create a copy of the current object and attach it to a new parent
        cls = self.__class__
        obj = cls()

        # Fields to ignore in duplication
        ignore_fields = ["id", "parent_id"]

        # Update fields which are not ignored
        for field in cls._meta.fields:
            if field.attname not in ignore_fields:
                setattr(obj, field.attname, getattr(self, field.attname))

        obj.parent = parent
        obj.save()


#
# Base translation model
#
class BasePageTranslation(BaseModel, PublishTranslation):
    title = models.CharField(_("Page title"), max_length=100)
    slug = models.SlugField(max_length=100)
    language_code = models.CharField(
        _("language"),
        max_length=7,
        choices=settings.CMS_LANGUAGES,
        blank=False,
        null=False,
    )
    content = models.TextField(blank=True)
    regions = models.TextField(blank=True)
    images = models.TextField(blank=True)

    class Meta:
        unique_together = ("parent", "language_code")
        abstract = True
        if len(settings.CMS_LANGUAGES) > 1:
            verbose_name = _("Translation")
            verbose_name_plural = _("Translations")
        else:
            verbose_name = _("Content")
            verbose_name_plural = _("Content")

    def __str__(self):
        return u"{} - {}".format(
            self.title, dict(settings.CMS_LANGUAGES).get(self.language_code)
        )

    def get_language(self):
        return dict(settings.CMS_LANGUAGES).get(self.language_code)

    @property
    def get_content(self):
        return json.loads(self.content)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    def get_attr(self, attr_name):
        try:
            value = self.get_content[attr_name]
            # In the case of page link field, we need to return the url
            if hasattr(value, "url"):
                return value["url"]
            return value
        except:
            return ""

    def translation_edit_url(self):
        return reverse(
            "admin:add_edit_translation_" + self.parent._meta.model_name,
            kwargs={"page_id": self.parent.id, "language_code": self.language_code},
        )

    def translation_revision_url(self):
        return reverse(
            "admin:translation_revision_" + self.parent._meta.model_name,
            kwargs={
                "page_id": self.parent.id,
                "language_code": self.language_code,
                "translation_id": self.id,
            },
        )

    def translation_recover_url(self):
        return "{}translation/{}/{}/recover".format(
            reverse("admin:{}_{}_changelist").format(
                self.parent._meta.app_label, self.parent._meta.model_name
            ),
            self.parent.id,
            self.language_code,
        )

    def get_absolute_url(self):
        return self.parent.get_absolute_url()


#############################
# Create the working models #
#############################


class PageTranslation(BasePageTranslation):
    parent = models.ForeignKey(
        "Page", related_name="translations", on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="translation_created_by",
        on_delete=models.SET_NULL,
    )

    updated_by = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="translation_updated_by",
        on_delete=models.SET_NULL,
    )

    parent_field = "parent"


reversion.register(PageTranslation)


class Page(BasePage):

    created_by = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="created_by",
        on_delete=models.SET_NULL,
    )

    updated_by = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="updated_by",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        permissions = (("publish_page", "Can publish page"),)

    class CMSMeta:
        # A tuple of templates paths and names
        templates = settings.CMS_PAGE_TEMPLATES
        # Indicate which Translation class to use for content
        translation_class = PageTranslation
        # Provide the url name to create a url for that model
        model_url_name = "cms-public:page"
        admin_url_name = "cms-admin:page-detail"


reversion.register(Page, follow=["translations"])

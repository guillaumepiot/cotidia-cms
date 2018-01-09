from django.urls import reverse


def admin_menu(context):
    return [
        {
            "text": "Pages",
            "icon": "file-text-o",
            "url": reverse("cms-admin:page-list"),
            "permissions": [
                "cms.add_page",
                "cms.change_page",
                "cms.delete_page",
            ],
        }
    ]

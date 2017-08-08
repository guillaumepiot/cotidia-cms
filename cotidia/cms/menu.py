from django.core.urlresolvers import reverse


def admin_menu(context):
    return [
        {
            "text": "CMS",
            "nav_items": [
                {
                    "text": "Pages",
                    "url": reverse("cms-admin:page-list"),
                    "permissions": [
                        "cms.add_page",
                        "cms.change_page",
                        "cms.delete_page",
                    ],
                },
                {
                    "text": "Images",
                    "url": reverse("cms-admin:image-list"),
                    "permissions": [
                        "cms.add_image",
                        "cms.change_image",
                        "cms.delete_image",
                    ],
                }
            ]
        }
    ]

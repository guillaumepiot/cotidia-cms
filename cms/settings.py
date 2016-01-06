from django.conf import settings

# The default page templates
CMS_PAGE_TEMPLATES = getattr(settings, 'CMS_PAGE_TEMPLATES', (
	('cms/page.html', 'Default page'),
	('cms/page-sidebar-left.html', 'Page with left sidebar'),
	))

# Hash uploaded file
CMS_HASH_FILE_NAMES = getattr(settings, 'CMS_HASH_FILE_NAMES', True)

# The path to save the search index initial
SEARCH_INDEX_PATH = getattr(settings, 'SEARCH_INDEX_PATH', 'indexes')

# List available languages
LANGUAGES = (
	('en', "English"),
	('fr', "French"),
)

CMS_LANGUAGES = getattr(settings, 'CMS_LANGUAGES', LANGUAGES)

CMS_DEFAULT_LANGUAGE = CMS_LANGUAGES[0]

# Auto prefix
CMS_PREFIX = None

# Display default language
# If the page doesn't exists in the current language, fall back to default
# language. Set to False to not render if no language version available.

DEFAULT_LANGUAGE_FALLBACK = False
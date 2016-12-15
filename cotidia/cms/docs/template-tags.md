Template tags
=============

## Filters

`get_page_url`

Return the absolute URL for a page and for a specific language. By default,
it will return the page with the default language specified by 
CMS_DEFAULT_LANGUAGE.

Example:

	{% load cms_tags %}
	{{page|get_page_url:"en"}}
#################
# Content tools #
#################

API = require './../react-ui/api.coffee'
ImageUploader = require './image-uploader.coffee'

onLoad = ->

    onResize()

    editor = undefined

    ContentTools.IMAGE_UPLOADER = ImageUploader

    getImages = ->
        
        # Return an object containing image URLs and widths for all regions
        descendants = undefined
        i = undefined
        images = undefined
        images = {}
        
        for name of editor.regions
            `name = name`
            # Search each region for images
            descendants = editor.regions[name].descendants()
            i = 0
            while i < descendants.length
                # Filter out elements that are not images
                if descendants[i].constructor.name != 'Image'
                                            i++
                    continue
                images[descendants[i].attr('src')] = descendants[i].size()[0]
                i++
        images

    
    editor = ContentTools.EditorApp.get()

    # ContentTools.StylePalette.add([

    #     new ContentTools.Style('Header hero', 'head-text--hero', ['h1'])
    #     new ContentTools.Style('Header second level', 'head-text--second-level', ['h2'])
    #     new ContentTools.Style('Header third level', 'head-text--third-level', ['h3'])
        
    #     new ContentTools.Style('Image centered', 'image-center', ['img'])
    #     new ContentTools.Style('Text white', 'text-white', ['h1', 'h2', 'h3', 'h4', 'h5', 'p'])
        
    # ])
    
    editor.init '.editable', 'data-name'
    
    editor.bind 'save', (regions) ->
    
        onStateChange = undefined
        payload = undefined
        xhr = undefined
        
        # Collect the contents of each region into a FormData instance
        payload = new FormData()
        payload.append('images', JSON.stringify(getImages()))
        payload.append('regions', JSON.stringify(regions))

        onSuccess = ->
            new (ContentTools.FlashUI)('ok')

        onError = ->
            new (ContentTools.FlashUI)('no')

        element = document.querySelector('meta[name="page-id"]')
        page_id = element.getAttribute('content')
        
        url = "/api/cms/update/#{page_id}/"

        API.call('post', url, payload, false, onSuccess, onError, null, 'formData')


################
# Menu control #
################

menu = document.getElementById('menu')
content = document.getElementById('content')
toolbar = document.getElementById('toolbar')

onResize = ->

	if window.innerWidth < 1024
		if menu
			menu.className = 'menu menu--collapse'
		if content
			content.className = 'content content--menu-collapse'
		if toolbar
			toolbar.className = 'toolbar toolbar--menu-collapse'
	else
		if menu
			menu.className = 'menu menu--open'
		if content
			content.className = 'content content--menu-open'
		if toolbar
			toolbar.className = 'toolbar toolbar--menu-open'

window.addEventListener('resize', onResize)
window.addEventListener('load', onLoad)
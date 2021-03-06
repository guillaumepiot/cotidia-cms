#################
# Content tools #
#################

API = require './api.coffee'
ImageUploader = require './image-uploader.coffee'
BackgroundImage = require './background-image.coffee'
Underline = require './underline.coffee'
AudioDialog = require './audio.coffee'

onLoad = ->

    ContentTools.IMAGE_UPLOADER = ImageUploader
    ContentTools.DEFAULT_TOOLS[0].push('underline')
    ContentTools.DEFAULT_TOOLS[0].push('audio')

    editor = ContentTools.EditorApp.get()

    getImages = ->

        # Return an object containing image URLs and widths for all regions
        descendants = undefined
        i = undefined
        images = undefined
        images = {}

        for name, region of editor.regions()
            # Search each region for images
            descendants = region.descendants()
            i = 0
            while i < descendants.length
                # Filter out elements that are not images
                if descendants[i]._tagName != 'img'
                    i++
                    continue
                src = descendants[i]._attributes['src']
                # Remove the ignore url suffix
                src = src.replace(/\?_ignore=.*/, '')
                images[src] = descendants[i]._attributes['width']
                i++
        images

    ContentTools.StylePalette.add([
        new ContentTools.Style('Text white', 'text-white', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text grey dark', 'text-grey-dark', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text grey medium', 'text-grey-medium', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text grey light', 'text-grey-light', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text blue', 'text-blue', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text bold', 'text-strong', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text italic', 'text-italic', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: hero', 'text-hero', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: large', 'text-large', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: medium', 'text-medium', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: emphasis', 'text-emphasis', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: normal', 'text-normal', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
        new ContentTools.Style('Text size: micro', 'text-micro', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])
    ])

    editor.init('[data-editable], [data-fixture]', 'data-name')

    editor.addEventListener 'saved', (ev) ->

        regions = ev.detail().regions

        onStateChange = undefined
        payload = undefined
        xhr = undefined

        # Collect the contents of each region into a FormData instance
        payload = new FormData()
        payload.append('images', JSON.stringify(getImages()))
        payload.append('regions', JSON.stringify(regions))

        # Add the model name to the POST request
        model = document.querySelector('meta[name="content_type_id"]')
        payload.append('content_type_id', model.getAttribute('content'))

        onSuccess = ->
            new (ContentTools.FlashUI)('ok')

        onError = ->
            new (ContentTools.FlashUI)('no')

        element = document.querySelector('meta[name="object_id"]')
        page_id = element.getAttribute('content')

        url = "/api/cms/update/#{page_id}/"

        API.call('post', url, payload, false, onSuccess, onError, null, 'formData')

window.addEventListener('load', onLoad)

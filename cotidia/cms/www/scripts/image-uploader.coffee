API = require './api.coffee'

ImageUploader = (dialog) ->
    image = undefined
    xhr = undefined
    xhrComplete = undefined
    xhrProgress = undefined
    # Set up the event handlers

    rotateImage = (direction) =>

        # Request a rotated version of the image from the server
        formData = undefined

        # Define a function to handle on success
        onSuccess = (data) ->

            # Free the dialog from its busy state
            dialog.busy false

            # Populate the dialog
            dialog.populate data.image, data.size


        # Define a function to handle on error
        onError = (data) ->

            # Free the dialog from its busy state
            dialog.busy false

            # The request failed, notify the user
            new (ContentTools.FlashUI)('no')

        # Set the dialog to busy while the rotate is performed
        dialog.busy true

        # Build the form data to post to the server
        payload = new FormData
        payload.append 'direction', direction

        # Make the request
        url = "/api/cms/images/update/#{image.id}/"

        this.r = API.call('post', url, payload, false, onSuccess, onError, null, 'formData')


    dialog.addEventListener 'imageuploader.cancelupload', =>

        # Cancel the current upload
        this.r.abort()

        # Set the dialog to empty
        dialog.state 'empty'


    dialog.addEventListener 'imageuploader.clear', =>

        # Clear the current image
        dialog.clear()
        image = null


    dialog.addEventListener 'imageuploader.fileready', (ev) =>

        file = ev.detail().file

        # Upload a file to the server
        formData = undefined

        # Define functions to handle upload progress and completion
        onProgress = (ev) ->
            console.log 'onProgress'
            # Set the progress for the upload
            # dialog.progress ev.loaded / ev.total * 100
            dialog.progress 50

        onSuccess = (data) ->

            # Store the image details
            image =
                id: data.uuid
                name: data.name
                size: null
                width: null
                url: data.f

            # Populate the dialog
            dialog.populate image.url, image.size

        # Define a function to handle on error
        onError = (data) ->
            # The request failed, notify the user
            new (ContentTools.FlashUI)('no')

        # Set the dialog state to uploading and reset the progress bar to 0
        dialog.state 'uploading'
        dialog.progress 0

        # Build the form data to post to the server

        content_type = document.querySelector('meta[name="content_type_id"]')
        object_id = document.querySelector('meta[name="object_id"]')

        payload = new FormData
        payload.append 'f', file
        payload.append('content_type', content_type.getAttribute('content'))
        payload.append('object_id', object_id.getAttribute('content'))

        # Set the width of the image when it's inserted, this is a default
        # the user will be able to resize the image afterwards.
        # payload.append 'width', 600

        # Make the request
        url = '/api/file/upload'
        this.r = API.call('post', url, payload, false, onSuccess, onError, onProgress,  'formData')


    dialog.addEventListener 'imageuploader.save', =>

        dialog.save image.url, image.size

        # Trigger the save event against the dialog with details of the
        # image to be inserted.
        # dialog.save data.image, data.size,
        #     'alt': data.name
        #     'data-ce-max-width': image.size[0]

        # crop = undefined
        # cropRegion = undefined
        # formData = undefined

        # # Define a function to handle the request completion
        # onSuccess = (data) ->

        #     # Free the dialog from its busy state
        #     dialog.busy false

        #     # Trigger the save event against the dialog with details of the
        #     # image to be inserted.
        #     dialog.save data.image, data.size,
        #         'alt': data.name
        #         'data-ce-max-width': image.size[0]

        # # Define a function to handle on error
        # onError = (data) ->
        #     # The request failed, notify the user
        #     new (ContentTools.FlashUI)('no')

        # # Set the dialog to busy while the rotate is performed
        # dialog.busy true

        # # Build the form data to post to the server
        # payload = new FormData

        # # Check if a crop region has been defined by the user
        # if dialog.cropRegion()
        #     payload.append 'crop', dialog.cropRegion()


        # Make the request
        # url = "/api/cms/images/update/#{image.id}/"
        # this.r = API.call('post', url, payload, false, onSuccess, onError, null,  'formData')


    dialog.addEventListener 'imageuploader.rotateccw', ->
        rotateImage 'CCW'


    dialog.addEventListener 'imageuploader.rotatecw', ->
        rotateImage 'CW'


module.exports = ImageUploader


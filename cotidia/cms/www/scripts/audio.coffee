class ContentEdit.Audio extends ContentEdit.ResizableElement

    # An editable video (e.g <video><source src="..." type="..."></video>).
    # The `Video` element supports 2 special tags to allow the the size of the
    # image to be constrained (data-ce-min-width, data-ce-max-width).
    #
    # NOTE: YouTube and Vimeo provide support for embedding videos using the
    # <iframe> tag. For this reason we support both video and iframe tags.
    #
    # `sources` should be specified or set against the element as a list of
    # dictionaries containing `src` and `type` key values.

    constructor: (tagName, attributes, sources=[]) ->
        super(tagName, attributes)

        # List of sources for <video> elements
        @sources = sources

        # Set the aspect ratio for the image based on it's initial width/height
        size = @size()
        @_aspectRatio = size[1] / size[0]

    # Read-only properties

    cssTypeName: () ->
        return 'video'

    type: () ->
        # Return the type of element (this should be the same as the class name)
        return 'Video'

    typeName: () ->
        # Return the name of the element type (e.g Image, List item)
        return 'Video'

    _title: () ->
        # Return a title (based on the source) for the video. This is intended
        # for internal use only.
        src = ''
        if @attr('src')
            src = @attr('src')
        else
            if @sources.length
                src = @sources[0]['src']
        if not src
            src = 'No video source set'

        # Limit the length to something sensible
        if src.length > 80
            src = src.substr(0, 80) + '...'

        return src

    # Methods

    createDraggingDOMElement: () ->
        # Create a DOM element that visually aids the user in dragging the
        # element to a new location in the editiable tree structure.
        unless @isMounted()
            return

        helper = super()
        helper.innerHTML = @_title()
        return helper

    html: (indent='') ->
        # Return a HTML string for the node
        le = ContentEdit.LINE_ENDINGS
        if @tagName() == 'video'
            sourceStrings = []
            for source in @sources
                attributes = ContentEdit.attributesToString(source)
                sourceStrings.push(
                    "#{ indent }#{ ContentEdit.INDENT }<source #{ attributes }>"
                    )
            return "#{ indent }<video#{ @_attributesToString() }>#{ le }" +
                sourceStrings.join(le) +
                "#{ le }#{ indent }</video>"
        else
            return "#{ indent }<#{ @_tagName }#{ @_attributesToString() }>" +
                "</#{ @_tagName }>"

    mount: () ->
        # Mount the element on to the DOM

        # Create the DOM element to mount
        @_domElement = document.createElement('div')

        # Set the classes for the video, we use the wrapping <a> tag's class if
        # it exists, else we use the class applied to the image.
        if @a and @a['class']
            @_domElement.setAttribute('class', @a['class'])

        else if @_attributes['class']
            @_domElement.setAttribute('class', @_attributes['class'])

        # Set any styles for the element
        style = if @_attributes['style'] then @_attributes['style'] else ''

        # Set the size using style
        if @_attributes['width']
            style += "width:#{ @_attributes['width'] }px;"

        if @_attributes['height']
            style += "height:#{ @_attributes['height'] }px;"

        @_domElement.setAttribute('style', style)

        # Set the title of the element (for mouse over)
        @_domElement.setAttribute('data-ce-title', @_title())

        super()

    unmount: () ->
        # Unmount the element from the DOM

        if @isFixed()
            # Revert the DOM element to an iframe
            wrapper = document.createElement('div')
            wrapper.innerHTML = @html()
            domElement = wrapper.querySelector('iframe')

            # Replace the current DOM element with the iframe
            @_domElement.parentNode.replaceChild(domElement, @_domElement)
            @_domElement = domElement

        super()

    # Class properties

    @droppers:
        'Image': ContentEdit.Element._dropBoth
        'PreText': ContentEdit.Element._dropBoth
        'Static': ContentEdit.Element._dropBoth
        'Text': ContentEdit.Element._dropBoth
        'Video': ContentEdit.Element._dropBoth

    # List of allowed drop placements for the class, supported values are:
    @placements: ['above', 'below', 'left', 'right', 'center']

    # Class methods

    @fromDOMElement: (domElement) ->
        # Convert an element (DOM) to an element of this type

        # Check for source elements
        childNodes = (c for c in domElement.childNodes)
        sources = []
        for childNode in childNodes
            if childNode.nodeType == 1 \
                    and childNode.tagName.toLowerCase() == 'source'
                sources.push(@getDOMElementAttributes(childNode))

        return new @(
            domElement.tagName,
            @getDOMElementAttributes(domElement),
            sources
            )


# Register `ContentEdit.Video` the class with associated tag names
ContentEdit.TagNames.get().register(ContentEdit.Video, 'iframe', 'video')

class ContentTools.Tools.Audio extends ContentTools.Tool

    # Insert a Soundcloud embed.
    ContentTools.ToolShelf.stow(@, 'audio')

    @label = 'Audio'
    @icon = 'audio'

    @canApply: (element, selection) ->
        # Return true if the tool can be applied to the current
        # element/selection.
        return not element.isFixed()

    @apply: (element, selection, callback) ->

        # Dispatch `apply` event
        toolDetail = {
            'tool': this,
            'element': element,
            'selection': selection
            }
        if not @dispatchEditorEvent('tool-apply', toolDetail)
            return

        # If supported allow store the state for restoring once the dialog is
        # cancelled.
        if element.storeState
            element.storeState()

        # Set-up the dialog
        app = ContentTools.EditorApp.get()

        # Modal
        modal = new ContentTools.ModalUI()

        # Dialog
        dialog = new ContentTools.AudioDialog()

        # Support cancelling the dialog
        dialog.addEventListener 'cancel', () =>

            modal.hide()
            dialog.hide()

            if element.restoreState
                element.restoreState()

            callback(false)

        # Support saving the dialog
        dialog.addEventListener 'save', (ev) =>
            url = ev.detail().url

            if url
                regex = /<iframe.*?src="(.*?)"/
                src = regex.exec(url)[1]

                # audio = document.createElement('div')
                # audio.innerHTML = url
                # @_domView.appendChild(@_domPreview)
                # # Create the new audio
                audio = new ContentEdit.Audio(
                    'iframe', {
                        'frameborder': 0,
                        'height': ContentTools.DEFAULT_VIDEO_HEIGHT,
                        'src': src,
                        'width': "100%"
                        })

                # Find insert position
                [node, index] = @_insertAt(element)
                node.parent().attach(audio, index)

                # Focus the new audio
                audio.focus()

            else
                # Nothing to do restore state
                if element.restoreState
                    element.restoreState()

            modal.hide()
            dialog.hide()

            applied = url != ''
            callback(applied)

            # Dispatch `applied` event
            if applied
                @dispatchEditorEvent('tool-applied', toolDetail)

        # Show the dialog
        app.attach(modal)
        app.attach(dialog)
        modal.show()
        dialog.show()


class ContentTools.AudioDialog extends ContentTools.DialogUI

    # A dialog to support inserting a video

    constructor: ()->
        super('Insert audio')

    clearPreview: () ->
        # Clear the current video preview
        if @_domPreview
            @_domPreview.parentNode.removeChild(@_domPreview)
            @_domPreview = undefined

    mount: () ->
        # Mount the widget
        super()

        # Update dialog class
        ContentEdit.addCSSClass(@_domElement, 'ct-video-dialog')

        # Update view class
        ContentEdit.addCSSClass(@_domView, 'ct-video-dialog__preview')

        # Add controls
        domControlGroup = @constructor.createDiv(['ct-control-group'])
        @_domControls.appendChild(domControlGroup)

        # Input
        @_domInput = document.createElement('input')
        @_domInput.setAttribute('class', 'ct-video-dialog__input')
        @_domInput.setAttribute('name', 'url')
        @_domInput.setAttribute(
            'placeholder',
            ContentEdit._('Paste Soundcloud embed code')
            )
        @_domInput.setAttribute('type', 'text')
        domControlGroup.appendChild(@_domInput)

        # Insert button
        @_domButton = @constructor.createDiv([
            'ct-control',
            'ct-control--text',
            'ct-control--insert'
            'ct-control--muted'
            ])
        @_domButton.textContent = ContentEdit._('Insert')
        domControlGroup.appendChild(@_domButton)

        # Add interaction handlers
        @_addDOMEventListeners()

    preview: (embedCode) ->
        # Preview the specified URL

        # Remove any existing preview
        @clearPreview()

        # Insert the preview iframe
        @_domPreview = document.createElement('div')
        @_domPreview.innerHTML = embedCode
        @_domView.appendChild(@_domPreview)

    save: () ->
        # Save the video. This method triggers the save method against the
        # dialog allowing the calling code to listen for the `save` event and
        # manage the outcome.

        # Attempt to parse a video embed URL
        videoURL = @_domInput.value.trim()
        embedURL = ContentTools.getEmbedVideoURL(videoURL)
        if embedURL
            @dispatchEvent(@createEvent('save', {'url': embedURL}))
        else
            # If we can't generate an embed URL trust that the user's knows what
            # they are doing and save with the supplied URL.
            @dispatchEvent(@createEvent('save', {'url': videoURL}))

    show: () ->
        # Show the widget
        super()

        # Once visible automatically give focus to the link input
        @_domInput.focus()

    unmount: () ->
        # Unmount the component from the DOM

        # Unselect any content
        if @isMounted()
            @_domInput.blur()

        super()

        @_domButton = null
        @_domInput = null
        @_domPreview = null

    # Private methods

    _addDOMEventListeners: () ->
        # Add event listeners for the widget
        super()

        # Provide a preview of the video whenever a valid URL is inserted into
        # the input.
        @_domInput.addEventListener 'input', (ev) =>

            # If the input field is empty we disable the insert button
           if ev.target.value
                ContentEdit.removeCSSClass(@_domButton, 'ct-control--muted')
            else
                ContentEdit.addCSSClass(@_domButton, 'ct-control--muted')

            # We give the user half a second to make additional changes before
            # updating the preview video otherwise changes to the text input can
            # appear to stutter as the browser updates the preview on every
            # change.

            if @_updatePreviewTimeout
                clearTimeout(@_updatePreviewTimeout)

            updatePreview = () =>
                videoURL = @_domInput.value.trim()
                @preview(videoURL)
                # embedURL = ContentTools.getEmbedVideoURL(videoURL)
                # if embedURL
                #     @preview(embedURL)
                # else
                #     @clearPreview()

            @_updatePreviewTimeout = setTimeout(updatePreview, 500)

        # Add support for saving the video whenever the `return` key is pressed
        # or the button is selected.

        # Input
        @_domInput.addEventListener 'keypress', (ev) =>
            if ev.keyCode is 13
                @save()

        # Button
        @_domButton.addEventListener 'click', (ev) =>
            ev.preventDefault()

            # Check the button isn't muted, if it is then the video URL fields
            # isn't populated.
            cssClass = @_domButton.getAttribute('class')
            if cssClass.indexOf('ct-control--muted') == -1
                @save()

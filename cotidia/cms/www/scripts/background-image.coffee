# Example integration of a background-image uploader
# Author: Guillaume Piot
# Email: guillaume@cotidia.com
# Company: Cotidia Ltd
# Licence: MIT
#
# The div holder is absolute positioned within the parent div
#
# <div class="[ article__image ] [ article-image ] [ editable ] [ parallax ]"  data-name="article_image">
#     <div
#        data-ce-tag="bkgimg"
#        class="article-image__container"
#        style="background-image:url('/static/img/blog-header-placeholder.jpg')"></div>
# </div>

class ContentEdit.BackgroundImage extends ContentEdit.Element

    # An editable background image element
    # (e.g <div data-ce-type="bkgimg" data-url="..."></div>).

    constructor: (attributes) ->
        super('bkgimg', attributes)

    # Read-only properties

    cssTypeName: () ->
        return 'background-image'

    type: () ->
        # Return the type of element (this should be the same as the class name)
        return 'BackgroundImage'

    typeName: () ->
        # Return the name of the element type (e.g BackgroundImage, List item)
        return 'BackgroundImage'

    # Methods

    html: (indent='') ->
        # Return a HTML string for the node
        bkgimg = "#{ indent }<div#{ @_attributesToString() }></div>"
        return bkgimg

    mount: () ->
        # Mount the element on to the DOM
        console.log "Mount bkgimg"

        # Create the DOM element to mount
        @_domElement = document.createElement('div')

        # Set the classes for the backgound image element
        classes = ''

        if @_attributes['class']
            classes += ' ' + @_attributes['class']

        @_domElement.setAttribute('class', classes)

        # Set the background image for the
        style = if @_attributes['style'] then @_attributes['style'] else ''

        @_domElement.setAttribute('style', style)

        # Add the button to edit the background image
        @_domButtonElement = document.createElement("button")
        buttonText = document.createTextNode("Upload background image");
        @_domButtonElement.appendChild(buttonText)
        @_domButtonElement.className = 'btn btn--upload-background-image'
        @_domButtonElement.style.position = 'absolute'

        super()

        # Just below the toolbox level
        @_domButtonElement.style.zIndex = '9998'
        @_domElement.parentNode.parentNode.appendChild(@_domButtonElement)



        # Get the selected element position
        rect = @_domElement.getBoundingClientRect()
        # @_domButtonElement.style.bottom = "16px"
        @_domButtonElement.style.right = "16px"

    _addDOMEventListeners: () ->
        super()

        @_domButtonElement.addEventListener 'click', (ev) =>
            ev.preventDefault()
            editor = ContentTools.EditorApp.get()

            modal = new ContentTools.ModalUI(transparent=false, allowScrolling=false)
            dialog = new ContentTools.ImageDialog()

            # Support cancelling the dialog
            dialog.addEventListener 'cancel', () =>
                modal.hide()
                dialog.hide()

            # Insert the image url into the element once saved
            dialog.addEventListener 'save', (ev) =>

                detail = ev.detail()
                imageURL = detail.imageURL
                imageSize = detail.imageSize
                imageAttrs = detail.imageAttrs

                if not imageAttrs
                    imageAttrs = {}

                imageAttrs.height = imageSize[1]
                imageAttrs.src = imageURL
                imageAttrs.width = imageSize[0]

                # node = document.querySelector('[data-name="page_image"]')
                # element.style.backgroundImage = "url('#{imageURL}')";
                # imageNode = region.descendants()[0]

                style = "background-image: url('#{imageURL}')"
                @attr('style', style)

                modal.hide()
                dialog.hide()


            editor.attach(modal)
            editor.attach(dialog)
            modal.show()
            dialog.show()

    # Class properties

    # Class methods

    @fromDOMElement: (domElement) ->
        # Convert an element (DOM) to an element of this type
        attributes = @getDOMElementAttributes(domElement)

        return new @(attributes)


# Register `ContentEdit.BackgroundImage` the class with associated tag names
ContentEdit.TagNames.get().register(ContentEdit.BackgroundImage, 'bkgimg')

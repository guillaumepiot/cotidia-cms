request = require('superagent')

API = {}

API.domain = window.API_ENDPOINT

API.call = (type='get', url='/', data=null, auth=true, onSuccess=null, onError=null, onProgress=null, dataType=null)->

    #
    # Create the request instance based on the type of request
    #

    url = "#{this.domain}#{url}"

    switch type
        when 'get'
            r = request.get(url)
        when 'post'
            r = request.post(url)
        when 'put'
            r = request.put(url)
        when 'patch'
            r = request.patch(url)
        when 'delete'
            r = request.del(url)
        else
            console.log "Request type #{type} is not supported"

    #
    # Set the headers
    #
    if dataType == 'json'
        r.set('Content-Type', 'application/json')

    if dataType == 'html'
        r.set('Content-Type', 'text/html')

    if auth
        r.set("Authorization", "Token #{ localStorage.token }")

    #
    # If we have a CSRF token on the page, then add it to the headers
    #
    if document.getElementsByName("csrfmiddlewaretoken").length > 0
        r.set("X-CSRFToken", document.getElementsByName("csrfmiddlewaretoken")[0].value)


    #
    # Add data if applicable
    #

    if data
        if type == 'get'
            r.query(data)
        else
            r.send(data)

    #
    # Set default callbacks
    #

    if not onSuccess
        onSuccess = (res)->
            console.log 'Success', res

    if not onError
        onError = (res)->
            console.log 'Error', res

    #
    # Send the request
    #

    r.end((err, res)->

        if res and res.status == 204
            onSuccess({})

        if res and res.status == 404
            alert 'The API url called does not exist'
            return

        if err and not res
            alert 'Connection error'
            return

        status = res.status
        type = status / 100 | 0
        if dataType == 'html'
            data = res.text
        else
            data = res.body



        switch type
            when 2
                onSuccess(data)
            when 4
                onError(data)
            when 5
                alert('Server error')
                console.log 'Server error'
        )

    if onProgress
        r.on('progress', onProgress)

    return r

module.exports = API

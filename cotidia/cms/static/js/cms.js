(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){

/**
 * Expose `Emitter`.
 */

if (typeof module !== 'undefined') {
  module.exports = Emitter;
}

/**
 * Initialize a new `Emitter`.
 *
 * @api public
 */

function Emitter(obj) {
  if (obj) return mixin(obj);
};

/**
 * Mixin the emitter properties.
 *
 * @param {Object} obj
 * @return {Object}
 * @api private
 */

function mixin(obj) {
  for (var key in Emitter.prototype) {
    obj[key] = Emitter.prototype[key];
  }
  return obj;
}

/**
 * Listen on the given `event` with `fn`.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.on =
Emitter.prototype.addEventListener = function(event, fn){
  this._callbacks = this._callbacks || {};
  (this._callbacks['$' + event] = this._callbacks['$' + event] || [])
    .push(fn);
  return this;
};

/**
 * Adds an `event` listener that will be invoked a single
 * time then automatically removed.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.once = function(event, fn){
  function on() {
    this.off(event, on);
    fn.apply(this, arguments);
  }

  on.fn = fn;
  this.on(event, on);
  return this;
};

/**
 * Remove the given callback for `event` or all
 * registered callbacks.
 *
 * @param {String} event
 * @param {Function} fn
 * @return {Emitter}
 * @api public
 */

Emitter.prototype.off =
Emitter.prototype.removeListener =
Emitter.prototype.removeAllListeners =
Emitter.prototype.removeEventListener = function(event, fn){
  this._callbacks = this._callbacks || {};

  // all
  if (0 == arguments.length) {
    this._callbacks = {};
    return this;
  }

  // specific event
  var callbacks = this._callbacks['$' + event];
  if (!callbacks) return this;

  // remove all handlers
  if (1 == arguments.length) {
    delete this._callbacks['$' + event];
    return this;
  }

  // remove specific handler
  var cb;
  for (var i = 0; i < callbacks.length; i++) {
    cb = callbacks[i];
    if (cb === fn || cb.fn === fn) {
      callbacks.splice(i, 1);
      break;
    }
  }
  return this;
};

/**
 * Emit `event` with the given args.
 *
 * @param {String} event
 * @param {Mixed} ...
 * @return {Emitter}
 */

Emitter.prototype.emit = function(event){
  this._callbacks = this._callbacks || {};
  var args = [].slice.call(arguments, 1)
    , callbacks = this._callbacks['$' + event];

  if (callbacks) {
    callbacks = callbacks.slice(0);
    for (var i = 0, len = callbacks.length; i < len; ++i) {
      callbacks[i].apply(this, args);
    }
  }

  return this;
};

/**
 * Return array of callbacks for `event`.
 *
 * @param {String} event
 * @return {Array}
 * @api public
 */

Emitter.prototype.listeners = function(event){
  this._callbacks = this._callbacks || {};
  return this._callbacks['$' + event] || [];
};

/**
 * Check if this emitter has `event` handlers.
 *
 * @param {String} event
 * @return {Boolean}
 * @api public
 */

Emitter.prototype.hasListeners = function(event){
  return !! this.listeners(event).length;
};

},{}],2:[function(require,module,exports){
/**
 * Root reference for iframes.
 */

var root;
if (typeof window !== 'undefined') { // Browser window
  root = window;
} else if (typeof self !== 'undefined') { // Web Worker
  root = self;
} else { // Other environments
  console.warn("Using browser-only version of superagent in non-browser environment");
  root = this;
}

var Emitter = require('component-emitter');
var RequestBase = require('./request-base');
var isObject = require('./is-object');
var isFunction = require('./is-function');
var ResponseBase = require('./response-base');
var shouldRetry = require('./should-retry');

/**
 * Noop.
 */

function noop(){};

/**
 * Expose `request`.
 */

var request = exports = module.exports = function(method, url) {
  // callback
  if ('function' == typeof url) {
    return new exports.Request('GET', method).end(url);
  }

  // url first
  if (1 == arguments.length) {
    return new exports.Request('GET', method);
  }

  return new exports.Request(method, url);
}

exports.Request = Request;

/**
 * Determine XHR.
 */

request.getXHR = function () {
  if (root.XMLHttpRequest
      && (!root.location || 'file:' != root.location.protocol
          || !root.ActiveXObject)) {
    return new XMLHttpRequest;
  } else {
    try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
    try { return new ActiveXObject('Msxml2.XMLHTTP.6.0'); } catch(e) {}
    try { return new ActiveXObject('Msxml2.XMLHTTP.3.0'); } catch(e) {}
    try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
  }
  throw Error("Browser-only verison of superagent could not find XHR");
};

/**
 * Removes leading and trailing whitespace, added to support IE.
 *
 * @param {String} s
 * @return {String}
 * @api private
 */

var trim = ''.trim
  ? function(s) { return s.trim(); }
  : function(s) { return s.replace(/(^\s*|\s*$)/g, ''); };

/**
 * Serialize the given `obj`.
 *
 * @param {Object} obj
 * @return {String}
 * @api private
 */

function serialize(obj) {
  if (!isObject(obj)) return obj;
  var pairs = [];
  for (var key in obj) {
    pushEncodedKeyValuePair(pairs, key, obj[key]);
  }
  return pairs.join('&');
}

/**
 * Helps 'serialize' with serializing arrays.
 * Mutates the pairs array.
 *
 * @param {Array} pairs
 * @param {String} key
 * @param {Mixed} val
 */

function pushEncodedKeyValuePair(pairs, key, val) {
  if (val != null) {
    if (Array.isArray(val)) {
      val.forEach(function(v) {
        pushEncodedKeyValuePair(pairs, key, v);
      });
    } else if (isObject(val)) {
      for(var subkey in val) {
        pushEncodedKeyValuePair(pairs, key + '[' + subkey + ']', val[subkey]);
      }
    } else {
      pairs.push(encodeURIComponent(key)
        + '=' + encodeURIComponent(val));
    }
  } else if (val === null) {
    pairs.push(encodeURIComponent(key));
  }
}

/**
 * Expose serialization method.
 */

 request.serializeObject = serialize;

 /**
  * Parse the given x-www-form-urlencoded `str`.
  *
  * @param {String} str
  * @return {Object}
  * @api private
  */

function parseString(str) {
  var obj = {};
  var pairs = str.split('&');
  var pair;
  var pos;

  for (var i = 0, len = pairs.length; i < len; ++i) {
    pair = pairs[i];
    pos = pair.indexOf('=');
    if (pos == -1) {
      obj[decodeURIComponent(pair)] = '';
    } else {
      obj[decodeURIComponent(pair.slice(0, pos))] =
        decodeURIComponent(pair.slice(pos + 1));
    }
  }

  return obj;
}

/**
 * Expose parser.
 */

request.parseString = parseString;

/**
 * Default MIME type map.
 *
 *     superagent.types.xml = 'application/xml';
 *
 */

request.types = {
  html: 'text/html',
  json: 'application/json',
  xml: 'application/xml',
  urlencoded: 'application/x-www-form-urlencoded',
  'form': 'application/x-www-form-urlencoded',
  'form-data': 'application/x-www-form-urlencoded'
};

/**
 * Default serialization map.
 *
 *     superagent.serialize['application/xml'] = function(obj){
 *       return 'generated xml here';
 *     };
 *
 */

 request.serialize = {
   'application/x-www-form-urlencoded': serialize,
   'application/json': JSON.stringify
 };

 /**
  * Default parsers.
  *
  *     superagent.parse['application/xml'] = function(str){
  *       return { object parsed from str };
  *     };
  *
  */

request.parse = {
  'application/x-www-form-urlencoded': parseString,
  'application/json': JSON.parse
};

/**
 * Parse the given header `str` into
 * an object containing the mapped fields.
 *
 * @param {String} str
 * @return {Object}
 * @api private
 */

function parseHeader(str) {
  var lines = str.split(/\r?\n/);
  var fields = {};
  var index;
  var line;
  var field;
  var val;

  lines.pop(); // trailing CRLF

  for (var i = 0, len = lines.length; i < len; ++i) {
    line = lines[i];
    index = line.indexOf(':');
    field = line.slice(0, index).toLowerCase();
    val = trim(line.slice(index + 1));
    fields[field] = val;
  }

  return fields;
}

/**
 * Check if `mime` is json or has +json structured syntax suffix.
 *
 * @param {String} mime
 * @return {Boolean}
 * @api private
 */

function isJSON(mime) {
  return /[\/+]json\b/.test(mime);
}

/**
 * Initialize a new `Response` with the given `xhr`.
 *
 *  - set flags (.ok, .error, etc)
 *  - parse header
 *
 * Examples:
 *
 *  Aliasing `superagent` as `request` is nice:
 *
 *      request = superagent;
 *
 *  We can use the promise-like API, or pass callbacks:
 *
 *      request.get('/').end(function(res){});
 *      request.get('/', function(res){});
 *
 *  Sending data can be chained:
 *
 *      request
 *        .post('/user')
 *        .send({ name: 'tj' })
 *        .end(function(res){});
 *
 *  Or passed to `.send()`:
 *
 *      request
 *        .post('/user')
 *        .send({ name: 'tj' }, function(res){});
 *
 *  Or passed to `.post()`:
 *
 *      request
 *        .post('/user', { name: 'tj' })
 *        .end(function(res){});
 *
 * Or further reduced to a single call for simple cases:
 *
 *      request
 *        .post('/user', { name: 'tj' }, function(res){});
 *
 * @param {XMLHTTPRequest} xhr
 * @param {Object} options
 * @api private
 */

function Response(req) {
  this.req = req;
  this.xhr = this.req.xhr;
  // responseText is accessible only if responseType is '' or 'text' and on older browsers
  this.text = ((this.req.method !='HEAD' && (this.xhr.responseType === '' || this.xhr.responseType === 'text')) || typeof this.xhr.responseType === 'undefined')
     ? this.xhr.responseText
     : null;
  this.statusText = this.req.xhr.statusText;
  var status = this.xhr.status;
  // handle IE9 bug: http://stackoverflow.com/questions/10046972/msie-returns-status-code-of-1223-for-ajax-request
  if (status === 1223) {
      status = 204;
  }
  this._setStatusProperties(status);
  this.header = this.headers = parseHeader(this.xhr.getAllResponseHeaders());
  // getAllResponseHeaders sometimes falsely returns "" for CORS requests, but
  // getResponseHeader still works. so we get content-type even if getting
  // other headers fails.
  this.header['content-type'] = this.xhr.getResponseHeader('content-type');
  this._setHeaderProperties(this.header);

  if (null === this.text && req._responseType) {
    this.body = this.xhr.response;
  } else {
    this.body = this.req.method != 'HEAD'
      ? this._parseBody(this.text ? this.text : this.xhr.response)
      : null;
  }
}

ResponseBase(Response.prototype);

/**
 * Parse the given body `str`.
 *
 * Used for auto-parsing of bodies. Parsers
 * are defined on the `superagent.parse` object.
 *
 * @param {String} str
 * @return {Mixed}
 * @api private
 */

Response.prototype._parseBody = function(str){
  var parse = request.parse[this.type];
  if(this.req._parser) {
    return this.req._parser(this, str);
  }
  if (!parse && isJSON(this.type)) {
    parse = request.parse['application/json'];
  }
  return parse && str && (str.length || str instanceof Object)
    ? parse(str)
    : null;
};

/**
 * Return an `Error` representative of this response.
 *
 * @return {Error}
 * @api public
 */

Response.prototype.toError = function(){
  var req = this.req;
  var method = req.method;
  var url = req.url;

  var msg = 'cannot ' + method + ' ' + url + ' (' + this.status + ')';
  var err = new Error(msg);
  err.status = this.status;
  err.method = method;
  err.url = url;

  return err;
};

/**
 * Expose `Response`.
 */

request.Response = Response;

/**
 * Initialize a new `Request` with the given `method` and `url`.
 *
 * @param {String} method
 * @param {String} url
 * @api public
 */

function Request(method, url) {
  var self = this;
  this._query = this._query || [];
  this.method = method;
  this.url = url;
  this.header = {}; // preserves header name case
  this._header = {}; // coerces header names to lowercase
  this.on('end', function(){
    var err = null;
    var res = null;

    try {
      res = new Response(self);
    } catch(e) {
      err = new Error('Parser is unable to parse the response');
      err.parse = true;
      err.original = e;
      // issue #675: return the raw response if the response parsing fails
      if (self.xhr) {
        // ie9 doesn't have 'response' property
        err.rawResponse = typeof self.xhr.responseType == 'undefined' ? self.xhr.responseText : self.xhr.response;
        // issue #876: return the http status code if the response parsing fails
        err.status = self.xhr.status ? self.xhr.status : null;
        err.statusCode = err.status; // backwards-compat only
      } else {
        err.rawResponse = null;
        err.status = null;
      }

      return self.callback(err);
    }

    self.emit('response', res);

    var new_err;
    try {
      if (!self._isResponseOK(res)) {
        new_err = new Error(res.statusText || 'Unsuccessful HTTP response');
        new_err.original = err;
        new_err.response = res;
        new_err.status = res.status;
      }
    } catch(e) {
      new_err = e; // #985 touching res may cause INVALID_STATE_ERR on old Android
    }

    // #1000 don't catch errors from the callback to avoid double calling it
    if (new_err) {
      self.callback(new_err, res);
    } else {
      self.callback(null, res);
    }
  });
}

/**
 * Mixin `Emitter` and `RequestBase`.
 */

Emitter(Request.prototype);
RequestBase(Request.prototype);

/**
 * Set Content-Type to `type`, mapping values from `request.types`.
 *
 * Examples:
 *
 *      superagent.types.xml = 'application/xml';
 *
 *      request.post('/')
 *        .type('xml')
 *        .send(xmlstring)
 *        .end(callback);
 *
 *      request.post('/')
 *        .type('application/xml')
 *        .send(xmlstring)
 *        .end(callback);
 *
 * @param {String} type
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.type = function(type){
  this.set('Content-Type', request.types[type] || type);
  return this;
};

/**
 * Set Accept to `type`, mapping values from `request.types`.
 *
 * Examples:
 *
 *      superagent.types.json = 'application/json';
 *
 *      request.get('/agent')
 *        .accept('json')
 *        .end(callback);
 *
 *      request.get('/agent')
 *        .accept('application/json')
 *        .end(callback);
 *
 * @param {String} accept
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.accept = function(type){
  this.set('Accept', request.types[type] || type);
  return this;
};

/**
 * Set Authorization field value with `user` and `pass`.
 *
 * @param {String} user
 * @param {String} [pass] optional in case of using 'bearer' as type
 * @param {Object} options with 'type' property 'auto', 'basic' or 'bearer' (default 'basic')
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.auth = function(user, pass, options){
  if (typeof pass === 'object' && pass !== null) { // pass is optional and can substitute for options
    options = pass;
  }
  if (!options) {
    options = {
      type: 'function' === typeof btoa ? 'basic' : 'auto',
    }
  }

  switch (options.type) {
    case 'basic':
      this.set('Authorization', 'Basic ' + btoa(user + ':' + pass));
    break;

    case 'auto':
      this.username = user;
      this.password = pass;
    break;
      
    case 'bearer': // usage would be .auth(accessToken, { type: 'bearer' })
      this.set('Authorization', 'Bearer ' + user);
    break;  
  }
  return this;
};

/**
 * Add query-string `val`.
 *
 * Examples:
 *
 *   request.get('/shoes')
 *     .query('size=10')
 *     .query({ color: 'blue' })
 *
 * @param {Object|String} val
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.query = function(val){
  if ('string' != typeof val) val = serialize(val);
  if (val) this._query.push(val);
  return this;
};

/**
 * Queue the given `file` as an attachment to the specified `field`,
 * with optional `options` (or filename).
 *
 * ``` js
 * request.post('/upload')
 *   .attach('content', new Blob(['<a id="a"><b id="b">hey!</b></a>'], { type: "text/html"}))
 *   .end(callback);
 * ```
 *
 * @param {String} field
 * @param {Blob|File} file
 * @param {String|Object} options
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.attach = function(field, file, options){
  if (file) {
    if (this._data) {
      throw Error("superagent can't mix .send() and .attach()");
    }

    this._getFormData().append(field, file, options || file.name);
  }
  return this;
};

Request.prototype._getFormData = function(){
  if (!this._formData) {
    this._formData = new root.FormData();
  }
  return this._formData;
};

/**
 * Invoke the callback with `err` and `res`
 * and handle arity check.
 *
 * @param {Error} err
 * @param {Response} res
 * @api private
 */

Request.prototype.callback = function(err, res){
  // console.log(this._retries, this._maxRetries)
  if (this._maxRetries && this._retries++ < this._maxRetries && shouldRetry(err, res)) {
    return this._retry();
  }

  var fn = this._callback;
  this.clearTimeout();

  if (err) {
    if (this._maxRetries) err.retries = this._retries - 1;
    this.emit('error', err);
  }

  fn(err, res);
};

/**
 * Invoke callback with x-domain error.
 *
 * @api private
 */

Request.prototype.crossDomainError = function(){
  var err = new Error('Request has been terminated\nPossible causes: the network is offline, Origin is not allowed by Access-Control-Allow-Origin, the page is being unloaded, etc.');
  err.crossDomain = true;

  err.status = this.status;
  err.method = this.method;
  err.url = this.url;

  this.callback(err);
};

// This only warns, because the request is still likely to work
Request.prototype.buffer = Request.prototype.ca = Request.prototype.agent = function(){
  console.warn("This is not supported in browser version of superagent");
  return this;
};

// This throws, because it can't send/receive data as expected
Request.prototype.pipe = Request.prototype.write = function(){
  throw Error("Streaming is not supported in browser version of superagent");
};

/**
 * Compose querystring to append to req.url
 *
 * @api private
 */

Request.prototype._appendQueryString = function(){
  var query = this._query.join('&');
  if (query) {
    this.url += (this.url.indexOf('?') >= 0 ? '&' : '?') + query;
  }

  if (this._sort) {
    var index = this.url.indexOf('?');
    if (index >= 0) {
      var queryArr = this.url.substring(index + 1).split('&');
      if (isFunction(this._sort)) {
        queryArr.sort(this._sort);
      } else {
        queryArr.sort();
      }
      this.url = this.url.substring(0, index) + '?' + queryArr.join('&');
    }
  }
};

/**
 * Check if `obj` is a host object,
 * we don't want to serialize these :)
 *
 * @param {Object} obj
 * @return {Boolean}
 * @api private
 */
Request.prototype._isHost = function _isHost(obj) {
  // Native objects stringify to [object File], [object Blob], [object FormData], etc.
  return obj && 'object' === typeof obj && !Array.isArray(obj) && Object.prototype.toString.call(obj) !== '[object Object]';
}

/**
 * Initiate request, invoking callback `fn(res)`
 * with an instanceof `Response`.
 *
 * @param {Function} fn
 * @return {Request} for chaining
 * @api public
 */

Request.prototype.end = function(fn){
  if (this._endCalled) {
    console.warn("Warning: .end() was called twice. This is not supported in superagent");
  }
  this._endCalled = true;

  // store callback
  this._callback = fn || noop;

  // querystring
  this._appendQueryString();

  return this._end();
};

Request.prototype._end = function() {
  var self = this;
  var xhr = this.xhr = request.getXHR();
  var data = this._formData || this._data;

  this._setTimeouts();

  // state change
  xhr.onreadystatechange = function(){
    var readyState = xhr.readyState;
    if (readyState >= 2 && self._responseTimeoutTimer) {
      clearTimeout(self._responseTimeoutTimer);
    }
    if (4 != readyState) {
      return;
    }

    // In IE9, reads to any property (e.g. status) off of an aborted XHR will
    // result in the error "Could not complete the operation due to error c00c023f"
    var status;
    try { status = xhr.status } catch(e) { status = 0; }

    if (!status) {
      if (self.timedout || self._aborted) return;
      return self.crossDomainError();
    }
    self.emit('end');
  };

  // progress
  var handleProgress = function(direction, e) {
    if (e.total > 0) {
      e.percent = e.loaded / e.total * 100;
    }
    e.direction = direction;
    self.emit('progress', e);
  }
  if (this.hasListeners('progress')) {
    try {
      xhr.onprogress = handleProgress.bind(null, 'download');
      if (xhr.upload) {
        xhr.upload.onprogress = handleProgress.bind(null, 'upload');
      }
    } catch(e) {
      // Accessing xhr.upload fails in IE from a web worker, so just pretend it doesn't exist.
      // Reported here:
      // https://connect.microsoft.com/IE/feedback/details/837245/xmlhttprequest-upload-throws-invalid-argument-when-used-from-web-worker-context
    }
  }

  // initiate request
  try {
    if (this.username && this.password) {
      xhr.open(this.method, this.url, true, this.username, this.password);
    } else {
      xhr.open(this.method, this.url, true);
    }
  } catch (err) {
    // see #1149
    return this.callback(err);
  }

  // CORS
  if (this._withCredentials) xhr.withCredentials = true;

  // body
  if (!this._formData && 'GET' != this.method && 'HEAD' != this.method && 'string' != typeof data && !this._isHost(data)) {
    // serialize stuff
    var contentType = this._header['content-type'];
    var serialize = this._serializer || request.serialize[contentType ? contentType.split(';')[0] : ''];
    if (!serialize && isJSON(contentType)) {
      serialize = request.serialize['application/json'];
    }
    if (serialize) data = serialize(data);
  }

  // set header fields
  for (var field in this.header) {
    if (null == this.header[field]) continue;

    if (this.header.hasOwnProperty(field))
      xhr.setRequestHeader(field, this.header[field]);
  }

  if (this._responseType) {
    xhr.responseType = this._responseType;
  }

  // send stuff
  this.emit('request', this);

  // IE11 xhr.send(undefined) sends 'undefined' string as POST payload (instead of nothing)
  // We need null here if data is undefined
  xhr.send(typeof data !== 'undefined' ? data : null);
  return this;
};

/**
 * GET `url` with optional callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed|Function} [data] or fn
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.get = function(url, data, fn){
  var req = request('GET', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.query(data);
  if (fn) req.end(fn);
  return req;
};

/**
 * HEAD `url` with optional callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed|Function} [data] or fn
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.head = function(url, data, fn){
  var req = request('HEAD', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

/**
 * OPTIONS query to `url` with optional callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed|Function} [data] or fn
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.options = function(url, data, fn){
  var req = request('OPTIONS', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

/**
 * DELETE `url` with optional `data` and callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed} [data]
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

function del(url, data, fn){
  var req = request('DELETE', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

request['del'] = del;
request['delete'] = del;

/**
 * PATCH `url` with optional `data` and callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed} [data]
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.patch = function(url, data, fn){
  var req = request('PATCH', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

/**
 * POST `url` with optional `data` and callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed} [data]
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.post = function(url, data, fn){
  var req = request('POST', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

/**
 * PUT `url` with optional `data` and callback `fn(res)`.
 *
 * @param {String} url
 * @param {Mixed|Function} [data] or fn
 * @param {Function} [fn]
 * @return {Request}
 * @api public
 */

request.put = function(url, data, fn){
  var req = request('PUT', url);
  if ('function' == typeof data) fn = data, data = null;
  if (data) req.send(data);
  if (fn) req.end(fn);
  return req;
};

},{"./is-function":3,"./is-object":4,"./request-base":5,"./response-base":6,"./should-retry":7,"component-emitter":1}],3:[function(require,module,exports){
/**
 * Check if `fn` is a function.
 *
 * @param {Function} fn
 * @return {Boolean}
 * @api private
 */
var isObject = require('./is-object');

function isFunction(fn) {
  var tag = isObject(fn) ? Object.prototype.toString.call(fn) : '';
  return tag === '[object Function]';
}

module.exports = isFunction;

},{"./is-object":4}],4:[function(require,module,exports){
/**
 * Check if `obj` is an object.
 *
 * @param {Object} obj
 * @return {Boolean}
 * @api private
 */

function isObject(obj) {
  return null !== obj && 'object' === typeof obj;
}

module.exports = isObject;

},{}],5:[function(require,module,exports){
/**
 * Module of mixed-in functions shared between node and client code
 */
var isObject = require('./is-object');

/**
 * Expose `RequestBase`.
 */

module.exports = RequestBase;

/**
 * Initialize a new `RequestBase`.
 *
 * @api public
 */

function RequestBase(obj) {
  if (obj) return mixin(obj);
}

/**
 * Mixin the prototype properties.
 *
 * @param {Object} obj
 * @return {Object}
 * @api private
 */

function mixin(obj) {
  for (var key in RequestBase.prototype) {
    obj[key] = RequestBase.prototype[key];
  }
  return obj;
}

/**
 * Clear previous timeout.
 *
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.clearTimeout = function _clearTimeout(){
  clearTimeout(this._timer);
  clearTimeout(this._responseTimeoutTimer);
  delete this._timer;
  delete this._responseTimeoutTimer;
  return this;
};

/**
 * Override default response body parser
 *
 * This function will be called to convert incoming data into request.body
 *
 * @param {Function}
 * @api public
 */

RequestBase.prototype.parse = function parse(fn){
  this._parser = fn;
  return this;
};

/**
 * Set format of binary response body.
 * In browser valid formats are 'blob' and 'arraybuffer',
 * which return Blob and ArrayBuffer, respectively.
 *
 * In Node all values result in Buffer.
 *
 * Examples:
 *
 *      req.get('/')
 *        .responseType('blob')
 *        .end(callback);
 *
 * @param {String} val
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.responseType = function(val){
  this._responseType = val;
  return this;
};

/**
 * Override default request body serializer
 *
 * This function will be called to convert data set via .send or .attach into payload to send
 *
 * @param {Function}
 * @api public
 */

RequestBase.prototype.serialize = function serialize(fn){
  this._serializer = fn;
  return this;
};

/**
 * Set timeouts.
 *
 * - response timeout is time between sending request and receiving the first byte of the response. Includes DNS and connection time.
 * - deadline is the time from start of the request to receiving response body in full. If the deadline is too short large files may not load at all on slow connections.
 *
 * Value of 0 or false means no timeout.
 *
 * @param {Number|Object} ms or {response, read, deadline}
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.timeout = function timeout(options){
  if (!options || 'object' !== typeof options) {
    this._timeout = options;
    this._responseTimeout = 0;
    return this;
  }

  for(var option in options) {
    switch(option) {
      case 'deadline':
        this._timeout = options.deadline;
        break;
      case 'response':
        this._responseTimeout = options.response;
        break;
      default:
        console.warn("Unknown timeout option", option);
    }
  }
  return this;
};

/**
 * Set number of retry attempts on error.
 *
 * Failed requests will be retried 'count' times if timeout or err.code >= 500.
 *
 * @param {Number} count
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.retry = function retry(count){
  // Default to 1 if no count passed or true
  if (arguments.length === 0 || count === true) count = 1;
  if (count <= 0) count = 0;
  this._maxRetries = count;
  this._retries = 0;
  return this;
};

/**
 * Retry request
 *
 * @return {Request} for chaining
 * @api private
 */

RequestBase.prototype._retry = function() {
  this.clearTimeout();

  // node
  if (this.req) {
    this.req = null;
    this.req = this.request();
  }

  this._aborted = false;
  this.timedout = false;

  return this._end();
};

/**
 * Promise support
 *
 * @param {Function} resolve
 * @param {Function} [reject]
 * @return {Request}
 */

RequestBase.prototype.then = function then(resolve, reject) {
  if (!this._fullfilledPromise) {
    var self = this;
    if (this._endCalled) {
      console.warn("Warning: superagent request was sent twice, because both .end() and .then() were called. Never call .end() if you use promises");
    }
    this._fullfilledPromise = new Promise(function(innerResolve, innerReject){
      self.end(function(err, res){
        if (err) innerReject(err); else innerResolve(res);
      });
    });
  }
  return this._fullfilledPromise.then(resolve, reject);
}

RequestBase.prototype.catch = function(cb) {
  return this.then(undefined, cb);
};

/**
 * Allow for extension
 */

RequestBase.prototype.use = function use(fn) {
  fn(this);
  return this;
}

RequestBase.prototype.ok = function(cb) {
  if ('function' !== typeof cb) throw Error("Callback required");
  this._okCallback = cb;
  return this;
};

RequestBase.prototype._isResponseOK = function(res) {
  if (!res) {
    return false;
  }

  if (this._okCallback) {
    return this._okCallback(res);
  }

  return res.status >= 200 && res.status < 300;
};


/**
 * Get request header `field`.
 * Case-insensitive.
 *
 * @param {String} field
 * @return {String}
 * @api public
 */

RequestBase.prototype.get = function(field){
  return this._header[field.toLowerCase()];
};

/**
 * Get case-insensitive header `field` value.
 * This is a deprecated internal API. Use `.get(field)` instead.
 *
 * (getHeader is no longer used internally by the superagent code base)
 *
 * @param {String} field
 * @return {String}
 * @api private
 * @deprecated
 */

RequestBase.prototype.getHeader = RequestBase.prototype.get;

/**
 * Set header `field` to `val`, or multiple fields with one object.
 * Case-insensitive.
 *
 * Examples:
 *
 *      req.get('/')
 *        .set('Accept', 'application/json')
 *        .set('X-API-Key', 'foobar')
 *        .end(callback);
 *
 *      req.get('/')
 *        .set({ Accept: 'application/json', 'X-API-Key': 'foobar' })
 *        .end(callback);
 *
 * @param {String|Object} field
 * @param {String} val
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.set = function(field, val){
  if (isObject(field)) {
    for (var key in field) {
      this.set(key, field[key]);
    }
    return this;
  }
  this._header[field.toLowerCase()] = val;
  this.header[field] = val;
  return this;
};

/**
 * Remove header `field`.
 * Case-insensitive.
 *
 * Example:
 *
 *      req.get('/')
 *        .unset('User-Agent')
 *        .end(callback);
 *
 * @param {String} field
 */
RequestBase.prototype.unset = function(field){
  delete this._header[field.toLowerCase()];
  delete this.header[field];
  return this;
};

/**
 * Write the field `name` and `val`, or multiple fields with one object
 * for "multipart/form-data" request bodies.
 *
 * ``` js
 * request.post('/upload')
 *   .field('foo', 'bar')
 *   .end(callback);
 *
 * request.post('/upload')
 *   .field({ foo: 'bar', baz: 'qux' })
 *   .end(callback);
 * ```
 *
 * @param {String|Object} name
 * @param {String|Blob|File|Buffer|fs.ReadStream} val
 * @return {Request} for chaining
 * @api public
 */
RequestBase.prototype.field = function(name, val) {

  // name should be either a string or an object.
  if (null === name ||  undefined === name) {
    throw new Error('.field(name, val) name can not be empty');
  }

  if (this._data) {
    console.error(".field() can't be used if .send() is used. Please use only .send() or only .field() & .attach()");
  }

  if (isObject(name)) {
    for (var key in name) {
      this.field(key, name[key]);
    }
    return this;
  }

  if (Array.isArray(val)) {
    for (var i in val) {
      this.field(name, val[i]);
    }
    return this;
  }

  // val should be defined now
  if (null === val || undefined === val) {
    throw new Error('.field(name, val) val can not be empty');
  }
  if ('boolean' === typeof val) {
    val = '' + val;
  }
  this._getFormData().append(name, val);
  return this;
};

/**
 * Abort the request, and clear potential timeout.
 *
 * @return {Request}
 * @api public
 */
RequestBase.prototype.abort = function(){
  if (this._aborted) {
    return this;
  }
  this._aborted = true;
  this.xhr && this.xhr.abort(); // browser
  this.req && this.req.abort(); // node
  this.clearTimeout();
  this.emit('abort');
  return this;
};

/**
 * Enable transmission of cookies with x-domain requests.
 *
 * Note that for this to work the origin must not be
 * using "Access-Control-Allow-Origin" with a wildcard,
 * and also must set "Access-Control-Allow-Credentials"
 * to "true".
 *
 * @api public
 */

RequestBase.prototype.withCredentials = function(on){
  // This is browser-only functionality. Node side is no-op.
  if(on==undefined) on = true;
  this._withCredentials = on;
  return this;
};

/**
 * Set the max redirects to `n`. Does noting in browser XHR implementation.
 *
 * @param {Number} n
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.redirects = function(n){
  this._maxRedirects = n;
  return this;
};

/**
 * Convert to a plain javascript object (not JSON string) of scalar properties.
 * Note as this method is designed to return a useful non-this value,
 * it cannot be chained.
 *
 * @return {Object} describing method, url, and data of this request
 * @api public
 */

RequestBase.prototype.toJSON = function(){
  return {
    method: this.method,
    url: this.url,
    data: this._data,
    headers: this._header
  };
};


/**
 * Send `data` as the request body, defaulting the `.type()` to "json" when
 * an object is given.
 *
 * Examples:
 *
 *       // manual json
 *       request.post('/user')
 *         .type('json')
 *         .send('{"name":"tj"}')
 *         .end(callback)
 *
 *       // auto json
 *       request.post('/user')
 *         .send({ name: 'tj' })
 *         .end(callback)
 *
 *       // manual x-www-form-urlencoded
 *       request.post('/user')
 *         .type('form')
 *         .send('name=tj')
 *         .end(callback)
 *
 *       // auto x-www-form-urlencoded
 *       request.post('/user')
 *         .type('form')
 *         .send({ name: 'tj' })
 *         .end(callback)
 *
 *       // defaults to x-www-form-urlencoded
 *      request.post('/user')
 *        .send('name=tobi')
 *        .send('species=ferret')
 *        .end(callback)
 *
 * @param {String|Object} data
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.send = function(data){
  var isObj = isObject(data);
  var type = this._header['content-type'];

  if (this._formData) {
    console.error(".send() can't be used if .attach() or .field() is used. Please use only .send() or only .field() & .attach()");
  }

  if (isObj && !this._data) {
    if (Array.isArray(data)) {
      this._data = [];
    } else if (!this._isHost(data)) {
      this._data = {};
    }
  } else if (data && this._data && this._isHost(this._data)) {
    throw Error("Can't merge these send calls");
  }

  // merge
  if (isObj && isObject(this._data)) {
    for (var key in data) {
      this._data[key] = data[key];
    }
  } else if ('string' == typeof data) {
    // default to x-www-form-urlencoded
    if (!type) this.type('form');
    type = this._header['content-type'];
    if ('application/x-www-form-urlencoded' == type) {
      this._data = this._data
        ? this._data + '&' + data
        : data;
    } else {
      this._data = (this._data || '') + data;
    }
  } else {
    this._data = data;
  }

  if (!isObj || this._isHost(data)) {
    return this;
  }

  // default to json
  if (!type) this.type('json');
  return this;
};


/**
 * Sort `querystring` by the sort function
 *
 *
 * Examples:
 *
 *       // default order
 *       request.get('/user')
 *         .query('name=Nick')
 *         .query('search=Manny')
 *         .sortQuery()
 *         .end(callback)
 *
 *       // customized sort function
 *       request.get('/user')
 *         .query('name=Nick')
 *         .query('search=Manny')
 *         .sortQuery(function(a, b){
 *           return a.length - b.length;
 *         })
 *         .end(callback)
 *
 *
 * @param {Function} sort
 * @return {Request} for chaining
 * @api public
 */

RequestBase.prototype.sortQuery = function(sort) {
  // _sort default to true but otherwise can be a function or boolean
  this._sort = typeof sort === 'undefined' ? true : sort;
  return this;
};

/**
 * Invoke callback with timeout error.
 *
 * @api private
 */

RequestBase.prototype._timeoutError = function(reason, timeout, errno){
  if (this._aborted) {
    return;
  }
  var err = new Error(reason + timeout + 'ms exceeded');
  err.timeout = timeout;
  err.code = 'ECONNABORTED';
  err.errno = errno;
  this.timedout = true;
  this.abort();
  this.callback(err);
};

RequestBase.prototype._setTimeouts = function() {
  var self = this;

  // deadline
  if (this._timeout && !this._timer) {
    this._timer = setTimeout(function(){
      self._timeoutError('Timeout of ', self._timeout, 'ETIME');
    }, this._timeout);
  }
  // response timeout
  if (this._responseTimeout && !this._responseTimeoutTimer) {
    this._responseTimeoutTimer = setTimeout(function(){
      self._timeoutError('Response timeout of ', self._responseTimeout, 'ETIMEDOUT');
    }, this._responseTimeout);
  }
}

},{"./is-object":4}],6:[function(require,module,exports){

/**
 * Module dependencies.
 */

var utils = require('./utils');

/**
 * Expose `ResponseBase`.
 */

module.exports = ResponseBase;

/**
 * Initialize a new `ResponseBase`.
 *
 * @api public
 */

function ResponseBase(obj) {
  if (obj) return mixin(obj);
}

/**
 * Mixin the prototype properties.
 *
 * @param {Object} obj
 * @return {Object}
 * @api private
 */

function mixin(obj) {
  for (var key in ResponseBase.prototype) {
    obj[key] = ResponseBase.prototype[key];
  }
  return obj;
}

/**
 * Get case-insensitive `field` value.
 *
 * @param {String} field
 * @return {String}
 * @api public
 */

ResponseBase.prototype.get = function(field){
    return this.header[field.toLowerCase()];
};

/**
 * Set header related properties:
 *
 *   - `.type` the content type without params
 *
 * A response of "Content-Type: text/plain; charset=utf-8"
 * will provide you with a `.type` of "text/plain".
 *
 * @param {Object} header
 * @api private
 */

ResponseBase.prototype._setHeaderProperties = function(header){
    // TODO: moar!
    // TODO: make this a util

    // content-type
    var ct = header['content-type'] || '';
    this.type = utils.type(ct);

    // params
    var params = utils.params(ct);
    for (var key in params) this[key] = params[key];

    this.links = {};

    // links
    try {
        if (header.link) {
            this.links = utils.parseLinks(header.link);
        }
    } catch (err) {
        // ignore
    }
};

/**
 * Set flags such as `.ok` based on `status`.
 *
 * For example a 2xx response will give you a `.ok` of __true__
 * whereas 5xx will be __false__ and `.error` will be __true__. The
 * `.clientError` and `.serverError` are also available to be more
 * specific, and `.statusType` is the class of error ranging from 1..5
 * sometimes useful for mapping respond colors etc.
 *
 * "sugar" properties are also defined for common cases. Currently providing:
 *
 *   - .noContent
 *   - .badRequest
 *   - .unauthorized
 *   - .notAcceptable
 *   - .notFound
 *
 * @param {Number} status
 * @api private
 */

ResponseBase.prototype._setStatusProperties = function(status){
    var type = status / 100 | 0;

    // status / class
    this.status = this.statusCode = status;
    this.statusType = type;

    // basics
    this.info = 1 == type;
    this.ok = 2 == type;
    this.redirect = 3 == type;
    this.clientError = 4 == type;
    this.serverError = 5 == type;
    this.error = (4 == type || 5 == type)
        ? this.toError()
        : false;

    // sugar
    this.accepted = 202 == status;
    this.noContent = 204 == status;
    this.badRequest = 400 == status;
    this.unauthorized = 401 == status;
    this.notAcceptable = 406 == status;
    this.forbidden = 403 == status;
    this.notFound = 404 == status;
};

},{"./utils":8}],7:[function(require,module,exports){
var ERROR_CODES = [
  'ECONNRESET',
  'ETIMEDOUT',
  'EADDRINFO',
  'ESOCKETTIMEDOUT'
];

/**
 * Determine if a request should be retried.
 * (Borrowed from segmentio/superagent-retry)
 *
 * @param {Error} err
 * @param {Response} [res]
 * @returns {Boolean}
 */
module.exports = function shouldRetry(err, res) {
  if (err && err.code && ~ERROR_CODES.indexOf(err.code)) return true;
  if (res && res.status && res.status >= 500) return true;
  // Superagent timeout
  if (err && 'timeout' in err && err.code == 'ECONNABORTED') return true;
  if (err && 'crossDomain' in err) return true;
  return false;
};

},{}],8:[function(require,module,exports){

/**
 * Return the mime type for the given `str`.
 *
 * @param {String} str
 * @return {String}
 * @api private
 */

exports.type = function(str){
  return str.split(/ *; */).shift();
};

/**
 * Return header field parameters.
 *
 * @param {String} str
 * @return {Object}
 * @api private
 */

exports.params = function(str){
  return str.split(/ *; */).reduce(function(obj, str){
    var parts = str.split(/ *= */);
    var key = parts.shift();
    var val = parts.shift();

    if (key && val) obj[key] = val;
    return obj;
  }, {});
};

/**
 * Parse Link header fields.
 *
 * @param {String} str
 * @return {Object}
 * @api private
 */

exports.parseLinks = function(str){
  return str.split(/ *, */).reduce(function(obj, str){
    var parts = str.split(/ *; */);
    var url = parts[0].slice(1, -1);
    var rel = parts[1].split(/ *= */)[1].slice(1, -1);
    obj[rel] = url;
    return obj;
  }, {});
};

/**
 * Strip content related fields from `header`.
 *
 * @param {Object} header
 * @return {Object} header
 * @api private
 */

exports.cleanHeader = function(header, shouldStripCookie){
  delete header['content-type'];
  delete header['content-length'];
  delete header['transfer-encoding'];
  delete header['host'];
  if (shouldStripCookie) {
    delete header['cookie'];
  }
  return header;
};
},{}],9:[function(require,module,exports){
var API, request;

request = require('superagent');

API = {};

API.domain = window.API_ENDPOINT;

API.call = function(type, url, data, auth, onSuccess, onError, onProgress, dataType) {
  var r;
  if (type == null) {
    type = 'get';
  }
  if (url == null) {
    url = '/';
  }
  if (data == null) {
    data = null;
  }
  if (auth == null) {
    auth = true;
  }
  if (onSuccess == null) {
    onSuccess = null;
  }
  if (onError == null) {
    onError = null;
  }
  if (onProgress == null) {
    onProgress = null;
  }
  if (dataType == null) {
    dataType = null;
  }
  url = "" + this.domain + url;
  switch (type) {
    case 'get':
      r = request.get(url);
      break;
    case 'post':
      r = request.post(url);
      break;
    case 'put':
      r = request.put(url);
      break;
    case 'patch':
      r = request.patch(url);
      break;
    case 'delete':
      r = request.del(url);
      break;
    default:
      console.log("Request type " + type + " is not supported");
  }
  if (dataType === 'json') {
    r.set('Content-Type', 'application/json');
  }
  if (dataType === 'html') {
    r.set('Content-Type', 'text/html');
  }
  if (auth) {
    r.set("Authorization", "Token " + localStorage.token);
  }
  if (document.getElementsByName("csrfmiddlewaretoken").length > 0) {
    r.set("X-CSRFToken", document.getElementsByName("csrfmiddlewaretoken")[0].value);
  }
  if (data) {
    if (type === 'get') {
      r.query(data);
    } else {
      r.send(data);
    }
  }
  if (!onSuccess) {
    onSuccess = function(res) {
      return console.log('Success', res);
    };
  }
  if (!onError) {
    onError = function(res) {
      return console.log('Error', res);
    };
  }
  r.end(function(err, res) {
    var status;
    if (res && res.status === 204) {
      onSuccess({});
    }
    if (res && res.status === 404) {
      alert('The API url called does not exist');
      return;
    }
    if (err && !res) {
      alert('Connection error');
      return;
    }
    status = res.status;
    type = status / 100 | 0;
    if (dataType === 'html') {
      data = res.text;
    } else {
      data = res.body;
    }
    switch (type) {
      case 2:
        return onSuccess(data);
      case 4:
        return onError(data);
      case 5:
        alert('Server error');
        return console.log('Server error');
    }
  });
  if (onProgress) {
    r.on('progress', onProgress);
  }
  return r;
};

module.exports = API;


},{"superagent":2}],10:[function(require,module,exports){
var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

ContentEdit.Audio = (function(superClass) {
  extend(Audio, superClass);

  function Audio(tagName, attributes, sources) {
    var size;
    if (sources == null) {
      sources = [];
    }
    Audio.__super__.constructor.call(this, tagName, attributes);
    this.sources = sources;
    size = this.size();
    this._aspectRatio = size[1] / size[0];
  }

  Audio.prototype.cssTypeName = function() {
    return 'video';
  };

  Audio.prototype.type = function() {
    return 'Video';
  };

  Audio.prototype.typeName = function() {
    return 'Video';
  };

  Audio.prototype._title = function() {
    var src;
    src = '';
    if (this.attr('src')) {
      src = this.attr('src');
    } else {
      if (this.sources.length) {
        src = this.sources[0]['src'];
      }
    }
    if (!src) {
      src = 'No video source set';
    }
    if (src.length > 80) {
      src = src.substr(0, 80) + '...';
    }
    return src;
  };

  Audio.prototype.createDraggingDOMElement = function() {
    var helper;
    if (!this.isMounted()) {
      return;
    }
    helper = Audio.__super__.createDraggingDOMElement.call(this);
    helper.innerHTML = this._title();
    return helper;
  };

  Audio.prototype.html = function(indent) {
    var attributes, i, le, len, ref, source, sourceStrings;
    if (indent == null) {
      indent = '';
    }
    le = ContentEdit.LINE_ENDINGS;
    if (this.tagName() === 'video') {
      sourceStrings = [];
      ref = this.sources;
      for (i = 0, len = ref.length; i < len; i++) {
        source = ref[i];
        attributes = ContentEdit.attributesToString(source);
        sourceStrings.push("" + indent + ContentEdit.INDENT + "<source " + attributes + ">");
      }
      return (indent + "<video" + (this._attributesToString()) + ">" + le) + sourceStrings.join(le) + ("" + le + indent + "</video>");
    } else {
      return (indent + "<" + this._tagName + (this._attributesToString()) + ">") + ("</" + this._tagName + ">");
    }
  };

  Audio.prototype.mount = function() {
    var style;
    this._domElement = document.createElement('div');
    if (this.a && this.a['class']) {
      this._domElement.setAttribute('class', this.a['class']);
    } else if (this._attributes['class']) {
      this._domElement.setAttribute('class', this._attributes['class']);
    }
    style = this._attributes['style'] ? this._attributes['style'] : '';
    if (this._attributes['width']) {
      style += "width:" + this._attributes['width'] + "px;";
    }
    if (this._attributes['height']) {
      style += "height:" + this._attributes['height'] + "px;";
    }
    this._domElement.setAttribute('style', style);
    this._domElement.setAttribute('data-ce-title', this._title());
    return Audio.__super__.mount.call(this);
  };

  Audio.prototype.unmount = function() {
    var domElement, wrapper;
    if (this.isFixed()) {
      wrapper = document.createElement('div');
      wrapper.innerHTML = this.html();
      domElement = wrapper.querySelector('iframe');
      this._domElement.parentNode.replaceChild(domElement, this._domElement);
      this._domElement = domElement;
    }
    return Audio.__super__.unmount.call(this);
  };

  Audio.droppers = {
    'Image': ContentEdit.Element._dropBoth,
    'PreText': ContentEdit.Element._dropBoth,
    'Static': ContentEdit.Element._dropBoth,
    'Text': ContentEdit.Element._dropBoth,
    'Video': ContentEdit.Element._dropBoth
  };

  Audio.placements = ['above', 'below', 'left', 'right', 'center'];

  Audio.fromDOMElement = function(domElement) {
    var c, childNode, childNodes, i, len, sources;
    childNodes = (function() {
      var i, len, ref, results;
      ref = domElement.childNodes;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        c = ref[i];
        results.push(c);
      }
      return results;
    })();
    sources = [];
    for (i = 0, len = childNodes.length; i < len; i++) {
      childNode = childNodes[i];
      if (childNode.nodeType === 1 && childNode.tagName.toLowerCase() === 'source') {
        sources.push(this.getDOMElementAttributes(childNode));
      }
    }
    return new this(domElement.tagName, this.getDOMElementAttributes(domElement), sources);
  };

  return Audio;

})(ContentEdit.ResizableElement);

ContentEdit.TagNames.get().register(ContentEdit.Video, 'iframe', 'video');

ContentTools.Tools.Audio = (function(superClass) {
  extend(Audio, superClass);

  function Audio() {
    return Audio.__super__.constructor.apply(this, arguments);
  }

  ContentTools.ToolShelf.stow(Audio, 'audio');

  Audio.label = 'Audio';

  Audio.icon = 'audio';

  Audio.canApply = function(element, selection) {
    return !element.isFixed();
  };

  Audio.apply = function(element, selection, callback) {
    var app, dialog, modal, toolDetail;
    toolDetail = {
      'tool': this,
      'element': element,
      'selection': selection
    };
    if (!this.dispatchEditorEvent('tool-apply', toolDetail)) {
      return;
    }
    if (element.storeState) {
      element.storeState();
    }
    app = ContentTools.EditorApp.get();
    modal = new ContentTools.ModalUI();
    dialog = new ContentTools.AudioDialog();
    dialog.addEventListener('cancel', (function(_this) {
      return function() {
        modal.hide();
        dialog.hide();
        if (element.restoreState) {
          element.restoreState();
        }
        return callback(false);
      };
    })(this));
    dialog.addEventListener('save', (function(_this) {
      return function(ev) {
        var applied, audio, index, node, ref, regex, src, url;
        url = ev.detail().url;
        if (url) {
          regex = /<iframe.*?src="(.*?)"/;
          src = regex.exec(url)[1];
          audio = new ContentEdit.Audio('iframe', {
            'frameborder': 0,
            'height': ContentTools.DEFAULT_VIDEO_HEIGHT,
            'src': src,
            'width': "100%"
          });
          ref = _this._insertAt(element), node = ref[0], index = ref[1];
          node.parent().attach(audio, index);
          audio.focus();
        } else {
          if (element.restoreState) {
            element.restoreState();
          }
        }
        modal.hide();
        dialog.hide();
        applied = url !== '';
        callback(applied);
        if (applied) {
          return _this.dispatchEditorEvent('tool-applied', toolDetail);
        }
      };
    })(this));
    app.attach(modal);
    app.attach(dialog);
    modal.show();
    return dialog.show();
  };

  return Audio;

})(ContentTools.Tool);

ContentTools.AudioDialog = (function(superClass) {
  extend(AudioDialog, superClass);

  function AudioDialog() {
    AudioDialog.__super__.constructor.call(this, 'Insert audio');
  }

  AudioDialog.prototype.clearPreview = function() {
    if (this._domPreview) {
      this._domPreview.parentNode.removeChild(this._domPreview);
      return this._domPreview = void 0;
    }
  };

  AudioDialog.prototype.mount = function() {
    var domControlGroup;
    AudioDialog.__super__.mount.call(this);
    ContentEdit.addCSSClass(this._domElement, 'ct-video-dialog');
    ContentEdit.addCSSClass(this._domView, 'ct-video-dialog__preview');
    domControlGroup = this.constructor.createDiv(['ct-control-group']);
    this._domControls.appendChild(domControlGroup);
    this._domInput = document.createElement('input');
    this._domInput.setAttribute('class', 'ct-video-dialog__input');
    this._domInput.setAttribute('name', 'url');
    this._domInput.setAttribute('placeholder', ContentEdit._('Paste Soundcloud embed code'));
    this._domInput.setAttribute('type', 'text');
    domControlGroup.appendChild(this._domInput);
    this._domButton = this.constructor.createDiv(['ct-control', 'ct-control--text', 'ct-control--insert', 'ct-control--muted']);
    this._domButton.textContent = ContentEdit._('Insert');
    domControlGroup.appendChild(this._domButton);
    return this._addDOMEventListeners();
  };

  AudioDialog.prototype.preview = function(embedCode) {
    this.clearPreview();
    this._domPreview = document.createElement('div');
    this._domPreview.innerHTML = embedCode;
    return this._domView.appendChild(this._domPreview);
  };

  AudioDialog.prototype.save = function() {
    var embedURL, videoURL;
    videoURL = this._domInput.value.trim();
    embedURL = ContentTools.getEmbedVideoURL(videoURL);
    if (embedURL) {
      return this.dispatchEvent(this.createEvent('save', {
        'url': embedURL
      }));
    } else {
      return this.dispatchEvent(this.createEvent('save', {
        'url': videoURL
      }));
    }
  };

  AudioDialog.prototype.show = function() {
    AudioDialog.__super__.show.call(this);
    return this._domInput.focus();
  };

  AudioDialog.prototype.unmount = function() {
    if (this.isMounted()) {
      this._domInput.blur();
    }
    AudioDialog.__super__.unmount.call(this);
    this._domButton = null;
    this._domInput = null;
    return this._domPreview = null;
  };

  AudioDialog.prototype._addDOMEventListeners = function() {
    AudioDialog.__super__._addDOMEventListeners.call(this);
    this._domInput.addEventListener('input', (function(_this) {
      return function(ev) {
        var updatePreview;
        if (ev.target.value) {
          ContentEdit.removeCSSClass(_this._domButton, 'ct-control--muted');
        } else {
          ContentEdit.addCSSClass(_this._domButton, 'ct-control--muted');
        }
        if (_this._updatePreviewTimeout) {
          clearTimeout(_this._updatePreviewTimeout);
        }
        updatePreview = function() {
          var videoURL;
          videoURL = _this._domInput.value.trim();
          return _this.preview(videoURL);
        };
        return _this._updatePreviewTimeout = setTimeout(updatePreview, 500);
      };
    })(this));
    this._domInput.addEventListener('keypress', (function(_this) {
      return function(ev) {
        if (ev.keyCode === 13) {
          return _this.save();
        }
      };
    })(this));
    return this._domButton.addEventListener('click', (function(_this) {
      return function(ev) {
        var cssClass;
        ev.preventDefault();
        cssClass = _this._domButton.getAttribute('class');
        if (cssClass.indexOf('ct-control--muted') === -1) {
          return _this.save();
        }
      };
    })(this));
  };

  return AudioDialog;

})(ContentTools.DialogUI);


},{}],11:[function(require,module,exports){
var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

ContentEdit.BackgroundImage = (function(superClass) {
  extend(BackgroundImage, superClass);

  function BackgroundImage(attributes) {
    BackgroundImage.__super__.constructor.call(this, 'bkgimg', attributes);
  }

  BackgroundImage.prototype.cssTypeName = function() {
    return 'background-image';
  };

  BackgroundImage.prototype.type = function() {
    return 'BackgroundImage';
  };

  BackgroundImage.prototype.typeName = function() {
    return 'BackgroundImage';
  };

  BackgroundImage.prototype.html = function(indent) {
    var bkgimg;
    if (indent == null) {
      indent = '';
    }
    bkgimg = indent + "<div" + (this._attributesToString()) + "></div>";
    return bkgimg;
  };

  BackgroundImage.prototype.mount = function() {
    var buttonText, classes, rect, style;
    this._domElement = document.createElement('div');
    classes = '';
    if (this._attributes['class']) {
      classes += ' ' + this._attributes['class'];
    }
    this._domElement.setAttribute('class', classes);
    style = this._attributes['style'] ? this._attributes['style'] : '';
    this._domElement.setAttribute('style', style);
    this._domButtonElement = document.createElement("button");
    buttonText = document.createTextNode("Upload image");
    this._domButtonElement.appendChild(buttonText);
    this._domButtonElement.className = 'btn btn--small btn--change btn--upload-background-image';
    this._domButtonElement.style.position = 'absolute';
    BackgroundImage.__super__.mount.call(this);
    this._domButtonElement.style.zIndex = '9998';
    this._domElement.parentNode.parentNode.appendChild(this._domButtonElement);
    rect = this._domElement.getBoundingClientRect();
    this._domButtonElement.style.bottom = "16px";
    return this._domButtonElement.style.right = "16px";
  };

  BackgroundImage.prototype._addDOMEventListeners = function() {
    BackgroundImage.__super__._addDOMEventListeners.call(this);
    return this._domButtonElement.addEventListener('click', (function(_this) {
      return function(ev) {
        var allowScrolling, dialog, editor, modal, transparent;
        ev.preventDefault();
        editor = ContentTools.EditorApp.get();
        modal = new ContentTools.ModalUI(transparent = false, allowScrolling = false);
        dialog = new ContentTools.ImageDialog();
        dialog.addEventListener('imageuploader.mount', function(e) {
          return dialog._domInput.setAttribute('accept', 'image/*,video/*');
        });
        dialog.addEventListener('cancel', function() {
          modal.hide();
          return dialog.hide();
        });
        dialog.addEventListener('save', function(ev) {
          var detail, imageAttrs, imageSize, imageURL, style;
          detail = ev.detail();
          imageURL = detail.imageURL;
          imageSize = detail.imageSize;
          if (!imageAttrs) {
            imageAttrs = {};
          }
          imageAttrs.src = imageURL;
          style = "background-image: url('" + imageURL + "')";
          _this.attr('style', style);
          modal.hide();
          return dialog.hide();
        });
        editor.attach(modal);
        editor.attach(dialog);
        modal.show();
        return dialog.show();
      };
    })(this));
  };

  BackgroundImage.fromDOMElement = function(domElement) {
    var attributes;
    attributes = this.getDOMElementAttributes(domElement);
    return new this(attributes);
  };

  return BackgroundImage;

})(ContentEdit.Element);

ContentEdit.TagNames.get().register(ContentEdit.BackgroundImage, 'bkgimg');


},{}],12:[function(require,module,exports){
var API, AudioDialog, BackgroundImage, ImageUploader, Underline, onLoad;

API = require('./api.coffee');

ImageUploader = require('./image-uploader.coffee');

BackgroundImage = require('./background-image.coffee');

Underline = require('./underline.coffee');

AudioDialog = require('./audio.coffee');

onLoad = function() {
  var editor, getImages;
  ContentTools.IMAGE_UPLOADER = ImageUploader;
  ContentTools.DEFAULT_TOOLS[0].push('underline');
  ContentTools.DEFAULT_TOOLS[0].push('audio');
  editor = ContentTools.EditorApp.get();
  getImages = function() {
    var descendants, i, images, name, ref, region, src;
    descendants = void 0;
    i = void 0;
    images = void 0;
    images = {};
    ref = editor.regions();
    for (name in ref) {
      region = ref[name];
      descendants = region.descendants();
      i = 0;
      while (i < descendants.length) {
        if (descendants[i]._tagName !== 'img') {
          i++;
          continue;
        }
        src = descendants[i]._attributes['src'];
        src = src.replace(/\?_ignore=.*/, '');
        images[src] = descendants[i]._attributes['width'];
        i++;
      }
    }
    return images;
  };
  ContentTools.StylePalette.add([new ContentTools.Style('Text white', 'text-white', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text grey dark', 'text-grey-dark', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text grey medium', 'text-grey-medium', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text grey light', 'text-grey-light', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text blue', 'text-blue', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text bold', 'text-strong', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text italic', 'text-italic', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: hero', 'text-hero', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: large', 'text-large', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: medium', 'text-medium', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: emphasis', 'text-emphasis', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: normal', 'text-normal', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a']), new ContentTools.Style('Text size: micro', 'text-micro', ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'a'])]);
  editor.init('[data-editable], [data-fixture]', 'data-name');
  return editor.addEventListener('saved', function(ev) {
    var element, model, onError, onStateChange, onSuccess, page_id, payload, regions, url, xhr;
    regions = ev.detail().regions;
    onStateChange = void 0;
    payload = void 0;
    xhr = void 0;
    payload = new FormData();
    payload.append('images', JSON.stringify(getImages()));
    payload.append('regions', JSON.stringify(regions));
    model = document.querySelector('meta[name="content_type_id"]');
    payload.append('content_type_id', model.getAttribute('content'));
    onSuccess = function() {
      return new ContentTools.FlashUI('ok');
    };
    onError = function() {
      return new ContentTools.FlashUI('no');
    };
    element = document.querySelector('meta[name="object_id"]');
    page_id = element.getAttribute('content');
    url = "/api/cms/update/" + page_id + "/";
    return API.call('post', url, payload, false, onSuccess, onError, null, 'formData');
  });
};

window.addEventListener('load', onLoad);


},{"./api.coffee":9,"./audio.coffee":10,"./background-image.coffee":11,"./image-uploader.coffee":13,"./underline.coffee":14}],13:[function(require,module,exports){
var API, ImageUploader;

API = require('./api.coffee');

ImageUploader = function(dialog) {
  var image, rotateImage, xhr, xhrComplete, xhrProgress;
  image = void 0;
  xhr = void 0;
  xhrComplete = void 0;
  xhrProgress = void 0;
  rotateImage = (function(_this) {
    return function(direction) {
      var formData, onError, onSuccess, payload, url;
      formData = void 0;
      onSuccess = function(data) {
        dialog.busy(false);
        return dialog.populate(data.image, data.size);
      };
      onError = function(data) {
        dialog.busy(false);
        return new ContentTools.FlashUI('no');
      };
      dialog.busy(true);
      payload = new FormData;
      payload.append('direction', direction);
      url = "/api/cms/images/update/" + image.id + "/";
      return _this.r = API.call('post', url, payload, false, onSuccess, onError, null, 'formData');
    };
  })(this);
  dialog.addEventListener('imageuploader.cancelupload', (function(_this) {
    return function() {
      _this.r.abort();
      return dialog.state('empty');
    };
  })(this));
  dialog.addEventListener('imageuploader.clear', (function(_this) {
    return function() {
      dialog.clear();
      return image = null;
    };
  })(this));
  dialog.addEventListener('imageuploader.fileready', (function(_this) {
    return function(ev) {
      var content_type, file, formData, object_id, onError, onProgress, onSuccess, payload, url;
      file = ev.detail().file;
      formData = void 0;
      onProgress = function(ev) {
        console.log('onProgress');
        return dialog.progress(50);
      };
      onSuccess = function(data) {
        image = {
          id: data.uuid,
          name: data.name,
          size: [data.width, data.height],
          url: data.f
        };
        return dialog.populate(image.url, image.size);
      };
      onError = function(data) {
        return new ContentTools.FlashUI('no');
      };
      dialog.state('uploading');
      dialog.progress(0);
      content_type = document.querySelector('meta[name="content_type_id"]');
      object_id = document.querySelector('meta[name="object_id"]');
      payload = new FormData;
      payload.append('f', file);
      payload.append('content_type', content_type.getAttribute('content'));
      payload.append('object_id', object_id.getAttribute('content'));
      payload.append('public', true);
      url = '/api/file/upload';
      return _this.r = API.call('post', url, payload, false, onSuccess, onError, onProgress, 'formData');
    };
  })(this));
  dialog.addEventListener('imageuploader.save', (function(_this) {
    return function() {
      return dialog.save(image.url, image.size);
    };
  })(this));
  dialog.addEventListener('imageuploader.rotateccw', function() {
    return rotateImage('CCW');
  });
  return dialog.addEventListener('imageuploader.rotatecw', function() {
    return rotateImage('CW');
  });
};

module.exports = ImageUploader;


},{"./api.coffee":9}],14:[function(require,module,exports){
var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

ContentTools.Tools.Underline = (function(superClass) {
  extend(Underline, superClass);

  function Underline() {
    return Underline.__super__.constructor.apply(this, arguments);
  }

  ContentTools.ToolShelf.stow(Underline, 'underline');

  Underline.label = 'Underline';

  Underline.icon = 'underline';

  Underline.tagName = 'u';

  return Underline;

})(ContentTools.Tools.Bold);


},{}]},{},[12]);


// modernised version of https://www.npmjs.com/package/JSONStream

const Parser = require('./parser.js')
const nodestream = require('stream')
const stringify = require('./stringify.js')

exports.stringify = stringify

exports.parse = function (path, map) {
  const parser = new Parser()

  // create stream transformer
  const stream = new nodestream.Transform({ objectMode: true })

  // add _transform function
  stream._transform = function (chunk, encoding, done) {
    if (typeof chunk === 'string') {
      chunk = Buffer.from(chunk)
    }
    parser.write(chunk)
    done()
  }

  if (typeof path === 'string') {
    path = path.split('.').map(function (e) {
      if (e === '$*') {
        return { emitKey: true }
      } else if (e === '*') {
        return true
      } else if (e === '') { // '..'.split('.') returns an empty string
        return { recurse: true }
      } else {
        return e
      }
    })
  }

  if (!path || !path.length) {
    path = null
  }

  parser.onValue = function (value) {
    if (!this.root) {
      stream.root = value
    }

    if (!path) return

    let i = 0 // iterates on path
    let j = 0 // iterates on stack
    let emitKey = false
    let emitPath = false
    while (i < path.length) {
      const key = path[i]
      let c
      j++

      if (key && !key.recurse) {
        c = (j === this.stack.length) ? this : this.stack[j]
        if (!c) return
        if (!check(key, c.key)) {
          return
        }
        emitKey = !!key.emitKey
        emitPath = !!key.emitPath
        i++
      } else {
        i++
        const nextKey = path[i]
        if (!nextKey) return
        while (true) {
          c = (j === this.stack.length) ? this : this.stack[j]
          if (!c) return
          if (check(nextKey, c.key)) {
            i++
            if (!Object.isFrozen(this.stack[j])) {
              this.stack[j].value = null
            }
            break
          }
          j++
        }
      }
    }
    if (j !== this.stack.length) {
      return
    }

    const actualPath = this.stack.slice(1).map(function (element) {
      return element.key
    }).concat([this.key])
    let data = value
    if (data != null) {
      if ((data = map ? map(data, actualPath) : data) != null) {
        if (emitKey || emitPath) {
          data = { value: data }
          if (emitKey) {
            data.key = this.key
          }
          if (emitPath) {
            data.path = actualPath
          }
        }
        stream.push(data)
      }
    }
    if (this.value) {
      delete this.value[this.key]
    }
    for (const k in this.stack) {
      if (!Object.isFrozen(this.stack[k])) {
        this.stack[k].value = null
      }
    }
  }
  parser._onToken = parser.onToken

  parser.onToken = function (token, value) {
    parser._onToken(token, value)
    if (this.stack.length === 0) {
      if (stream.root) {
        if (!path) {
          stream.push(stream.root)
        }
        stream.root = null
      }
    }
  }

  parser.onError = function (err) {
    if (err.message.indexOf('at position') > -1) {
      err.message = 'Invalid JSON (' + err.message + ')'
    }
    stream.emit('error', err)
  }

  return stream
}

function check (x, y) {
  if (typeof x === 'string') {
    return y === x
  } else if (x && typeof x.exec === 'function') {
    return x.exec(y)
  } else if (typeof x === 'boolean' || typeof x === 'object') {
    return x
  } else if (typeof x === 'function') {
    return x(y)
  }
  return false
}

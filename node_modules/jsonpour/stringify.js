const stream = require('stream')
const stringify = new stream.Transform({ objectMode: true })
stringify._transform = function (obj, encoding, done) {
  // stringify the object
  this.push(JSON.stringify(obj) + '\n')
  done()
}
module.exports = stringify
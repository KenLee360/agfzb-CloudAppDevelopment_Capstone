# jsonpour

A no-dependency streaming JSON parser. Based on [JSONStream](https://www.npmjs.com/package/JSONStream) and [jsonparse](http://npmjs.com/package/jsonparse) which were no longer maintained.

This is stripped down somewhat and uses more modern JS syntax.

## Usage

```sh
npm install --save jsonpour
```

## Examples


Listen for the `data` event:

```js
const fs = require('rs')

const rs = fs.createReadStream('./test.json')
// parse an incoming JSON doc looking for a results:[] array containing a 'doc' sub-object
rs.pipe(jsonpour.parse('results.*.doc')).on('data', function(obj) {
  console.log('Found a doc', obj)
}).on('finish', function() {
  console.log('done')
})
```

Piping:

```js
const jsonpour = require('jsonpour')
const fs = require('fs')

// streaming transform
const stream = require('stream')
const filter = new stream.Transform({ objectMode: true })
filter._transform = function (obj, encoding, done) {
  // stringify the object
  this.push(JSON.stringify(obj) + '\n')
  done()
}

const rs = fs.createReadStream('./test.json')
// stream every object from the results array via a filter to stdout
rs.pipe(jsonpour.parse('results.*'))
  .pipe(filter)
  .pipe(process.stdout)
```
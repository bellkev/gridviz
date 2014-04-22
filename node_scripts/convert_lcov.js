/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

var coveralls = require('coveralls');
var fs = require('fs');

var inPath = process.argv[2];
var outPath = process.argv[3];

if (!(inPath && outPath)) {
    console.log("ERROR: You must specify both an input and output location");
    console.log("   e.g. node convert_lcov.js in_file out_file");
}

coveralls.convertLcovToCoveralls(fs.readFileSync(inPath, {encoding: 'utf8'}), {}, function (err, data) {
    if (err) {
        throw err;
    }
    fs.writeFileSync(outPath, JSON.stringify(data));
});
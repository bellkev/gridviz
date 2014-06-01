/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

module.exports = function (grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        copy: {
            main: {
                files: [
                    {expand: true, src: ['img/*'], dest: 'compiled_static_dev/'}
                ],
            }
        },
        less: {
            development: {
                files: {
                    "compiled_static_dev/css/gridviz.css": "less/gridviz.less"
                }
            }
        },
        watch: {
            styles: {
                // Which files to watch (all .less files recursively in the less directory)
                files: ['less/**/*.less', 'img/*'],
                tasks: ['less', 'copy'],
                options: {
                    nospawn: true
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
};

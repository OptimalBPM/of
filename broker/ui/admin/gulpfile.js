/* global require */

var gulp = require('gulp');
var webserver = require('gulp-webserver');

var templateCache = require('gulp-angular-templatecache');
var minifyHtml = require('gulp-minify-html');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var streamqueue = require('streamqueue');
var jscs = require('gulp-jscs');
var tsc = require('gulp-tsc');
var gfi = require("gulp-file-insert");

gulp.task('template-caches', function () {

    // Create cache
    gulp.src('./src/views/nodes.html')
        .pipe(minifyHtml({
            empty: true,
            spare: true,
            quotes: true
        }))
        .pipe(templateCache({
            module: 'nodesModule',
            root: 'directives/views'
        }))
        .pipe(concat('./.build/nodesTemplate.js'))
        .pipe(gulp.dest('.'));
    // Create cache
    gulp.src('./src/views/schematree.html')
        .pipe(minifyHtml({
            empty: true,
            spare: true,
            quotes: true
        }))
        .pipe(templateCache({
            module: 'schemaTreeModule',
            root: 'directives/views'
        }))
        .pipe(concat('./.build/schemaTreeTemplate.js'))
        .pipe(gulp.dest('.'));

});


gulp.task('build-output', function () {
    gulp.src('./src/init.ts')
        .pipe(gfi({
            "// {nodesTemplateCache}": "./.build/nodesTemplate.js",
            "// {schemaTreeTemplateCache}": "./.build/schemaTreeTemplate.js"
        }))
        .pipe(concat('./dist/nodes.ts'))
        .pipe(gulp.dest('.'));
});


gulp.task('default', [
    'template-caches',
    'build-output'
]);

gulp.task('jscs', function () {
    gulp.src('./src/**/*.js')
        .pipe(jscs());
});


gulp.task('watch', function () {
    gulp.watch('./src/**/*', ['default']);
});

gulp.task('webserver', function () {
    gulp.src('.')
        .pipe(webserver({
            livereload: true,
            port: 8001,
            open: true
        }));
});

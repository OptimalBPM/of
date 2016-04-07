// Karma configuration
// Generated on Sun Jul 26 2015 00:56:36 GMT+0200 (CEST)

module.exports = function (config) {
    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: './',

        plugins: ['karma-chrome-launcher', 'karma-systemjs', 'karma-mocha', 'karma-chai-sinon'],

        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['systemjs','mocha', "chai-sinon"],

        systemjs: {
            // Path to your SystemJS configuration file
            configFile: 'config.js',

            // SystemJS configuration specifically for tests, added after your config file.
            // Good for adding test libraries and mock modules
            config: {
                paths: {
                    'systemjs': "jspm_packages/system.src.js",
                    'es6-module-loader': "node_modules/es6-module-loader/dist/es6-module-loader.js",
                    'system-polyfills': "node_modules/systemjs/dist/system-polyfills.js",
                    'typescript': "node_modules/typescript/lib/typescript.js",
                    'jasmine': "node_modules/jasmine-core/lib/jasmine-core.js",
                    'angular-mocks': "node_modules/angular-mocks/angular-mocks.js"
                },
                transpiler: "typescript",
                packages: {
                    "test": {
                        "defaultExtension": "ts"
                    }
                }

            },
            // Specify the suffix used for test suite file names.  Defaults to .test.js, .spec.js, _test.js, and _spec.js
            testFileSuffix: 'node.spec.ts',
            // list of files / patterns to load in the browser
            files: [
                "node_modules/chai/chai.ts",
                "node_modules/es6-module-loader/dist/es6-module-loader.js",
                "node_modules/systemjs/dist/system-polyfills.js",
                "node_modules/typescript/lib/typescript.js",
                "node_modules/jasmine-core/lib/jasmine-core.js",
                "node_modules/jasmine-core/lib/jasmine-core/node_boot.js"
            ]
        },

        files: [
          {pattern: 'controllers/**/*.*', included: false, served: true},
          {pattern: 'directives/**/*.*', included: false, served: true},
          {pattern: 'scripts/**/*.*', included: false, served: true},
          {pattern: 'views/**/*.*', included: false, served: true},
          {pattern: 'types/**/*.*', included: false, served: true},
          {pattern: 'jspm_packages/**/*.*', included: false, served: true},
          {pattern: 'node_modules/angular*/*.*', included: false, served: true},
          {pattern: 'node_modules/karma-chai-sinon*/*.*', included: false, served: true},
          {pattern: 'test/*.*', included: false, served: true},
          {pattern: 'test/*spec*', included: true, served: true}
        ],

        // list of files to exclude
        exclude: [],

        preprocessors: {
          'src/**/*.js': ['coverage'],
          'src/**/*.html': ['ng-html2js']
        },
        ngHtml2JsPreprocessor: {
          cacheIdFromPath: function(filepath) {
            return 'directives/decorators/bootstrap/strap/' + filepath.substr(4);
          },
          moduleName: 'templates'
        },

        autoWatchBatchDelay: 2000,

        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {},


        // test results reporter to use
        // possible values: 'dots', 'progress'
        // available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['progress', 'coverage'],


        // web server port
        port: 9876,


        // enable / disable colors in the output (reporters and logs)
        colors: true,


        // level of logging
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,


        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,


        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: ['Chrome'],


        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    })
};

module.exports = (grunt) ->

    # Project configuration.
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json')

        browserify:
            backend:
                options:
                    transform: ['coffee-reactify']
                files:
                    '<%= pkg.www %>/js/cms.js': [
                        'scripts/cms.coffee'
                    ]

        uglify:
            options:
                    mangle: false

            backend:
                files:
                    '<%= pkg.www %>/js/cms.min.js': '<%= pkg.www %>/js/cms.js'


        watch:
            "backend-scripts":
                files: [
                    'scripts/admin/*.coffee'
                    'scripts/admin/*/*.coffee'
                    'scripts/admin/*/*/*.coffee'
                    ],
                tasks: ['backend-scripts']

    })

    # Plugins
    grunt.loadNpmTasks 'grunt-contrib-uglify'
    grunt.loadNpmTasks 'grunt-contrib-watch'
    grunt.loadNpmTasks 'grunt-browserify'

    # Tasks


    grunt.registerTask 'backend-scripts', [
        'browserify:backend'
    ]

    grunt.registerTask 'backend-production', [
        'browserify:backend'
        'uglify:backend'
    ]

    # Watch
    grunt.registerTask 'watch-backend-scripts', ['watch:backend-scripts']

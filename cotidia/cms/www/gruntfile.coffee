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

        sass:
            dist:
                options:
                    loadPath: require('node-neat').includePaths.concat(require('node-bourbon').includePaths)

                files:
                    '<%= pkg.static %>/css/cms.css': 'styles/cms.scss'

        cssmin:
            dist:
                files:
                    '<%= pkg.static %>/css/cms.min.css': '<%= pkg.static %>/css/cms.css'

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
    grunt.loadNpmTasks 'grunt-contrib-sass'
    grunt.loadNpmTasks 'grunt-contrib-cssmin'

    # Tasks

    grunt.registerTask 'backend-styles', [
        'sass',
        'cssmin'
    ]

    grunt.registerTask 'backend-scripts', [
        'browserify:backend'
    ]

    grunt.registerTask 'backend-production', [
        'browserify:backend'
        'uglify:backend'
        'sass',
        'cssmin'
    ]

    # Watch
    grunt.registerTask 'watch-backend-scripts', ['watch:backend-scripts']

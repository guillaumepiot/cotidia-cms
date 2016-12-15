module.exports = (grunt) ->

    # Project configuration.
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json')

        sass:
            backend:
                options:
                    # // includePaths: require('node-neat').with('other/path', 'another/path') 
                    # // - or - 
                    loadPath: require('node-neat').includePaths
                files:
                    '<%= pkg.www %>/css/backend.css': 'styles/admin/backend.scss'

            frontend:
                options:
                    loadPath: require('node-neat').includePaths
                files:
                    '<%= pkg.www %>/css/frontend.css': 'styles/public/frontend.scss'
                    '<%= pkg.www %>/css/form.css': 'styles/public/form.scss'

        browserify:
            backend:
                options:
                    transform: ['coffee-reactify']
                files:
                    '<%= pkg.www %>/js/backend.js': [
                        'scripts/admin/backend.coffee'
                    ]
            frontend:
                options:
                    transform: ['coffee-reactify']
                files:
                    '<%= pkg.www %>/js/frontend.js': [
                        'scripts/public/frontend.coffee'
                    ]

        uglify:
            options:
                    mangle: false

            frontend:
                files:
                    '<%= pkg.www %>/js/frontend.min.js': '<%= pkg.www %>/js/frontend.js'

            backend:
                files:
                    '<%= pkg.www %>/js/backend.min.js': '<%= pkg.www %>/js/backend.js'

        cssmin:
            backend:
                files:
                    '<%= pkg.www %>/css/backend.min.css': '<%= pkg.www %>/css/backend.css'
            frontend:
                files:
                    '<%= pkg.www %>/css/frontend.min.css': '<%= pkg.www %>/css/frontend.css'
                    '<%= pkg.www %>/css/form.min.css': '<%= pkg.www %>/css/form.css'

        watch:
            frontend:
                files: [
                    'scripts/public/*.coffee'
                    'styles/public/*.scss'
                    ],
                tasks: ['frontend']

            backend:
                files: [
                    'scripts/admin/*.coffee'
                    'scripts/admin/*/*.coffee'
                    'scripts/admin/*/*/*.coffee'
                    'styles/admin/*.scss'
                    ],
                tasks: ['backend']

            "backend-styles":
                files: [
                    'styles/admin/*.scss'
                    ],
                tasks: ['backend-styles']

            "backend-scripts":
                files: [
                    'scripts/admin/*.coffee'
                    'scripts/admin/*/*.coffee'
                    'scripts/admin/*/*/*.coffee'
                    ],
                tasks: ['backend-scripts']

            "frontend-styles":
                files: [
                    'styles/public/*.scss'
                    ],
                tasks: ['frontend-styles']

            "frontend-scripts":
                files: [
                    'scripts/public/*.coffee'
                    'scripts/public/*/*.coffee'
                    'scripts/public/*/*/*.coffee'
                    ],
                tasks: ['frontend-scripts']

        clean:
            frontend: [
                'js/frontend.jsx'
                'js/frontend.js'
            ]
            backend: [
                '<%= pkg.www %>/js/backend.jsx'
                '<%= pkg.www %>/js/backend.js'
            ]

        'string-replace': {                 
            dev: {
                files: {
                    "<%= pkg.www %>/js/backend.js": "<%= pkg.www %>/js/backend.js"
                },
                options: {
                    replacements: [{
                        pattern: /API_ENDPOINT/g,
                        replacement: "http://localhost:8000"
                    }]
                }
            }
            prod: {
                files: {
                    "<%= pkg.www %>/js/backend.js": "<%= pkg.www %>/js/backend.js"
                },
                options: {
                    replacements: [{
                        pattern: /API_ENDPOINT/g,
                        replacement: "http://cotidia.com"
                    }]
                }
            }
        }

    })

    # Plugins
    grunt.loadNpmTasks 'grunt-contrib-clean'
    grunt.loadNpmTasks 'grunt-contrib-cssmin'
    grunt.loadNpmTasks 'grunt-contrib-less'
    grunt.loadNpmTasks 'grunt-contrib-uglify'
    grunt.loadNpmTasks 'grunt-contrib-watch'
    grunt.loadNpmTasks 'grunt-browserify'
    grunt.loadNpmTasks 'grunt-contrib-sass'
    grunt.loadNpmTasks 'grunt-string-replace'

    # Tasks
    grunt.registerTask 'frontend-scripts', [
        'browserify:frontend'
        'uglify:frontend'
    ]

    grunt.registerTask 'frontend-styles', [
        'sass:frontend'
        'cssmin:frontend'
    ]

    grunt.registerTask 'frontend', [
        'browserify:frontend'
        'uglify:frontend'
        'sass:frontend'
        'cssmin:frontend'
    ]

    grunt.registerTask 'frontend-production', [
        'browserify:frontend'
        'uglify:frontend'
        'sass:frontend'
        'cssmin:frontend'
    ]

    grunt.registerTask 'backend-scripts', [
        'browserify:backend'
        'string-replace:dev'
    ]

    grunt.registerTask 'backend-styles', [
        'sass:backend'
        'cssmin:backend'
    ]

    grunt.registerTask 'backend-production', [
        'browserify:backend'
        'string-replace:prod'
        'uglify:backend'
        'sass:backend'
        'cssmin:backend'
    ]

    # Watch
    grunt.registerTask 'watch-frontend', ['watch:frontend']
    grunt.registerTask 'watch-backend', ['watch:backend']
    grunt.registerTask 'watch-backend-styles', ['watch:backend-styles']
    grunt.registerTask 'watch-backend-scripts', ['watch:backend-scripts']
    grunt.registerTask 'watch-frontend-styles', ['watch:frontend-styles']
    grunt.registerTask 'watch-frontend-scripts', ['watch:frontend-scripts']
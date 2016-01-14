module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'libraries.js': /^(?!app\/)/
      'app.js': /^app\//
    stylesheets:
      joinTo:
        'libraries.css': /^bower_components\//
        'app.css': /^(app)/
      order:
        before: ['bower_components/normalize-css/normalize.css']
  plugins:
    coffeescript:
      bare: yes
    sass:
      mode: 'native'
    autoReload:
      enabled: yes
  conventions:
    ignored: [
      /fontawesome/
    ]

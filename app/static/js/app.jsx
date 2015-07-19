/** @jsx React.DOM */

require.config({
    baseUrl: '/static/',
    urlArgs: "d=" + parseInt(Config.cache_buster, 10),
    paths: {
        // Dependencies
        "bootstrap": "components/bootstrap/dist/js/bootstrap.min",
        "history": "components/history.js/scripts/bundled/html4%2Bhtml5/native.history",
        "jquery": "components/jquery/dist/jquery.min",
        "moment": "components/momentjs/min/moment-with-locales.min",
        "moment-timezone": "components/moment-timezone/builds/moment-timezone.min",
        "react": "components/react/react-with-addons",
        "router": "components/routerjs/Router",
        "underscore": "components/underscore/underscore-min",

        // Angular deps for uploader. To be refactored to use React instead
        "angular": "components/angular/angular.min",
        "jquery-serialize-object": "components/jquery-serialize-object/jquery.serialize-object.compiled",
        "dirname": "components/phpjs/functions/filesystem/dirname",
        "number_format": "components/phpjs/functions/strings/number_format",
        "in_array": "components/phpjs/functions/array/in_array",
        "basename": "components/phpjs/functions/filesystem/basename",

        // Helpers
        "modal": "js/helpers/Modal",

        // App
        "files-list": "js/FilesList",
        "routes": "js/routes",
        "uploader": "js/uploader/Uploader",
    },
    shim: {
        'angular': {
            exports: 'angular'
        },
        'basename': {
            exports: 'basename'
        },
        'bootstrap': {
            deps: ['jquery']
        },
        'dirname': {
            exports: 'dirname'
        },
        'history': {
            exports: 'window.History'
        },
        'in_array': {
            exports: 'in_array'
        },
        'jquery-serialize-object': {
            deps: ['jquery']
        },
        'linear-partition': {
            exports: 'linear_partition'
        },
        'number_format': {
            exports: 'number_format'
        },
        'router': {
            exports: 'window.Router',
            deps: ['history']
        },
        'underscore': {
            exports: '_'
        }
    }
});

// Defer loading angular
// http://code.angularjs.org/1.2.1/docs/guide/bootstrap#overview_deferred-bootstrap
window.name = "NG_DEFER_BOOTSTRAP!";

// Configure the application
Config.App = {
    // The DOM id of the app container
    elementId: 'app',
    modalElementId: 'app-modal'
};

define(["moment"], function (moment) {
    moment().locale('en-US');
});

require(['react', 'routes', 'jquery', 'underscore', 'bootstrap'], function (React,  router, $, _, bs) {
    // Setup React
    React.initializeTouchEvents(true);

    // Start the router
    router.start(window.location.pathname);
});

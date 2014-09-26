/** @jsx React.DOM */

define('routes', ['router'], function() {
    var router = new Router();

    // Files List
    router.route('/', function() {
        require(['react', 'files-list'], function (React, FilesList) {
            React.renderComponent(
                <FilesList url="/rest/file/" />,
                document.getElementById(Config.App.elementId)
            );
        });
    });

    // File Uploader
    router.route('/upload/', function() {
        require(['uploader'], function () {
            // Resume bootstrapping
            // http://code.angularjs.org/1.2.1/docs/guide/bootstrap#overview_deferred-bootstrap
            angular.resumeBootstrap();
        });
    });

    // Users list
    router.route('/users/', function () {
        $('.btn-delete').on('click', function (e) {
            return confirm("Are you sure you want to delete this user?");
        });
    });

    return router;
});

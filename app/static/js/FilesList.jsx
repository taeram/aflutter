/** @jsx React.DOM */

define('files-list', ['react', 'modal', 'number_format', 'moment', 'moment-timezone'], function(React, Modal, number_format, moment, moment_timezone) {

    var FilesList = React.createClass({
        nextPageInterval: null,

        getInitialState: function () {
            return {
                data: [],
                hasMorePages: true,
                isLoading: true,
                page: 1
            };
        },

        url: function (file) {
            return 'https://' + Config.s3_bucket + '.s3.amazonaws.com' + '/' + file.folder + '/' + file.name;
        },

        formatSize: function (size) {
            if (size >= Math.pow(2,30)) {
                size = size / Math.pow(2,30)
                identifier = 'GB';
            } else if (size >= Math.pow(2,20)) {
                size = size / Math.pow(2,20)
                identifier = 'MB';
            } else if (size >= Math.pow(2,10)) {
                size = size / Math.pow(2,10)
                identifier = 'kB';
            } else {
                identifier = 'bytes';
            }

            return number_format(size) + ' ' + identifier;
        },

        componentWillMount: function () {
            this.retrieve();
            this.nextPageInterval = setInterval(this.triggerNextPage, 250);
        },

        retrieve: function () {
            var searchQuery = "";
            if ($('#search').val()) {
                searchQuery = "&q=" + $('#search').val();
            }

            $.ajax({
                url: '/rest/file/?page=' + this.state.page + searchQuery,
                success: function (results) {
                    var data;
                    if (this.state.data.length > 0) {
                        data = this.state.data;
                        for (var i=0; i < results.length; i++) {
                            data.push(results[i]);
                        }
                    } else {
                        data = results;
                    }

                    this.setState(({
                        isLoading: false,
                        data: data,
                        hasMorePages: (results.length > 0),
                    }))
                }.bind(this),
                error: function () {
                    this.setState(({
                        isLoading: false,
                        hasMorePages: false
                    }))
                }.bind(this)
            });
        },

        deleteFile: function (file) {
            $.ajax({
                url: '/rest/file/' + file.id,
                method: 'DELETE',
                success: function (file) {
                    for (var i=0; i < this.state.data.length; i++) {
                        if (file.id == this.state.data[i].id) {
                            delete this.state.data[i];
                            break;
                        }
                    }

                    // Remove the undefined elements from the array
                    this.state.data = _.reject(this.state.data, function (file) { 
                        return file === undefined;
                    });

                    this.setState(({
                        data: this.state.data
                    }))
                }.bind(this)
            });
        },

        showDeleteFileModal: function (file) {
            // Unmount the existing component, if any
            React.unmountComponentAtNode(document.getElementById(Config.App.modalElementId));

            React.renderComponent(
                <Modal
                    title={"Delete " + file.name + "?"}
                    content={"Are you sure you want to delete " + file.name + "?"}
                    submitButtonText="Delete"
                    submitButtonClass="btn-danger"
                    onClickSubmit={this.deleteFile.bind(this, file)} />,
                document.getElementById(Config.App.modalElementId)
            );
        },
        
        triggerNextPage: function () {
            // Don't bother triggering if there are no more pages
            if (!this.state.hasMorePages) {
                clearInterval(this.nextPageInterval);
                return;
            }

            var pageHeight = $(document).height();
            var scrollbarPosition = $(window).scrollTop() + $(window).height();
            var fudge = 100;

            if (pageHeight - fudge <= scrollbarPosition) {
                this.nextPage();
            }
        },

        nextPage: function () {
            this.state.page++;
            this.setState({
                isLoading: true,
                page: this.state.page
            });

            this.retrieve();
        },

        render: function() {
            var fileNodes;
            if (this.state.data.length > 0) {
                fileNodes = this.state.data.map(function(file, i) {
                    var deleteButtonNode;
                    if (Config.User.role) {
                        deleteButtonNode = (
                            <td>
                                <button className="btn btn-mini btn-danger btn-delete" onClick={this.deleteFile.bind(this, file)}>
                                    <i className="fa fa-trash-o"></i>
                                </button>
                            </td>
                        );
                    }

                    return (
                        <tr key={"file-" + file.id }>
                            <td>
                                <a href={this.url(file)} target="_blank">{file.name}</a>
                            </td>
                            <td>{ this.formatSize(file.size) }</td>
                            <td>{ moment(file.created, 'YYYY-MM-DD HH:mm:ss ZZ').format('lll') }</td>
                            {deleteButtonNode}
                        </tr>
                    );
                }.bind(this));
            } else {
                fileNodes = (
                    <tr>
                        <td colSpan="999">
                            <div className="alert alert-info text-center">
                                No files found
                            </div>
                        </td>
                    </tr>
                );
            }

            var loadingNode;
            if (this.state.isLoading) {
                loadingNode = (
                    <tr key={"files-loading-node"}>
                        <td colSpan="999">
                            <div className="text-center text-large" style={{fontSize: "24px", height: "60px"}}>
                                <i className="fa fa-spin fa-circle-o-notch"></i>
                            </div>
                        </td>
                    </tr>
                );
            }

            var allFilesDisplayedNode;
            if (this.state.hasMorePages == false) {
                var totalSize = _.reduce(this.state.data, function (memo, file) {
                    return memo + file.size;
                }, 0);

                allFilesDisplayedNode = (
                    <div className="text-center" style={{ marginBottom: "20px"}} >
                        <strong>{this.state.data.length} files</strong> totalling <strong>{ this.formatSize(totalSize) }</strong>
                    </div>
                );
            }

            var tableHeaderButtonColumnNode;
            if (Config.User.role) {
                tableHeaderButtonColumnNode = (
                    <th></th>
                );
            }

            return (
                <div>
                    <table className="table table-striped table-files">
                        <colgroup>
                            <col />
                            <col style={{width: "75px"}} />
                            <col style={{width: "190px"}} />
                            {Config.User.role ? (<col style={{width: "60px"}} />) : null}
                        </colgroup>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Size</th>
                                <th>Uploaded</th>
                                {Config.User.role ? (<th></th>) : null}
                            </tr>
                        </thead>
                        <tbody>
                            {fileNodes}
                            {loadingNode}
                        </tbody>
                    </table>
                    {allFilesDisplayedNode}
                </div>
            );
        }
    });

    return FilesList;
});

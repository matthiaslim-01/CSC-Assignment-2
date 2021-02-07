$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)')
        .exec(window.location.search);

    return (results !== null) ? results[1] || 0 : false;
}

$('#commentsContainer').comments({
    textareaPlaceholderText: 'Leave a comment',
    enableEditing: true,
    enableUpvoting: false,
    enableDeleting: true,
    enableDeletingCommentWithReplies: false,
    enableAttachments: false,
    enableHashtags: false,
    enablePinging: false,
    postCommentOnEnter: false,
    forceResponsive: true,
    readOnly: false,
    getComments: function (success, error) {
        console.log($.urlParam('talentId'));
        $.ajax({
            method: 'GET',
            url: `https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/get-comments?talentId=${$.urlParam('talentId')}&userId=${$.urlParam('userId')}`,
            dataType: 'json',
            async: true,
            cache: false
        }).done(function (data) {
            console.log(data);

            success(data);

        })//End of ajax().done()

        $('#commentsContainer .textarea-wrapper .textarea').attr('contentEditable', 'false')
        $('#commentsContainer .data-container .action').prop('disabled', true)


    },
    postComment: function (commentJSON, success, error) {
        console.dir(commentJSON);

        // commentJSON["userId"] = customerAccountID
        // commentJSON["talentId"] =
        console.dir(commentJSON)

        $.ajax({
            method: 'POST',
            url: 'https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/create-comments',
            data: commentJSON,
            success: function (comment) {
                success(comment)
                //console.dir(comment);
            },
            error: error

        });
    }
});
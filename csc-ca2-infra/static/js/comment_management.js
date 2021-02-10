$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)')
        .exec(window.location.search);

    return (results !== null) ? results[1] || 0 : false;
}

$('#commentsContainer .textarea-wrapper .textarea').attr('contentEditable', 'false');
$('#commentsContainer .data-container .action').prop('disabled', true);

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
            console.log(data.data.commentResult);
            $('#img').attr("src", data.data.talDetails[0].UrlLink);
            success(data.data.commentResult);

            data = data.data.commentResult;

            for (var i = 0; i < data.length; i++) {
                console.log(data[i].createdByCurrentUser === true)
                if (data[i].createdByCurrentUser === true) {
                    if (data[i].Subscription === "Paid") {
                        $('#commentsContainer .textarea-wrapper .textarea').attr('contentEditable', 'true');
                        $('#commentsContainer .data-container .action').prop('disabled', false);
                        break;
                    }
                    else {
                        $('#commentsContainer .textarea-wrapper .textarea').attr('contentEditable', 'false');
                        $('#commentsContainer .data-container .action').prop('disabled', true);
                        break;
                    }
                }
                else {
                    continue;
                }
            }
        })//End of ajax().done()




    },
    postComment: function (commentJSON, success, error) {
        console.dir(commentJSON);

        commentJSON["userId"] = $.urlParam('userId')
        commentJSON["talentId"] = $.urlParam('talentId')
        console.dir(commentJSON)

        $.ajax({
            method: 'POST',
            url: 'https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/create-comment',
            data: JSON.stringify(commentJSON),
            success: function (comment) {
                console.log(comment);
                success(comment.data);
                //console.dir(comment);
            },
            error: error

        });
    }
});
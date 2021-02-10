$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)')
        .exec(window.location.search);

    return (results !== null) ? results[1] || 0 : false;
}

function renderData(inData) {
    var $pElement;
    $divElement = $('<div></div>', { id: 'talentDetails' });

    $pElement = $('<p>', { text: inData.name });
    $divElement.append($pElement);

    $pElement = $('<p>', { text: inData.bio });
    $divElement.append($pElement);

    $('#talent').append($divElement);
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

        $.ajax({
            method: 'GET',
            url: `https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/get-talent-detail?talentId=${$.urlParam('talentId')}`,
            dataType: 'json',
            async: true,
            cache: false
        }).done(function (data) {

            console.log(data);

            $('#img').attr("src", data.data.urlLink);

            renderData(data.data);

        })//End of ajax().done()

        $.ajax({
            method: 'GET',
            url: `https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/get-comments?talentId=${$.urlParam('talentId')}&userId=${$.urlParam('userId')}`,
            dataType: 'json',
            async: true,
            cache: false
        }).done(function (data) {

            success(data.data.commentResult);

            commentData = data.data.commentResult;

            talData = data.data.talDetails;

            for (var i = 0; i < commentData.length; i++) {
                if (commentData[i].createdByCurrentUser === true) {
                    if (commentData[i].Subscription === "Paid") {
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

        commentJSON["userId"] = $.urlParam('userId')
        commentJSON["talentId"] = $.urlParam('talentId')

        $.ajax({
            method: 'POST',
            url: 'https://2v4tslm6qk.execute-api.us-east-1.amazonaws.com/dev/api/create-comment',
            data: JSON.stringify(commentJSON),
            success: function (comment) {
                console.log(comment);
                success(comment.data);
            },
            error: error

        });
    }
});
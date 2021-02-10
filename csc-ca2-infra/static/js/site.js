// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

// Check if session cookie is present
let re = new RegExp('(?<=session=)[^ ;]+');
var session_token = document.cookie.toString().match(re);
if (session_token !== null){
    $('.loginBtn').css('display', 'none');
    $('.createTalent').css('display', 'block');
    $('.manageBillBtn').css('display', 'block');
    $('.logoutBtn').css('display', 'block');
}

//LOGOUT
const logoutBtn = document.querySelector('.logoutBtn');
logoutBtn.addEventListener('click', function (e) {
    e.preventDefault();
    fetch('/dev/api/logout', {
        method: 'POST',
        credentials: "include",
    })
        .then((response) => response.json())
        .then((json) => { return json.data })
        .then((data) => {
            window.location.href = "/dev/Index.html"
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});

// UPLOAD Method
$("#submitTalent").click((e) => {
    e.preventDefault();

    let fileList = $("#formFile")[0].files;
    let file = fileList[0];
    let talentName = $("#formName")
    let talentBio = $("#formBio")
    let $result = $("#result")
    if (file !== undefined || talentName !== undefined || talentBio !== undefined) {
        let formData = new FormData();
        formData.append("photo", file);
        formData.append("talentName", talentName);
        formData.append("talentBio", talentBio);

        $.ajax({
            url: "https://vytealar0d.execute-api.us-east-1.amazonaws.com/dev/api/uploadImage",
            method: "POST",
            processData: false,
            contentType: false,
            data: formData
        }).done((data) => {
            console.log(data)
            $result.text("Talent successfully created.");
        }).fail((data) => {
            console.log(data)
            $result.text(data.responseJSON.Message)
        })
    } else {
        $result.text("Check your inputs.")
    }
});

//SEARCH Method
$('#search').keyup(function () {
    //get data from json file
    //var urlForJson = "data.json";

    //get data from Restful web Service in development environment
    var urlForJson = "https://vytealar0d.execute-api.us-east-1.amazonaws.com/dev/api/getAllTalents";

    //Url for the Cloud image hosting
    var urlForCloudImage = "https://csc-assignment-photo-bucket-teh.s3.amazonaws.com/";

    var searchField = $('#search').val();
    var myExp = new RegExp(searchField, "i");
    $.getJSON(urlForJson, function (data) {
        var output = '<ul class="searchresults">';
        $.each(data, function (key, val) {
            //for debug
            console.log(data);
            if ((val.Name.search(myExp) != -1) ||
			(val.Bio.search(myExp) != -1)) {
                output += '<li>';
                output += '<h2>' + val.Name + '</h2>';
                //get the absolute path for local image
                //output += '<img src="images/'+ val.ShortName +'_tn.jpg" alt="'+ val.Name +'" />';

                //get the image from cloud hosting
                output += '<img src=' + urlForCloudImage + val.ShortName + "_tn.jpg alt=" + val.Name + '" />';
                output += '<p>' + val.Bio + '</p>';
                output += '</li>';
            }
        });
        output += '</ul>';
        $('#update').html(output);
    }); //get JSON
});

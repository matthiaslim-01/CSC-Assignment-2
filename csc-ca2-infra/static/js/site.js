// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

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
            url: "https://7aitolysoe.execute-api.us-east-1.amazonaws.com/dev/api/uploadImage",
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
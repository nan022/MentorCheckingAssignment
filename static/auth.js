function sign_in() {
    let email = $("#email").val();
    let password = $("#password").val();

    if (email === "") {
        $("#help-email").text("Please input your email.");
        $("#email").focus();
        return;
    } else {
        $("#help-email").text("");
    }

    if (password === "") {
        $("#help-password").text("Please input your password.");
        $("#password").focus();
        return;
    } else {
        $("#help-password").text("");
    }

    console.log(email, password);
    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            email_give: email,
            password_give: password,
        },
        success: function (response) {
            if (response["result"] === "success") {
                $.cookie("gungnir", response["token"], { path: "/" });
                window.location.replace("/");
            } else {
                alert(response["msg"]);
            }
        },
    });
}

function sign_out() {
    Swal.fire({
        icon: 'success',
        title: 'You Logged Off',
        text: 'Click OK to go to login page',
        willClose: () => {
            $.removeCookie('gungnir', { path: '/' });
            window.location.replace('/login')
        }
  });
}
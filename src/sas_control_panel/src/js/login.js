














const client = new sasapi.Client();
document.addEventListener("DOMContentLoaded", () => {
    const message_box = document.getElementsByClassName("message")[0];
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        message_box.innerText = "";
        const username = document.getElementById("username-input").value;
        const password = document.getElementById("password-input").value;

        client.username = username;
        client.password = password;
        if(await client.users_login()) {
            document.cookie = `username=${btoa(username)}`;
            document.cookie = `password=${btoa(password)}`;
            window.location = "/html/view.html";
        }
        else {
            message_box.innerText = "Wrong Credentials";
        }
        return false;
    });

    client.connect();
})
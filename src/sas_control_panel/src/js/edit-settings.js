





document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("change-password").addEventListener("click", async () => {
        const new_password = window.prompt("New password:");
        if(new_password !== null && new_password !== '') {
            var changed = await client.users_alter(APP_USERNAME, new_password);
            if(changed) {
                client.password = new_password;
                document.cookie = `password=${btoa(new_password)}; path=/`;
            }
        }
    });

    document.getElementById("logout").addEventListener("click", () => {
        document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "password=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        window.location = "/index.html"
    });

    client.connect();

});
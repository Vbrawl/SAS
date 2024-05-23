





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
        window.location = "/index.html";
    });

    document.getElementById("save-settings").addEventListener("click", async () => {
        const operations = [];
        var status = true;
        operations.push(
            client.sms_api_key_alter(document.getElementById("api-key-field").value));
        operations.push(
            client.telephone_alter(document.getElementById("telephone-field").value));
        operations.push(
            client.timezone_alter(document.getElementById("timezone-selector").value));

        for (let i = 0; i < operations.length; i++) {
            const operation = operations[i];
            status &= await operation;
        }

        alert(status ? "Settings saved!" : "Settings could not be saved.");
        if(status) {window.location.reload();}
    });

    client.connect(async () => {
        document.getElementById("api-key-field").value = await client.sms_api_key_get();
        document.getElementById("telephone-field").value = await client.telephone_get();
        document.getElementById("timezone-selector").value = await client.timezone_get();
    });

});
let GETparams = new URLSearchParams(window.location.search);
let page_object_id = GETparams.get("id");
page_object_id = (page_object_id ? parseInt(page_object_id) : null);



// Client is initialized in common.js
document.addEventListener("DOMContentLoaded", () => {
    document.getElementsByClassName("discard-button")[0].addEventListener("click", () => {
        window.location.reload();
    });

    document.getElementsByClassName("apply-button")[0].addEventListener("click", async () => {
        const msg = document.getElementsByClassName("template-message-text")[0].value;
        const label = document.getElementById("template-label-text").value;

        if(page_object_id === null) {
            const new_id = await client.template_add(new sasapi.Template(msg, null, label));
            GETparams.set("id", new_id);
            window.location.search = GETparams.toString();
        } else {
            await client.template_alter(new sasapi.Template(msg, page_object_id, label));
            window.location.reload();
        }
    });

    client.connect(async (evt) => {
        if(page_object_id !== null) {
            const templates = await client.template_get(page_object_id);

            if(templates.length != 0) {
                const template = templates[0];
                document.getElementsByClassName("template-message-text")[0].value = template.message;
                document.getElementById("template-label-text").value = template.label;
            }
        }
    });
})
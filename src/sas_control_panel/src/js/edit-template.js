let GETparams = new URLSearchParams(window.location.search);
let page_object_id = GETparams.get("id");
page_object_id = (page_object_id ? parseInt(page_object_id) : null);



const client = new sasapi.Client();
document.addEventListener("DOMContentLoaded", () => {
    document.getElementsByClassName("discard-button")[0].addEventListener("click", () => {
        window.location.reload();
    });

    document.getElementsByClassName("apply-button")[0].addEventListener("click", async () => {
        const dom_msg = document.getElementsByClassName("template-message-text")[0];
        const msg = dom_msg.value;
        await client.template_alter(new sasapi.Template(msg, page_object_id));
        window.location.reload();
    })

    client.connect("127.0.0.1", 8585, async (evt) => {
        const templates = await client.template_get(page_object_id);

        if(templates.length != 0) {
            const template = templates[0];
            document.getElementsByClassName("template-message-text")[0].value = template.message;
        }
    });
})
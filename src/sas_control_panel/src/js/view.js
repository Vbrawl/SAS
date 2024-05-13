
/**
 * Create a DOM-element with the details of a template.
 * @param {Template} template The template object
 * @param {boolean} is_header When true the template object is ignored and a header is generated.
 * @returns The generated object.
 */
function dom_template_item(template, is_header = false) {
    const item = document.createElement("div");
    item.classList.add("list-item-wrapper");
    if(!is_header) {item.setAttribute('data-id', template.id);}

    const msg = document.createElement("div");
    msg.classList.add("template-message");
    msg.textContent = is_header ? 'Template Message' : template.message;

    const sep1 = document.createElement('span');
    sep1.classList.add("col");

    const buttons = document.createElement('div');
    buttons.classList.add("button-holder");


    if(is_header) {
        const button_label = document.createElement('div');
        button_label.classList.add("button-holder-label");
        button_label.textContent = "Select All";
        buttons.appendChild(button_label);
    }
    const checkbox = document.createElement('input');
    checkbox.setAttribute("type", "checkbox");
    buttons.appendChild(checkbox);

    item.appendChild(msg);
    item.appendChild(sep1);
    item.appendChild(buttons);
    return item;
}

/**
 * Fill dom_element with dom template items.
 * @param {DOMElement} dom_element The element to fill.
 * @param {Array<Template>} templates The list with all templates.
 */
function fill_with_templates(dom_element, templates) {
    dom_element.html = "";

    const header = dom_template_item(null, true);
    header.classList.add("list-header");
    dom_element.appendChild(header);

    for (let i = 0; i < templates.length; i++) {
        const template = templates[i];
        const item = dom_template_item(template);
        dom_element.appendChild(item);
    }
}




/**
 * The entry point of the script.
 */
document.addEventListener("DOMContentLoaded", () => {
    var client = new sasapi.Client();
    
    client.connect("127.0.0.1", 8585);

    client.ws.onopen = async (evt) => {
        fill_with_templates(
            document.getElementsByClassName("list")[0],
            await client.template_get()
        );
    }
});

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
    else {item.classList.add("list-header");}

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
    checkbox.classList.add("item-selector");
    checkbox.setAttribute("type", "checkbox");
    if(is_header) checkbox.addEventListener("click", set_all_state);
    else checkbox.addEventListener("click", set_header_state)
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
    dom_element.appendChild(header);

    for (let i = 0; i < templates.length; i++) {
        const template = templates[i];
        const item = dom_template_item(template);
        dom_element.appendChild(item);
    }
}

/**
 * Create a DOM-element with the details of a PersonTemplateArguments.
 * @param {PersonTemplateArguments} person The PersonTemplateArguments object.
 * @param {boolean} is_header When true the PersonTemplateArguments object is ignored and a header is generated.
 * @returns The generated object.
 */
function dom_person_item(person, is_header = false) {
    const item = document.createElement("div");
    item.classList.add("list-item-wrapper");
    if(!is_header) {item.setAttribute('data-id', person.args.id);}
    else {item.classList.add("list-header");}

    const fname = document.createElement("div");
    fname.classList.add("first-name");
    fname.textContent = is_header ? "First Name" : person.args.first_name;
    
    const sep1 = document.createElement('span');
    sep1.classList.add("col");

    const lname = document.createElement("div");
    lname.classList.add("last-name");
    lname.textContent = is_header ? "Last Name" : person.args.last_name;

    const sep2 = document.createElement('span');
    sep2.classList.add("col");

    const telephone = document.createElement("div");
    telephone.classList.add("telephone");
    telephone.textContent = is_header ? "Telephone" : person.args.telephone;

    const sep3 = document.createElement("div");
    sep3.classList.add("col");

    const address = document.createElement("div");
    address.classList.add("address");
    address.textContent = is_header ? "Address" : person.args.address;

    const sep4 = document.createElement("div");
    sep4.classList.add("col");

    const buttons = document.createElement('div');
    buttons.classList.add("button-holder");


    if(is_header) {
        const button_label = document.createElement('div');
        button_label.classList.add("button-holder-label");
        button_label.textContent = "Select All";
        buttons.appendChild(button_label);
    }
    const checkbox = document.createElement('input');
    checkbox.classList.add("item-selector");
    checkbox.setAttribute("type", "checkbox");
    if(is_header) checkbox.addEventListener("click", set_all_state);
    else checkbox.addEventListener("click", set_header_state)
    buttons.appendChild(checkbox);

    item.appendChild(fname);
    item.appendChild(sep1);
    item.appendChild(lname);
    item.appendChild(sep2);
    item.appendChild(telephone);
    item.appendChild(sep3);
    item.appendChild(address);
    item.appendChild(sep4);
    item.appendChild(buttons);
    return item;
}

function fill_with_people(dom_element, people) {
    dom_element.html = "";

    const header = dom_person_item(null, true);
    dom_element.appendChild(header);

    for (let i = 0; i < people.length; i++) {
        const person = people[i];
        const item = dom_person_item(person);
        dom_element.appendChild(item);
    }
}


/**
 * Set all checkboxes to match the header's one.
 * @param {Event} evt The event object
 */
function set_all_state(evt) {
    const list = evt.currentTarget.parentElement.parentElement.parentElement;
    const myState = evt.currentTarget.checked;
    const list_items = list.getElementsByClassName("item-selector");

    for (let i = 0; i < list_items.length; i++) {
        const item_selector = list_items[i];
        const item = item_selector.parentElement.parentElement;
        if(item.classList.contains("list-header")) {continue;}

        item_selector.checked = myState;
    }
}

/**
 * Set the header's checkbox state depending on if all
 * checkboxes in the list are checked or not.
 * @param {Event} evt The event object
 */
function set_header_state(evt) {
    const list = evt.currentTarget.parentElement.parentElement.parentElement;
    const item_selectors = list.getElementsByClassName("item-selector");

    var header_selector = null;
    var all_checked = true;

    for (let i = 0; i < item_selectors.length; i++) {
        const item = item_selectors[i];

        if(item.parentElement.parentElement.classList.contains("list-header")) {
            header_selector = item;
        } else if (!item.checked) {all_checked = false;}
    }

    if(header_selector) header_selector.checked = all_checked;
}




/**
 * The entry point of the script.
 */
document.addEventListener("DOMContentLoaded", () => {
    var client = new sasapi.Client();
    
    client.connect("127.0.0.1", 8585);

    client.ws.onopen = async (evt) => {
        // fill_with_templates(
        //     document.getElementsByClassName("list")[0],
        //     await client.template_get()
        // );

        fill_with_people(
            document.getElementsByClassName("list")[0],
            await client.people_get()
        );
    }
});
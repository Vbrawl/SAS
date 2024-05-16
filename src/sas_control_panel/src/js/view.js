let GETparams = new URLSearchParams(window.location.search);
let page_object_type = GETparams.get("object_type");
if(page_object_type == null) {page_object_type = "template";}


function add_section(item, class_name, textContent) {
    const section = document.createElement("div");
    section.classList.add(class_name);
    section.textContent = textContent;

    item.appendChild(section);
}

function add_colon(item) {
    const sep = document.createElement('span');
    sep.classList.add("col");

    item.appendChild(sep);
}

function dom_list_item(obj_name, obj, is_header = false) {
    const item = document.createElement("div");
    item.classList.add("list-item-wrapper");
    if(is_header) {item.classList.add("list-header");}
    else {item.setAttribute("data-id", obj_name == "people" ? obj.args.id : obj.id);}

    switch (obj_name) {
        case "template":
            add_section(item, "template-label", is_header ? "Label" : obj.label);
            add_colon(item);
            add_section(item, "template-message", is_header ? "Message" : obj.message);
            break;
        case "people":
            add_section(item, "first-name", is_header ? "First Name" : obj.args.first_name);
            add_colon(item);
            add_section(item, "last-name", is_header ? "Last Name" : obj.args.last_name);
            add_colon(item);
            add_section(item, "telephone", is_header ? "Telephone" : obj.args.telephone);
            add_colon(item);
            add_section(item, "address", is_header ? "Address" : obj.args.address);
            break;
        case "rule":
            add_section(item, "recipient-count", is_header ? 'Recipient Count' : obj.recipients.length);
            add_colon(item);
            add_section(item, "start-date", is_header ? "Start Date" : sasapi.date_to_string(obj.start_date));
            add_colon(item);
            add_section(item, "end-date", is_header ? "End Date" : (obj.end_date ? sasapi.date_to_string(obj.end_date) : ''));
            break;
    }


    add_colon(item);
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
    if(is_header) checkbox.addEventListener("change", set_all_state);
    else checkbox.addEventListener("change", set_header_state)
    checkbox.addEventListener("change", set_action_buttons_state);
    buttons.appendChild(checkbox);

    item.appendChild(buttons);
    return item;
}

async function fill_list(object_name, objects, dom_element) {
    dom_element.html = '';

    dom_element.appendChild(
        dom_list_item(object_name, null, true)
    );

    for (let i = 0; i < objects.length; i++) {
        const obj = objects[i];
        const item = dom_list_item(object_name, obj);
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


function set_action_buttons_state(evt) {
    const list = evt.currentTarget.parentElement.parentElement.parentElement;
    const item_selectors = list.getElementsByClassName("item-selector");

    var count = 0;
    for (let i = 0; i < item_selectors.length; i++) {
        const item = item_selectors[i];
        
        if(item.parentElement.parentElement.classList.contains("list-header"))
            continue; // short circuit

        if(item.checked) {
            count += 1;
            if(count > 1)
                break; // short circuit
        }
    }

    if(count == 0) {
        document.getElementsByClassName("edit-button")[0].setAttribute("disabled", '');
        document.getElementsByClassName("delete-button")[0].setAttribute("disabled", '');
    }
    else if(count == 1) {
        document.getElementsByClassName("edit-button")[0].removeAttribute("disabled");
        document.getElementsByClassName("delete-button")[0].removeAttribute("disabled");
    }
    else { // count > 1
        document.getElementsByClassName("edit-button")[0].setAttribute("disabled", '');
        document.getElementsByClassName("delete-button")[0].removeAttribute("disabled");
    }

    return count;
}


async function delete_action(object_name) {
    const items = document.getElementsByClassName("item-selector");
    const operations = [];

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if(item.checked) {
            const itemID = parseInt(item.parentElement.parentElement.getAttribute("data-id"));
            operations.push(client.common_remove(object_name, itemID));
        }
    }

    for (let i = 0; i < operations.length; i++) {
        const op = operations[i];
        await op;
    }

    window.location.reload();
}


/**
 * The entry point of the script.
 */
var client = new sasapi.Client();
document.addEventListener("DOMContentLoaded", () => {
    
    const delete_button = document.getElementsByClassName("delete-button")[0];
    const edit_button = document.getElementsByClassName("edit-button")[0];

    delete_button.setAttribute("disabled", "");
    delete_button.addEventListener("click", () => {
        delete_action(page_object_type);
    });

    edit_button.setAttribute("disabled", "");
    edit_button.addEventListener("click", () => {
        const items = document.getElementsByClassName("item-selector");

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if(item.checked) {
                const itemID = parseInt(item.parentElement.parentElement.getAttribute("data-id"));
                window.location.href = `/html/edit-${page_object_type}.html?id=${itemID}`;
            }
        }
    });

    client.connect("127.0.0.1", 8585);

    client.ws.onopen = async (evt) => {
        var items = [];

        switch (page_object_type) {
            case "template":
                items = await client.template_get();
                break;

            case "people":
                items = await client.people_get();
                break;

            case "rule":
                items = await client.rule_get();
                break;
        }

        fill_list(
            page_object_type,
            items,
            document.getElementsByClassName("list")[0]
        );
    }
});
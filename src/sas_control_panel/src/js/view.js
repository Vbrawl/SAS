
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
    if(is_header) checkbox.addEventListener("change", set_all_state);
    else checkbox.addEventListener("change", set_header_state)
    checkbox.addEventListener("change", set_action_buttons_state);
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
    if(is_header) checkbox.addEventListener("change", set_all_state);
    else checkbox.addEventListener("change", set_header_state)
    checkbox.addEventListener("change", set_action_buttons_state);
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
 * Create a DOM-element with the details of a rule.
 * @param {SendMessageRule} rule The rule object
 * @param {boolean} is_header When true the rule object is ignored and a header is generated.
 * @returns The generated object.
 */
function dom_rule_item(rule, is_header = false) {
    const item = document.createElement("div");
    item.classList.add("list-item-wrapper");
    if(!is_header) {item.setAttribute('data-id', rule.id);}
    else {item.classList.add("list-header");}

    const recipient_count = document.createElement("div");
    recipient_count.classList.add("recipient-count");
    recipient_count.textContent = is_header ? 'Recipient Count' : rule.recipients.length;

    const sep1 = document.createElement('span');
    sep1.classList.add("col");


    const start_date = document.createElement("div");
    start_date.classList.add("start-date");
    start_date.textContent = is_header ? "Start Date" : sasapi.date_to_string(rule.start_date);

    const sep2 = document.createElement('span');
    sep2.classList.add("col");

    const end_date = document.createElement("div");
    end_date.classList.add("end-date");
    end_date.textContent = is_header ? "End Date" : (rule.end_date ? sasapi.date_to_string(rule.end_date) : '');

    const sep3 = document.createElement('span');
    sep3.classList.add("col");

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
    else checkbox.addEventListener("change", set_header_state);
    checkbox.addEventListener("change", set_action_buttons_state);
    buttons.appendChild(checkbox);

    item.appendChild(recipient_count);
    item.appendChild(sep1);
    item.appendChild(start_date);
    item.appendChild(sep2);
    item.appendChild(end_date);
    item.appendChild(sep3);
    item.appendChild(buttons);
    return item;
}

function fill_with_rules(dom_element, rules) {
    dom_element.html = "";

    const header = dom_rule_item(null, true);
    dom_element.appendChild(header);

    for (let i = 0; i < rules.length; i++) {
        const rule = rules[i];
        const item = dom_rule_item(rule);
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


async function template_delete() {
    const items = document.getElementsByClassName("item-selector");
    const operations = [];

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if(item.checked) {
            const itemID = parseInt(item.parentElement.parentElement.getAttribute("data-id"));
            operations.push(client.template_remove(itemID));
        }
    }

    for (let i = 0; i < operations.length; i++) {
        const op = operations[i];
        await op;
    }

    window.location.reload();
}

async function people_delete() {
    const items = document.getElementsByClassName("item-selector");
    const operations = [];

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if(item.checked) {
            const itemID = parseInt(item.parentElement.parentElement.getAttribute("data-id"));
            operations.push(client.people_remove(itemID));
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
    
    // document.getElementsByClassName("delete-button")[0].addEventListener("click", template_delete);
    document.getElementsByClassName("delete-button")[0].addEventListener("click", people_delete);

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

        // fill_with_rules(
        //     document.getElementsByClassName("list")[0],
        //     await client.rule_get()
        // );
    }
});
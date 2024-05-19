let GETparams = new URLSearchParams(window.location.search);
let page_object_type = GETparams.get("object_type");
if(page_object_type == null) {page_object_type = "template";}



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
            const item_parent = item.parentElement.parentElement;
            if (item_parent.classList.contains("list-header")) {continue;}
            const itemID = parseInt(item_parent.getAttribute("data-id"));
            if(itemID !== null) {
                operations.push(client.common_remove(object_name, itemID));
            }
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
// Client is initialized in common.js
document.addEventListener("DOMContentLoaded", () => {

    document.getElementsByClassName("add-button")[0].parentElement.setAttribute("href", `/html/edit-${page_object_type}.html`);

    const dlist = new domlist.DOMList(document.getElementsByClassName("list")[0]);
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

    client.connect(async (evt) => {
        let temp_items = [];
        var items = [];

        switch (page_object_type) {
            case "template":
                temp_items = await client.template_get();
                items.push(new domlist.TemplateDOMListItem(null));
                for (let i = 0; i < temp_items.length; i++) {
                    const item_obj = temp_items[i];
                    items.push(new domlist.TemplateDOMListItem(item_obj));
                }
                break;

            case "people":
                temp_items = await client.people_get();
                items.push(new domlist.PeopleDOMListItem(null));
                for (let i = 0; i < temp_items.length; i++) {
                    const item_obj = temp_items[i];
                    items.push(new domlist.PeopleDOMListItem(item_obj));
                }
                break;

            case "rule":
                temp_items = await client.rule_get();
                items.push(new domlist.RuleDOMListItem(null));
                for (let i = 0; i < temp_items.length; i++) {
                    const item_obj = temp_items[i];
                    items.push(new domlist.RuleDOMListItem(item_obj));
                }
                break;
        }
        delete temp_items;

        dlist.add_items(items);
        dlist.render(set_action_buttons_state);
    });
});
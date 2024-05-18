



(function(domlist) {
    
    domlist.DOMListItem = class {
        constructor(obj) {
            this.obj = obj;
        }

        add_section(item, class_name, content) {
            const section = document.createElement("div");
            section.classList.add(class_name);
            section.textContent = content;

            item.appendChild(section);
        }

        add_colon(item) {
            const colon = document.createElement('span');
            colon.classList.add('col');

            item.appendChild(colon);
        }

        render(set_state__header, set_state__all, custom_handler = () => {}) {
            const is_header = this.obj === null;

            const item = document.createElement('div');
            item.classList.add('list-item-wrapper');
            if(is_header) {item.classList.add("list-header");}
            this.customize_item(item);

            this.add_colon(item);
            const buttons = document.createElement('div');
            buttons.classList.add("button-holder");

            if(is_header) {
                const button_label = document.createElement('div');
                button_label.classList.add('button-holder-label');
                button_label.textContent = "Select All";
                buttons.appendChild(button_label);
            }
            const checkbox = document.createElement('input');
            checkbox.classList.add('item-selector');
            checkbox.setAttribute('type', 'checkbox');
            if(is_header)
                {checkbox.addEventListener('change', set_state__all);}
            else
                {checkbox.addEventListener('change', set_state__header);}
            checkbox.addEventListener('change', custom_handler);

            buttons.appendChild(checkbox);
            item.appendChild(buttons);
            return item;
        }

        customize_item(item) {
            // NOTE: This is a virtual function and needs be implemented in subclasses.
            throw 'Virtual function not implemented in subclass.';
        }
    }

    domlist.DOMList = class {
        constructor(dom_element) {
            this.dom_element = dom_element;
            this.items = [];
        }

        add_item(item) {
            this.items.push(item);
        }

        add_items(items) {
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                this.add_item(item);
            }
        }

        render(custom_handler = () => {}) {
            this.dom_element.html = '';

            for (let i = 0; i < this.items.length; i++) {
                const item = this.items[i];
                this.dom_element.appendChild(item.render(
                    // NOTE: We use lambdas to keep the list as "this" inside the handlers.
                    (evt) => {this.set_state__header(evt);},
                    (evt) => {this.set_state__all(evt);},
                    (evt) => {custom_handler(evt);}));
            }
        }

        /**
         * Set all checkboxes to match the header's one.
         * @param {Event} evt The event object
         */
        set_state__all(evt) {
            const list_items = this.dom_element.getElementsByClassName("item-selector");
            const myState = evt.currentTarget.checked;

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
        set_state__header(evt) {
            const item_selectors = this.dom_element.getElementsByClassName("item-selector");

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
    }

    domlist.TemplateDOMListItem = class extends domlist.DOMListItem {
        customize_item(item) {
            const is_header = this.obj === null;
            if(!is_header) {item.setAttribute("data-id", this.obj.id);}

            this.add_section(item, "template-label", is_header ? "Label" : this.obj.label);
            this.add_colon(item);
            this.add_section(item, "template-message", is_header ? "Message" : this.obj.message);
        }
    }

    domlist.PeopleDOMListItem = class extends domlist.DOMListItem {
        customize_item(item) {
            const is_header = this.obj === null;
            if(!is_header) {item.setAttribute("data-id", this.obj.args.id);}

            this.add_section(item, "first-name", is_header ? "First Name" : this.obj.args.first_name);
            this.add_colon(item);
            this.add_section(item, "last-name", is_header ? "Last Name" : this.obj.args.last_name);
            this.add_colon(item);
            this.add_section(item, "telephone", is_header ? "Telephone" : this.obj.args.telephone);
            this.add_colon(item);
            this.add_section(item, "address", is_header ? "address" : this.obj.args.address);
        }
    }

    domlist.RuleDOMListItem = class extends domlist.DOMListItem {
        customize_item(item) {
            const is_header = this.obj === null;
            if(!is_header) {item.setAttribute("data-id", this.obj.id);}

            this.add_section(item, "rule-label", is_header ? "Label" : this.obj.label);
            this.add_colon(item);
            this.add_section(item, "recipient-count", is_header ? "Recipient Count" : this.obj.recipients.length);
            this.add_colon(item);
            this.add_section(item, "start-date", is_header ? "Start Date" : sasapi.date_to_string(this.obj.start_date));
            this.add_colon(item);
            this.add_section(item, "end-date", is_header ? "End Date" : (this.obj.end_date ? sasapi.date_to_string(this.obj.end_date) : ''));
        }
    }

}(window.domlist = window.domlist || {}));

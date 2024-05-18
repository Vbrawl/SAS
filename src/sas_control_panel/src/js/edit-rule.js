let GETparams = new URLSearchParams(window.location.search);
let page_object_id = GETparams.get("id");
page_object_id = (page_object_id ? parseInt(page_object_id) : null);

function parse_datetime(dom_date, dom_time) {
    const mDate = dom_date.value; // YYYY-MM-DD
    const mTime = dom_time.value; // HH:MM

    if(mDate === '' || mTime === '') {
        return null;
    }

    const datetime_string = mDate + ' ' + mTime + ':00.000'; // Add seconds and milliseconds
    return sasapi.date_from_string(datetime_string);
}

function parse_interval(dom_interval, dom_interval_unit) {
    const mInterval = parseInt(dom_interval.value); // number
    const mIntervalUnit = parseInt(dom_interval_unit.value); // 1-5

    var ret = mInterval;
    switch (mIntervalUnit) {
        case 1: // Days
            ret = ret * 24;
        case 2: // Hours
            ret = ret * 60;
        case 3: // Minutes
            ret = ret * 60;
    }

    return ret;
}

function fill_template_selector(template_selector, templates, selected_template_id = null) {
    /**
     * Fill template-selector (which is a <select>) with options
     */
    template_selector.innerHTML = '';
    for (let i = 0; i < templates.length; i++) {
        const template = templates[i];
        const option = document.createElement('option');
        option.value = template.id;
        option.textContent = (template.label !== '' ? template.label : template.message);

        if(selected_template_id === option.id) {option.setAttribute("selected", "");}
        template_selector.appendChild(option);
    }
}

const client = new sasapi.Client();
document.addEventListener('DOMContentLoaded', () => {
    const recipient_list = new domlist.DOMList(document.getElementById("recipient-selector"));

    document.getElementsByClassName("discard-button")[0].addEventListener("click", () => {
        window.location.reload();
    });

    document.getElementsByClassName("apply-button")[0].addEventListener("click", async () => {
        const label = document.getElementById("rule-label-text").value;
        const template = document.getElementById("template-selector").value;
        if(template === '') {
            alert("You need to select a template");
            return;
        }

        const start_at = parse_datetime(document.getElementById("start-input-date"), document.getElementById("start-input-time"));
        if(start_at === null) {
            alert("Start date/time is required.");
            return;
        }
        
        const end_at = parse_datetime(document.getElementById("end-input-date"), document.getElementById("end-input-time"));
        const interval = parse_interval(document.getElementById("interval"), document.getElementById("interval-unit"));
        const last_executed = parse_datetime(document.getElementById("lastexecuted-input-date"), document.getElementById("lastexecuted-input-time"));

        const checkboxes = document.getElementsByClassName("item-selector");
        const recipients = [];

        for (let i = 0; i < checkboxes.length; i++) {
            const checkbox = checkboxes[i];
            if(checkbox.checked) {
                recipients.push(parseInt(checkbox.parentElement.parentElement.getAttribute("data-id")));
            }
        }

        if(page_object_id === null) {
            const new_id = await client.rule_add(new sasapi.SendMessageRule(
                recipients,
                template,
                start_at,
                end_at,
                interval,
                last_executed,
                null,
                label
            ));
            GETparams.set("id", new_id);
            window.location.search = GETparams.toString();
        }
        else {
            await client.rule_alter(new sasapi.SendMessageRule(
                recipients,
                template,
                start_at,
                end_at,
                interval,
                last_executed,
                page_object_id,
                label
            ));
            window.location.reload();
        }
    });
    
    client.connect("127.0.0.1", 8585, async (evt) => {
        const people = await client.people_get();
        for (let i = 0; i < people.length; i++) {
            const person = people[i];
            recipient_list.add_item(new domlist.PeopleDOMListItem(person));
        }

        if(page_object_id !== null) {
            const rules = await client.rule_get(page_object_id, 1);
            
            if(rules.length != 0) {
                const rule = rules[0];
                
                document.getElementById("rule-label-text").value = rule.label;
                
                fill_template_selector(
                    document.getElementById("template-selector"),
                    await client.template_get(),
                    rule.template);

                document.getElementById("start-input-date").value = `${rule.start_date.getFullYear()}-${String(rule.start_date.getMonth()+1).padStart(2, '0')}-${String(rule.start_date.getDate()).padStart(2, '0')}`;
                document.getElementById("start-input-time").value = `${String(rule.start_date.getHours()).padStart(2, '0')}:${String(rule.start_date.getMinutes()).padStart(2, '0')}`;
                    
                if(rule.end_date !== null) {
                    document.getElementById("end-input-date").value = `${rule.end_date.getFullYear()}-${String(rule.end_date.getMonth()+1).padStart(2, '0')}-${String(rule.end_date.getDate()).padStart(2, '0')}`;
                    document.getElementById("end-input-time").value = `${String(rule.end_date.getHours()).padStart(2, '0')}:${String(rule.end_date.getMinutes()).padStart(2, '0')}`;
                }
                    
                // Decide unit
                var interval = rule.interval;
                var interval_unit = 4;
                if(Number.isInteger(interval / 60)) {
                    interval = interval / 60;
                    interval_unit = 3;
                    if(Number.isInteger(interval / 60)) {
                        interval = interval / 60;
                        interval_unit = 2;
                        if(Number.isInteger(interval / 24)) {
                            interval = interval / 24;
                            interval_unit = 1;
                        }
                    }
                }
                if(interval_unit === 4) {interval = 0; interval_unit = 1;}
                document.getElementById("interval").value = interval;
                document.getElementById("interval-unit").value = interval_unit;
                
                if(rule.last_executed !== null) {
                    document.getElementById("lastexecuted-input-date").value = `${rule.last_executed.getFullYear()}-${String(rule.last_executed.getMonth()+1).padStart(2, '0')}-${String(rule.last_executed.getDate()).padStart(2, '0')}`;
                    document.getElementById("lastexecuted-input-time").value = `${String(rule.last_executed.getHours()).padStart(2, '0')}:${String(rule.last_executed.getMinutes()).padStart(2, '0')}`;
                }

                for (let i = 0; i < rule.recipients.length; i++) {
                    const recipientID = rule.recipients[i];
                    for (let j = 0; j < recipient_list.items.length; j++) {
                        const item = recipient_list.items[j];
                        if(item.obj.args.id == recipientID) {
                            item.selected = true;
                        }
                    }
                }

            }
        }
        else {
            fill_template_selector(
                document.getElementById("template-selector"),
                await client.template_get());
        }
            
        recipient_list.render();
        });

    });
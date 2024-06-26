let GETparams = new URLSearchParams(window.location.search);
let page_object_id = GETparams.get("id");
page_object_id = (page_object_id ? parseInt(page_object_id) : null);


// Client is initialized in common.js
document.addEventListener("DOMContentLoaded", () => {
    document.getElementsByClassName("discard-button")[0].addEventListener("click", async () => {
        window.location.reload();
    });

    document.getElementsByClassName("apply-button")[0].addEventListener("click", async () => {
        const fname = document.getElementById("first-name-input").value;
        const lname = document.getElementById("last-name-input").value;
        const telephone = document.getElementById("telephone-input").value;
        const address = document.getElementById("address-input").value;

        if(page_object_id === null) {
            const new_id = await client.people_add(new sasapi.PersonTemplateArguments(
                telephone,
                null,
                fname,
                lname,
                address
            ));

            alert(new_id != null ? "New person added!" : "Person could not be saved.");
            if(new_id != null) {
                GETparams.set("id", new_id);
                window.location.search = GETparams.toString();
            }
        } else {
            const status = await client.people_alter(new sasapi.PersonTemplateArguments(
                telephone,
                page_object_id,
                fname,
                lname,
                address
            ));

            alert(status ? "Person saved!" : "Person could not be saved.");
            if(status) {window.location.reload();}
        }
    });

    client.connect(async (evt) => {
        if(page_object_id !== null) {
            const people = await client.people_get(page_object_id, 1);

            if(people.length != 0) {
                const person = people[0];
                document.getElementById("first-name-input").value = person.args.first_name;
                document.getElementById("last-name-input").value = person.args.last_name;
                document.getElementById("telephone-input").value = person.args.telephone;
                document.getElementById("address-input").value = person.args.address;
            }
        }
    });
});
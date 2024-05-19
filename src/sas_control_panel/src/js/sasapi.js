



(function(sasapi) {
    sasapi.DEFAULT_PROTOCOL = "ws";
    sasapi.DEFAULT_HOST = "127.0.0.1";
    sasapi.DEFAULT_PORT = 8585;

    sasapi.date_from_string = function(s) {
        const splits        = s.split(' ');
        const date          = splits[0].split('-');
        const time          = splits[1].split(':');
        const sms_splits    = time[2].split('.');

        const year          = date[0];
        const month         = date[1];
        const day           = date[2];

        const hour          = time[0];
        const minute        = time[1];
        const second        = sms_splits[0];
        const millisec      = sms_splits[1];

        return new Date(year, month - 1, day, hour, minute, second, millisec);
    }

    sasapi.date_to_string = function(d) {
        return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}.${d.getMilliseconds()}`;
    }


    sasapi.TemplateArguments = class {
        /**
         * @param {Array} args All keyword parameters should go here.
         */
        constructor(args = {}) {
            this.args = args;
        }
    }

    sasapi.PersonTemplateArguments = class extends sasapi.TemplateArguments {
        /**
         * @param {string} telephone 
         * @param {int} id 
         * @param {string} first_name 
         * @param {string} last_name 
         * @param {string} address 
         * @param {string} args 
         */
        constructor(telephone, id = null, first_name = null, last_name = null, address = null, args = {}) {
            super(args);
            this.args.telephone = telephone;
            if(id != null) this.args.id = id;
            if(first_name != null) this.args.first_name = first_name;
            if(last_name != null) this.args.last_name = last_name;
            if(address != null) this.args.address = address;
        }

        static fromJSON(data) {
            return new sasapi.PersonTemplateArguments(data.telephone, data.id, data.first_name, data.last_name, data.address, data);
        }
    }

    sasapi.Template = class {
        /** 
         * @param {string} message 
         * @param {int} id 
         */
        constructor(message, id = null, label = null) {
            this.id = id;
            this.label = label;
            this.message = message;
        }

        static fromJSON(data) {
            return new sasapi.Template(data.message, data.id, data.label);
        }
    }

    sasapi.SendMessageRule = class {
        /**
         * @param {Array<int>} recipients 
         * @param {int} template 
         * @param {Date} start_date 
         * @param {Date} end_date 
         * @param {int} interval Acts as timedelta (difference between times)
         * @param {Date} last_executed 
         * @param {int} id 
         */
        constructor(recipients, template, start_date, end_date = null, interval = 0, last_executed = null, id = null, label = null) {
            this.recipients = recipients;
            this.template = template;
            this.start_date = start_date;
            this.end_date = end_date;
            this.interval = interval;
            this.last_executed = last_executed;
            this.id = id;
            this.label = label;
        }


        static fromJSON(data) {
            return new sasapi.SendMessageRule(
                data.recipients,
                data.template,
                sasapi.date_from_string(data.start_date),
                data.end_date ? sasapi.date_from_string(data.end_date) : null,
                data.interval,
                data.last_executed ? sasapi.date_from_string(data.last_executed) : null,
                data.id,
                data.label
            );
        }
    }

    sasapi.ClientRequest = class {
        constructor(timeoutSeconds = 15) {
            this.promise = new Promise((resolve, reject) => {
                this._resolve = resolve;
                this._reject = reject;

                this.timeoutID = setTimeout(() => {
                    this.reject();
                }, timeoutSeconds * 1000) // x * second
            });
        }

        resolve(value) {
            clearTimeout(this.timeoutID);
            this._resolve(value);
        }

        reject(reason) {
            clearTimeout(this.timeoutID);
            this._reject(reason);
        }
    }

    sasapi.Client = class {
        constructor(username, password) {
            this.username = username;
            this.password = password;
            this.ws = null;
            this.requests = {};
        }

        /**
         * Generate a unique ID
         * @returns string
         */
        generateID() {
            return Math.random().toString();
        }

        /**
         * Connect to the API
         * @param {string} host The host of the API
         * @param {int} port The port to the API
         * @param {string} protocol Either "ws" or "wss"
         */
        connect(callback, host = null, port = null, protocol = null) {
            if(host === null) host = sasapi.DEFAULT_HOST;
            if(port === null) port = sasapi.DEFAULT_PORT;
            if(protocol === null) protocol = sasapi.DEFAULT_PROTOCOL;

            this.ws = new WebSocket(`${protocol}://${host}:${port}/`);
            this.ws.addEventListener("message", (evt) => {
                this.on_message(evt);
            });

            this.ws.addEventListener("open", callback);
        }

        /**
         * Close the connection to the API
         */
        close() {
            this.ws.close();
        }

        /**
         * That's a callback, shouldn't be called manually.
         */
        on_message(evt) {
            var msg = JSON.parse(evt.data);
            if(this.requests.hasOwnProperty(msg.id)) {
                this.requests[msg.id].resolve(msg);
                delete this.requests[msg.id];
            }
        }

        async send_and_wait(req) {
            const mid = this.generateID();
            req.id = mid;
            req.username = this.username;
            req.password = this.password;
            this.ws.send(JSON.stringify(req));

            const request = new sasapi.ClientRequest();
            this.requests[mid] = request;
            return await request.promise;
        }

        async common_get(object_converter, object_name, id = null, limit = null, offset = null) {
            const data = await this.send_and_wait({
                action: [object_name, 'get'],
                parameters: {
                    id: id,
                    limit: limit,
                    offset: offset
                }
            });

            // Convert to objects
            var res = [];
            for (let i = 0; i < data.results.length; i++) {
                const item = data.results[i];
                res.push(object_converter.fromJSON(item));
            }
            return res;
        }

        async common_add(object_name, params) {
            const resp = await this.send_and_wait({
                action: [object_name, "add"],
                parameters: params
            });

            return (resp.hasOwnProperty("added_id") ? resp.added_id : null);
        }

        async common_alter(object_name, params) {
            const resp = await this.send_and_wait({
                action: [object_name, "alter"],
                parameters: params
            });

            return resp.hasOwnProperty("status") && resp.status == "success";
        }

        async common_remove(object_name, id) {
            const resp = await this.send_and_wait({
                action: [object_name, "remove"],
                parameters: {
                    id: id
                }
            });

            return resp.hasOwnProperty("status") && resp.status == "success";
        }

        /**
         * Fetch a list of templates.
         * NOTE: To fetch all templates don't use any parameters.
         * @param {int} id The template's ID to receive.
         * @param {int} limit The maximum templates to return.
         * @param {int} offset The number of templates to skip when fetching.
         * @returns Array of Templates
         */
        async template_get(id = null, limit = null, offset = null) {
            return await this.common_get(sasapi.Template, "template", id, limit, offset);
        }

        async template_add(template) {
            return await this.common_add("template", {
                label: template.label,
                message: template.message
            });
        }

        async template_alter(template) {
            return await this.common_alter("template", {
                id: template.id,
                label: template.label,
                message: template.message
            });
        }

        async template_remove(id) {
            return await this.common_remove("template", id);
        }


        async people_get(id = null, limit = null, offset = null) {
            return await this.common_get(sasapi.PersonTemplateArguments, "people", id, limit, offset);
        }

        async people_add(person) {
            return await this.common_add("people", {
                first_name: person.args.first_name,
                last_name: person.args.last_name,
                telephone: person.args.telephone,
                address: person.args.address
            });
        }

        async people_alter(person) {
            return await this.common_alter("people", {
                id: person.args.id,
                first_name: person.args.first_name,
                last_name: person.args.last_name,
                telephone: person.args.telephone,
                address: person.args.address
            });
        }

        async people_remove(id) {
            return await this.common_remove("people", id);
        }

        async rule_get(id = null, limit = null, offset = null) {
            return await this.common_get(sasapi.SendMessageRule, "rule", id, limit, offset);
        }

        async rule_add(obj) {
            return await this.common_add("rule", {
                label: obj.label,
                template: obj.template,
                recipients: obj.recipients,
                start_date: sasapi.date_to_string(obj.start_date),
                end_date: obj.end_date === null ? null : sasapi.date_to_string(obj.end_date),
                interval: obj.interval,
                last_executed: obj.last_executed === null ? null : sasapi.date_to_string(obj.end_date)
            });
        }

        async rule_alter(obj) {
            return await this.common_alter("rule", {
                label: obj.label,
                id: obj.id,
                template: obj.template,
                recipients: obj.recipients,
                start_date: sasapi.date_to_string(obj.start_date),
                end_date: obj.end_date === null ? null : sasapi.date_to_string(obj.end_date),
                interval: obj.interval,
                last_executed: obj.last_executed === null ? null : sasapi.date_to_string(obj.last_executed)
            });
        }

        async rule_remove() {
            return await this.common_remove("rule", id);
        }

        async users_login() {
            var resp = await this.send_and_wait({
                action: ["users", "login"],
                parameters: {}
            });

            return (resp.hasOwnProperty("status") && resp.status === "success");
        }

        async users_alter(new_username, new_password) {
            return await this.common_alter("users", {
                new_username: new_username,
                new_password: new_password
            });
        }

        async timezone_get() {
            var resp = await this.send_and_wait({
                action: ["timezone", "get"],
                parameters: {}
            });

            if(resp.hasOwnProperty("timezone"))
                {return resp.timezone;}
        }

        async timezone_alter(timezone_identifier) {
            return await this.common_alter("timezone", {
                timezone: timezone_identifier
            })
        }
    }
}(window.sasapi = window.sasapi || {}))
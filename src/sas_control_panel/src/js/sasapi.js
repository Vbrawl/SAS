



(function(sasapi) {

    function date_from_string(s) {
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
            if(address != address) this.args.address = address;
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
        constructor(message, id = null) {
            this.id = id;
            this.message = message;
        }

        static fromJSON(data) {
            return new sasapi.Template(data.message, data.id);
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
        constructor(recipients, template, start_date, end_date = null, interval = null, last_executed = null, id = null) {
            this.recipients = recipients;
            this.template = template;
            this.start_date = start_date;
            this.end_date = end_date;
            this.interval = interval != null ? interval : new Date(0, 0, 0, 0, 0, 0, 0); // interval or null date.
            this.last_executed = last_executed;
            this.id = id;
        }


        static fromJSON(data) {
            return new sasapi.SendMessageRule(
                data.recipients,
                data.template,
                date_from_string(data.start_date),
                data.end_date ? date_from_string(data.end_date) : null,
                data.interval,
                data.last_executed ? date_from_string(data.last_executed) : null,
                data.id
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
        constructor() {
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
        connect(host, port, protocol = "ws") {
            this.ws = new WebSocket(`${protocol}://${host}:${port}/`);
            this.ws.onmessage = (evt) => {
                this.on_message(evt);
            };
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
            this.ws.send(JSON.stringify(req));

            const request = new sasapi.ClientRequest();
            this.requests[mid] = request;
            return await request.promise;
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
            const data = await this.send_and_wait({
                action: ["template", "get"],
                parameters: {
                    id: id,
                    limit: limit,
                    offset: offset
                }
            });

            // Convert everything to templates
            var res = [];
            for (let i = 0; i < data.results.length; i++) {
                const ptemplate = data.results[i];
                res.push(sasapi.Template.fromJSON(ptemplate));
            }
            return res;
        }

        template_add(template) {
            // TODO: Add template to the database
        }

        template_alter(template) {
            // TODO: Alter template in the database
        }

        template_remove(template) {
            // TODO: Remove template from the database
        }


        async people_get(id = null, limit = null, offset = null) {
            const data = this.send_and_wait({
                action: ["people", "get"],
                parameters: {
                    id: id,
                    limit: limit,
                    offset: offset
                }
            });

            // Convert to objects
            var res = [];
            for (let i = 0; i < data.results.length; i++) {
                const pperson = data.results[i];
                res.push(sasapi.PersonTemplateArguments.fromJSON(pperson));
            }
            return res;
        }

        people_add() {
            // TODO: Implement me
        }

        people_alter() {
            // TODO: Implement me
        }

        people_remove() {
            // TODO: Implement me
        }

        async rule_get(id = null, limit = null, offset = null) {
            const data = await this.send_and_wait({
                action: ["rule", "get"],
                parameters: {
                    id: id,
                    limit: limit,
                    offset: offset
                }
            });

            // Convert to objects
            var res = [];
            for (let i = 0; i < data.results.length; i++) {
                const prule = data.results[i];
                res.push(sasapi.SendMessageRule.fromJSON(prule))
            }
            return res;
        }

        rule_add() {
            // TODO: Implement me
        }

        rule_alter() {
            // TODO: Implement me
        }

        rule_remove() {
            // TODO: Implement me
        }
    }
}(window.sasapi = window.sasapi || {}))
# SAS (Send Automated SMS)
This is a micro-service daemon designed to send automated messages through the [Telnyx SMS Gateway](https://telnyx.com/) API.

## Tools
- python 3.12.3

## Features
- [Templates](#templates)
- [Send On Interval](#send-on-interval)
- [Send On Date](#send-on-date)


### Templates
Templates are pre-made messages with placeholder for automatically filling personalized info.

An example template would look like this:
```TEXT
Hello $(first_name),
I would like to ask you about some stuff.
Is this the correct address for your home?
$(address)

I wanted to send you a package, I will send it tomorrow.
I will also add your phone number to the package so please confirm.
$(phone_number)

Talk to you soon.
```

If the above was supposed to be sent to a person/client with the following details:
```JSON
{
    "first_name": "John",
    "address": "City, Street, 1",
    "phone_number": "+1 256 418 8575"
}
```

Then the final message would be:
```TEXT
Hello John,
I would like to ask you about some stuff.
Is this the correct address for your home?
City, Street, 1

I wanted to send you a package, I will send it tomorrow.
I will also add your phone number to the package so please confirm.
+1 256 418 8575

Talk to you soon.
```

### Send On Interval
This feature allows one to set a message to be sent every time between an interval.


### Send On Date
This feature allows one to set a message to be sent at a specific date and time.



# Extras
- To use this daemon on real-time data we would need to have some kind of interface, that's another application which will be designed in the future.

# License
This project is licensed under the [Apache License 2.0](./LICENSE)
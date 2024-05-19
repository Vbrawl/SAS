const cookie_parts = document.cookie.split('; ');
function getCookie(key) {
    key += '=';
    for (let i = 0; i < cookie_parts.length; i++) {
        const cookie_part = cookie_parts[i];
        if(cookie_part.startsWith(key)) {
            return cookie_part.substring(key.length);
        }
    }
}

var APP_USERNAME = getCookie("username");
var APP_PASSWORD = getCookie("password");

if(!APP_USERNAME || !APP_PASSWORD) {
    window.location = "/index.html";
}
else {
    APP_USERNAME = atob(APP_USERNAME);
    APP_PASSWORD = atob(APP_PASSWORD);
    var client = new sasapi.Client(APP_USERNAME, APP_PASSWORD);
}
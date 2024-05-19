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

const APP_USERNAME = getCookie("username");
const APP_PASSWORD = getCookie("password");

if(!APP_USERNAME || !APP_PASSWORD) {
    window.location = "/index.html";
}
else {
    var client = new sasapi.Client(atob(APP_USERNAME), atob(APP_PASSWORD));
}
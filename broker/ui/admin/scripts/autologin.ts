/**
 * Created by nibo on 2016-01-18.
 */
import "jquery";

var username = "root";
var password = "root";

function get_environment_data (){

    return {
        "hostname": null,
        "implementation": {
            "language": "javascript",
            "appCodeName": navigator.appCodeName,
            "appName": navigator.appName,
            "appVersion": navigator.appVersion,
            "cookieEnabled": navigator.cookieEnabled,
            "language": navigator.language,
            "platform": navigator.platform,
            "product": navigator.product,
            "userAgent": navigator.userAgent,
        },
        "platform": navigator.platform,
        "processor": null,
        "systemPid": null,
        "user": username,
    }

};

function postJSON(url, data, callback) {
    var settings: JQueryAjaxSettings;
    settings = {};
    settings.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    };
    settings.type = "post";
    settings.url = url;
    settings.data = JSON.stringify(data);
    settings.dataType = "json";
    settings.success = callback;
    return jQuery.ajax(settings);
};

export function auto_login(_callback){


    var data: any = {
        "credentials": {
            "usernamePassword": {
                "username": username,
                "password": password
            }
        },
        "environment": get_environment_data(),
        "peerType": "admin",
        "address": null
    };

    postJSON('/register', data, _callback());

};


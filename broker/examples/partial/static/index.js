/**
 * Created by nibo on 2015-03-17.
 */


document.cookie = "session_id=;expires=" + new Date(0).toGMTString();

function log_data(_data) {
    var dest = $("#log_output")[0];
    dest.textContent += "\n" + _data;
    dest.scrollTop = 999999;
}

function callMethod(method, data, callback) {
    var _line = "-----------------------------------";
    log_data("Method call " + method + ": client will send:\n" + JSON.stringify(data));
    $.ajax({
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        'type': 'POST',
        'url': method,
        'data': JSON.stringify(data),
        'dataType': 'json',
        'success': function (_data) {
            log_data("Method call " + method + ": Server returned:\n" + JSON.stringify(_data) + "\n" + _line);
            callback(_data);
        },
        'error': function (_error) {
            log_data("Method call " + method + ": Server returned error:\n" + JSON.stringify(_error));

        }
    });

}


function login() {
    callMethod(
        "node/login",
        {credentials: {usernamePassword: {username: "root", password: "root"}}},
        function (response) {
            $("#session_status")[0].textContent = "Logged in";
            $("#session_status_div")[0].style.backgroundColor = "#007020";
            $("#examples")[0].style.visibility = "visible";
            $("#please_login")[0].style.visibility = "hidden";

        }
    )
}


function logout() {
    callMethod(
        "node/logout",
        {},
        function (response) {
            $("#session_status")[0].textContent = "Logged out";
            $("#session_status_div")[0].style.backgroundColor = "#d55537";
            $("#examples")[0].style.visibility = "hidden";
            $("#please_login")[0].style.visibility = "visible";

        }
    )
}


function load_lookup(parentId, destinationId) {
    callMethod(
        "node/lookup",
        {conditions: {parent_id: parentId}, collection: "node"},
        function (response) {
            $("#" + destinationId)[0].options.length = 0;
            response.forEach(function (item) {
                var dest = $("#" + destinationId)[0];
                var option = document.createElement("option");
                option.value = item.value;
                option.text = item.text;
                dest.add(option);

            });
        }
    );
}


function load_sel_data(selectorId) {
    var _selectedId = $("#sel_" + selectorId)[0].value;
    if (_selectedId) {
        callMethod(
            "node/load_node",
            {_id: _selectedId},
            function (response) {
                $("#in_" + selectorId)[0].value = response["name"];
                var id = $("#id_" + selectorId)[0];
                id.textContent = response["_id"];
                id.nodeobj = response;
            }
        );
    }
    else {
        alert("You must select a node.")
    }
}


function delete_sel_node(selectorId) {
    var _selectedId = $("#sel_" + selectorId)[0].value;
    if (_selectedId) {
        callMethod(
            "node/remove",
            {_id: _selectedId},
            function (response) {
                $("#in_" + selectorId)[0].value = response["name"];
                var id = $("#id_" + selectorId)[0];
                id.textContent = "";
                id.nodeobj = null;
            }
        );
    }
    else {
        alert("You must select a node.")
    }
}

function save_sel_data(selectorId) {
    var _obj = $("#id_" + selectorId)[0].nodeobj;
    if (_obj) {
        _obj.name = $("#in_" + selectorId)[0].value;

        callMethod(
            "node/save",
            _obj
        );
    }
    else {
        alert("You must first load some data so that the system knows what node to update.");
    }
}

function reset_database(selectorId) {
    if (confirm("Are you sure you want to reset the database?") == true) {
        callMethod(
            "reset_database",
            {},
            function (response) {
                console.log("Reloading page after resetting database.");
                location.reload( true );

            }
        );
    }

}
var minichat_timer_delay = 30000;
var minichat_content;
var minichat_content_url;
var minichat_post_url;

var minichat_form = "#minichat_form";
var minichat_button = "#minichat_form button[type='submit']";
var minichat_input_text = "#minichat_form input[type='text']";
var minichat_chars_output = "#minichat_form .minichat-remainingChars";

var minichat_template = "minichat/latests.html";

function minichat_init_display(content, get_url) {
    minichat_content = content
    minichat_content_url = get_url;

    if (minichat_content) {
        setInterval(minichat_refresh_fallback, minichat_timer_delay);
        minichat_refresh();
        if (ws_client){
            ws_client.register('minichat', 'on_message', minichat_websocket_message_dispatch);
        }
    };

}

function minichat_refresh_fallback() {
    if (!ws_client || !ws_client.isConnected()){
        minichat_refresh();
    }
}

function minichat_websocket_message_dispatch(data) {
    switch(data.action) {
        case 'reload_minichat':
            minichat_refresh();
            break;
    }
}

function minichat_refresh() {
    $.get(minichat_content_url, function(data) {
        data_with_username = $.extend({ user: USERNAME }, data);
        $(minichat_content).html(nunjucks.render(minichat_template, data_with_username));
        replace_invalid_avatar($(minichat_content));
        activate_tooltips($(minichat_content));
    });
}

function minichat_init_post() {
    minichat_post_url = $(minichat_form).attr("action");

    $(minichat_button).click(
        function(e) {
            e.preventDefault();
            $(minichat_button).find('span').addClass('fa-spinner fa-spin');
            minichat_post_message();
        }
    );
}

function minichat_post_message() {
    $.post(minichat_post_url, $(minichat_form).serialize())
        .done(function(data) {
            if (data.substituted) {
                contrib_message("info", "Votre dernier message est devenu \"<em>"+ data.substituted.text +"</em>\".");
            }
            if (data.anchors.length > 0) {
                var beautified_users;
                if (data.anchors.length > 1) {
                    var users = data.anchors.join(', à ');
                    var comma = users.lastIndexOf(', à ');
                    beautified_users = users.substr(0, comma) + ' et' + users.substr(comma+1)
                } else {
                    beautified_users = data.anchors[0];
                }
                contrib_message("info", "Une notification a été envoyée à " + beautified_users + ".")
            }
            $(minichat_button).find('span').removeClass('fa-spinner fa-spin fa-warning btn-warning');
            $(minichat_input_text).val("");
            minichat_update_chars_count();
            minichat_refresh_fallback();
        })
        .fail(function(data) {
            $(minichat_button).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
            minichat_refresh_fallback();
        });
}

function minichat_update_chars_count() {
    var remaining = $(minichat_input_text).attr("maxlength") - $(minichat_input_text).val().length;
    var plural = "";
    if (remaining > 1) plural = "s";
    $(minichat_input_text).parent().toggleClass("has-warning", remaining == 0);
    $(minichat_chars_output).text(remaining + "  caractère"+plural+" restant"+plural);
}

function minichat_init_remaining_chars() {
    minichat_update_chars_count();
    $(minichat_input_text).change(minichat_update_chars_count);
    $(minichat_input_text).keyup(minichat_update_chars_count);
}

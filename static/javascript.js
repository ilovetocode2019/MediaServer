function copy(text) {
    var textarea = document.createElement("textarea");
    document.body.appendChild(textarea);
    textarea.value = text;
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
}

function confirmation(text) {
    confirmed = confirm(text);
    return confirmed;
}

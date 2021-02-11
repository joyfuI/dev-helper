"use strict";

const log_textarea = document.getElementById('log_textarea');
const delete_btn = document.getElementById('delete_btn');
const add_textarea = document.getElementById('add_textarea');
const clear_btn = document.getElementById('clear_btn');
const auto_scroll = document.getElementById('auto_scroll');

const socket = io.connect(`${location.origin}/log`);
socket.emit('start', {
    'package': log
});

socket.on('on_start', (data) => {
    log_textarea.value += data.data;
    log_textarea.scrollTop = log_textarea.scrollHeight;
});

socket.on('add', (data) => {
    if (data.package === log) {
        add_textarea.value += data.data;
        if (auto_scroll.checked) {
            add_textarea.scrollTop = add_textarea.scrollHeight;
        }
    }
});

clear_btn.addEventListener('click', (event) => {
    event.preventDefault();
    add_textarea.value = '';
});

delete_btn.addEventListener('click', (event) => {
    event.preventDefault();
    fetch(`/${package_name}/ajax/delete`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: new URLSearchParams({
            log: log
        })
    });
});

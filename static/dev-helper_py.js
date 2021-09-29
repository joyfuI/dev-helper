"use strict";

const install_btn = document.getElementById('install_btn');
const list_div = document.getElementById('list_div');
const modal_title = document.getElementById('modal_title');
const modal_body = document.getElementById('modal_body');

const showModal = ({data}) => {
    let str = '';
    for (const i of data.content) {
        str += `<div>${i}</div>`;
    }
    modal_title.innerHTML = data.title;
    modal_body.innerHTML = str;
    $('#large_modal').modal();
};

// 패키지 설치
install_btn.addEventListener('click', (event) => {
    event.preventDefault();
    const name = document.getElementById('package').value;
    if (name === '') {
        notify('패키지명을 입력하세요.', 'warning');
        return;
    }
    fetch(`/${package_name}/ajax/install`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: new URLSearchParams({
            name: name
        })
    }).then((response) => response.json()).then(showModal);
});

// 패키지 업데이트/제거
list_div.addEventListener('click', (event) => {
    event.preventDefault();
    const target = event.target;
    if (target.tagName !== 'BUTTON') {
        return;
    }
    let name = target.id;
    switch (target.textContent) {
        case '업데이트':
            name = name.replace(/_upgrade$/u, '');
            fetch(`/${package_name}/ajax/install`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: new URLSearchParams({
                    name: name
                })
            }).then((response) => response.json()).then(showModal);
            break;

        case '제거':
            name = name.replace(/_uninstall$/u, '');
            fetch(`/${package_name}/ajax/uninstall`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: new URLSearchParams({
                    name: name
                })
            }).then((response) => response.json()).then(showModal);
            break;
    }
});

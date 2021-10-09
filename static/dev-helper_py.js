'use strict';

const install_btn = document.getElementById('install_btn');
const list_div = document.getElementById('list_div');
const modal_title = document.getElementById('modal_title');
const modal_body = document.getElementById('modal_body');

const showModal = (ret) => {
    if (ret.msg) {
        notify(ret.msg, ret.ret);
    } else {
        let str = '';
        for (const i of ret.data.content) {
            str += `<div>${i}</div>`;
        }
        modal_title.innerHTML = ret.data.title;
        modal_body.innerHTML = str;
        $('#large_modal').modal();
    }
};

// 패키지 설치
install_btn.addEventListener('click', (e) => {
    e.preventDefault();
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
list_div.addEventListener('click', (e) => {
    e.preventDefault();
    const {target} = e;
    if (target.tagName !== 'BUTTON') {
        return;
    }

    switch (target.textContent) {
        case '업데이트':
            fetch(`/${package_name}/ajax/install`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: new URLSearchParams({
                    name: target.id.replace(/_upgrade$/u, '')
                })
            }).then((response) => response.json()).then(showModal);
            break;

        case '제거':
            fetch(`/${package_name}/ajax/uninstall`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: new URLSearchParams({
                    name: target.id.replace(/_uninstall$/u, '')
                })
            }).then((response) => response.json()).then(showModal);
            break;
    }
});

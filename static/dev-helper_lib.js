'use strict';

const ffmpeg_version_btn = document.getElementById('ffmpeg_version_btn');
const ffmpeg_git_btn = document.getElementById('ffmpeg_git_btn');
const ffmpeg_release_btn = document.getElementById('ffmpeg_release_btn');
const modal_title = document.getElementById('modal_title');
const modal_body = document.getElementById('modal_body');

// FFmpeg 버전확인
ffmpeg_version_btn.addEventListener('click', (e) => {
  e.preventDefault();
  fetch('/ffmpeg/ajax/ffmpeg_version', {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    },
  })
    .then((response) => response.json())
    .then((data) => {
      let str = '';
      for (const i of data) {
        str += `<div>${i}</div>`;
      }
      modal_title.innerHTML = 'ffmpeg -version';
      modal_body.innerHTML = str;
      $('#large_modal').modal();
    });
});

const success = ({ data }) => {
  if (!data.success) {
    notify(data.message, 'warning');
  }
};

// FFmpeg 업데이트 (git master)
ffmpeg_git_btn.addEventListener('click', (e) => {
  e.preventDefault();
  fetch(`/${package_name}/ajax/ffmpeg`, {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    },
    body: new URLSearchParams({
      type: 'git',
      name: ffmpeg_git,
    }),
  })
    .then((response) => response.json())
    .then(success);
});

// FFmpeg 업데이트 (release)
ffmpeg_release_btn.addEventListener('click', (e) => {
  e.preventDefault();
  fetch(`/${package_name}/ajax/ffmpeg`, {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    },
    body: new URLSearchParams({
      type: 'release',
      name: ffmpeg_release,
    }),
  })
    .then((response) => response.json())
    .then(success);
});

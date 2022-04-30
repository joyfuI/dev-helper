'use strict';

let origin_data = {};

$('.btn_db_edit').each((idx, element) => {
  $(element).on('click', () => {
    let db = $(element).attr('data-db');
    let table = $(element).attr('data-column');
    let row_num = $(element).attr('id').split('_')[
      $(element).attr('id').split('_').length - 1
    ];
    let target_data = tables[table][Number(row_num)];
    origin_data = target_data;
    let new_html = '';
    for (let [k, v] of Object.entries(target_data)) {
      new_html += `<div class='row' style="padding-top: 10px; padding-bottom: 10px; align-items: center;">
    <div class='col-sm-3 set-left'>
        <strong>${k}</strong>
    </div>
    <div class='col-sm-9'>
        <div class="input-group col-sm-9">
            <input id="column_${k}" name="column_${k}" type="text" class="form-control form-control-sm" value="${v}">
        </div>
    </div>
</div>`;
    }
    $('#modal-body').html(new_html);
    $('#db_edit_property_db').text(db);
    $('#db_edit_property_table').text(table);
    $('#modal_db_edit').modal('toggle');
  });
});

$('.btn_db_delete').click((event) => {
  let element = event.currentTarget;
  let db = $(element).attr('data-db');
  let table = $(element).attr('data-column');
  let row_num = $(element).attr('id').split('_')[
    $(element).attr('id').split('_').length - 1
  ];
  let target_data = tables[table][Number(row_num)];

  if (confirm(`정말 삭제하시겠습니까?\n${JSON.stringify(target_data)}`)) {
    $.ajax({
      url: `/${package_name}/ajax/delete_db`,
      type: 'POST',
      cache: false,
      data: {
        db: db,
        table: table,
        req_data: JSON.stringify(target_data),
      },
      dataType: 'json',
    })
      .done(() => {
        location.reload();
      })
      .fail((res) => {
        console.log(res);
      });
  }
});

$('#btn_edit_save').click(() => {
  let req_data = {};
  let rows = $('#modal-body').children();
  let db = $('#db_edit_property_db').text().trim();
  let table = $('#db_edit_property_table').text().trim();
  for (let row of rows) {
    let key = $($(row).children()[0]).children().text().trim();
    let val = $($($(row).children()[1]).children()[0])
      .children()
      .val()
      .trim();
    if (val === 'null') {
      val = null;
    }
    switch (val) {
      case 'null':
        val = null;
        break;
      case 'True':
        val = true;
        break;
      case 'False':
        val = false;
        break;
    }
    req_data[key] = val;
  }
  $.ajax({
    url: `/${package_name}/ajax/edit_db`,
    type: 'POST',
    cache: false,
    data: {
      db: db,
      table: table,
      origin_data: JSON.stringify(origin_data),
      req_data: JSON.stringify(req_data),
    },
    dataType: 'json',
  })
    .done(() => {
      location.reload();
    })
    .fail((res) => {
      console.log(res);
    });
});

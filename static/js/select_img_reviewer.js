/*$(function() {
  $('input[type=file]').after('<span></span>');
  // アップロードするファイルを選択
  $('input[type=file]').change(function() {
      var file = $(this).prop('files')[0];

      // 画像以外は処理を停止
      if (! file.type.match('image.*')) {
          // クリア
          $(this).val('');
          $('span').html('');
          return;
      }

      // 画像表示
      var reader = new FileReader();
      reader.onload = function() {
          var img_src = $('<img width="200">').attr('src', reader.result);
          $('span').html(img_src);
      }
      reader.readAsDataURL(file);
  });
});*/

// クラスcustom-file-inpuに変更があった場合に起動するイベントハンドラを設定
$('.custom-file-input').on('change', handleFileSelect);
function handleFileSelect(evt) {
    $('#preview').remove();// プレビューを削除
    
    // 後ろにコンテンツを追加
    $(this).parents('.input-group').after('<div id="preview"></div>');

    // ファイルを受け取る???
    var files = evt.target.files;

    // ファイルの数だけ繰り返す
    for (var i = 0, f; f = files[i]; i++) {
        var reader = new FileReader();// ファイルリーダー

        reader.onload = (function(theFile) {
            return function(e) {
                // 画像では画像のプレビューの表示
                if (theFile.type.match('image.*')) {
                    // var $html = ['<div class="d-inline-block mr-1 mt-1"><img class="img-thumbnail" src="', e.target.result,'" title="', escape(theFile.name), '" style="height:100px;" /><div class="small text-muted text-center">', escape(theFile.name),'</div></div>'].join('');
                    // var $html = ['<div class="row mt-2 align-items-center"><div class="col-md-4" style="background: #ff00ff"><div class="row justify-content-center"><img class="img-thumbnail" src="', e.target.result,'" title="', escape(theFile.name), '" style="width: auto; height: 200px;" /></div></div><div class="col-md-8"><div class="row" style="background: #00ff00"><div class="col-md-12"><h2>予想落札価格</h2></div></div><div class="row justify-content-center" style="background: #66ff66"><h1>？円</h1></div></div></div>'].join('');
                    var $html = ['<div class="d-inline-block mr-1 mt-1"><img class="img-thumbnail" src="', e.target.result,'" title="', escape(theFile.name), '" style="height: 128px;" /></div>'].join('');
                //画像以外はファイル名のみの表示
                } else {
                    var $html = ['<div class="d-inline-block mr-1"><span class="small">', escape(theFile.name),'</span></div>'].join('');
                }

                $('#preview').append($html);// preview内に追加
            };
        })(f);

        reader.readAsDataURL(f);
    }
    $(this).next('.custom-file-label').html(+ files.length + '個のファイルを選択しました');
}

//ファイルの取消
$('.reset').click(function(){
    $(this).parent().prev().children('.custom-file-label').html('画像を選択してね！');
    $('.custom-file-input').val('');
    $('#preview').remove('');
})

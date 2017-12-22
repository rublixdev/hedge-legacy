// Function for displaying confirmation modal
function confirmModal(title, msg, callback) {
  var dialog = $('#confirmModal');
  dialog
    .find('.modal-title').text(title).end()
    .find('.modal-body').html(msg).end()
    .find('.btn-ok').on('click', function() {
      $(this).off('click');
      dialog.modal('hide');
      if (typeof(callback) === 'function') {
        callback();
      }
    }).end()
    .modal('show');
}
  
$(document).ready(function() {

  // Signout link
  $('#signout').click(function(e) {
    e.preventDefault();
    $('#form-signout').submit();
  });

  // Auto close alert messages
  $(".alert:not(.admin-warning)").delay(5000).slideUp(200, function() {
    $(this).alert('close');
  });
  
});
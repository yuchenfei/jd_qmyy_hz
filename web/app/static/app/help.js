$(document).ready(function () {
    var clipboard = new ClipboardJS('.btn')
    clipboard.on('success', function (e) {
        alert('已复制到粘贴板')
        e.clearSelection()
    })

    $("#submit").click(function () {
        var report = $('#report').val()
        if (report) {
            $("#error").addClass('hide')
            $.ajax({
                url: $('#url').val(),
                type: 'post',
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
                },
                data: {
                    id_list: $('#id_list').val(),
                    report: $('#report').val()
                },
                success: function (response) {
                    console.log(response)
                    if (response.status === 'success') {
                        $("#info").addClass('hide')
                        $("#example").addClass('hide')
                        $("#submit").addClass('hide')
                        $("#alert").html(response.message)
                        $("#alert").removeClass('alert-danger')
                        $("#alert").addClass('alert-info')
                        $("#alert").removeClass('hide')
                        $("#home").removeClass('hide')
                    }
                    if (response.status === 'error') {
                        $("#alert").html(response.message)
                        $("#alert").removeClass('alert-info')
                        $("#alert").addClass('alert-danger')
                        $("#alert").removeClass('hide')
                    }
                }
            })
        } else {
            $("#error").html('请填写执行结果')
            $("#error").removeClass('hide')
        }
    })
})
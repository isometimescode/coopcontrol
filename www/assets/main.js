function updateItem(data) {
    console.log(data);
    $('#js-'+data.name+'-status').text(data.status_str);

    panel = $('#js-'+data.name+'-panel');

    offbutton = panel.find('.btn-off');
    offbutton.data('id',data.id);
    offbutton.find('.glyphicon-refresh-animate').fadeOut('slow');

    onbutton = panel.find('.btn-on');
    onbutton.data('id',data.id);
    onbutton.find('.glyphicon-refresh-animate').fadeOut('slow');

    if (data.status) {
        // item is on, so enable the off button
        panel.removeClass('panel-off');
        offbutton.removeClass('disabled');

        panel.addClass('panel-on');
        onbutton.addClass('disabled');
    } else {
        // item is off, so enable the on button
        panel.removeClass('panel-on');
        onbutton.removeClass('disabled');

        panel.addClass('panel-off');
        offbutton.addClass('disabled');
    }
}

function updateError(request, status, error) {
    console.log(request);
    message = request.responseJSON ? request.responseJSON.message : error;
    $('#js-alert-message').append('<br/>'+message);
    $('.alert').fadeIn('slow');
}

function makeRequestToUpdate(e) {
    // don't follow the href
    // show a "loading" animation and disable further clicking
    e.preventDefault();
    $(e.toElement).blur();
    $(e.toElement).find('.glyphicon-refresh-animate').fadeIn('slow');
    $(e.toElement).addClass('disabled');

    // make a call to the API to update the status
    $.when($.ajax({
        url: 'update/id/'+$(e.toElement).data('id')+"/",
        data: "status="+$(e.toElement).data('status-value'),
        type: "POST",
        success: updateItem,
        error: updateError
    }));
}

function toggleVideo(e) {
    if ($('#js-video-icon').hasClass('glyphicon-menu-right')) {
        $('#js-video-icon').removeClass('glyphicon-menu-right').addClass('glyphicon-menu-down');
        $('#js-video').fadeIn('slow');
    } else {
        $('#js-video-icon').removeClass('glyphicon-menu-down').addClass('glyphicon-menu-right');
        $('#js-video').fadeOut('fast');
    }
}

$(document).ready(function() {
    // submit an update on link/button click
    $('a[data-status-value]').click(makeRequestToUpdate);

    $('#js-toggle-video').click(toggleVideo);

    // close dropdown on mobile
    $(document).ready(function () {
      $(".navbar-nav .dropdown-menu li a").click(function(event) {
        $(".navbar-collapse").collapse('hide');
      });
    });

    // initial grab of the current status for each panel
    $.when($.getJSON('info/light/','',updateItem).fail(updateError),
        $.getJSON('info/door/','',updateItem).fail(updateError))
    .fail(function(){$('.glyphicon-refresh-animate')
        .removeClass('glyphicon-refresh-animate')
        .addClass('glyphicon-exclamation-sign')});
});

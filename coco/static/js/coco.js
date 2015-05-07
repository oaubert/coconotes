$(document).ready( function () {
    var player = $("#videoplayer")[0];
    document.player = player;

    function pad(n, x, b) {
        b = b || 10;
        var s = (x).toString(b);
        while (s.length < n) {
            s = "0" + s;
        }
        return s;
    }

    function getHMS(t) {
        var _totalSeconds = Math.abs(Math.floor(t));
        return {
            hours : Math.floor(_totalSeconds / 3600),
            minutes : (Math.floor(_totalSeconds / 60) % 60),
            seconds : _totalSeconds % 60,
            milliseconds: (t * 1000) % 1000
        };
    }

    function format_timestamp(t) {
        var _hms = getHMS(t),
            _res = '';
        if (_hms.hours) {
            _res += _hms.hours + ':';
        }
        _res += pad(2, _hms.minutes) + ':' + pad(2, _hms.seconds);
        if (false) {
            _res += "." + Math.floor(_hms.milliseconds / 100);
        }
        return _res;
    };

    $(player).on("pause", function () {
        $(".playbutton").css({ "-webkit-transform": "scale(1)" });
    }).on("play", function () {
        $(".playbutton").css({"-webkit-transform": "scale(-1)" });
    }).on("durationchange", function () {
        $(".totaltime").text(format_timestamp(player.duration));
    }).on("timeupdate", function () {
        $(".currenttime").text(format_timestamp(player.currentTime));
    });

    $(".Ldt-AnnotationsList-li").on("click", function (e) {
        e.preventDefault();
        player.currentTime = li.dataset.begin / 1000;
    });

    $(".playbutton").on("click", function () {
        console.log(this);
        if (player.paused) {
            player.play();
        } else {
            player.pause();
        }
    });
    $(".fullscreenbutton").on("click", function () {
        if (player.requestFullscreen) {
            player.requestFullscreen();
        } else if (player.mozRequestFullScreen) {
            player.mozRequestFullScreen();
        } else if (player.webkitRequestFullscreen) {
            player.webkitRequestFullscreen();
        }
    });

});

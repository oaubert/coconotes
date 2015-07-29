$(document).ready( function () {
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

    $(".tabnames li").on("click", function () {
        var tabname = Array.prototype.slice.call(this.classList).filter( function (s) { return s.indexOf("tab-") == 0; });
        if (tabname.length) {
            $(".tabcomponent .selected").removeClass("selected");
            $(".tabcomponent ." + tabname[0]).addClass("selected");
        }
    });

    var username = localStorage.getItem('mla-username') || "Anonyme";
    $("#username").val(username)
        .on("blur", function () {
            set_username($("#username").val());
        });
    function generateUuid () {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random()*16|0, v = c === 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
    }
    var user_uuid = localStorage.getItem('mla-uuid') || generateUuid();
    localStorage.setItem('mla-uuid', user_uuid);

    /* Customized metadataplayer configuration */
    IriSP.libFiles.defaultDir = "../../static/libs/";
    IriSP.widgetsDir = "../../static/metadataplayer";
    IriSP.language = "fr";

    var _config = {
        width : '100%',
        container : 'MiscControlsContainer',
        default_options: {
            metadata: metadata
        },
        css : IriSP.widgetsDir + '/LdtPlayer-core.css',
        widgets: [
            {
                type: "HtmlPlayer",
                video: metadata.video_url,
                container: "VideoContainer",
                width: '100%',
                url_transform: function(n) {
                    var elements = /(.+)\.(\w\w\w)$/.exec(n);
                    var videoname = null;
                    var v = document.createElement("video");
                    if (v && v.canPlayType && v.canPlayType("video/mp4")) {
                        videoname = elements[1] + ".mp4";
                    } else {
                        videoname = elements[1] + ".ogv";
                    }
                    return videoname;
                }
            },
            { type: "Slider",
              container: "ControlledVideoPlayer"
            },
            { type: "Controller",
              container: "VideoControlContainer",
              disable_annotate_btn: true,
              always_show_search: true,
              fullscreen_widget: '#VideoContainer'
            },
            {
                type: "SlidePreview",
                container: "SlidePreviewContainer",
                annotation_type: "Slides"
            },
            {
                type: "EnrichedPlan",
                container: "AnnotationsContainer",
                annotation_type: "Slides"
            },
            { type: "Trace",
              url: "http://comin-ocw.org/trace/",
              requestmode: "GET",
              default_subject: "comin"
            },
            { type: "Mediafragment"},
            { type: "Shortcuts"}
        ]
    }; //
    _myPlayer = new IriSP.Metadataplayer(_config);
    _myPlayer.on("trace-ready", function () {
        var tracer = tracemanager.get_trace("test");
        tracer.trace("PlayerStart", { url: document.URL });
        IriSP.jQuery(".TraceMe").on("mousedown mouseenter mouseleave", function(_e) {
            tracer.trace('Mdp_' + _e.type,
                         {
                             "widget": "coco",
                             "target": this.id
                         });
        });
        document.addEventListener("visibilitychange", function() {
            tracer.trace("VisibilityChange", {
                "state": document.visibilityState,
                "url": document.URL
            });
        });

    });
    document._myPlayer = _myPlayer;

    function find_widgets_by_type(typ) {
        if (_myPlayer.widgets) {
            return _myPlayer.widgets.filter(function (w) {
                return w.type == typ; });
        } else {
            return [];
        }
    }

    function set_username(u) {
        name = u;
        localStorage.setItem('mla-username', u);
        _myPlayer.config.username = u;
        // Find CreateAnnotation widget and update creator_name
        find_widgets_by_type("CreateAnnotation").forEach( function (w) { w.creator_name = u; });
        find_widgets_by_type("Quiz").forEach( function (w) { w.user = u; w.userid=user_uuid; w.creator_name = u;});
    };

    var get_tab_index = function (id) {
        var l = $("#tab > ul > li a").map(function (i, tab) { if (id == tab.getAttribute('href')) return i;});
        // Return 0 index if the id is not found
        return l[0] || 0;
    };

    /* Piwik */
    var _paq = _paq || [];
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
    (function() {
        var u="//comin-ocw.org/analytics/";
        _paq.push(['setTrackerUrl', u+'piwik.php']);
        _paq.push(['setSiteId', 1]);
        var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
        g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'piwik.js'; s.parentNode.insertBefore(g,s);
    })();
    /* Piwik */

    var splitter, splitter2;
    // Splitter between the Player/metadataplayer column and the tabs column
    splitter =  $("#main").touchSplit({ barPosition: .66,
                                        thickness: "22px",
                                        secondMin: 400 })
        .on("dragstart", function () {
            $(this).find(".splitter-bar").addClass("active");
        })
        .on("dragstop", function () {
            $(this).find(".splitter-bar").removeClass("active");
            // on_resize();
        });

    /*
    // Splitter between the video player and the rest of the metadataplayer
    splitter2 = $("#PlayerContainer").touchSplit({orientation:"vertical", topMin: 220});
    _myPlayer.on("widgets-loaded", function () {
        set_username(name);
        window.setTimeout(function () {
            on_resize();
        }, 500);
    });

    // Handle browser window resize
    $(window).on("resize", function () { on_resize(); });

     */
});
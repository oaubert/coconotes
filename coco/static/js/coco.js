
$(document).ready(function () {
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
        var tabname = Array.prototype.slice.call(this.classList).filter(function (s) { return s.indexOf("tab-") == 0; });
        if (tabname.length) {
            $(".tabcomponent .selected").removeClass("selected");
            $(".tabcomponent ." + tabname[0]).addClass("selected");
        }
    });

    function generateUuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    var user_uuid = localStorage.getItem('mla-uuid') || generateUuid();
    localStorage.setItem('mla-uuid', user_uuid);

    /* Customized metadataplayer configuration */
    IriSP.libFiles.defaultDir = "../../static/libs/";
    IriSP.widgetsDir = "../../static/metadataplayer";
    IriSP.language = metadata.lang || "fr";

    var _myPlayer,
        _config = {
        width : '100%',
        container : 'MiscControlsContainer',
        default_options: {
            metadata: metadata
        },
        css : IriSP.widgetsDir + '/LdtPlayer-core.css',
        widgets: [
            {
                type: "SlideVideoPlayer",
                mode: "pip",
                video: metadata.video_url,
                container: "VideoContainer",
                width: '100%',
                url_transform: function (n) {
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
            { type: "BarSlider",
              container: "BarSliderContainer"
            },
            { type: "CocoController",
              container: "VideoControlContainer",
              fullscreen_widget: '.videoplayer',
              width: '100%'
            },
            {
                type: "SlidePreview",
                container: "SlidePreviewContainer",
                annotation_type: "Slides"
            },
            {
                type: "CocoCreateAnnotation",
                container: "coco_annotation_input_widget",
                annotation_type: "Contributions",
                api_endpoint_template: "/api/v1/annotation_add",
                api_serializer: "ldt_annotate",
                api_method: 'POST'
            },
            {
                type: "EnrichedPlan",
                container: "PlanContainer",
                annotation_type: "Slides",
                annotation_types: [ "Contributions" ],
                show_controls: true,
                show_slides: false,
                show_teacher_notes: false,
                show_other_notes: false,
                show_own_notes: true,
                is_admin: metadata.is_admin
            },
            {
                type: "EnrichedPlan",
                container: "OwnAnnotationsContainer",
                annotation_type: "Slides",
                annotation_types: [ "Contributions" ],
                show_controls: true,
                show_slides: false,
                show_teacher_notes: false,
                show_other_notes: false,
                show_own_notes: true,
                is_admin: metadata.is_admin
            },
            {
                type: "EnrichedPlan",
                container: "GroupAnnotationsContainer",
                annotation_type: "Slides",
                annotation_types: [ "Contributions" ],
                show_controls: true,
                show_slides: false,
                show_teacher_notes: true,
                show_other_notes: true,
                show_own_notes: false,
                is_admin: metadata.is_admin
            },
            {
                type: "EnrichedPlan",
                container: "PublicAnnotationsContainer",
                annotation_type: "Slides",
                annotation_types: [ "Contributions" ],
                show_controls: true,
                show_slides: true,
                show_teacher_notes: false,
                show_other_notes: true,
                show_own_notes: false,
                is_admin: metadata.is_admin
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
        // Setup CSRF globally
        var csrftoken = Cookies.get('csrftoken');
        if (csrftoken !== undefined) {
            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            IriSP.jQuery.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }

        // Hook trace sensors
        tracer.trace("PlayerStart", { url: document.URL });
        IriSP.jQuery(".TraceMe").on("mousedown mouseenter mouseleave", function (_e) {
            tracer.trace('Mdp_' + _e.type,
                         {
                             "widget": "coco",
                             "target": this.id
                         });
        });
        document.addEventListener("visibilitychange", function () {
            tracer.trace("VisibilityChange", {
                "state": document.visibilityState,
                "url": document.URL
            });
        });

    });
    document._myPlayer = _myPlayer;

    _myPlayer.on("Annotation.create", function () {
        e.preventDefault();
        IriSP.jQuery('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load("/annotation/add/").appendTo('body').dialog({ width: "70%" });
    });

    _myPlayer.on("Annotation.edit", function (annotation_id) {
        IriSP.jQuery('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load("/annotation/" + annotation_id + "/edit/")
            .appendTo('body')
            .dialog({ width: "60%",
                      closeOnEscape: true,
                      dialogClass: "annotation_edit_popup",
                      modal: true,
                      position: { my: "top", at: "top" },
                      title: "Edition"
                    });
    });

    function find_widgets_by_type(typ) {
        if (_myPlayer.widgets) {
            return _myPlayer.widgets.filter(function (w) {
                return w.type == typ; });
        } else {
            return [];
        }
    }

    var get_tab_index = function (id) {
        var l = $("#tab > ul > li a").map(function (i, tab) { if (id == tab.getAttribute('href')) { return i; } });
        // Return 0 index if the id is not found
        return l[0] || 0;
    };

    /* Piwik */
    var _paq = _paq || [];
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
    (function () {
        var u = "//comin-ocw.org/analytics/";
        _paq.push(['setTrackerUrl', u + 'piwik.php']);
        _paq.push(['setSiteId', 1]);
        var d = document, g = d.createElement('script'), s = d.getElementsByTagName('script')[0];
        g.type = 'text/javascript'; g.async = true; g.defer = true; g.src = u + 'piwik.js'; s.parentNode.insertBefore(g, s);
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

    $(".videodetails").on("click touchstart", function (e) {
        e.stopPropagation();
        e.preventDefault();
        IriSP.jQuery('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load("/video/" + metadata.video_id + "/info/", function () {
                IriSP.jQuery(this).appendTo('body').dialog({
                    width: "60%",
                    closeOnEscape: true,
                    dialogClass: "video_info_popup",
                    modal: true,
                    position: { my: "center", at: "center" },
                    title: IriSP.jQuery(this).find("h4").text()
                });
            });
    });

});

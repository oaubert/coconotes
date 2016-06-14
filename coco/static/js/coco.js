
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

    var getAbsoluteUrl = (function() {
        var a;
        return function(url) {
            if (!a) { a = document.createElement('a'); }
            a.href = url;
            return a.href;
        };
    })();

    function generateUuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    var user_uuid = localStorage.getItem('mla-uuid') || generateUuid();
    localStorage.setItem('mla-uuid', user_uuid);

    function action_url(action, elementid) {
        switch (action) {
        case 'admin':
            return '/admin/coco/annotation/' + elementid;
            break;
        case 'edit':
            return "/annotation/" + elementid + "/edit/";
            break;
        case 'level':
            return "/annotation/" + elementid + "/level/";
            break;
        case 'add_annotation':
            return "/api/v1/annotation_add";
            break;
        case 'featured':
            return "/annotation/" + elementid + "/toggle/featured/";
            break;
        case 'public':
            return "/annotation/" + elementid + "/toggle/public/";
            break;
        case 'log':
        case 'quiz_log':
            return "/accounts/profile/log";
            break;
        }
        return "/annotation/" + elementid + "#broken_action_url";
    }
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
                mode: metadata.has_slides == false ? "videoonly" : "pip",
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
                type: "CocoCreateAnnotation",
                container: "coco_annotation_input_widget",
                annotation_type: "Notes",
                api_endpoint_template: action_url("add_annotation"),
                api_serializer: "ldt_annotate",
                api_method: 'POST',
                current_group: function () {
                    /* Return undefined if no shared tab is displayed, -1 if the public tab is displayed, else the group id */
                    return $(".tabnames .selected[data-group-id]").data('group-id');
                }
            },
            {
                type: "Quiz",
                container: "VideoContainer",
                session_id: generateUuid(),
                annotation_type: "Quiz",
                api_method: 'POST',
                analytics_api: action_url('quiz_log'),
                enable_add_question: false
            },
            {
                type: "EnrichedPlan",
                container: "PlanContainer",
                annotation_type: "Slides",
                annotation_types: [ "Notes" ],
                show_controls: true,
                show_slides: true,
                show_featured_notes: true,
                show_other_notes: false,
                show_own_notes: false,
                is_admin: metadata.is_admin,
                action_url: action_url,
                bar_container: "AnnotationBarContainer"
            },
            {
                type: "EnrichedPlan",
                container: "OwnAnnotationsContainer",
                annotation_type: "Slides",
                annotation_types: [ "Notes" ],
                show_controls: true,
                show_slides: false,
                show_featured_notes: false,
                show_other_notes: false,
                show_own_notes: true,
                is_admin: metadata.is_admin,
                action_url: action_url,
                flat_mode: true
            }
        ].concat($("[class^=tab-group]").map(function () {
            /* Generate 1 component by defined group */
            var gid = this.dataset.groupId;
            return {
                type: "EnrichedPlan",
                container: "Group" + gid + "AnnotationsContainer",
                annotation_type: "Slides",
                group: gid,
                annotation_types: [ "Notes" ],
                show_controls: true,
                show_slides: false,
                show_featured_notes: true,
                show_other_notes: true,
                show_own_notes: true,
                flat_mode: true,
                is_admin: metadata.is_admin,
                action_url: action_url
            };
        }).toArray(), [
            {
                type: "EnrichedPlan",
                container: "PublicAnnotationsContainer",
                annotation_type: "Slides",
                annotation_types: [ "Notes", "Quiz" ],
                group: -1,
                show_controls: true,
                show_slides: true,
                show_featured_notes: true,
                show_other_notes: true,
                show_own_notes: true,
                flat_mode: true,
                is_admin: metadata.is_admin,
                action_url: action_url
            },
            { type: "Trace",
              url: getAbsoluteUrl("/trace/"),
              requestmode: "POST",
              default_subject: metadata.username || user_uuid
            },
            { type: "Mediafragment"},
            { type: "Shortcuts"}
        ])
    }; //
    _myPlayer = new IriSP.Metadataplayer(_config);
    function find_widgets_by_type(typ) {
        if (_myPlayer.widgets) {
            return _myPlayer.widgets.filter(function (w) {
                return w.type == typ; });
        } else {
            return [];
        }
    }

    _myPlayer.on("trace-ready", function () {
        var tracer = tracemanager.get_trace("test");

        find_widgets_by_type("CocoController")[0].onMediaEvent("play", function (e) {
            var media = this;
            IriSP.jQuery.ajax({
                url: action_url("log"),
                timeout: 2000,
                type: "POST",
                contentType: 'application/json',
                data: JSON.stringify({ action: "played",
                                       object: media.id,
                                       time: media.currentTime.milliseconds }),
                dataType: 'json'});
            return false;
        });
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
        $(".TraceMe").on("mousedown mouseenter mouseleave", function (_e) {
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

    $(".tabnames li").on("click", function () {
        var tabname = Array.prototype.slice.call(this.classList).filter(function (s) { return s.indexOf("tab-") == 0; });
        if (tabname.length) {
            $(".tabcomponent .selected").removeClass("selected");
            $(".tabcomponent ." + tabname[0]).addClass("selected");
            find_widgets_by_type("CocoCreateAnnotation")[0].set_placeholder(this.dataset.placeholder);
        }
    });

    var tablabels = $(".tabnames")[0];
    function check_tablabels_overflow() {
        if (tablabels.offsetHeight + 10 < tablabels.scrollHeight || tablabels.offsetWidth + 10 < tablabels.scrollWidth) {
            // There is an overflow
            $(".tabnames_overflow_indicator").addClass("overflowing");
        } else {
            $(".tabnames_overflow_indicator").removeClass("overflowing");
        }
    }

    _myPlayer.on("Annotation.create", function () {
        e.preventDefault();
        IriSP.jQuery('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load("/annotation/add/").appendTo('body').dialog({width: "60%"});
    });

    _myPlayer.on("Annotation.edit", function (annotation_id) {
        var edit_url = action_url('edit', annotation_id);
        IriSP.jQuery('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load(edit_url, function () {
                function validate(dialog) {
                    var formdata = IriSP.jQuery(dialog).find("form").serializeArray();
                    /* We know we do not have multiple attributes with the same name */
                    var data = IriSP._.object(IriSP._.pluck(formdata, 'name'), IriSP._.pluck(formdata, 'value'));
                    IriSP.jQuery.ajax({
                        url: edit_url,
                        timeout: 5000,
                        type: "POST",
                        contentType: 'application/json',
                        data: JSON.stringify(data),
                        dataType: 'json',
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            alert("An error has occurred making the request: " + errorThrown);
                        },
                        success: function(data) {
                            IriSP.jQuery(dialog).dialog("close");
                            // Get the modified annotation
                            var a = _myPlayer.sourceManager.getElement(annotation_id);
                            // Update its content according to the returned data
                            a.source.deSerialize(data);
                            _myPlayer.trigger("AnnotationsList.refresh");
                        }
                    });
                };
                IriSP.jQuery(this).appendTo('body')
                    .dialog({
                        width: "60%",
                        closeOnEscape: true,
                        dialogClass: "annotation_edit_popup",
                        modal: true,
                        position: { my: "top", at: "top" },
                        title: "Edition",
                        open: function() {
                            var dialog = this;
                            // On open, hide the original submit button
                            IriSP.jQuery(this).find("[type=submit]").hide();
                            $(dialog).keypress(function(e) {
                                if (e.ctrlKey && (e.keyCode == $.ui.keyCode.ENTER || e.keyCode == 10)) {
                                    e.preventDefault();
                                    validate(dialog);
                                }
                            });
                        },
                        buttons: [
                            {
                                text: "Save",
                                click: function () {
                                    validate(this);
                                }
                            },
                            {
                                text: "Close",
                                click: function () {
                                    IriSP.jQuery(this).dialog("close");
                                }
                            },
                            {
                                text: "Delete",
                                click: function () {
                                    var dialog = this;
                                    // Delete annotation
                                    IriSP.jQuery.ajax({
                                        url: edit_url,
                                        timeout: 5000,
                                        type: "DELETE",
                                        dataType: 'json',
                                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                                            alert("An error has occurred making the request: " + errorThrown);
                                        },
                                        success: function(data) {
                                            IriSP.jQuery(dialog).dialog("close");
                                            var a = _myPlayer.sourceManager.getElement(annotation_id);
                                            a.source.getAnnotations().removeElement(a);
                                            _myPlayer.trigger("AnnotationsList.refresh");
                                        }
                                    });
                                }
                            }
                        ]
                    });
            });
    });

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

    var splitter;
    if ($(window).width() > 640) {
        // Splitter between the Player/metadataplayer column and the tabs column
        splitter =  $("#main").touchSplit({ barPosition: .66,
                                            thickness: "22px",
                                            secondMin: 400 })
            .on("dragstart", function () {
                $(this).find(".splitter-bar").addClass("active");
            })
            .on("dragstop", function () {
                $(this).find(".splitter-bar").removeClass("active");
                check_tablabels_overflow();
            });
        check_tablabels_overflow();
    };

    $(window).on("resize", function () {
        check_tablabels_overflow();
    });
    function popup_tabconfig_dialog() {
        $('<div/>', {'class': 'tabconfig-form-dialog', 'id': IriSP.generateUuid() })
            .load("/accounts/profile/tabconfig/form", function () {
                $(this).appendTo('body').dialog({
                    width: "60%",
                    closeOnEscape: true,
                    dialogClass: "tabconfig_popup",
                    modal: true,
                    position: { my: "center", at: "center" },
                    open: function() {
                        var dialog = this;
                        // On open, hide the original submit button
                        $(this).find("[type=submit]").hide();
                        $('.ui-widget-overlay').on('click', function () {
                            $(dialog).dialog('close');
                        });
                    },
                    buttons: [
                        {
                            text: "Validate",
                            click: function () {
                                var dialog = $(this);
                                var form = $(dialog).find("form");
                                $.ajax({
                                    type: form.attr("method"),
                                    url: form.attr("action"),
                                    cache: false,
                                    data: form.serialize(),
                                    timeout: 5000,
                                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                                        // FIXME: shoudl report error
                                        dialog.dialog("close");
                                    },
                                    success: function (data) {
                                        dialog.dialog("close");
                                        location.reload();
                                    }
                                });
                            }
                        },
                        {
                            text: "Close",
                            click: function () {
                                $(this).dialog("close");
                            }
                        }
                    ]
                });
            });
    }

    $(".tabnames_overflow_indicator").on("click", popup_tabconfig_dialog);
    _myPlayer.on("Player.tabconfig", popup_tabconfig_dialog);

    $(".playertitle").on("click touchstart", function (e) {
        e.stopPropagation();
        e.preventDefault();
        $('<div/>', {'class': 'element-form-dialog', 'id': IriSP.generateUuid() })
            .load("/video/" + metadata.video_id + "/info/", function () {
                $(this).appendTo('body').dialog({
                    width: "60%",
                    closeOnEscape: true,
                    dialogClass: "video_info_popup",
                    modal: true,
                    position: { my: "center", at: "center" },
                    title: $(this).find("h4").text(),
                    open: function() {
                        var dialog = this;
                        $('.ui-widget-overlay').on('click', function () {
                            $(dialog).dialog('close');
                        });
                    }
                });
            });
    });
    _myPlayer.on("Player.tweet", function () {
        var title = $(".videotitle").text();
        var mf = find_widgets_by_type("Mediafragment");
        if (mf.length) {
            // Update URL
            mf[0].setHashToTime();
        }
        var el = $(".Ldt-EnrichedPlan-Selected-Timecode");
        if (el.length) {
            title = el.find(".Ldt-EnrichedPlan-Note-Text").text();
            mf[0].setHashToAnnotation({
                id: el[0].dataset.id,
                begin: el[0].dataset.timecode
            });
        } else {
            mf[0].setHashToTime();
        }
        var twitter_param = $.param({
            url: document.location.href,
            text: IriSP.textFieldHtml(title) + ' #COCoNotes'
        });
        window.open("https://twitter.com/intent/tweet?" + twitter_param);
    });

    $('.profilemenu_help_usage').on("click", function () {
        $("#profilemenu_help_menu")[0].checked = false;
        $(".player_usage").dialog({
            width: "60%",
            closeOnEscape: true,
            dialogClass: "video_info_popup",
            modal: true,
            position: { my: "center", at: "center" },
            title: "Usage",
            open: function() {
                var dialog = this;
                $('.ui-widget-overlay').on('click', function () {
                    $(dialog).dialog('close');
                });
            }
        });
    });
});

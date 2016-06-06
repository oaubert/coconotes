IriSP.Widgets.EnrichedPlan = function (player, config) {
    var _this = this;
    IriSP.Widgets.Widget.call(this, player, config);
    this.throttledRefresh = IriSP._.throttle(function (full) {
        _this.update_content();
    }, 800, {leading: false});

};

IriSP.Widgets.EnrichedPlan.prototype = new IriSP.Widgets.Widget();

IriSP.Widgets.EnrichedPlan.prototype.messages = {
    en: {
        delete_annotation: "Delete note",
        confirm_delete_message: "You are about to delete {{ annotation.title }}. Are you sure you want to delete it?",
        featured_notes: "Featured notes",
        toggle_featured: "Toggle featured state",
        other_notes: "Other Notes",
        own_notes: "Pers. notes",
        quiz_notes: "Quiz questions",
        popup_tabconfig: "Configure tab display",
        slides: "Slides",
        search: "Search...",
        whole_video: "Whole video"
    },
    fr: {
        delete_annotation: "Supprimer la note",
        confirm_delete_message: "Vous allez supprimer {{ annotation.title }}. Êtes-vous certain(e) ?",
        featured_notes: "Notes Promues",
        toggle_featured: "Dé/promouvoir",
        other_notes: "Notes Autres",
        own_notes: "Notes perso.",
        quiz_notes: "Questions de quiz",
        popup_tabconfig: "Configurer les onglets",
        slides: "Diapo",
        search: "Recherchez...",
        whole_video: "Vidéo entière"
    }
};

IriSP.Widgets.EnrichedPlan.prototype.defaults = {
    // Main type for toc segmentation
    annotation_type: "Slides",
    // If no annotation type list is specified, use all other types
    annotation_types: [],
    show_controls: true,
    show_slides: true,
    show_featured_notes: true,
    show_other_notes: true,
    show_own_notes: true,
    show_quiz_notes: false,
    is_admin: false,
    flat_mode: false,
    /* Group is either a group id, or -1 for public notes */
    group: undefined,
    // action_url should be a function (action, elementid) that returns a URL
    // Possible actions: admin, edit, level, public, featured
    action_url: function (action, elementid) { return ""; },
    bar_container: undefined
};

IriSP.Widgets.EnrichedPlan.prototype.template =
      '<div class="Ldt-EnrichedPlan-Container {{#flat_mode}}Ldt-EnrichedPlan-FlatMode{{/flat_mode}}">'
    + '<div class="Ldt-EnrichedPlan-Content"></div>'
    + '<form class="Ldt-EnrichedPlan-Controls">'
    + '{{#show_controls}}'
    + '<div class="Ldt-EnrichedPlan-ControlMenu">'
    + ' <label for="{{ prefix }}control_menu" class="Ldt-EnrichedPlan-Toggle"></label>'
    + ' <input type="checkbox" class="Ldt-EnrichedPlan-ControlMenuHome" id="{{ prefix }}control_menu"/>'
    + '<ul>'
    + ' <li class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Tabconfig">{{l10n.popup_tabconfig}}</li>'
    + ' <li>'
    + '  <input id="{{prefix}}featured_note_checkbox" class="Ldt-EnrichedPlan-Control-Checkbox Ldt-EnrichedPlan-Note-Featured" {{#show_featured_notes}}checked{{/show_featured_notes}} type="checkbox">'
    + '  <label for="{{prefix}}featured_note_checkbox" class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Note-Featured">{{ l10n.featured_notes }}</label>'
    + ' </li>'
    + ' <li>'
    + '  <input id="{{prefix}}other_note_checkbox" class="Ldt-EnrichedPlan-Control-Checkbox Ldt-EnrichedPlan-Note-Other" {{#show_other_notes}}checked{{/show_other_notes}} type="checkbox">'
    + '  <label for="{{prefix}}other_note_checkbox" class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Note-Other">{{ l10n.other_notes }}</label>'
    + ' </li>'
    + ' <li>'
    + '  <input id="{{prefix}}own_notes_checkbox" class="Ldt-EnrichedPlan-Control-Checkbox Ldt-EnrichedPlan-Note-Own" {{#show_own_notes}}checked{{/show_own_notes}} type="checkbox">'
    + '  <label for="{{prefix}}own_notes_checkbox" class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Note-Own">{{ l10n.own_notes }}</label>'
    + ' </li>'
    + ' <li>'
    + '  <input id="{{prefix}}quiz_notes_checkbox" class="Ldt-EnrichedPlan-Control-Checkbox Ldt-EnrichedPlan-Note-Quiz" {{#show_quiz_notes}}checked{{/show_quiz_notes}} type="checkbox">'
    + '  <label for="{{prefix}}quiz_notes_checkbox" class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Note-Quiz">{{ l10n.quiz_notes }}</label>'
    + ' </li>'
    + '{{^flat_mode}}'
    + ' <li>'
    + '  <input id="{{prefix}}slide_display_checkbox" class="Ldt-EnrichedPlan-Control-Checkbox Ldt-EnrichedPlan-Slide-Display" {{#show_slides}}checked{{/show_slides}} type="checkbox">'
    + '  <label for="{{prefix}}slide_display_checkbox" class="Ldt-EnrichedPlan-Control-Label Ldt-EnrichedPlan-Slide-Display">{{ l10n.slides }}<br/>&nbsp;</label>'
    + ' </li>'
    + '{{/flat_mode}}'
    + ' </ul>'
    + '</li>'
    + '</ul>'
    + '</div>'
    + '{{/show_controls}}'
    + '<input class="Ldt-EnrichedPlan-Search-Input {{^show_controls}}Ldt-EnrichedPlan-Search-Input-Full{{/show_controls}}" type="search" incremental placeholder="{{ l10n.search }}"/>'
    + '</form>'
    + '</div>';

IriSP.Widgets.EnrichedPlan.prototype.barTemplate =
    '<div class="Ldt-EnrichedPlan-BarContainer"></div>';

IriSP.Widgets.EnrichedPlan.prototype.slideTemplate =
      '<div data-id="{{ id }}" class="Ldt-EnrichedPlan-Slide">'
    + '  <div class="Ldt-EnrichedPlan-SlideItem Ldt-EnrichedPlan-SlideTimecode">{{ begin }}</div>'
    + '  <div data-timecode="{{begintc}}" class="Ldt-EnrichedPlan-SlideItem {{^show_slides}}filtered_out{{/show_slides}} Ldt-EnrichedPlan-SlideThumbnail Ldt-EnrichedPlan-Slide-Display">{{#thumbnail}}<img title="{{ begin }} - {{ atitle }}" src="{{ thumbnail }}">{{/thumbnail}}</div>'
    + '  <div class="Ldt-EnrichedPlan-SlideContent">'
    + '     <div data-timecode="{{begintc}}" class="Ldt-EnrichedPlan-SlideTitle Ldt-EnrichedPlan-SlideTitle{{ level }}" data-level="{{level}}">{{#is_admin}}<div class="adminactions"><a target="_blank" href="{{ admin_url }}" class="editelement">&#x270f;</a> <a data-id="{{id}}" target="_blank" class="level_decr">&nbsp;&lt;&nbsp;</a> <a data-id="{{id}}" target="_blank" class="level_incr">&nbsp;&gt;&nbsp;</a></div>{{/is_admin}}{{ atitle }}</div>'
    + '     <div class="Ldt-EnrichedPlan-SlideNotes">{{{ notes }}}</div>'
    + '  </div>'
    + '</div>';

IriSP.Widgets.EnrichedPlan.prototype.slideBarTemplate =
      '<div data-id="{{ id }}" data-timecode="{{begintc}}" data-level="{{level}}" title="{{begin}} - {{atitle}}" style="left: {{position}}%" class="Ldt-EnrichedPlan-Bar-Slide Ldt-EnrichedPlan-Slide-Display Ldt-EnrichedPlan-Bar-Slide{{ level }}">'
    + '</div>';

IriSP.Widgets.EnrichedPlan.prototype.annotationTemplate = '<div title="{{ begin }} - {{ atitle }}" data-id="{{ id }}" data-timecode="{{begintc}}" class="Ldt-EnrichedPlan-SlideItem Ldt-EnrichedPlan-Note {{category}} {{filtered}} Ldt-EnrichedPlan-{{visibility}} {{#featured}}Ldt-EnrichedPlan-Note-Featured{{/featured}}"><div class="Ldt-EnrichedPlan-NoteTimecode">{{ begin }}</div><a class="Ldt-EnrichedPlan-Note-Link" href="{{ url }}"><span class="Ldt-EnrichedPlan-Note-Text">{{{ text }}}</span></a> <span class="Ldt-EnrichedPlan-Note-Author">{{ author }}</span> {{#can_edit}}<span class="Ldt-EnrichedPlan-EditControl">{{#is_admin}}<span data-id="{{id}}" title="{{l10n.toggle_featured}}" class="Ldt-EnrichedPlan-EditControl-Featured"></span>{{/is_admin}}<span data-id="{{id}}" class="Ldt-EnrichedPlan-EditControl-Edit"></span></span>{{/can_edit}}{{#is_admin}}<div class="adminactions"> <a target="_blank" data-id="{{id}}" href="{{ admin_url }}" class="editelement">&#x270f;</a></div>{{/is_admin}}</div>';

IriSP.Widgets.EnrichedPlan.prototype.annotationBarTemplate = '<div title="{{ begin }} - {{ atitle }}" data-id="{{ id }}" data-timecode="{{begintc}}" style="left: {{position}}%" class="Ldt-EnrichedPlan-Bar-Note {{category}} {{filtered}} {{#featured}}Ldt-EnrichedPlan-Note-Featured{{/featured}}"></div>';


/**
 * Initialize the component
 */
IriSP.Widgets.EnrichedPlan.prototype.init_component = function () {
    var _this = this;
    _this.bar = undefined;

    // Get slides here so that it correctly initializes implicit
    // flat_mode if necessary (see template)
    var _slides = this.get_slides();

    // Generate a unique prefix, so that ids of input fields
    // (necessary for label association) are unique too.
    _this.prefix = IriSP.generateUuid();
    _this.renderTemplate();
    if (_this.bar_container) {
        // Container for the annotation bar
        _this.bar = IriSP.jQuery(_this.templateToHtml(_this.barTemplate));
        IriSP.jQuery("#" + _this.bar_container).append(_this.bar);
    }
    _this.container = _this.$.find('.Ldt-EnrichedPlan-Container');
    _this.content = _this.$.find('.Ldt-EnrichedPlan-Content');

    function go_to_timecode() {
        _this.media.setCurrentTime(Number(this.dataset.timecode));
        IriSP.jQuery(".Ldt-EnrichedPlan-Selected-Timecode").removeClass("Ldt-EnrichedPlan-Selected-Timecode");
        IriSP.jQuery(this).addClass("Ldt-EnrichedPlan-Selected-Timecode");
    };
    _this.container.on("click", "[data-timecode]", go_to_timecode);
    if (_this.bar) {
        _this.bar.on("click", "[data-timecode]", go_to_timecode);
    }

    _this.container.on("click", ".Ldt-EnrichedPlan-Tabconfig", function () {
        _this.player.trigger("Player.tabconfig");
    });

    _this.container.on("click", ".Ldt-EnrichedPlan-Control-Checkbox", function () {
        var classname = _.first(_.filter(this.classList, function (s) {
            return s != "Ldt-EnrichedPlan-Control-Checkbox";
        }));
        if (classname !== undefined) {
            if (IriSP.jQuery(this).is(':checked')) {
                _this.content.find(".Ldt-EnrichedPlan-Slide ." + classname).removeClass("filtered_out");
                if (_this.bar) {
                    _this.bar.find("." + classname).removeClass("filtered_out");
                }
            } else {
                _this.content.find(".Ldt-EnrichedPlan-Slide ." + classname).addClass("filtered_out");
                if (_this.bar) {
                    _this.bar.find("." + classname).addClass("filtered_out");
                }
            }
        }
    });

    _this.container.on("click", ".Ldt-EnrichedPlan-EditControl-Edit", function () {
        _this.player.trigger("Annotation.edit", this.dataset.id);
    });
    _this.container.on("click", ".Ldt-EnrichedPlan-EditControl-Featured", toggle_featured);
    _this.container.on("click", ".Ldt-EnrichedPlan-EditControl-Delete", function () {
        var _annotation = _this.source.getElement(this.dataset.id);
        if (confirm(Mustache.to_html(_this.l10n.confirm_delete_message, { annotation: _annotation }))) {
            _this.source.getAnnotations().removeElement(_annotation);
            _this.player.trigger("Annotation.delete", this.dataset.id);
        }
    });

    function toggle_featured(e) {
        var aid = e.target.dataset.id;
        e.preventDefault();
        IriSP.jQuery.ajax({
            url: _this.action_url("featured", aid),
            timeout: 2000,
            type: "POST",
            contentType: 'application/json',
            data: "",
            dataType: 'json',
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert("An error has occurred making the request: " + errorThrown);
            },
            success: function(data) {
                // Update the local value.
                var an = _this.source.getElement(aid);
                an.meta['coco:featured'] = data.meta['coco:featured'];
                _this.player.trigger("AnnotationsList.refresh");
            }
        });
    }

    function update_level(el, inc) {
        var an = _this.source.getElement(el.dataset.id);
        if (an.content.data === "") {
            an.content.data = {level: 1};
        };
        an.content.data.level = (an.content.data.level || 1) + inc;
        IriSP.jQuery.ajax({
            url: _this.action_url("level", el.dataset.id),
            timeout: 2000,
            type: "POST",
            contentType: 'application/json',
            data: JSON.stringify({'level': an.content.data.level}),
            dataType: 'json',
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert("An error has occurred making the request: " + errorThrown);
            },
            success: function(data) {
                _this.player.trigger("AnnotationsList.refresh");
            }
        });
    };

    _this.container.on("click", ".level_incr", function () {
        update_level(this, +1);
    }).on("click", ".level_decr", function () {
        update_level(this, -1);
    });

    _this.container.find(".Ldt-EnrichedPlan-Search-Input").on("search", function () {
        var q = IriSP.jQuery(this).val().toLocaleLowerCase();
        if (q === "") {
            // Show all
            _this.content.find(".Ldt-EnrichedPlan-Note").removeClass("non_matching");
        } else {
            _this.content.find(".Ldt-EnrichedPlan-Note").each(function () {
                var node = IriSP.jQuery(this);
                if (node.text().toLocaleLowerCase().indexOf(q) > -1) {
                    node.removeClass("non_matching");
                } else {
                    node.addClass("non_matching");
                }
            });
        }
    });
};

IriSP.Widgets.EnrichedPlan.prototype.get_slides = function () {
    var _slides = this.flat_mode ? [] : this.getWidgetAnnotations().sortBy(function (_annotation) {
        return _annotation.begin;
    });
    if (_slides.length == 0) {
        // Enforce flat_mode, so that it is defined in the template
        this.flat_mode = true;
        // No valid segmentation defined. Let's pretend there is a
        // unique global segment.
        var title = this.l10n.whole_video;
        _slides = [ {
            id: "whole",
            title: title,
            begin: 0,
            end: this.media.duration,
            media: this.media,
            thumbnail: "",
            getTitleOrDescription: function () {
                return title;
            }
        } ];
    };
    return _slides;
};

IriSP.Widgets.EnrichedPlan.prototype.update_content = function () {
    var _this = this;
    var _slides = this.get_slides();

    var _annotations = this.media.getAnnotations().filter(function (a) {
        return a.getAnnotationType().title != _this.annotation_type;
    }).sortBy(function (_annotation) {
        return _annotation.begin;
    });

    if (_this.group > 0) {
        _annotations = _annotations.filter(function (a) {
            return a.meta['coco:group'] == _this.group;
        });
    } else if (_this.group == -1) {
        _annotations = _annotations.filter(function (a) {
            return a.meta['coco:visibility'] == "public";
        });
    }

    // Reference annotations in each slide: assume that slide end time is
    // correctly set.
    _slides.forEach(function (slide) {
        slide.annotations = _annotations.filter(function (a) {
            return a.begin >= slide.begin && a.begin < slide.end;
        });
    });

    if (this.container === undefined) {
        // Initialization, render the container template
        var els = _this.init_component();
    } else {
        // Update: empty the container
        // (Should do an incremental update, TBD)
        _this.content.empty();
        if (_this.bar) {
            _this.bar.empty();
        }
    }

    function capitalize(s) {
        // This function is defined in recent versions of _
        return s.replace(/^[a-z]/g, function (match) {
            return match.toUpperCase();
        });
    };

    // Returns the note category: Own, Other, Featured
    function note_category(a) {
        var category = a.meta["coco:category"] || 'other';
        if (a.getAnnotationType().title == 'Quiz') {
            category = "quiz";
        };
        return capitalize(category);
    };

    _slides.forEach(function (slide) {
        var slideData = {
            id : slide.id,
            atitle : IriSP.textFieldHtml(slide.getTitleOrDescription()),
            level: (slide.content !== undefined && slide.content.data !== undefined) ? (slide.content.data.level || 1) : 1,
            begin : slide.begin.toString(),
            begintc: slide.begin.milliseconds,
            position: 100 * slide.begin.milliseconds / _this.media.duration,
            thumbnail: slide.thumbnail,
            show_slides: _this.show_slides,
            is_admin: _this.is_admin,
            admin_url: _this.action_url('admin', slide.id),
            notes: slide.annotations.map(function (a) {
                var cat = note_category(a);
                var annData = {
                    id: a.id,
                    text: IriSP.textFieldHtml(a.getTitleOrDescription()),
                    url: document.location.href.replace(/#.*$/, '') + '#id=' + a.id + '&t=' + (a.begin / 1000.0),
                    author: a.creator,
                    begin: a.begin.toString(),
                    begintc: a.begin.milliseconds,
                    atitle: a.getTitleOrDescription().slice(0, 20),
                    is_admin: _this.is_admin,
                    position: 100 * a.begin.milliseconds / _this.media.duration,
                    can_edit: a.meta['coco:can_edit'],
                    visibility: cat == 'Own' ? ((a.meta['coco:visibility'] || "").indexOf('shared-') == 0 ? "shared" : (a.meta['coco:visibility'] || "private")) : "none",
                    featured: a.meta['coco:featured'],
                    admin_url: _this.action_url('admin', a.id),
                    category: "Ldt-EnrichedPlan-Note-" + cat,
                    filtered: ((cat == 'Own' && !_this.show_own_notes)
                                || (cat == 'Other' && !_this.show_other_notes)
                                || (cat == 'Featured' && !_this.show_featured_notes)
                               || (cat == 'Quiz' && !_this.show_quiz_notes)
                              ) ? 'filtered_out' : ''
                };
                if (_this.bar) {
                    _this.bar.append(IriSP.jQuery(Mustache.to_html(_this.annotationBarTemplate, annData)));
                }
                return Mustache.to_html(_this.annotationTemplate, annData);
            }).join("\n")
        };
        _this.content.append(IriSP.jQuery(Mustache.to_html(_this.slideTemplate, slideData)));
        if (_this.bar) {
            var el = IriSP.jQuery(Mustache.to_html(_this.slideBarTemplate, slideData));
            _this.bar.append(el);
        }
    });
};

IriSP.Widgets.EnrichedPlan.prototype.draw = function () {
    var _this = this;
    _this.init_component();
    _this.update_content();

    _this.onMdpEvent("AnnotationsList.refresh", function () {
        _this.throttledRefresh(false);
    });
};

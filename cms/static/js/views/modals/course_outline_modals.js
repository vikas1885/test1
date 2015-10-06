/**
 * The CourseOutlineXBlockModal is a Backbone view that shows an editor in a modal window.
 * It has nested views: for release date, due date and grading format.
 * It is invoked using the editXBlock method and uses xblock_info as a model,
 * and upon save parent invokes refresh function that fetches updated model and
 * re-renders edited course outline.
 */
define([
    'jquery',
    'underscore',
    'gettext',
    'js/views/modals/base_modal',
    'js/view/modals/editors',
    'js/views/utils/xblock_utils'
], function($, _, gettext, BaseModal, Editors, XBlockViewUtils) {
    'use strict';
    var CourseOutlineXBlockModal, SettingsXBlockModal, PublishXBlockModal;

    CourseOutlineXBlockModal = BaseModal.extend({
        events : {
            'click .action-save': 'save'
        },

        options: $.extend({}, BaseModal.prototype.options, {
            modalName: 'course-outline',
            modalType: 'edit-settings',
            addSaveButton: true,
            modalSize: 'med',
            viewSpecificClasses: 'confirm',
            editors: []
        }),

        initialize: function() {
            BaseModal.prototype.initialize.call(this);
            this.events = $.extend({}, BaseModal.prototype.events, this.events);
            this.template = this.loadTemplate('course-outline-modal');
            this.options.title = this.getTitle();
        },

        afterRender: function () {
            BaseModal.prototype.afterRender.call(this);
            this.initializeEditors();
        },

        initializeEditors: function () {
            this.options.editors = _.map(this.options.editors, function (Editor) {
                return new Editor({
                    parentElement: this.$('.modal-section'),
                    model: this.model,
                    xblockType: this.options.xblockType
                });
            }, this);
        },

        getTitle: function () {
            return '';
        },

        getIntroductionMessage: function () {
            return '';
        },

        getContentHtml: function() {
            return this.template(this.getContext());
        },

        save: function(event) {
            event.preventDefault();
            var requestData = this.getRequestData();
            if (!_.isEqual(requestData, { metadata: {} })) {
                XBlockViewUtils.updateXBlockFields(this.model, requestData, {
                    success: this.options.onSave
                });
            }
            this.hide();
        },

        /**
         * Return context for the modal.
         * @return {Object}
         */
        getContext: function () {
            return $.extend({
                xblockInfo: this.model,
                introductionMessage: this.getIntroductionMessage()
            });
        },

        /**
         * Return request data.
         * @return {Object}
         */
        getRequestData: function () {
            var requestData = _.map(this.options.editors, function (editor) {
                return editor.getRequestData();
            });

            return $.extend.apply(this, [true, {}].concat(requestData));
        }
    });

    SettingsXBlockModal = CourseOutlineXBlockModal.extend({
        getTitle: function () {
            return interpolate(
                gettext('%(display_name)s Settings'),
                { display_name: this.model.get('display_name') }, true
            );
        },

        getIntroductionMessage: function () {
            return interpolate(
                gettext('Change the settings for %(display_name)s'),
                { display_name: this.model.get('display_name') }, true
            );
        }
    });


    PublishXBlockModal = CourseOutlineXBlockModal.extend({
        events : {
            'click .action-publish': 'save'
        },

        initialize: function() {
            CourseOutlineXBlockModal.prototype.initialize.call(this);
            if (this.options.xblockType) {
                this.options.modalName = 'bulkpublish-' + this.options.xblockType;
            }
        },

        getTitle: function () {
            return interpolate(
                gettext('Publish %(display_name)s'),
                { display_name: this.model.get('display_name') }, true
            );
        },

        getIntroductionMessage: function () {
            return interpolate(
                gettext('Publish all unpublished changes for this %(item)s?'),
                { item: this.options.xblockType }, true
            );
        },

        addActionButtons: function() {
            this.addActionButton('publish', gettext('Publish'), true);
            this.addActionButton('cancel', gettext('Cancel'));
        }
    });


    return {
        getModal: function (type, xblockInfo, options) {
            if (type === 'edit') {
                return this.getEditModal(xblockInfo, options);
            } else if (type === 'publish') {
                return this.getPublishModal(xblockInfo, options);
            }
        },

        getEditModal: function (xblockInfo, options) {
            var editors = [];

            if (xblockInfo.isChapter()) {
                editors = [Editors.ReleaseDateEditor, Editors.StaffLockEditor];
            } else if (xblockInfo.isSequential()) {
                editors = [Editors.ReleaseDateEditor, Editors.GradingEditor, Editors.DueDateEditor];

                // since timed/proctored exams are optional
                // we want it before the StaffLockEditor
                // to keep it closer to the GradingEditor
                if (options.enable_proctored_exams) {
                    editors.push(Editors.TimedExaminationPreferenceEditor);
                }

                editors.push(Editors.StaffLockEditor);

            } else if (xblockInfo.isVertical()) {
                editors = [Editors.StaffLockEditor];

                if (xblockInfo.hasVerifiedCheckpoints()) {
                    editors.push(Editors.VerificationAccessEditor);
                }
            }
            /* globals course */
            if (course.get('self_paced')) {
                editors = _.without(editors, Editors.ReleaseDateEditor, Editors.DueDateEditor);
            }
            return new SettingsXBlockModal($.extend({
                editors: editors,
                model: xblockInfo
            }, options));
        },

        getPublishModal: function (xblockInfo, options) {
            return new PublishXBlockModal($.extend({
                editors: [Editors.PublishEditor],
                model: xblockInfo
            }, options));
        }
    };
});

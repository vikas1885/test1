from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from component_editor import ComponentEditorView


class HtmlComponentEditorView(ComponentEditorView):
    """
    Represents the rendered view of an HTML component editor.
    """
    def set_content_and_save(self, content, raw=False):
        """
        Types content into the html component and presses Save.
        """
        self.set_content(content, raw)
        self.save()

    def set_content_and_cancel(self, content, raw=False):
        """
        Types content into the html component and presses Cancel to abort the change.
        """
        self.set_content(content, raw)
        self.cancel()

    def set_content(self, content, raw=False):
        """
        Types content into the html component, leaving the component open.
        """
        self.q(css='.edit-xblock-modal .editor-modes .editor-button').click()
        if raw:
            self.q(css='[aria-label="Edit HTML"]').click()
            ActionChains(self.browser).send_keys([Keys.CONTROL, 'a']).key_up(Keys.CONTROL).send_keys(content).perform()
            self.q(css='.mce-foot .mce-primary').click()
        else:
            editor = self.q(css=self._bounded_selector('.html-editor .mce-edit-area'))[0]
            ActionChains(self.browser).click(editor).\
            send_keys([Keys.CONTROL, 'a']).key_up(Keys.CONTROL).send_keys(content).perform()

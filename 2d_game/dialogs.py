from UI import *


class BaseDialog(UI):
    """
    Класс который реализует возможность создовать диалоговые окна.
    От лица какого-то персонажа.
    С регулируемым положением обектов.
    """
    talking_character: UISprite
    text_field: UIDiv
    text_shower: UIMultipleFadeText

    def __init__(self, display, text_field, text_shower):
        text_field.set_display(display)
        text_field.add_inner_element(text_shower)
        self.text_field = text_field
        self.text_shower = text_shower

    def update_text(self, string: str) -> None:
        self.text_shower.update_text(string)

    def dose_text_finished():
        return self.text_shower.dose_text_finished()

    def draw(self):
        self.text_field.draw()
        # self.talking_character.draw()

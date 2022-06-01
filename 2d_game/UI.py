from abc import abstractmethod
from typing import NoReturn
import time

import pygame
from pygame.locals import *
pygame.init()

TIME_FUNC = lambda: int(time.time() * 1000)


class TypeErrorDecorator(object):
    pass

class RelativePosition(object):
    """
    Класс который реализует возможность задавать позицию UI элемента
    относительно заданного display
    """
    def __init__(self, orientation):
        self.orientation = orientation

    def count_position(self, display):
        display_info = display.get_size()
        x, y = display_info[0], display_info[1]
        position = [x//2, y//2]

        if "center" == self.orientation:
            pass
        else:
            if "left" in self.orientation:
                position[0] = 0
            if "right" in self.orientation:
                position[0] = x
            if "top" in self.orientation:
                position[1] = 0
            if "down" in self.orientation:
                position[1] = y

        return position


class UI(object):
    """
    Класс который реализует базовую логику UI обектов
    """
    is_position_reletive: bool = False
    size: tuple[int]
    position: tuple[int]
    reletive_position: RelativePosition
    orientation: str
    display: pygame.display

    def __init__(self):
        self.full_position = [0, 0]

    def UI_init_with_reletive_position(
            self, display, size, orientation, reletive_position):
        self.__init__()
        self.set_display(display)
        self.set_size(size)
        self.set_orientation(orientation)
        self.set_reletive_position(reletive_position)

    def UI_init_with_position(
            self, display, size, orientation, position):
        self.__init__()
        self.set_display(display)
        self.set_size(size)
        self.set_orientation(orientation)
        self.set_position(position)

    @abstractmethod
    def draw(self):
        pass

    def set_image(self, image):
        match image:
            case pygame.Surface():
                self.image = pygame.transform.scale(image, self.size)
                # self.rect = self.image.get_rect()
            case _:
                raise TypeError(
                    f'wrong input data {size=}.\
                    Should be pygame.Surface type'
                )

    def set_size(self, size: tuple[int]) -> NoReturn:
        match size:
            case int(w), int(h):
                self.size = size
            case _:
                raise TypeError(
                    f'wrong input data {size=}.\
                    Should be tuple thet consist of 2 int values'
                )

    def set_position(self, position: tuple[int]) -> NoReturn:
        match position:
            case int(x), int(y):
                self.position = position
                self.is_position_reletive = False
            case _:
                raise TypeError(
                    f'wrong input data {position=}.\
                    Should be tuple thet consist of 2 int values'
                )

    def set_reletive_position(self, reletive_position: tuple[int]) -> NoReturn:
        match reletive_position:
            case RelativePosition():
                self.reletive_position = reletive_position
                self.is_position_reletive = True
            case _:
                raise TypeError(
                    f'wrong input data {reletive_position=}.\
                    Should be instance of RelativePosition'
                )

    def set_display(self, display: pygame.Surface) -> NoReturn:
        match display:
            case pygame.Surface():
                self.display = display
            case _:
                raise TypeError(
                    f'wrong input data {display=} with type={type(display)}.\
                    Should be instance of pygame.Surface'
                )

    def set_orientation(self, orientation: str) -> NoReturn:
        match orientation:
            case str():
                self.orientation = orientation
            case _:
                raise TypeError(
                    f'wrong input data {orientation=}.\
                    Should be instance of str'
                )

    def update_orientation(self):
        if "center" == self.orientation:
            self.full_position[0] -= self.size[0]//2
            self.full_position[1] -= self.size[1]//2
        if "left" in self.orientation:
            self.full_position[0] = self.position[0]
        if "right" in self.orientation:
            self.full_position[0] -= self.size[0]
        if "top" in self.orientation:
            self.full_position[1] = self.position[1]
        if "down" in self.orientation:
            self.full_position[1] -= self.size[1]
        if "mh" in self.orientation:
            self.full_position[1] = self.position[1] - self.size[1]//2
        if "mw" in self.orientation:
            self.full_position[0] = self.position[0] - self.size[0]//2

    def count_location(self) -> NoReturn:
        if self.is_position_reletive:
            self.position = self.reletive_position.count_position(self.display)

        self.full_position[0] = self.position[0]
        self.full_position[1] = self.position[1]
        self.update_orientation()


class UISprite(UI):
    def draw(self):
        self.count_location()
        self.display.blit(self.image, self.full_position)


class UIDiv(UI):
    inner_elements: list[UI]

    def __base_init(self):
        self.inner_elements = list()
        # print(self.size)
        self.surface = pygame.Surface(self.size)

    def init_with_reletive_position(self, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init()

    def init_with_position(self, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init()

    def add_inner_element(self, elm: UI) -> NoReturn:
        elm.set_display(self.surface)
        self.inner_elements.append(elm)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def draw(self) -> NoReturn:
        self.count_location()
        # self.Surface.blit(self.image, self.full_position)
        # pygame.draw.rect(
        #     self.display,
        #     (120, 120, 120),
        #     (*self.full_position, *self.size)
        # )
        self.surface.fill((120, 120, 120))

        for elm in self.inner_elements:
            elm.draw()

        self.display.blit(self.surface, self.full_position)


class UIRect(UI):
    def __base_init(self, color):
        self.set_color(color)

    def init_with_reletive_position(self, color, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init(color)

    def init_with_position(self, color, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init(color)

    def set_color(self, new_color: tuple[int]):
        if not isinstance(new_color, tuple):
            raise TypeError("color mast be tuple")
        if len(new_color) != 3:
            raise TypeError("color mast be tuple that consist 3 elements")

        self.color = new_color

    def draw(self):
        self.count_location()
        pygame.draw.rect(
            self.display,
            self.color,
            (*self.full_position, *self.size)
        )


class UIText(UI):
    def __base_init(self, text, color):
        self._text = text
        self.set_color(color)

        self.font = pygame.font.Font(None, self.size[1])
        self.update_text(text)

    def init_with_reletive_position(self, text, color, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init(text, color)

    def init_with_position(self, text, color, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init(text, color)

    def set_color(self, color: tuple[int]):
        if not isinstance(color, tuple):
            raise TypeError("color mast be tuple")
        if len(color) != 3:
            raise TypeError("color mast be tuple that consist 3 elements")

        self.color = color

    def draw(self):
        self.count_location()
        self.display.blit(self.converted_text, self.full_position)

    def update_text(self, text):
        self._text = text
        self.converted_text = self.font.render(self._text, 1, self.color)
        self.count_size(self.size[0])

    def count_size(self, size):
        self.size = [len(self._text)*size, size]


class UIFadeText(UI):
    _dose_print_full_text: bool = False
    _dose_start_draw: bool = False
    _start_time: int = 0

    def __init__(self):
        super().__init__()

    def __base_init(self, text, color, appearing_time):
        self.appearing_time = appearing_time
        self._text = text
        self.set_color(color)
        self.font = pygame.font.Font(None, self.size[1])
        self.update_text(text)

    def init_with_reletive_position(self, text, color, appearing_time, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init(text, color, appearing_time)

    def init_with_position(self, text, color, appearing_time, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init(text, color, appearing_time)

    def set_color(self, new_color: tuple[int]):
        if not isinstance(new_color, tuple):
            raise TypeError("color mast be tuple")
        if len(new_color) != 3:
            raise TypeError("color mast be tuple that consist 3 elements")

        self.color = new_color
        color_add = 50
        self.fin_color = tuple((c + color_add if c + color_add <= 255 else 255 for c in new_color))

    def draw(self):
        self.count_location()
        if self._dose_print_full_text:
            self.display.blit(self.converted_text, self.full_position)
        elif not self._dose_start_draw:
            self._dose_start_draw = True
            self._dose_print_full_text = False
            self._start_time = TIME_FUNC()
        else:
            delta_time = TIME_FUNC() - self._start_time

            if delta_time >= self.appearing_time:
                self._dose_print_full_text = True
                self.display.blit(self.converted_text, self.full_position)
            else:
                last_char_id = int(len(self._text) * (delta_time / self.appearing_time))
                appeared_text1 = self.font.render(
                    self._text[:last_char_id],
                    1,
                    self.color
                )
                appeared_text2 = self.font.render(
                    self._text[last_char_id],
                    1,
                    self.fin_color
                )
                self.display.blit(appeared_text1, self.full_position)
                f_pos2 = (
                    self.full_position[0] + appeared_text1.get_width(),
                    self.full_position[1])
                self.display.blit(appeared_text2, f_pos2)

    def update_text(self, text):
        self._dose_start_draw = False
        self._dose_print_full_text = False
        self._start_time = 0
        self._text = text
        self.converted_text = self.font.render(self._text, 1, self.color)
        self.count_size(self.size[0])

    def count_size(self, size):
        self.size = [len(self._text) * size, size]


class UIMultipleFadeText(UIFadeText):
    _now_text_id: int = 0

    def __init__(self):
        super().__init__()

    def __base_init(self, texts, color, appearing_time):
        self.appearing_time = appearing_time
        self._texts = texts
        self.set_color(color)
        self.font = pygame.font.Font(None, self.size[1])
        self.update_text(texts[0])

    def init_with_reletive_position(self, texts, color, appearing_time, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init(texts, color, appearing_time)

    def init_with_position(self, texts, color, appearing_time, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init(texts, color, appearing_time)

    def go_to_next_text(self) -> bool:
        if self._now_text_id >= len(self._texts):
            return False

        self.update_text(self._texts[self._now_text_id])
        self._now_text_id += 1
        return True

    def dose_text_finished():
        if self._now_text_id >= len(self._texts):
            return False

        return True


class UIProgressBar(UI):
    def __init__(self):
        super().__init__()

    def __base_init(self, color1, color2, progress: int):
        self.set_color1(color1)
        self.set_color2(color2)
        self.progress = progress

    def init_with_reletive_position(self, color1, color2, progress, *args, **kwargs):
        super().UI_init_with_reletive_position(*args, **kwargs)
        self.__base_init(color1, color2, progress)

    def init_with_position(self, color1, color2, progress, *args, **kwargs):
        super().UI_init_with_position(*args, **kwargs)
        self.__base_init(color1, color2, progress)

    def check_color(self, color: tuple[int]) -> bool:
        if not isinstance(color, tuple):
            raise TypeError("color mast be tuple")
            return False

        if len(color) != 3:
            raise TypeError("color mast be tuple that consist 3 elements")
            return False

        return True

    def set_color1(self, color: tuple[int]):
        if self.check_color(color):
            self.color1 = color

    def set_color2(self, color: tuple[int]):
        if self.check_color(color):
            self.color2 = color

    def draw(self):
        self.count_location()

        rect1 = (
            self.full_position[0],
            self.full_position[1],
            self.size[0],
            self.size[1]
        )

        rect2 = (
            self.full_position[0],
            self.full_position[1],
            round(self.size[0] * self.progress / 100),
            self.size[1]
        )

        pygame.draw.rect(
            self.display,
            self.color1,
            rect1
        )
        pygame.draw.rect(
            self.display,
            self.color2,
            rect2
        )


CENTER = RelativePosition('center')
LEFT = RelativePosition('left')
RIGHT = RelativePosition('right')
TOP = RelativePosition('top')
DOWN = RelativePosition('down')
LEFT_TOP = RelativePosition('left-top')
LEFT_DOWN = RelativePosition('left-down')
RIGHT_TOP = RelativePosition('right-top')
RIGHT_DOWN = RelativePosition('right-down')

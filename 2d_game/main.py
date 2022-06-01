import math
import time
from typing import NoReturn

import pygame
from pygame.locals import *

from UI import *
from dialogs import *
from event import *


class BaseCellObject(object):
    x: int
    y: int
    size: tuple
    image: tuple

    def __init__(self, size, x=0, y=0, img=None):
        self.size = size
        self.x = x
        self.y = y
        self.have_img = False
        if img is not None:
            self.image = img
            self.have_img = True


class LayoutSpace(object):
    """
    Класс реализующий пространство по которому может перемещаться персонаж
    """
    cell_size: tuple = (30, 30)
    is_open: bool     # у персонажа есть возможность передвигаться в этом пространстве
    is_looped: bool   # при подходе к граници карты либо соединить вер и низ, право и лево карты либо сделать границу
    size: tuple
    surface: pygame.Surface
    have_cell_img: bool
    cells_objects: dict
    frozen_object_map: list
    cells_surface: pygame.Surface
    #cell_object_id

    def __init__(self, size: tuple, is_open: bool = True,\
            is_looped: bool = False, cell_img: pygame.image = None) -> None:
        self.size = size
        self.frozen_object_map = [['*' for i in range(size[0])] for i in range(size[1])]
        self.is_open = is_open
        self.is_looped = is_looped
        self.surface = pygame.Surface(tuple(self.cell_size[i]*self.size[i] for i in range(2)))
        self.have_cell_img = False
        self.cell_object_id = 0
        self.cells_objects = dict()
        if cell_img is not None:
            self.cell_img = cell_img
            self.have_cell_img = True

    def get_objects_by_area(self, area: tuple):
        objects = set()

        i_start = area[1] if area[1] >= 0 else 0
        i_end = area[1] + area[3] + 1
        if i_end > self.size[1]:
            i_end = self.size[1]

        j_start = area[0] if area[0] >= 0 else 0
        j_end = area[0] + area[2] + 1
        if j_end > self.size[0]:
            j_end = self.size[0]

        for i in range(i_start, i_end):
            for j in range(j_start, j_end):
                obj_id = self.frozen_object_map[i][j]
                if isinstance(obj_id, int):
                    objects.add(self.cells_objects[obj_id])

        return objects

    def add_cell_object(self, obj : BaseCellObject):
        x = obj.x
        y = obj.y
        size = obj.size

        if self.size[0] < x or self.size[1] < y\
                or x + size[0] < 0 or y + size[1] < 0:
            return False

        for i in range(0, size[1]):
            for j in range(0, size[0]):
                try:
                    self.frozen_object_map[i + y][j + x] = self.cell_object_id
                except Exception as e:
                    pass

        #if self.cell_object_id not in self.cells_objects:
        self.cells_objects[self.cell_object_id] = obj
        self.cell_object_id += 1


class Player(object):
    x: int
    y: int
    size: tuple
    have_img: bool

    def __init__(self, size, x = 0, y = 0, img : pygame.image = None):
        self.size = size
        self.x = x
        self.y = y
        self.have_img = False
        if img is not None:
            self.image = img
            self.have_img = True


class PlayerController(object):
    player: Player
    space: LayoutSpace

    def __init__(self, player, space):
        self.player = player
        self.space = space
        self.step = 1
        if self.space.is_looped:
            self.move = self.looped_move
        else:
            self.move = self.unlooped_move

    def move(self, x, y):
        pass

    def looped_move(self, x, y):
        self.player.x = (self.player.x + x)\
            % (self.space.size[0] * self.space.cell_size[0])
        self.player.y = (self.player.y + y)\
            % (self.space.size[1] * self.space.cell_size[1])

    def unlooped_move(self, x, y):
        self.player.x += x
        if self.player.x > self.space.size[0]*self.space.cell_size[0]:
            self.player.x = self.space.size[0]*self.space.cell_size[0]
        elif self.player.x < 0:
            self.player.x = 0
        self.player.y += y
        if self.player.y > self.space.size[1]*self.space.cell_size[1]:
            self.player.y = self.space.size[1]*self.space.cell_size[1]
        elif self.player.y < 0:
            self.player.y = 0

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step



def count_time(func):
    def wrap(*args, **kwargs):
        ts = time.time()
        func(*args, **kwargs)
        print(f'time={time.time() - ts}')
    return wrap


class TargetCamera(object):
    camera_capture_area_size: tuple
    #target
    #layout

    def __init__(self, camera_capture_area_size, target, space):
        self.target = target
        self.space = space
        self.camera_capture_area_size = camera_capture_area_size
        self.update_rander_func()

    def get_camera_position(self):
        x = self.target.x + self.target.size[0] / 2\
            - self.camera_capture_area_size[0] / 2
        y = self.target.y + self.target.size[1] / 2\
            - self.camera_capture_area_size[1] / 2
        return (x, y)

    def draw_target(self, surface: pygame.Surface,
            scale_transformation, x = 0, y = 0):
        x = self.camera_capture_area_size[0] // 2
        y = self.camera_capture_area_size[1] // 2
        transformed_size = (self.target.size[0] * scale_transformation[0],
                            self.target.size[1] * scale_transformation[1])

        if self.target.have_img:
            img = pygame.transform.scale(self.target.image, transformed_size)
            surface.blit(img,
                (x*scale_transformation[0] - transformed_size[0] // 2,
                y*scale_transformation[1] - transformed_size[1] // 2,
                *transformed_size)
            )
        else:
            pygame.draw.rect(
                surface, (255, 0, 0),
                (x*scale_transformation[0] - transformed_size[0] // 2,
                    y*scale_transformation[1] - transformed_size[1] // 2,
                    *transformed_size
                )
            )

    def unlooped_draw_space(self, surface: pygame.Surface, scale_transformation):
        cell_size = self.space.cell_size
        camera_position = self.get_camera_position()

        transformed_size = (cell_size[0]*scale_transformation[0],
                            cell_size[1]*scale_transformation[1])


        delta_x = camera_position[0] % cell_size[0]
        delta_y = camera_position[1] % cell_size[1]

        if camera_position[0] + self.camera_capture_area_size[0] > cell_size[0]*self.space.size[0]:
            x_end = int((cell_size[0]*self.space.size[0] - camera_position[0]) // cell_size[1]) + 1# - self.camera_capture_area_size[1]
        else:
            x_end = math.ceil(self.camera_capture_area_size[0]/cell_size[0])
        x_end -= 0 if camera_position[0]%cell_size[0] == 0 else -1
        if camera_position[0] < 0:
            x_start = int((-camera_position[0])//cell_size[0])
        else:
            x_start = 0 if camera_position[0]%cell_size[0] == 0 else -1
        x_start += 0 if camera_position[0]%cell_size[0] == 0 else 1

        if camera_position[1] + self.camera_capture_area_size[1] > cell_size[1]*self.space.size[1]:
            y_end = int((cell_size[1]*self.space.size[1] - camera_position[1]) // cell_size[1]) + 1# - self.camera_capture_area_size[1]
        else:
            y_end = math.ceil(self.camera_capture_area_size[1]/cell_size[1])
        y_end -= 0 if camera_position[1]%cell_size[1] == 0 else -1
        if camera_position[1] < 0:
            y_start = int((-camera_position[1])//cell_size[1])
        else:
            y_start = 0 if camera_position[1]%cell_size[1] == 0 else -1
        y_start += 0 if camera_position[1]%cell_size[1] == 0 else 1
        img = pygame.transform.scale(self.space.cell_img, transformed_size)
        for cell_y in range(y_start, y_end):
            for cell_x in range(x_start, x_end):
                x = -delta_x + cell_x * cell_size[0]
                y = -delta_y + cell_y * cell_size[1]
                surface.blit(img,
                    (x*scale_transformation[0],
                    y*scale_transformation[1],
                    *transformed_size))

    def looped_draw_space(self, surface : pygame.Surface, scale_transformation):
        cell_size = self.space.cell_size
        camera_position = self.get_camera_position()

        transformed_size = (cell_size[0]*scale_transformation[0],
                            cell_size[1]*scale_transformation[1])


        delta_x = camera_position[0]%cell_size[0]
        delta_y = camera_position[1]%cell_size[1]
        x_end = math.ceil(self.camera_capture_area_size[0]/cell_size[0])
        x_end -= 0 if camera_position[0]%cell_size[0] == 0 else -1
        x_start = 0 if camera_position[0]%cell_size[0] == 0 else -1
        x_start += 0 if camera_position[0]%cell_size[0] == 0 else 1

        y_end = math.ceil(self.camera_capture_area_size[1]/cell_size[1])
        y_end -= 0 if camera_position[1]%cell_size[1] == 0 else -1
        y_start = 0 if camera_position[1]%cell_size[1] == 0 else -1
        y_start += 0 if camera_position[1]%cell_size[1] == 0 else 1
        img = pygame.transform.scale(self.space.cell_img, transformed_size)

        for cell_y in range(y_start, y_end):
            for cell_x in range(x_start, x_end):
                x = -delta_x + cell_x * cell_size[0]
                y = -delta_y + cell_y * cell_size[1]

                surface.blit(img,
                    (x*scale_transformation[0],
                    y*scale_transformation[1],
                    *transformed_size))


    def unlooped_draw_cells_obj(self, surface : pygame.Surface, scale_transformation):
        cell_size = self.space.cell_size
        space_size = (self.space.size[0] * cell_size[0],
            self.space.size[1] * cell_size[1])
        camera_position = self.get_camera_position()

        transformed_cell_size = (cell_size[0] * scale_transformation[0],
            cell_size[1] * scale_transformation[1])

        areas = list()
        camera_areas = list()
        # x_start = camera_position[0]%space_size[0]
        # y_start = camera_position[1]%space_size[1]
        x_start = camera_position[0]
        y_start = camera_position[1]
        x_len = self.camera_capture_area_size[0]
        y_len = self.camera_capture_area_size[1]
        area = (x_start, y_start, x_len, y_len)

        if area[0] + area[2] > space_size[0]:
            if area[1] + area[3] > space_size[1]:
                areas.append((0, 0, area[2] + area[0] - space_size[0], area[3] + area[1] - space_size[1]))
                camera_areas.append((space_size[0]-area[0], space_size[1]-area[1], area[2], area[3]))
            else:
                areas.append((0, area[1], area[2] + area[0] - space_size[0], area[3]))
                camera_areas.append((space_size[0]-area[0], 0, area[2], area[3]))
        else:
            if area[1] + area[3] > space_size[1]:
                areas.append((area[0], 0, area[2], area[3] + area[1] - space_size[1]))
                camera_areas.append((0, space_size[1]-area[1], area[2], area[3]))
            else:
                areas.append(area)
                camera_areas.append((0, 0, area[2], area[3]))

        for area_id in range(len(areas)):
            area = areas[area_id]
            camera_area = camera_areas[area_id]
            cropped_area = tuple([int(area[i]//cell_size[i%2]) for i in range(4)])
            for obj in self.space.get_objects_by_area(cropped_area):
                transformed_size = (obj.size[0]*transformed_cell_size[0],
                    obj.size[1]*transformed_cell_size[1])
                img = pygame.transform.scale(obj.image, transformed_size)
                x = obj.x*cell_size[0] - area[0] + camera_area[0]
                y = obj.y*cell_size[1] - area[1] + camera_area[1]
                # ("\t", f'{area=}, {cropped_area=}, {id(obj)=}, {obj.x=}, {obj.y=}, all_x={x}, all_y={y}')

                surface.blit(img,
                    (x*scale_transformation[0],
                    y*scale_transformation[1],
                    *transformed_size))

    def looped_draw_cells_obj(self,
            surface: pygame.Surface, scale_transformation):
        cell_size = self.space.cell_size
        space_size = (self.space.size[0] * cell_size[0],
            self.space.size[1] * cell_size[1])
        camera_position = self.get_camera_position()

        transformed_cell_size = (cell_size[0]*scale_transformation[0],
            cell_size[1]*scale_transformation[1])

        areas = list()
        camera_areas = list()
        x_start = camera_position[0] % space_size[0]
        y_start = camera_position[1] % space_size[1]
        x_len = self.camera_capture_area_size[0]
        y_len = self.camera_capture_area_size[1]
        area = (x_start, y_start, x_len, y_len)

        if area[0] + area[2] > space_size[0]:
            if area[1] + area[3] > space_size[1]:
                areas.append((area[0], area[1], space_size[0]-area[0], space_size[1]-area[1]))
                camera_areas.append((0, 0, space_size[0]-area[0], space_size[1]-area[1]))

                areas.append((0, 0, area[2] + area[0] - space_size[0], area[3] + area[1] - space_size[1]))
                camera_areas.append((space_size[0]-area[0], space_size[1]-area[1], area[2], area[3]))

                areas.append((0, area[1], area[2] + area[0] - space_size[0], space_size[1] - area[1]))
                camera_areas.append((space_size[0]-area[0], 0, area[2], space_size[1]-area[1]))

                areas.append((area[0], 0, space_size[0]-area[0], area[3] + area[1] - space_size[1]))
                camera_areas.append((0, space_size[1]-area[1], space_size[0]-area[0], area[3]))
            else:
                areas.append((area[0], area[1], space_size[0]-area[0], area[3]))
                camera_areas.append((0, 0, space_size[0]-area[0], area[3]))
                areas.append((0, area[1], area[2] + area[0] - space_size[0], area[3]))
                camera_areas.append((space_size[0]-area[0], 0, area[2], area[3]))
        else:
            if area[1] + area[3] > space_size[1]:
                areas.append((area[0], area[1], area[2], space_size[1]-area[1]))
                camera_areas.append((0, 0, area[2], space_size[1]-area[1]))
                areas.append((area[0], 0, area[2], area[3] + area[1] - space_size[1]))
                camera_areas.append((0, space_size[1]-area[1], area[2], area[3]))
            else:
                areas.append(area)
                camera_areas.append((0, 0, area[2], area[3]))

        for area_id in range(len(areas)):
            area = areas[area_id]
            camera_area = camera_areas[area_id]
            cropped_area = tuple([int(area[i]//cell_size[i%2]) for i in range(4)])
            for obj in self.space.get_objects_by_area(cropped_area):
                transformed_size = (obj.size[0]*transformed_cell_size[0],
                    obj.size[1]*transformed_cell_size[1])
                img = pygame.transform.scale(obj.image, transformed_size)
                x = obj.x*cell_size[0] - area[0] + camera_area[0]
                y = obj.y*cell_size[1] - area[1] + camera_area[1]
                # print("\t", f'{area=}, {cropped_area=}, {id(obj)=}, {obj.x=}, {obj.y=}, all_x={x}, all_y={y}')

                surface.blit(img,
                    (x*scale_transformation[0],
                    y*scale_transformation[1],
                    *transformed_size))

    # @count_time
    def unlooped_render(self, screen):
        screen_size = screen.get_size()
        alpha = screen_size[0] / self.camera_capture_area_size[0]
        beta = screen_size[1] / self.camera_capture_area_size[1]
        self.unlooped_draw_space(screen, (alpha, beta))
        self.unlooped_draw_cells_obj(screen, (alpha, beta))
        self.draw_target(screen, (alpha, beta))

    # @count_time
    def looped_render(self, screen):
        screen_size = screen.get_size()
        alpha = screen_size[0] / self.camera_capture_area_size[0]
        beta = screen_size[1] / self.camera_capture_area_size[1]

        self.looped_draw_space(screen, (alpha, beta))
        self.looped_draw_cells_obj(screen, (alpha, beta))
        self.draw_target(screen, (alpha, beta))

    def update_rander_func(self):
        if self.space.is_looped:
            self.render = self.looped_render
        else:
            self.render = self.unlooped_render


def get_gradient(color: list = [0, 0, 0]):
    color_change = [0, 0, 0]
    i = 0
    last_i = None
    is_next = False
    color_change[i] = 1
    color_step = 2
    min_color_param = 0
    max_color_param = 255

    while True:
        for _ in range(len(color_change)):
            color[_] += color_change[_]

        if is_next:
            if color[last_i] <= min_color_param:
                # color = [0, 0, 0]
                color[last_i] = min_color_param
                color[i] = max_color_param
                color_change = [0, 0, 0]
                color_change[i] = -color_step
                is_next = 0
        else:
            if color[i] >= max_color_param:
                color = [min_color_param for _ in range(3)]
                color[i] = max_color_param
                color_change = [0, 0, 0]
                color_change[i] = -color_step
                last_i = i
                i = (i + 1) % 3
                color_change[i] = color_step
                is_next = 1
            elif color[i] <= min_color_param:
                color = [min_color_param for _ in range(3)]
                color[i] = min_color_param
                color_change = [0, 0, 0]
                color_change[i] = color_step

        # print(color)
        yield tuple(color)


class OneLayoutGameRunner(object):
    background_color: tuple = (0, 0, 0)
    FPS: int = 60
    camera: TargetCamera
    layout: LayoutSpace
    player: Player
    events: EventsListener
    screen: pygame.display

    def __init__(self, player, layout, camera, events):
        self.player = player
        self.layout = layout
        self.camera = camera
        self.events = events

    def is_game_run(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

        return True

    def start(self, window_resolution: tuple) -> None:
        screen = pygame.display.set_mode(window_resolution)
        is_run = True
        clock = pygame.time.Clock()

        player_controller = PlayerController(self.player, self.layout)
        player_controller.set_step(5)
        step = player_controller.get_step() / self.FPS * 20
        e_w = KeyboardEvent(
            pygame.K_w, KeyboardEvent.PRESSED,
            player_controller.move, (0, -step)
        )
        e_s = KeyboardEvent(
            pygame.K_s, KeyboardEvent.PRESSED,
            player_controller.move, (0, step)
        )
        e_a = KeyboardEvent(
            pygame.K_a, KeyboardEvent.PRESSED,
            player_controller.move, (-step, 0)
        )
        e_d = KeyboardEvent(
            pygame.K_d, KeyboardEvent.PRESSED,
            player_controller.move, (step, 0)
        )
        self.events.add(e_w)
        self.events.add(e_s)
        self.events.add(e_a)
        self.events.add(e_d)

        FPS_text = UIText()
        FPS_text.init_with_position(
            str(-1), (255, 0, 0),
            screen, (50, 50), 'left-top', (0, 0)
        )

        fade_test = UIFadeText()
        fade_test.init_with_position(
            str('ooo'), (120, 0, 0), 1000,
            screen, (50, 50), 'left-top', (0, 50)
        )

        texts = [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce et feugiat velit. Nunc in pharetra lacus. Suspendisse dui quam, iaculis vitae faucibus nec, commodo eget quam. Nullam vitae porttitor neque. Maecenas ornare ultricies dui, faucibus pellentesque lacus consectetur id. Interdum et malesuada fames ac ante ipsum primis in faucibus. Proin non eros velit. Praesent ullamcorper sed erat id efficitur.',
            'Donec luctus metus quis mauris ullamcorper, nec porttitor orci vulputate. Sed pharetra neque sit amet viverra auctor. Aliquam diam diam, ornare venenatis iaculis ac, bibendum convallis mauris. Cras molestie urna eget pretium elementum. Duis sodales dignissim mauris, mollis bibendum odio dignissim eget. Suspendisse potenti. Nam elit sapien, luctus porttitor risus eget, accumsan hendrerit felis. Sed massa lacus, ullamcorper in nulla vitae, semper mattis arcu.',
            'Suspendisse fermentum viverra ornare. Curabitur commodo, elit id pulvinar sagittis, urna sapien dapibus est, eget hendrerit eros turpis vel magna. Etiam vitae suscipit mi. Vestibulum sit amet tincidunt lorem, at finibus dui. Phasellus tempus metus quis elementum iaculis. Curabitur volutpat bibendum facilisis. Integer gravida urna eget justo tincidunt, eu suscipit felis rutrum.',
            'Suspendisse sed odio et libero commodo lobortis quis sed tellus. Quisque tristique mollis tempus. Nullam et erat ullamcorper, semper ex ac, mollis diam. Vestibulum non nisi id nunc semper egestas et a nisl. Pellentesque ut accumsan purus. Mauris efficitur, lacus a laoreet auctor, dui elit efficitur mi, at tempus ex metus nec massa. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Phasellus volutpat, orci id interdum fringilla, lorem sem sagittis dui, nec sollicitudin ante turpis ut turpis. Fusce nec fermentum erat. Curabitur auctor ornare risus ut tempor. Nulla fringilla urna nec tellus dapibus, id fringilla mi convallis. Maecenas malesuada nulla sit amet magna dignissim porttitor. In at varius orci. Nulla erat sapien, tincidunt at lacus vel, elementum interdum magna. Aliquam congue purus vitae quam interdum pellentesque. Phasellus sed magna non sapien imperdiet rhoncus.',
            'Nunc semper ante non erat tristique, eget luctus augue ullamcorper. Cras tincidunt, quam ut maximus rutrum, erat enim placerat purus, non suscipit leo metus a nisi. In eget nibh lorem. Suspendisse eget tristique lacus. Aliquam vel eros commodo, varius eros accumsan, pretium velit. Etiam finibus et risus ut tincidunt. In eleifend vehicula velit. Donec eget nibh quis enim pellentesque tincidunt. Sed tempus cursus urna, in dapibus dui sodales at. Vestibulum suscipit varius lectus. Ut elementum porta rhoncus. Vivamus posuere dapibus sagittis. ',
        ]
        mfade_text = UIMultipleFadeText()
        mfade_text.init_with_position(
            texts, (120, 0, 0), 100000,
            screen, (50, 50), 'left-top', (0, 250)
        )

        HP_bar = UIProgressBar()
        HP_bar.init_with_reletive_position(
            (100, 100, 100), (100, 100, 255), 100,
            screen, (200, 20), 'mw-down', DOWN
        )

        some_rect = UIRect()
        some_rect.init_with_reletive_position(
            (0, 0, 255),
            screen, (20, 20), 'right-top', RIGHT_TOP
        )

        fade1 = UIMultipleFadeText()
        fade1.init_with_reletive_position(
            texts, (120, 0, 0), 10000,
            screen, (20, 20), 'left-top', LEFT_TOP
        )
        div1 = UIDiv()
        div1.init_with_reletive_position(
            screen, (300, 80), 'left-down', LEFT_DOWN)

        next_text = KeyboardEvent(
            pygame.K_SPACE, KeyboardEvent.DOWN, fade1.go_to_next_text)
        self.events.add(next_text)

        dialog1 = BaseDialog(screen, div1, fade1)

        grad_gen = get_gradient()

        while 1:
            self.events.update()
            if is_run := (not self.is_game_run()):
                break

            screen.fill(self.background_color)

            #self.player.draw(self.layout.surface)
            self.camera.render(screen)
            FPS_text.update_text(str(clock.get_fps()))
            FPS_text.draw()
            fade_test.draw()
            dialog1.draw()
            mfade_text.draw()
            HP_bar.draw()
            some_rect.set_color(next(grad_gen))
            some_rect.draw()
            #print(1)

            pygame.display.update()
            clock.tick(self.FPS)

        pygame.quit()


def main():
    p1 = Player((30, 30), img=pygame.image.load('./images/player.png'))
    s1 = LayoutSpace((30, 30), is_looped=True, cell_img=pygame.image.load('./images/ground_block.jpg'))
    box1 = BaseCellObject((2, 1), x=0, y=0, img=pygame.image.load('./images/box1.png'))
    box2 = BaseCellObject((2, 1), x=28, y=0, img=pygame.image.load('./images/box1.png'))
    s1.add_cell_object(box1)
    s1.add_cell_object(box2)
    # print(s1.cells_objects)
    c1 = TargetCamera((500, 500), p1, s1)
    el1 = EventsListener()
    game = OneLayoutGameRunner(p1, s1, c1, el1)
    game.start((500, 500))


if __name__ == '__main__':
    main()

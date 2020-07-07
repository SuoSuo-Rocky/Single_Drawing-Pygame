
import copy
import math
import sys


from pygame import freetype

from core.settings import *


class Manager:
    """ 游戏管理类 """

    def __init__(self, screen_size, lev_obj, font):
        self.size = screen_size                      # 窗口尺寸
        self.screen = pygame.display.set_mode(screen_size)
        self.center = self.screen.get_rect().center  # 窗口中心点坐标
        self.font = font                             # pygame 字体对象
        self.game_level = 1                          # 游戏初始关卡等级
        self.lev_obj = lev_obj                       # 关卡对象
        self.frame = self.lev_obj.frame              # 矩阵元素列表
        self.row_num = Frame_Height // Frame_size    # 矩阵行数
        self.col_num = Frame_Width // Frame_size     # 矩阵列数
        self.frame_ele_len = Frame_size              # 矩阵元素边长
        self.ori_frame = copy.deepcopy(self.frame)   # 保存本关矩阵数据
        self.next_frame_switch = False               # 下一关卡开关
        self.conn_dot_li = []                        # 已连接的线段
        self.game_is_died = False                    # 游戏是否死亡开关

        self.init_data()

    def init_data(self):
        """  初始化线段数据 """
        self.lines_dict = {}  # 所有有效线段字典， 区分方向
        self.vaild_conn_dict = {} # 所有点的 有效连接点数
        start_pos = None
        end_pos = None
        for k, dot in enumerate(self.frame):
            if k == 0:
                start_dot =  dot
                continue
            end_pos = self.cell_xy(*dot)
            start_pos = self.cell_xy(*start_dot)
            front_line = (start_pos, end_pos)
            rever_line = (end_pos, start_pos)
            self.lines_dict[front_line] = False
            self.lines_dict[rever_line] = False

            # 判断 起点 是否已存在 连接点字典中
            if self.vaild_conn_dict.get(start_pos, None):
                self.vaild_conn_dict[start_pos] += 1
            else:
                self.vaild_conn_dict[start_pos] = 1
            # 判断 终点 是否已存在 连接点字典中
            if self.vaild_conn_dict.get(end_pos, None):
                self.vaild_conn_dict[end_pos] += 1
            else:
                self.vaild_conn_dict[end_pos] = 1
            start_dot = dot

            # print(f'line = {line}')
        # print(f"lines_dict = {self.lines_dict}")
        # 预先创建一个 连接点的 精灵
        self.conn_dot_spire = Ele_Sprite((self.frame_ele_len * 2, self.frame_ele_len * 2))
        # 用于检测时使用的 圆形区域的缩放比例
        self.circle_ratio = self.frame_ele_len / (math.sqrt(2) * self.frame_ele_len)
        self.collide_circle_ratio = pygame.sprite.collide_circle_ratio(self.circle_ratio)
        # 创建点精灵
        self.dot_sprite = Ele_Sprite((1, 1))
        self.conn_lines = []            # 玩家已连接的线段列表
        self.end_line_start_pos = None  # 最后一条线段的 起点
        self.end_line_end_pos = None    # 最后一条线段的 终点
        self.is_first_line_start_pos = False   # 第一个连接点的点击
        self.is_first_line_end_pos = False     # 是否为第一次终点
        self.is_mouse_conti_down = False       # 鼠标按键持续按下的 开关
        self.tem_end_line_end_pos = (10, 10)       # 临时线段的 终点
        print(f'self.circle_ratio = {self.circle_ratio}')


    # 游戏页面绘制初始化
    def init_page(self):
        """ 游戏页面绘制初始化 """
        print(f"self.vaild_conn_dict=  {self.vaild_conn_dict}")
        start_dot = None
        end_dot = None
        # Element(Element.bg, (0, 0)).draw(self.screen) # 绘制背景图片
        # 绘制线段
        for k, line in enumerate(list(self.lines_dict)):
            end_pos = line[1]
            start_pos = line[0]
            if not self.lines_dict[line]:
                pygame.draw.line(self.screen, pygame.Color('blue'), start_pos, end_pos, 6)
            else:
                pygame.draw.line(self.screen, pygame.Color('green'), start_pos, end_pos, 6)
        # if not self.next_frame_switch:
        # 绘制 临时的 连接线段
        if self.is_mouse_conti_down:
            if not self.is_first_line_end_pos:
                pygame.draw.line(self.screen, pygame.Color('blue'), self.end_line_start_pos, self.end_line_end_pos, 6)
            else:
                pygame.draw.line(self.screen, pygame.Color('blue'), self.end_line_end_pos, self.tem_end_line_end_pos, 6)

        # 绘制点
        for k, dot in enumerate(self.frame):
            dot_pos = self.cell_xy(*dot)
            pygame.draw.circle(self.screen, pygame.Color(0, 255, 255), dot_pos, self.frame_ele_len)
        # 绘制游戏关卡等级
        # self.font = pygame.font.Font("font/SourceHanSansSC-Bold.otf", 26)
        # reset_font = self.font.render("Level: %d" % self.game_level, False, (0, 88, 77))
        # self.screen.blit(reset_font, (35, 24))


        # 判断下一关页面是否绘制
        # self.next_frame_switch = self.lev_obj.is_success()
        # if self.next_frame_switch:
        #     self.next_reset()

    def coord_detec(self, tem_pos):
        """ 坐标检测 """

        old_end_line_start_pos = self.end_line_start_pos
        old_end_line_end_pos = self.end_line_end_pos
        print("is mouse down ")
        # 按下坐标检测
        for dot in self.frame:
            dot_pos = self.cell_xy(*dot)
            if self.is_collide_dot(dot_pos, tem_pos):
                print(f'连接点坐标 = {dot_pos}--- 点击')
                # 第一次点击连接点， 起点
                if not self.is_first_line_start_pos:
                    self.end_line_start_pos = dot_pos
                    self.is_first_line_start_pos = True
                else:  # 点击连接的下一个连接点
                    # 是否为第一次终点
                    if not self.is_first_line_end_pos:
                        self.end_line_end_pos = dot_pos
                    else:
                        self.end_line_start_pos = self.end_line_end_pos
                        self.end_line_end_pos = dot_pos
                    line = (self.end_line_start_pos, self.end_line_end_pos)
                    # 判断是否为 有效的 线段
                    if line in list(self.lines_dict):
                        # 判断要连接的线段是否已经连接
                        if self.lines_dict[line]:
                            self.end_line_end_pos = old_end_line_end_pos
                            self.end_line_start_pos = old_end_line_start_pos
                        else:
                            # 改变 线段的 有效性
                            self.lines_dict[line] = True
                            self.lines_dict[(line[1], line[0])] = True
                            # 改变起点和终点的 有效连接点数
                            self.vaild_conn_dict[line[0]] -= 1
                            self.vaild_conn_dict[line[1]] -= 1
                        # 确定第一条线段的终点
                        if not self.is_first_line_end_pos:
                            self.is_first_line_end_pos = True
                    else:
                        self.end_line_end_pos = old_end_line_end_pos
                        self.end_line_start_pos = old_end_line_start_pos
                break


    # 事件监听
    def listen_event(self, event):
        """ 事件监听 """
        self.next_frame_switch = self.is_success()
        self.is_mouse_conti_down = False
        if self.game_is_died:
            print("你死了")
            return
        self.game_is_died = self.is_died()
        # 获取鼠标当前的 坐标
        cur_pos = pygame.mouse.get_pos()
        if not self.next_frame_switch:
            # if event.type == KEYDOWN:
                # 撤销回退一步
                # if event.key == K_BACKSPACE:
                #     if event.mod in [KMOD_LCTRL, KMOD_RCTRL]:
                #         self.undo_one_step()

                # 本关卡重置, 组合键(Ctrl + Enter)
                # if event.key == K_KP_ENTER or event.key == K_RETURN:
                #     if event.mod in [KMOD_LCTRL, KMOD_RCTRL]:
                #         self.again_head()
            # 鼠标按下事件
            if event.type == MOUSEBUTTONDOWN:
                self.coord_detec(event.pos)

            # 轮询 鼠标状态
            mouses = pygame.mouse.get_pressed()
            # 第一个线段的起点已确定
            if self.is_first_line_start_pos:
                if 1 in mouses:  # 存在鼠标按键按下
                    print("is press motion ")
                    self.is_mouse_conti_down = True
                    # 按下移动时， 第一条线段的终点还没确定
                    if not self.is_first_line_end_pos:
                        self.end_line_end_pos = cur_pos
                        self.coord_detec(cur_pos)
                    else:
                        self.tem_end_line_end_pos = cur_pos
                        self.coord_detec(cur_pos)
        else:
            pass


    # 矩阵转坐标
    def cell_xy(self, row, col):
        """ 矩阵转坐标 """
        add_x = self.center[0] - self.col_num // 2 * self.frame_ele_len
        add_y = self.center[1] - self.row_num // 2 * self.frame_ele_len
        return (col * self.frame_ele_len + add_x, row * self.frame_ele_len + add_y)


    # 坐标转矩阵
    def xy_cell(self, x, y):
        """ 坐标转矩阵 """
        add_x = self.center[0] - self.col_num // 2 * self.frame_ele_len
        add_y = self.center[1] - self.row_num // 2 * self.frame_ele_len
        return (x - add_x / self.frame_ele_len, y - add_y / self.frame_ele_len)

    def is_collide_dot(self, dot, mouse_pos):
        """
        是否接触连接点
        :param dot: 连接点坐标
        :param mouse_pos: 鼠标坐标
        :return: 布尔值
        """
        self.conn_dot_spire.rect.center = dot
        self.dot_sprite.rect.center = mouse_pos
        # 按比例缩放的圆圈检测两个精灵之间的碰撞
        if self.collide_circle_ratio(self.conn_dot_spire, self.dot_sprite):
            return True
        return False

    # 检查是否通关
    def is_success(self):
        """ 检测是否通关 """
        if False in list(self.lines_dict.values()):
            return False
        return True


    def is_died(self):
        """ 检测此关卡 游戏是否已经死亡 """
        if self.is_first_line_start_pos:
            if not self.is_first_line_end_pos:
                if self.vaild_conn_dict[self.end_line_start_pos]  == 0:
                     return True
            else:
                if self.vaild_conn_dict[self.end_line_end_pos] == 0:
                    return True
        return False


    # 撤销栈回退一步
    def undo_one_step(self):
        """ 撤销栈回退一步 """
        frame = self.lev_obj.undo_stack.pop()
        if frame:
            self.lev_obj.frame[:] = copy.deepcopy(frame) # important
            self.lev_obj.step -= 1

    # 本关重置
    def again_head(self):
        """ 本关重置 """
        self.lev_obj.frame[:] = copy.deepcopy(self.ori_frame) # important
        self.lev_obj.step = 0            # 步数归零
        self.lev_obj.undo_stack.clear()  # 清空撤销回退栈

    # 下一关重置
    def next_reset(self, event = None):
        """ 游戏下一关数据重置 """
        # 绘制下一关提示页面
        if not event:
            Element(Element.good, (0, 0)).draw(self.screen)
        # 下一关页面事件监听
        else:
            if event.type == KEYDOWN:
                # 下一关, 组合键(Ctrl + n)
                if event.key in [K_n, K_n - 62]:
                    if event.mod in [KMOD_LCTRL, KMOD_RCTRL]:
                        self.game_level += 1
                        self.lev_obj.level = self.game_level
                        self.frame = self.lev_obj.frame    # 矩阵元素列表
                        self.next_frame_switch = False
                        self.row_num = len(self.frame)     # 矩阵行数
                        self.col_num = len(self.frame[1])  # 矩阵列数
                        self.ori_frame = copy.deepcopy(self.frame)  # 保存记录本关矩阵元素
                        self.lev_obj.old_frame = copy.deepcopy(self.frame)  # 在移动之前记录关卡矩阵
                        self.font = pygame.font.Font("font/SourceHanSansSC-Bold.otf", 30)
                        self.lev_obj.step = 0              # 步数归零
                        self.lev_obj.undo_stack.clear()    # 清空撤销回退栈

                # 退出, 组合键(Ctrl + q)
                if event.key in [K_q, K_n - 62]:
                    if event.mod in [KMOD_LCTRL, KMOD_RCTRL]:
                        sys.exit()


class Element(pygame.sprite.Sprite):
    """ 游戏页面图片精灵类 """

    bg = "img/bg.png"

    def __init__(self, path, position):
        super(Element, self).__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = position

    # 绘制函数
    def draw(self, screen):
        """ 绘制函数 """
        screen.blit(self.image, self.rect)


class Ele_Sprite(pygame.sprite.Sprite):
    """ 自定义精灵类 """

    def __init__(self, img_file, *args, **kwargs):
        """ 精灵初始化 """
        super(Ele_Sprite, self).__init__()
        combi = None
        if isinstance(img_file, str):  # 图片文件名
            self.image = pygame.image.load(img_file)
        elif isinstance(img_file, (list, tuple)):                          # Surface 对象的 大小
            self.image = pygame.Surface(img_file, pygame.SRCALPHA, 32) # 透明图像
            # self.image = pygame.Surface(img_file)
        else:  # Font 对象
            assert isinstance(img_file, freetype.Font)
            assert isinstance(args[0], str) # 必须要有文本
            # 表示前景色
            if len(args) >= 2 and isinstance(args[1], (list, tuple, pygame.Color)):
                # 表示背景色
                if len(args) >=  3 and isinstance(args[2], (list, tuple, pygame.Color)):
                    combi = img_file.render(*args, **kwargs)
                else:
                    combi = img_file.render(args[0], args[1], **kwargs)
            else:
                combi = img_file.render(args[0], **kwargs)
        if combi:
            self.image, self.rect = combi
        else:
            self.rect = self.image.get_rect()
        self.orig_image = self.image
        self.orig_rec = self.rect
        self.is_move = True


    def draw(self, screen, angle):
        """ 绘制精灵 """
        self.rotate(angle)
        screen.blit(self.image, self.rect)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, angle)
        if angle != 0:
            wid = int(self.orig_rec.w * 1.6)
            hei = int(self.orig_rec.h * 1.6)
            self.image = pygame.transform.scale(self.image, (wid, hei))
        # self.image = pygame.transform.scale(self.image, (1.2, 1.2))
        self.rect = self.image.get_rect(center=self.rect.center)


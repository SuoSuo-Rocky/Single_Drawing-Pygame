

import sys
# 导入pygame 及常量库
import pygame
from pygame.locals import *


# 主函数
def main():

    # 标题
    title = "明日科技"
    # 屏幕尺寸（宽， 高）
    __screen_size = WIDTH, HEIGHT =800, 600
    # 颜色定义
    bg_color = (54, 59, 64)
    # 帧率大小
    FPS = 60

    # 初始化
    pygame.init()
    # 创建游戏窗口
    screen = pygame.display.set_mode(__screen_size)
    # 设置窗口标题
    pygame.display.set_caption(title)
    # 创建管理时间对象
    clock = pygame.time.Clock()
    # 创建字体对象
    font = pygame.font.Font("font/SourceHanSansSC-Bold.otf", 26)

    # 程序运行主体死循环
    while 1:
        # 1. 清屏(窗口纯背景色画纸的绘制)
        screen.fill(bg_color)  # 先准备一块深灰色布
        # 2. 绘制

        for event in pygame.event.get():  # 事件索取
            if event.type == QUIT:  # 判断点击窗口右上角“X”
                pygame.quit()       # 还原设备
                sys.exit()          # 程序退出

        # 3.刷新
        pygame.display.update()
        clock.tick(FPS)

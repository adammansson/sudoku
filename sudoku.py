import pygame as pg
import pygame.freetype
from collections import Counter

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (220,0,0)

class Square(pg.sprite.Sprite):
    def __init__(self, size, position, order, text):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.font = pg.font.Font("font.ttf", int(size/1.5))
        self.note_font = pg.font.Font("font.ttf", int(size/4))
        self.original_color = (200, 200, 200)
        self.color = self.original_color
        self.size = size
        self.order = order
        self.text = text
        self.note_text = ""

        self.row = None
        self.column = None
        self.rectangle = None

        self.clicked = False
        self.sec_clicked = False
        self.thi_clicked = False
        self.last_clicked = 0
        self.mistake = False

        self.image.fill(self.color)
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position

    def update(self):
        if self.mistake:
            self.color = RED
        elif self.clicked:
            self.color = (150, 150, 150)
        elif self.sec_clicked:
            self.color = (160, 160, 160)
        elif self.thi_clicked:
            self.color = (175, 175, 175)
        else:
            self.color = self.original_color

        self.image.fill(self.color)
        self.label = self.font.render(self.text, 1, BLACK)
        self.note_label = self.note_font.render(self.note_text, 1, BLACK)

        text_size = self.font.size(self.text)
        note_text_size = self.note_font.size(self.note_text)
        self.image.blit(self.label, (int(self.size/2-text_size[0]/2), int(self.size/2-text_size[1]/2)))
        self.image.blit(self.note_label, (self.size-note_text_size[0]-1, self.size-note_text_size[1]-1))

class Button(pg.sprite.Sprite):
    def __init__(self, size, position, text):
        super().__init__()
        self.image = pg.Surface(size)
        self.font = pg.font.Font("font.ttf", int(min(size)/1.5))
        self.color = (150, 150, 150)
        self.size = size
        self.text = text
        self.hover = False
        self.take_note = False
        self.last_clicked = 0

        self.image.fill(self.color)
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position

    def update(self):
        if self.take_note:
            self.color = (110, 110, 110)
        elif self.hover:
            self.color = (140, 140, 140)
        else:
            self.color = (150, 150, 150)

        self.image.fill(self.color)
        self.label = self.font.render(self.text, 1, BLACK)
        text_size = self.font.size(self.text)
        self.image.blit(self.label, (self.size[0]/2-text_size[0]/2, self.size[1]/2-text_size[1]/2))

class Sudoku:
    def __init__(self,):
        pg.init()
        pg.display.set_caption("Sudoku")
        self.window_width = 1280
        self.window_height = 720
        self.screen = pg.display.set_mode((self.window_width, self.window_height), pg.RESIZABLE)
        self.fake_screen = self.screen.copy()
        self.original_width = self.window_width
        self.original_height = self.window_height

        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.squares = pg.sprite.Group()
        self.buttons = pg.sprite.Group()

        restriction = min(self.window_width, self.window_height)
        self.square_size = int(restriction/11.5)
        self.button_size = int(restriction/11)
        self.board_size = (self.square_size+1)*9 + 6
        self.start_x = int((self.window_width - ((self.square_size+1)*9 + 6))/2)
        self.start_y = int(self.window_height/16)
        self.button_start = int(self.start_x + ((self.board_size-(self.button_size+7)*9)+7)/2)
        self.time_font = pg.font.Font("font.ttf", self.start_y)
        self.scale = [1, 1]


        self.clicked_square = None
        self.take_note = False
        self.rows = []
        self.columns = []
        self.rectangles = []
        self.mistake = False
        self.result_text = ""
        self.time_text = "0"

        self.done = False

    def new(self):
        #Add buttons
        counter = 1
        for x in range(self.button_start, self.window_width, self.button_size+7):
            if counter <= 9:
                b = Button((self.button_size, self.button_size), (x, self.start_y + self.board_size + self.button_size/4), str(counter))
                self.buttons.add(b)
                self.all_sprites.add(b)

                counter += 1

        #Add Eraser
        self.eraser = Button((self.button_size*2.125, self.button_size), (0, int(self.start_y + self.board_size/2)), "Eraser")
        self.buttons.add(self.eraser)
        self.all_sprites.add(self.eraser)

        #Add Notes
        self.note = Button((self.button_size*2.125, self.button_size), (0, int(self.start_y + self.board_size/2 + self.button_size)), "Note")
        self.buttons.add(self.note)
        self.all_sprites.add(self.note)

        #Add check solution button
        self.check_solution = Button((self.button_size*2.125, self.button_size), (0, int(self.start_y + self.board_size/2 + 2*self.button_size)), "Check")
        self.buttons.add(self.check_solution)
        self.all_sprites.add(self.check_solution)

        #Add squares
        start_list1 = ['', '9', '', '', '', '', '3', '', '', '', '', '', '3', '9', '7', '1', '', '','4', '', '3', '5', '', '6', '', '9', '', '', '7', '', '', '', '', '9', '1', '', '5', '3', '2', '9', '', '1', '7', '8', '6', '', '4', '1', '', '', '', '', '2', '', '', '6', '', '4', '', '9', '2', '', '1', '', '', '4', '8', '3', '2', '', '', '', '', '', '9', '', '', '', '', '3', '']

        self.x_range = list(range(self.start_x, self.start_x+(self.square_size+1)*3, (self.square_size+1))) + list(range(self.start_x+(self.square_size+1)*3 + 3, self.start_x+(self.square_size+1)*6 + 3, (self.square_size+1))) + list(range(self.start_x+(self.square_size+1)*6 + 6, self.start_x+(self.square_size+1)*9 + 6, (self.square_size+1)))
        self.y_range = list(range(self.start_y, self.start_y+(self.square_size+1)*3, (self.square_size+1))) + list(range(self.start_y+(self.square_size+1)*3 + 3, self.start_y+(self.square_size+1)*6 + 3, (self.square_size+1))) + list(range(self.start_y+(self.square_size+1)*6 + 6, self.start_y+(self.square_size+1)*9 + 6, (self.square_size+1)))

        x_counter = 0
        y_counter = 0
        for x in self.x_range:
            for y in self.y_range:
                text = start_list1[9*x_counter + y_counter]
                s = Square(self.square_size, [x, y], (x_counter, y_counter), text)
                self.squares.add(s)
                self.all_sprites.add(s)

                y_counter += 1
            x_counter += 1
            y_counter = 0

        self.start_time = pg.time.get_ticks()
        self.run()

    def run(self):
        #Main loop
        while not self.done:
            self.scale = [self.screen.get_rect().size[0]/self.fake_screen.get_rect().size[0], self.screen.get_rect().size[1]/self.fake_screen.get_rect().size[1]]
            self.clock.tick(30)
            self.time_text = str((pg.time.get_ticks()-self.start_time)//1000)

            self.events()
            self.draw()

            #Create rows, columns and rectangles
            self.rows = []
            self.columns = []
            self.rectangles = []
            for i in range(9):
                temp = []
                for s in self.squares:
                    if s.order[1] == i:
                        temp.append(s.text)
                        s.row = i
                self.rows.append(temp)

            for i in range(9):
                temp = []
                for s in self.squares:
                    if s.order[0] == i:
                        temp.append(s.text)
                        s.column = i
                self.columns.append(temp)

            for x in range(3):
                for y in range(3):
                    temp = []
                    for s in self.squares:
                        if (s.order[0])//3 == x and (s.order[1])//3 == y:
                            temp.append(s.text)
                            s.rectangle = 3*x + y
                    self.rectangles.append(temp)

            mouse = pg.mouse.get_pos()
            mouse = list(mouse)
            mouse[0] = int(mouse[0]/self.scale[0])
            mouse[1] = int(mouse[1]/self.scale[1])
            click = pg.mouse.get_pressed()

            for s in self.squares:
                if click[0] == 1 and s.rect.collidepoint(mouse) and not s.clicked and pg.time.get_ticks() - s.last_clicked >= 200:
                    if self.clicked_square:
                        self.clicked_square.clicked = False

                    self.clicked_square = s
                    s.clicked = True

                    s.last_clicked = pg.time.get_ticks()

                elif click[0] == 1 and s.rect.collidepoint(mouse) and s.clicked and self.clicked_square and pg.time.get_ticks() - s.last_clicked >= 200:
                    s.clicked = False
                    self.clicked_square = None

                    s.last_clicked = pg.time.get_ticks()

                if self.clicked_square:
                    if self.clicked_square.text != "" and s.text == self.clicked_square.text:
                        s.sec_clicked = True
                    else:
                        s.sec_clicked = False

                    if s.row == self.clicked_square.row or s.column == self.clicked_square.column or s.rectangle == self.clicked_square.rectangle:
                        s.thi_clicked = True
                    else:
                        s.thi_clicked = False

            for b in self.buttons:
                if b.rect.collidepoint(mouse):
                    b.hover = True
                else:
                    b.hover = False

                #Check solution
                if click[0] == 1 and b.rect.collidepoint(mouse) and b.text == "Check" and pg.time.get_ticks() - b.last_clicked >= 500:
                    for ls in [self.rows, self.columns, self.rectangles]:
                        for i in range(9):
                            temp = Counter(ls[i])
                            for x in temp.values():
                                if x > 1:
                                    for s in self.squares:
                                        if ls == self.rows:
                                            if s.row == i:
                                                s.mistake = True
                                        elif ls == self.columns:
                                            if s.column == i:
                                                s.mistake = True
                                        elif ls == self.rectangles:
                                            if s.rectangle == i:
                                                s.mistake = True
                                    self.mistake = True

                    if self.mistake == False:
                        self.result_text = "You won"
                    else:
                        self.result_text = "You lost"

                    b.last_clicked = pg.time.get_ticks()

                #Add notes to squares
                elif click[0] == 1 and b.rect.collidepoint(mouse) and self.clicked_square and pg.time.get_ticks() - b.last_clicked >= 200 and self.take_note:
                    if b.text == "Eraser":
                        self.clicked_square.note_text = ""

                    elif b.text == "Note":
                        self.take_note = False
                        self.note.take_note = False

                    elif b.text != self.clicked_square.note_text:
                        if self.clicked_square.note_text == "":
                            self.clicked_square.note_text = b.text
                        elif b.text not in self.clicked_square.note_text:
                            self.clicked_square.note_text += ", " + b.text

                    b.last_clicked = pg.time.get_ticks()


                #Add the numbers to squares
                elif click[0] == 1 and b.rect.collidepoint(mouse) and self.clicked_square and pg.time.get_ticks() - b.last_clicked >= 200:
                    if b.text == "Eraser":
                        self.clicked_square.text = ""

                    elif b.text == "Note":
                        self.take_note = True
                        self.note.take_note = True

                    elif b.text != self.clicked_square.text:
                        #Add the buttons number to the square
                        self.clicked_square.text = b.text
                        #Remove the squares note
                        self.clicked_square.note_text = ""

                    b.last_clicked = pg.time.get_ticks()

            self.all_sprites.update()

    def events(self):
        self.event_list = pg.event.get()
        for event in self.event_list:
            if event.type == pg. QUIT:
                self.done = True
            if event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(event.size, pg.RESIZABLE)
                self.window_width = event.w
                self.window_height = event.h

            if pg.key.get_pressed()[pg.K_ESCAPE]:
                self.done = True

    def draw(self):
        self.fake_screen.fill((250, 250, 250))

        #Draw "lines" behind the board
        pg.draw.rect(self.fake_screen, (0, 0, 0),(self.start_x-4, self.start_y-4, (self.square_size+1)*9 + 13, (self.square_size+1)*9 + 13))

        #Draw behind buttons
        pg.draw.rect(self.fake_screen, (0, 0, 0),(self.button_start-4, self.start_y + self.board_size + self.button_size/4 - 4, (self.button_size+7)*9 + 1, (self.button_size+8)))

        self.result_label = self.check_solution.font.render(self.result_text, 1, BLACK)
        self.fake_screen.blit(self.result_label, (0, 0))

        self.time_label = self.time_font.render(self.time_text, 1, BLACK)
        self.fake_screen.blit(self.time_label, (int(self.original_width/2-(self.time_font.size(self.time_text)[0])/2), -self.start_y/5))

        self.all_sprites.draw(self.fake_screen)

        self.screen.blit(pg.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))

        pg.display.flip()


s = Sudoku()
while not s.done:
    s.new()
pg.quit()

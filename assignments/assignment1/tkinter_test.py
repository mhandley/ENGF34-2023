from tkinter import *

done = False
def key(event):
    global done
    if event.char == 'q':
        done = True
        rootwindow.destroy()

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 200

rootwindow = Tk();
rootwindow.bind_all('<Key>', key)
canvas = Canvas(rootwindow, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack(side = LEFT, fill=BOTH, expand=TRUE)
textwidget = canvas.create_text(150, 100, anchor="c")
version = rootwindow.tk.call("info", "patchlevel")
canvas.itemconfig(textwidget, text="Success! Tk version: "  + version)
textwidget2 = canvas.create_text(150, 130, anchor="c")
canvas.itemconfig(textwidget2, text="Press q to exit")

while done == False:
    rootwindow.update()


# Import Module
from tkinter import *

# create root window
root = Tk()

# root window title and dimension
root.title("DegreesOfSpotify by Lucas Kanopka, Alessandro De-La-O, & Jordan Price")
# Set geometry(widthxheight)
root.geometry('700x200')

# adding menu bar in root window
# new item in menu bar labeled as 'New'
# adding more items in the menu bar
menu = Menu(root)
item = Menu(menu)
item.add_command(label='New')
menu.add_cascade(label='File', menu=item)
root.config(menu=menu)

# adding a label to the root window for Artist 1
lbl = Label(root, text = "Artist 1")
lbl.grid()

# adding Entry Field for Artist 1
txt = Entry(root, width=20)
txt.grid(column =1, row =0)

# adding a label to the root window for Artist 2
lbl2 = Label(root, text = "Artist 2")
lbl2.grid(column =4, row =0)

# adding Entry Field for Artist 2
txt2 = Entry(root, width=20)
txt2.grid(column =5, row =0)

# global variables for Artist 1 and Artist 2
Artist1 = "Artist 1"

Artist2 = "Artist 2"

# adding a label to the root window for start of line of connections from Artist 1 to Artist 2
lbl7 = Label(root, text = "")
lbl7.grid(column =0, row =5)

# function to display user text when
# button is clicked
#global res
#res = ""
def clicked():

    res = txt.get()
    global Artist1
    Artist1 = res
    lbl.configure(text = "Artist 1: " + res)
    #lbl7.configure(text = "Similar Artists to " + res + ": ")
    lbl7.configure(text= res)

def clicked2():

    res2 = txt2.get()
    global Artist2
    Artist2 = res2
    lbl2.configure(text = "Artist 2: " + res2)

# button widget with red color text inside
btn = Button(root, text = "Confirm" ,
             fg = "red", command=clicked)
# Set Button Grid for Artist 1
btn.grid(column=2, row=0)

# button widget with green color text inside
btn2 = Button(root, text = "Confirm" ,
             fg = "green", command=clicked2)
# Set Button Grid for Artist 2
btn2.grid(column=6, row=0)

# adding a label to the root window for Select Search Algorithm
lbl5 = Label(root, text = "Select Search Algorithm")
lbl5.grid(column =0, row =2)

def clicked3():

    res3 = "You Selected: Depth First Search"
    lbl5.configure(text = res3)

# button widget with orange color text inside
btn3 = Button(root, text = "DFS" ,
             fg = "orange", command=clicked3)
# Set Button Grid for DFS
btn3.grid(column=1, row=2)

def clicked4():
    res4 = "You Selected: Breadth First Search"
    lbl5.configure(text=res4)

# button widget with blue color text inside
btn4 = Button(root, text = "BFS" ,
             fg = "blue", command=clicked4)
# Set Button Grid for BFS
btn4.grid(column=2, row=2)

# adding a label to the root window for the Degree of Separation
lbl6 = Label(root, text = "Find Degrees of Separation")
lbl6.grid(column =0, row =3)

def clicked5():
    res5 = "Find Degrees of Separation !!!!!!"
    lbl6.configure(text=res5)

# button widget with blue color text inside
btn4 = Button(root, text = "Search" ,
             fg = "black", command=clicked5)
# Set Button Grid for Search
btn4.grid(column=1, row=3)

# adding a label to the root window for the Degree of Separation
lbl3 = Label(root, text = "Degree of Separation: ")
lbl3.grid(column =0, row =4)

# deg is the degree of separation
deg = "3"
lbl4 = Label(root, text = deg)
lbl4.grid(column =1, row =4)

#Artist2 = "Artist 2"

# adding a label to the root window for First Connection from Artist 1 to Artist 2
if deg == "1":
    Cartist1 = "--> " + Artist2
else:
    Cartist1 = "--> A"
lbl8 = Label(root, text = Cartist1)
lbl8.grid(column =1, row =5)

# adding a label to the root window for Second Connection from Artist 1 to Artist 2
if int(deg) < 2:
    Cartist2 = "BLANK"
elif deg == "2":
    Cartist2 = "--> " + Artist2
else:
    Cartist2 = "--> B"
lbl9 = Label(root, text = Cartist2)
lbl9.grid(column =2, row =5)
#lbl9.configure(text = "--> " + Artist2)

# adding a label to the root window for Third Connection from Artist 1 to Artist 2
if int(deg) < 3:
    Cartist3 = "BLANK"
elif deg == "3":
    Cartist3 = "--> " + Artist2
else:
    Cartist3 = "--> C"
lbl10 = Label(root, text = Cartist3)
lbl10.grid(column =3, row =5)

# adding a label to the root window for Fourth Connection from Artist 1 to Artist 2
if int(deg) < 4:
    Cartist4 = "BLANK"
elif deg == "4":
    Cartist4 = "--> " + Artist2
else:
    Cartist4 = "--> D"
lbl11 = Label(root, text = Cartist4)
lbl11.grid(column =4, row =5)

# adding a label to the root window for Fifth Connection from Artist 1 to Artist 2
if int(deg) < 5:
    Cartist5 = "BLANK"
elif deg == "5":
    Cartist5 = "--> " + Artist2
else:
    Cartist5 = "--> E"
lbl12 = Label(root, text = Cartist5)
lbl12.grid(column =5, row =5)

# adding a label to the root window for the Credits
#lbl7 = Label(root, text = "Credits: Lucas Kanopka, Alessandro De-La-O, & Jordan Price")
#lbl7.grid(column =0, row =5)

# Execute Tkinter
root.mainloop()
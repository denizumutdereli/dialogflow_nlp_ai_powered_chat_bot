from tkinter import *
from tkinter import messagebox
window = Tk()
window.title("Test")
window.geometry("400x200")
def ButtonFunc():
 messagebox.showinfo( "Hello Python", "Hello World")
B = Button(window, text ="Hello", command = ButtonFunc)
B.pack()
window.mainloop()
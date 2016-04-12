import users as users

from tkinter import *
from tkinter import ttk

# Global Variables
HEADER1 = ("Verdana",40)
LARGE_FONT = ("Verdana", 12)
REGULAR_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)


def popup_msg(msg):
    # generate the popup
    popup = Tk()
    # add a title
    popup.wm_title("!")
    # create the label
    label = ttk.Label(popup, text=msg, font=REGULAR_FONT)
    label.pack(side="top", fill="x", pady=10)
    # make the button
    b1 = ttk.Button(popup, text="OK", command=popup.destroy)
    b1.pack()

    # run the popup
    popup.mainloop()


class JaysCleaners(Tk):
    """Opening class"""

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        Tk.iconbitmap(self, default="")
        Tk.wm_title(self, string="Jays Cleaners")

        # Build the frame(s)
        frame_main = Frame(self, bg="yellow")
        # frame_main.pack(side="top",fill="both",expand = True)
        for r in range(6):
            frame_main.rowconfigure(r, weight=1)
        for c in range(6):
            frame_main.columnconfigure(c, weight=1)
        frame_main.grid()

        # frame_main.grid_rowconfigure(0,weight =1)
        # frame_main.grid_columnconfigure(0,weight=1)
        # start menu bar
        menubar = Menu(self)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Settings")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=file_menu)

        Tk.config(self, menu=menubar)

        # frame - main content
        self.frames = {}
        for F in (Main, PageTwo):
            frame = F(frame_main, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky=N+E+W+S)
            # frame.pack(side="top",fill="both",expand = True)
            # frame.grid_rowconfigure(0,weight =1)
            # frame.grid_columnconfigure(0,weight=1)
        self.show_frame(Main)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Pages
class Main(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        username_label = Label(self, text="Username: ")
        password_label = Label(self, text="Password: ")
        username_input = Entry(self)
        password_input = Entry(self)
        remember_me_checkbox = Checkbutton(self, text="Remember me?")

        username_label.grid(row=0, sticky=E)
        password_label.grid(row=1, sticky=E)
        username_input.grid(row=0, column=1, sticky=E+W)
        password_input.grid(row=1, column=1, sticky=E+W)
        remember_me_checkbox.grid(columnspan=2)


        # button2 = ttk.Button(self, text="Agree", command=lambda: controller.show_frame(PageTwo))
        # button2.pack()
        # button0 = ttk.Button(self, text="Disagree", command=lambda: controller.show_frame(Main))
        # button0.pack()


class PageTwo(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page Two", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        button3 = ttk.Button(self, text="Create User", command=self.test_create)
        button3.pack()
        button4 = ttk.Button(self, text="View Users", command=self.test_select)
        button4.pack()
        button0 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(Main))
        button0.pack()

    def test_create(self):
        user = {
            'id': 1,
            'company_id': 1,
            'first_name': 'Wondo',
            'last_name': 'Choung',
            'email': 'wondo@eyelevate.com',
            'phone': '2069315327'
        }

        if users.add(user):
            popup_msg("Successfully added a new user!")
        else:
            popup_msg("Was not able to save user!")

    def test_select(self):
        try:
            data = users.User.select().order_by(users.User.id.desc())
        except AttributeError:
            popup_msg("There was an attribute error")
        except TypeError:
            popup_msg('There was an error with your request')

        for user in data:

            print("{} {} with id = {}".format(user.first_name,user.last_name,user.id))




app = JaysCleaners()
app.geometry("1270x780")
# ani = animation.FuncAnimation(f,animate, interval=3000)
app.mainloop()

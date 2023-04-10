from tkinter import Tk, Label, Listbox, END, StringVar, Button, Scrollbar, Frame, PhotoImage, Toplevel, Entry, OptionMenu
from subprocess import Popen, PIPE
from re import sub
from bs4 import BeautifulSoup
from requests import get
from ctypes import windll
from threading import Thread
from re import sub
print('Hello world')
#------------------------------------Functions----------------------------------------------------------------

# Action définie pour chaque nouvel élément séléctionné depuis la liste
def action(*args):
    description.config(image='')
    try:
        scope = liste.get(liste.curselection())[2:]
    except:
        return ''
    if prev_mod != scope:
        mod_title_val.set(scope if len(scope) <= 16 else scope[:16] + '...')
        descr_val.set('Loading...')
        Thread(target=ask_descr, args=(scope,)).start()
        remove_button.configure(command=lambda: [print(f'Removing {scope}...'), virtual_cmd(f'pip uninstall {scope} -y', 0), descr_val.set(
            f'{scope} successfully removed'), liste.delete(liste.get(0, END).index(liste.get(liste.curselection())))])

# Formatte les modules retournés par la commande pip mod=1 pour les majs
def form(x, mod): return {elem[0].upper() + sub(r'==.{1,}',
                                                '', elem)[1:]: sub(r'.{1,}==', '', elem) for elem in x} if not mod else [elem[0].upper() + elem[1:].split(' ')[0] for elem in x[2:]]

# Création d'un fenêtre d'installation
def install_menu():
    win.withdraw()
    mod_title_val.set('Select a module')
    install_win = Toplevel(master=win)
    install_win.geometry(f"350x200+{win.winfo_x() + 110}+{win.winfo_y()+65}")
    install_win.title('PIP install')
    install_win.iconbitmap('Images/Python_pip.ico')
    install_win.resizable(False, False)
    install_win.protocol("WM_DELETE_WINDOW", lambda: [
        win.geometry(f'+{install_win.winfo_x()-110}+{install_win.winfo_y()-65}'), install_win.destroy(), win.deiconify()])
    install_win.columnconfigure(0, weight=5)
    install_win.columnconfigure(1, weight=10)
    install_win.columnconfigure(2, weight=10)
    [install_win.rowconfigure(k, weight=1) for k in range(3)]

    install_lbl = Label(
        install_win, text='Enter the desired module:', font=('bahnschrift bold', 12))
    mod_selected = StringVar()
    search_label = Label(install_win, image=search_bar_img)
    find_mod = Entry(install_win, textvariable=mod_selected,
                     relief='flat', font=('bahnschrift', 10))
    confirm_btn = Button(install_win, image=confirm_img,
                         relief='flat', borderwidth=0, command=lambda: [Thread(target=lambda x:virtual_cmd(f'pip install {x}', 0), args=(find_mod.get(),)).start(), mod_selected.set(''), Thread(target=lambda:refresh_mod(0)).start()] if find_mod.get() != '' else print('Enter something...'))
    opt_var = StringVar()
    option_list = ['Update all', 'Reinstall all']
    more_opt = OptionMenu(install_win, opt_var, *option_list)
    more_opt.configure(image=option_img, indicatoron=0,
                       relief='flat', borderwidth=0)

    install_lbl.grid(row=0, column=0, columnspan=3, sticky='s')
    search_label.grid(row=1, column=0, columnspan=3)
    find_mod.grid(row=1, column=0, columnspan=3)
    more_opt.grid(row=2, column=0, sticky='ne', padx=1, pady=5)
    confirm_btn.grid(row=2, column=1, sticky='nw', columnspan=2)

# Envoie une requête pour récupérer la description d'un module
def ask_descr(package_name):
    global statut
    global prev_mod
    statut = False
    statut = True
    while statut:
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        url = f'https://pypi.org/project/{package_name}/'
        try:
            temp = BeautifulSoup(get(url=url, headers=headers).text, 'html.parser').find(
                'div', {'class': "project-description"}).text.replace('\n', ' ')
            temp = temp[:160] + '...' if len(temp) > 160 else temp
            if '/' and '>' in temp:
                descr_val.set('Wrong characters in description')
            else:
                no_blank = sub(r'[ ]{2,}', ' ', temp)
                if no_blank.startswith(' '):
                    descr_val.set(no_blank[1].upper() + no_blank[2:])
                else:
                    descr_val.set(no_blank[0].upper() + no_blank[1:])
        except Exception:
            descr_val.set(f'No description found for {package_name}')
        finally:
            prev_mod = package_name
            break

# Permet de rafraichir la liste de modules mod=0 pour trouver les majs
def refresh_mod(mod):
    if mod:
        req = form(virtual_cmd('pip list --outdated', 1).splitlines(), 1)
    else:
        req = form(virtual_cmd('pip freeze', 1).splitlines(), 0)
    liste.delete(0, END)
    for modules in req:
        liste.insert(END, '⊛ ' + modules)

# Permet d'exécuter une commande en temp réel, mode=1 pour récupérer le texte une fois la commande terminée
def virtual_cmd(command, mode):
    if mode == 0:
        cmd_inp = Popen(command, stderr=PIPE, text=True)
        while True:
            out = cmd_inp.stderr.read()
            if out.isalpha():
                print(out)
            else:
                break
    else:
        cmd_inp = Popen(command, stdout=PIPE, text=True)
        return cmd_inp.stdout.read()

#------------------------------------UX/UI--------------------------------------------------------------------


windll.shcore.SetProcessDpiAwareness(1)

win = Tk()
win.iconbitmap('Images/Python_pip.ico')
win.geometry('550x315+900+400')
win.title('PIP Manager - Bêta')
win.resizable(width=False, height=False)

# Importation des images
remove_pic = PhotoImage(file="Images/button.png").subsample(2)
dl_pic = PhotoImage(file="Images/button-install.png").subsample(2)
confirm_img = PhotoImage(file="Images/confirm_btn.png").subsample(6)
option_img = PhotoImage(file="Images/button_opt.png").subsample(4)
search_bar_img = PhotoImage(file="Images/Search_bar.png").subsample(12)
blank_pic = PhotoImage(file="Images/blank_bg.png").subsample(3)

# Mise en place de la fenetre
(win.rowconfigure(0, weight=20), win.columnconfigure(0, weight=120))  # title
(win.rowconfigure(1, weight=80), win.columnconfigure(
    1, weight=15))  # zone de recherche -> GRILLE EN 3x2
# win.columnconfigure(2, weight=2) # Check button
win.columnconfigure(2, weight=1)  # scrollbar place

# Mise en place de la frame
win.grid_propagate(False)

# Définition des variables
statut = None
prev_mod = None
mod_title_val = StringVar(value='Select a module')
descr_val = StringVar(value='This is where the description comes from')
cmd_output = StringVar(value='CMD output')

# Mise en place du menu déroulant
scroll_bar = Scrollbar(win)
liste = Listbox(win, yscrollcommand=scroll_bar.set, relief='flat', border=10, font=(
    'bahnschrift light', 9), selectbackground='#393737', activestyle='none')
scroll_bar.configure(command=liste.yview)
liste.bind('<<ListboxSelect>>', action)
scroll_bar.grid(column=2, rowspan=2, sticky='nsew')
liste.grid(sticky='nse', column=1, row=1)

refresh_mod(0)

action_frame = Frame(win)
action_frame.rowconfigure(0, weight=75)
action_frame.rowconfigure(1, weight=25)
action_frame.columnconfigure(0, weight=1)
action_frame.columnconfigure(1, weight=1)
action_frame.grid(column=0, row=1, sticky='nsew')

mod_title = Label(master=win, textvariable=mod_title_val,
                  font=('bahnschrift bold', 12))
mod_title.grid(column=0, row=0, padx=20)

mod_text = Label(win, text=f'Modules found : ', font=('bahnschrift light', 12))
mod_text.grid(column=1, row=0, pady=10)

description = Label(master=action_frame, textvariable=descr_val, font=(
    'bahnschrift light', 10), wraplength=250, image=blank_pic)
description.grid(column=0, row=0, columnspan=2)

remove_button = Button(action_frame, image=remove_pic,
                       relief='flat', borderwidth=0)
remove_button.grid(row=1, column=0, sticky='s', pady=10, padx=10)

install_button = Button(action_frame, image=dl_pic,
                        relief='flat', borderwidth=0, command=install_menu)
install_button.grid(row=1, column=1, sticky='s', pady=10, padx=10)

win.mainloop()

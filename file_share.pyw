#!/usr/bin/python
from Tkinter import Tk
from Tkinter import DISABLED
from Tkinter import NORMAL
from Tkinter import N, W, E, S
from Tkinter import StringVar
import tkFileDialog
import ttk
import socket
import struct


def get_file_size(fileobj):
    orig = fileobj.tell()
    fileobj.seek(0, 2)
    size = fileobj.tell()
    fileobj.seel(orig, 0)
    return size


class FileShareDialog(object):
    def __init__(self):
        self.init_gui()

    def mode_changed(self):
        self.filename_var.set("")
        if self.mode.get() == 'server':
            self.targethost_entry.config(state=DISABLED)
        else:
            self.targethost_entry.config(state=NORMAL)

    def browse(self):
        if self.mode.get() == 'client':
            filename = tkFileDialog.askopenfilename()
        else:
            filename = tkFileDialog.asksaveasfilename()
        self.filename_var.set(filename)

    def start(self):
        if self.mode.get() == 'server':
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("0.0.0.0", int(self.port_var.get())))
            server.listen(1)

            connector = server.accept()

            with open(self.filename_var.get(), "wb") as target_file:
                file_size = struct.unpack("<Q", connector.recv(8))
                file_recieved = 0
                while file_recieved < file_size:
                    read_size = file_size - file_recieved if  \
                        (file_size - file_recieved) < 4096 else 4096
                    data_recieved = connector.recv(read_size)
                    file_recieved += len(data_recieved)
                    target_file.write(data_recieved)
        else:
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sender.connect((self.targethost_var.get(),
                            int(self.port_var.get())))

            with open(self.filename_var.get(), "rb") as source_file:
                file_size = get_file_size(source_file)
                sender.sendall(struct.pack("<Q", file_size))
                file_sent = 0
                while file_sent < file_size:
                    read_size = file_size - file_sent if  \
                        (file_size - file_sent) < 4096 else 4096
                    data_to_send = source_file.read(read_size)
                    sender.sendall(data_to_send)
                    file_sent += len(data_to_send)

    def init_gui(self):
        self.root = Tk()
        root = self.root
        root.title("File Sharing Program")
        root.resizable(0, 0)

        # Create the main frame
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe = self.mainframe
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Create the mode selection radiobutton
        self.mode = StringVar()
        ttk.Label(mainframe, text="Mode:").grid(column=0, row=0, sticky=(E, N))
        self.server_mode = ttk.Radiobutton(mainframe, text='Recieve',
                                           variable=self.mode,
                                           value='server',
                                           command=self.mode_changed)

        self.server_mode.grid(column=1, row=0, sticky=N)
        self.client_mode = ttk.Radiobutton(mainframe, text='Send',
                                           variable=self.mode,
                                           value='client',
                                           command=self.mode_changed)
        self.client_mode.grid(column=2, row=0, sticky=N)
        self.mode.set('server')

        # Create the port set entry
        self.port_var = StringVar()
        ttk.Label(mainframe, text="Port:").grid(column=0, row=1, sticky=E)
        self.port_entry = ttk.Entry(mainframe, textvariable=self.port_var)
        self.port_entry.grid(column=1, row=1, sticky=(E, W))
        self.port_var.set('2000')

        # Create the filename box
        self.filename_var = StringVar()
        ttk.Label(mainframe, text="Path:").grid(column=0, row=2, sticky=E)
        self.filename_entry = ttk.Entry(mainframe,
                                        textvariable=self.filename_var)
        self.filename_entry.grid(column=1, row=2, sticky=(E, W))
        self.browse_button = ttk.Button(mainframe, text="Browse...",
                                        command=self.browse)
        self.browse_button.grid(column=2, row=2, sticky=W)

        # Create the target host entry
        self.targethost_var = StringVar()
        ttk.Label(mainframe, text="Target:").grid(column=0, row=3, sticky=E)
        self.targethost_entry = ttk.Entry(mainframe,
                                          textvariable=self.targethost_var,
                                          state=DISABLED)
        self.targethost_entry.grid(column=1, row=3, sticky=(E, W))
        self.start_button = ttk.Button(mainframe, text="Start!",
                                       command=self.start)
        self.start_button.grid(column=2, row=3, sticky=W)

        # Bind Enter to start the transfer
        root.bind('<Return>', self.start)

    def mainloop(self):
        self.root.mainloop()


def main():
    file_share_dialog = FileShareDialog()
    file_share_dialog.mainloop()

if __name__ == '__main__':
    main()

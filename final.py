import pandas as pd
import tkinter as tk
from datetime import datetime
from pandastable import Table, TableModel
from tkinter import scrolledtext
import serial
import time

studentRecord = pd.read_csv("Class Lists.csv")
electronics = pd.read_csv('PowerElectronics.csv')
control = pd.read_csv('ControlSystem.csv')
system = pd.read_csv('PowerSystem.csv')

def StudentInfo(df, rfid):
    matching_row = df[df['RFID'] == rfid]
    if not matching_row.empty:
        sid_value = str(matching_row.iloc[0]['SID'])
        name_value = str(matching_row.iloc[0]['NAME'])
        print(f"The RFID :  {rfid}  belongs to  {name_value}, SID: {sid_value}")
        return (sid_value, name_value)
    else:
        return (str(00000000), 'I am a ghost')


def create_new_column(df):
    dtt = datetime.now().strftime("%d %b, %a")
    prevName = df.columns[-1]
    if (prevName == 'NAME'):
        df[f'L-1 {datetime.now().strftime("%d %b, %a")}'] = 0
        return f'L-1 {datetime.now().strftime("%d %b, %a")}'

    newColName = f"L-{int(prevName.replace('-',' ').split()[1])+1} {dtt}" 
    df[newColName] = 0  
    return str(newColName)

def add_value_to_column_sid_wise(df, column_name, sid_value, value_to_add):
   
    if column_name not in df.columns:
        print("Column does not exist.")
        return

    index = df.index[df['SID']==sid_value]
    df.loc[index, column_name] = value_to_add
    print(f'ADDED ATTENDACE FOR SID {sid_value}\nFunction db id:{id(df)}')
    
    

dtt = datetime.now().strftime("%d %b, %a")
dtt

def add_to_status(text):
    status.configure(state='normal')
    status.insert(tk.INSERT , text + '\n')
    status.configure(state='disabled')
    status.update()

def runningAtt():
    print('INATATIING ATTENDANCE PROCESS')
    add_to_status('Starting attandence')
    
    newColName = create_new_column(subjectRecords[activeSubject][0])

    try:
        serial_port = 'COM4'
        baud_rate = 115200
        
        ser = serial.Serial(serial_port, baud_rate, timeout=None)
        line = ''
        
        while (line != 'C3 13 F5 FA'):
            line = ser.readline().decode('utf-8').strip()
            
            if (line == 'C3 13 F5 FA'):
                print('exiting')
                line = ''
                add_to_status('Attendance is complete')
                return
        
            (new_SID , new_NAME) = StudentInfo(studentRecord, line)
            
            if ((new_SID , new_NAME) != (str(00000000), 'I am a ghost')):                   

                print(f"SID:  {new_SID},  NAME:  {new_NAME}")
                add_to_status(f"SID:  {new_SID},  NAME:  {new_NAME}")
                
                add_value_to_column_sid_wise(df = subjectRecords[activeSubject][0], column_name = newColName , sid_value= int(new_SID) , value_to_add=1)
                print(id(subjectRecords[activeSubject][0]))
                print()
                middle.table.redraw()
                
                lcdDisplay = str(new_SID + "*" + new_NAME)
                ser.write(lcdDisplay.encode('utf-8'))
                time.sleep(2.2)
        
    except serial.SerialException:
        print('Your ESP32 is not connected')
        add_to_status(f"Failed to connect with ESP32.")
    
    finally:
        print('att over')
        if 'ser' in locals():
            ser.close()
        print(subjectRecords[activeSubject][0])
        
        subjectRecords[activeSubject][0].to_csv(subjectRecords[activeSubject][1], index=False)


def update_time_date_labels():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d - %m - %Y")
    time_label.config(text="Time: " + current_time)
    date_label.config(text="Date: " + current_date)
    root.after(1000, update_time_date_labels)  # Update every second

def subject_selected(showingSubject):
    # showingSubject = sub.get()
    subject_label.config(text="Subject: " + showingSubject)
    print(f"Showing {showingSubject} Attandence Record")
    show_db(showingSubject)

subjectRecords = {
            'CLass_List': (studentRecord, 'CLass List.csv'),
            'Power Electronics': (electronics, 'PowerElectronics.csv'), 
            'Control System': (control, 'ControlSystem.csv'),
            'Power System': (system, 'PowerSystem.csv')
        }
        
def show_db(subject):
    global activeSubject
    activeSubject = subject
    middle.table = Table(middle, dataframe=subjectRecords[subject][0], showtoolbar=False, showstatusbar=False ,editable=False, height = 550, width = 700)
    middle.table.show()


# global activeSubject
#################################Create the main window #######################
root = tk.Tk()
root.geometry("1500x1000")
# root.attributes('-fullscreen', True)
root.title("RFID Attendance System")

################################# TOP_L FRAME #######################
top_L = tk.Frame(root)
top_L.grid(row=0, column=0, pady=20, padx=20)

heading_label = tk.Label(top_L, text="Electrical Department", font=("Helvetica", 24))
date_label = tk.Label(top_L, text="Current Date: ", font=("Helvetica", 12))
time_label = tk.Label(top_L, text="Current Time: ", font=("Helvetica", 12))

heading_label.grid()
date_label.grid()
time_label.grid()


################################# TOP_R FRAME #######################
top_R = tk.Frame(root)
top_R.grid(row=0, column=1, pady=20, padx=20)

sub = tk.StringVar()
curr_sub = tk.OptionMenu(top_R, sub ,'CLass_List', 'Power Electronics', 'Control System', 'Power System', command = subject_selected)
subject_label = tk.Label(top_R, text="Subject :", font=("Helvetica", 12))

start_att = tk.Button(top_R, text='Start\nAttandence', command=runningAtt)


curr_sub.grid()
subject_label.grid()

################################# DATABASE FRAME #######################

middle = tk.Frame(root)
middle.grid(row=1, column=0, pady=20, padx=20)

################################# STATUS FRAME #######################
bottom = tk.Frame(root)
bottom.grid(row=1, column=1, pady=20, padx=20)

status = scrolledtext.ScrolledText(bottom, wrap = tk.WORD, width =70, height = 30, font = ("Times New Roman",12))
status.grid()

# ################################# TOP_R FRAME #######################
# top_R = tk.Frame(root)
# top_R.grid(row=0, column=1, pady=20, padx=20)

start_att.grid(row=0, column=3, padx=70)
# stop_att.grid(row=0, column=5, padx=40)

update_time_date_labels()
root.mainloop()

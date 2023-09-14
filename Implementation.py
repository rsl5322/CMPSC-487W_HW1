import tkinter as tk
import datetime
import mysql.connector
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from datetime import datetime


# SQL Database Information
host = "localhost"
port = 3306
user = "root"
password = "Donotforget25"
database = "mydb"

# Connection to SQL Database
conn = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

# Cursor for SQL functions
cursor = conn.cursor()

# Global text widget to be used throughout program
text_widget = None


# Function to determine if user found in system
def check_id():
    student_id = id_entry.get()

    # Query to check if the student ID exists in the table
    cursor.execute("SELECT * FROM staff_swipes WHERE student_id = %s", (student_id,))
    result = cursor.fetchone()

    if result:
        #record_swipe_timestamp(student_id)
        result_label.config(text="Access Granted")
        open_access_window()
    else:
        result_label.config(text="Access Denied")

# Function to record the swipe timestamp --- DOESN'T WORK
def record_swipe_timestamp(student_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Insert the timestamp into the table
    cursor.execute("INSERT INTO staff_swipes (student_id, swipe_time_in) VALUES (%s, %s)", (student_id, timestamp))
    conn.commit()  # Commit the transaction


# Function to open second window when access is granted
def open_access_window():
    global text_widget

    access_window = tk.Toplevel(app)
    access_window.title("Access Granted")

    # Frame to hold the table and student status controls
    table_frame = ttk.Frame(access_window)
    table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Frame for search options
    search_frame = ttk.Frame(access_window)
    search_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=False)

    # Scrollbars
    horizontal_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
    vertical_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)

    # Scrolled text widget for displaying the table
    text_widget = scrolledtext.ScrolledText(
        table_frame,
        width=60,
        height=10,
        wrap=tk.NONE,
        xscrollcommand=horizontal_scrollbar.set,  # Configure horizontal scrolling
        yscrollcommand=vertical_scrollbar.set      # Configure vertical scrolling
    )

    # Grid layout for the widgets in the table frame
    text_widget.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
    horizontal_scrollbar.grid(row=2, column=0, sticky=tk.EW)
    vertical_scrollbar.grid(row=0, column=1, sticky=tk.NS)

    # Scrollbar Configuration
    horizontal_scrollbar.config(command=text_widget.xview)
    vertical_scrollbar.config(command=text_widget.yview)

    # Entry fields and buttons for search criteria
    id_label = ttk.Label(search_frame, text="ID:")
    id_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    id_entry = ttk.Entry(search_frame)
    id_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

    # Search button for searching by ID
    search_id_button = ttk.Button(search_frame, text="Search by ID", command=lambda: search_by_id(id_entry.get()))
    search_id_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky=tk.W)

    # Labels and entry fields for search inputs
    date_label = ttk.Label(search_frame, text="Date (YYYY-MM-DD):")
    date_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    date_entry = ttk.Entry(search_frame)
    date_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    start_time_label = ttk.Label(search_frame, text="Start Time (HH:MM:SS):")
    start_time_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    start_time_entry = ttk.Entry(search_frame)
    start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    end_time_label = ttk.Label(search_frame, text="End Time (HH:MM:SS):")
    end_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    end_time_entry = ttk.Entry(search_frame)
    end_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    # Search button for date and time search
    search_button = ttk.Button(search_frame, text="Search", command=lambda: search_by_date_and_time(
        date_entry.get(),
        start_time_entry.get(),
        end_time_entry.get()
    ))
    search_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky=tk.W)

    # Display the results in the scrolled text widget
    cursor.execute("SELECT * FROM staff_swipes")
    table_data = cursor.fetchall()

    # Prepare the table data for display
    table_text = "\n".join(" | ".join(map(str, row)) for row in table_data)

    # Insert the table data into the scrolled text widget
    text_widget.insert(tk.END, table_text)

    # Disable editing
    text_widget.config(state=tk.DISABLED)

    # Vertical scrollbar for the text widget
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=text_widget.yview)
    scrollbar.grid(row=0, column=1, sticky=tk.NS)

    # Configuring the text widget to work with the scrollbar
    text_widget.config(yscrollcommand=scrollbar.set)

    # Frame for student status controls
    status_frame = ttk.Frame(table_frame)
    status_frame.grid(row=1, column=0, columnspan=2, pady=10)

    # Create a label and radio buttons for status selection
    status_label = ttk.Label(status_frame, text="Select student status:")
    status_label.grid(row=0, column=0, padx=5)

    status_var = tk.StringVar()
    status_var.set("activated")  # Default status selection
    activated_radio = ttk.Radiobutton(status_frame, text="Activated", variable=status_var, value="activated")
    suspended_radio = ttk.Radiobutton(status_frame, text="Suspended", variable=status_var, value="suspended")
    activated_radio.grid(row=0, column=1, padx=5)
    suspended_radio.grid(row=0, column=2, padx=5)

    # List of students with checkboxes
    students = [(row[0], row[1]) for row in table_data]  # Assuming student_id is in column 0 and student_name in column 1
    student_checkboxes = []

    for i, (student_id, student_name) in enumerate(students):
        checkbox = ttk.Checkbutton(status_frame, text=student_name, variable=tk.IntVar(), onvalue=1, offvalue=0)
        checkbox.grid(row=i + 1, column=0, columnspan=3, padx=5, pady=2)
        student_checkboxes.append((student_id, checkbox))

    # Function to update student status --- Display is what I wanted, but doesn't actually update the database
    def update_student_status():
        new_status = status_var.get()

        for student_id, checkbox in student_checkboxes:
            if checkbox.get() == 1:
                # Update the status in the database
                cursor.execute("UPDATE staff_swipes SET status = %s WHERE student_id = %s", (new_status, student_id))
                conn.commit()

        # Refresh the table with updated data
        cursor.execute("SELECT * FROM staff_swipes")
        updated_table_data = cursor.fetchall()
        updated_table_text = "\n".join(" | ".join(map(str, row)) for row in updated_table_data)
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, updated_table_text)
        text_widget.config(state=tk.DISABLED)

    # Create a button to update student status
    update_button = ttk.Button(status_frame, text="Update Status", command=update_student_status)
    update_button.grid(row=len(students) + 1, column=0, columnspan=3, pady=10)
    table_data = cursor.fetchall()

    # Insert the table data into the scrolled text widget
    text_widget.insert(tk.END, table_text)

    # Configuring the text widget to work with the scrollbar
    text_widget.config(yscrollcommand=scrollbar.set)

    # Create a frame for student status controls
    status_frame = ttk.Frame(table_frame)
    status_frame.grid(row=1, column=0, columnspan=2, pady=10)

    # List of students with checkboxes
    students = [(row[0], row[1]) for row in table_data]  # Assuming student_id is in column 0 and student_name in column 1
    student_checkboxes = []

    for i, (student_id, student_name) in enumerate(students):
        checkbox = ttk.Checkbutton(status_frame, text=student_name, variable=tk.IntVar(), onvalue=1, offvalue=0)
        checkbox.grid(row=i + 1, column=0, columnspan=3, padx=5, pady=2)
        student_checkboxes.append((student_id, checkbox))


# Function to get the current student status
def get_student_status(name, student_id):
    cursor.execute("SELECT status FROM staff_swipes WHERE student_name = %s AND student_id = %s", (name, student_id))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Function to update the student status
def update_student_status(name, student_id, new_status):
    cursor.execute("UPDATE staff_swipes SET status = %s WHERE student_name = %s AND student_id = %s", (new_status, name, student_id))
    conn.commit()

# Function to toggle the status
def toggle_status():
    student_name = name_entry.get()
    student_id = id_entry.get()

    # Check the current status
    current_status = get_student_status(student_name, student_id)

    if current_status is None:
        messagebox.showerror("Error", "Student not found in the database.")
    else:
        new_status = "suspended" if current_status == "activated" else "activated"
        update_student_status(student_name, student_id, new_status)
        messagebox.showinfo("Status Updated", f"Status for {student_name} with ID {student_id} is now {new_status}.")

# Shows Database if ID is found, denies access otherwise
def display_staff_swipes():
    # Check the status of the current user (staff or student)
    current_user_id = id_entry.get()

    cursor.execute("SELECT job FROM staff_swipes WHERE student_id = %s", (current_user_id,))
    user_status = cursor.fetchone()

    if user_status and user_status[0] == 'staff':
        # User is staff; allow access to the staff_swipes table
        cursor.execute("SELECT * FROM staff_swipes")
        result = cursor.fetchall()

        for row in result:
            print(row)  # Display the table data
    else:
        print("Access Denied")

# Function to search by ID
def search_by_id(id_number):
    global text_widget  # Access the global text_widget

    # Remove leading and trailing spaces from the entered ID
    id_number = id_number.strip()

    # Check if the entered ID is not empty
    if id_number:
        # Query the database to retrieve records matching the entered ID
        cursor.execute("SELECT * FROM staff_swipes WHERE student_id = %s", (id_number,))
        search_result = cursor.fetchall()

        # Check if any records were found
        if search_result:
            # Prepare the table data for display
            table_text = "\n".join(" | ".join(map(str, row)) for row in search_result)

            # Update the text_widget with the search results
            text_widget.config(state=tk.NORMAL)  # Enable editing
            text_widget.delete(1.0, tk.END)       # Clear the existing content
            text_widget.insert(tk.END, table_text) # Insert the search results
            text_widget.config(state=tk.DISABLED)  # Disable editing
        else:
            # No matching records found
            text_widget.config(state=tk.NORMAL)    # Enable editing
            text_widget.delete(1.0, tk.END)         # Clear the existing content
            text_widget.insert(tk.END, "No matching records found.")
            text_widget.config(state=tk.DISABLED)  # Disable editing
    else:
        # ID entry is empty, display a message
        text_widget.config(state=tk.NORMAL)    # Enable editing
        text_widget.delete(1.0, tk.END)         # Clear the existing content
        text_widget.insert(tk.END, "Please enter an ID.")
        text_widget.config(state=tk.DISABLED)  # Disable editing


# Function to search by date and time range --- DOESN'T WORK
def search_by_date_and_time(date_str, start_time_str, end_time_str):
    global text_widget  # Access the global text_widget

    # Remove leading and trailing spaces from the entered strings
    date_str = date_str.strip()
    start_time_str = start_time_str.strip()
    end_time_str = end_time_str.strip()

    try:
        # Parse the entered date string into a datetime object
        search_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Manually parse the entered time strings into datetime objects
        start_time_parts = start_time_str.split(':')
        end_time_parts = end_time_str.split(':')

        # Create datetime objects with the parsed time components
        start_time = datetime(1, 1, 1, int(start_time_parts[0]), int(start_time_parts[1]), int(start_time_parts[2]))
        end_time = datetime(1, 1, 1, int(end_time_parts[0]), int(end_time_parts[1]), int(end_time_parts[2]))

        # Combine the date and time to create datetime objects for the search range
        start_datetime = datetime.combine(search_date, start_time.time())
        end_datetime = datetime.combine(search_date, end_time.time())

        # Query the database to retrieve records within the specified date and time range
        cursor.execute("SELECT * FROM student_swipes WHERE swipe_time >= %s AND swipe_time <= %s", (start_datetime, end_datetime))
        search_result = cursor.fetchall()

        # Check if any records were found
        if search_result:
            # Prepare the table data for display
            table_text = "\n".join(" | ".join(map(str, row)) for row in search_result)

            # Update the text_widget with the search results
            text_widget.config(state=tk.NORMAL)  # Enable editing
            text_widget.delete(1.0, tk.END)       # Clear the existing content
            text_widget.insert(tk.END, table_text) # Insert the search results
            text_widget.config(state=tk.DISABLED)  # Disable editing
        else:
            # No matching records found
            text_widget.config(state=tk.NORMAL)    # Enable editing
            text_widget.delete(1.0, tk.END)         # Clear the existing content
            text_widget.insert(tk.END, "No matching records found.")
            text_widget.config(state=tk.DISABLED)  # Disable editing
    except ValueError:
        # Invalid input format entered
        text_widget.config(state=tk.NORMAL)    # Enable editing
        text_widget.delete(1.0, tk.END)         # Clear the existing content
        text_widget.insert(tk.END, "Invalid input format. Please enter valid dates and times.")
        text_widget.config(state=tk.DISABLED)  # Disable editing

#---------------------------------------------------------------------------------

# Create the main application window
app = tk.Tk()
app.title("SUN Lab Database")

# Create and place widgets in the window
id_label = tk.Label(app, text="Enter ID:")
id_label.pack()
id_entry = tk.Entry(app)
id_entry.pack()

check_button = tk.Button(app, text="Check Access", command=check_id)
check_button.pack()

result_label = tk.Label(app, text="")
result_label.pack()

display_staff_swipes()

# Start the Tkinter event loop
app.mainloop()

# Close the cursor and connection
cursor.close()
conn.close()


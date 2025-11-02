import tkinter as tk
from tkinter import ttk
import sys

def create_white_window():
    """Create a window with white background"""
    # Create the main window
    root = tk.Tk()
    
    # Set window title
    root.title("White Background Window")
    
    # Set window size
    root.geometry("800x600")
    
    # Set white background
    root.configure(bg='white')
    
    # Make the window resizable
    root.resizable(True, True)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Add some content to make it visible
    label = tk.Label(
        root, 
        text="This window has a white background!", 
        font=("Arial", 16),
        bg='white',
        fg='black'
    )
    label.pack(pady=50)
    
    # Add a button
    button = tk.Button(
        root,
        text="Click me!",
        font=("Arial", 12),
        bg='lightgray',
        fg='black',
        command=lambda: print("Button clicked!")
    )
    button.pack(pady=20)
    
    # Add instructions
    instructions = tk.Label(
        root,
        text="Close this window or press Ctrl+C to exit",
        font=("Arial", 10),
        bg='white',
        fg='gray'
    )
    instructions.pack(pady=10)
    
    return root

def main():
    """Main function to run the white window"""
    try:
        # Create and show the window
        window = create_white_window()
        
        # Start the GUI event loop
        window.mainloop()
        
    except KeyboardInterrupt:
        print("\nWindow closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating window: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Main GUI application for Airbnb Scraper
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
import pandas as pd

from scraper import AirbnbScraper
from config import CITIES, CSV_FILENAME, EXCEL_FILENAME
from utils import save_to_csv, save_to_excel, create_output_folder

class AirbnbScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Airbnb Scraper with GUI")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.scraper = None
        self.is_scraping = False
        self.scraped_data = []
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Airbnb Listing Scraper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # City selection
        ttk.Label(main_frame, text="Select Cities:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # City listbox with scrollbar
        city_frame = ttk.Frame(main_frame)
        city_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        city_frame.columnconfigure(0, weight=1)
        
        self.city_listbox = tk.Listbox(city_frame, selectmode=tk.MULTIPLE, height=8)
        city_scrollbar = ttk.Scrollbar(city_frame, orient=tk.VERTICAL, command=self.city_listbox.yview)
        self.city_listbox.configure(yscrollcommand=city_scrollbar.set)
        
        self.city_listbox.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        city_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Populate city listbox
        for city in CITIES:
            self.city_listbox.insert(tk.END, city)
        
        # Select all cities by default
        self.city_listbox.select_set(0, tk.END)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.select_all_btn = ttk.Button(button_frame, text="Select All", command=self.select_all_cities)
        self.select_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_selection_btn = ttk.Button(button_frame, text="Clear Selection", command=self.clear_city_selection)
        self.clear_selection_btn.pack(side=tk.LEFT, padx=5)
        
        # Scraping options
        options_frame = ttk.LabelFrame(main_frame, text="Scraping Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Use Selenium option
        self.use_selenium_var = tk.BooleanVar(value=True)
        selenium_check = ttk.Checkbutton(options_frame, text="Use Selenium (recommended)", 
                                        variable=self.use_selenium_var)
        selenium_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Output format
        ttk.Label(options_frame, text="Output Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_format_var = tk.StringVar(value="both")
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(format_frame, text="CSV", variable=self.output_format_var, 
                       value="csv").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Excel", variable=self.output_format_var, 
                       value="excel").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Both", variable=self.output_format_var, 
                       value="both").pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Progress Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Start Scraping", 
                                   command=self.start_scraping, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Scraping", 
                                  command=self.stop_scraping, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(control_frame, text="Export Data", 
                                    command=self.export_data, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_btn = ttk.Button(control_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, pady=10, sticky=tk.W+tk.E)
    
    def select_all_cities(self):
        """Select all cities in the listbox"""
        self.city_listbox.select_set(0, tk.END)
    
    def clear_city_selection(self):
        """Clear city selection"""
        self.city_listbox.selection_clear(0, tk.END)
    
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Start the scraping process"""
        selected_indices = self.city_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one city to scrape.")
            return
        
        selected_cities = [CITIES[i] for i in selected_indices]
        
        self.is_scraping = True
        self.scraped_data = []
        
        # Update UI state
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)
        
        self.log_message(f"Starting to scrape {len(selected_cities)} cities...")
        self.update_progress(0)
        
        # Start scraping in a separate thread
        scraping_thread = threading.Thread(target=self.scraping_worker, args=(selected_cities,))
        scraping_thread.daemon = True
        scraping_thread.start()
    
    def scraping_worker(self, cities):
        """Worker function for scraping (runs in separate thread)"""
        try:
            # Initialize scraper
            self.scraper = AirbnbScraper(use_selenium=self.use_selenium_var.get())
            
            total_cities = len(cities)
            
            for i, city in enumerate(cities):
                if not self.is_scraping:
                    break
                
                self.log_message(f"Scraping city {i+1}/{total_cities}: {city}")
                
                try:
                    city_listings = self.scraper.scrape_city_listings(city, self.log_message)
                    self.scraped_data.extend(city_listings)
                    
                    self.log_message(f"Found {len(city_listings)} listings for {city}")
                    
                except Exception as e:
                    self.log_message(f"Error scraping {city}: {str(e)}")
                
                # Update progress
                progress = ((i + 1) / total_cities) * 100
                self.update_progress(progress)
            
            if self.is_scraping:
                self.log_message(f"Scraping completed! Total listings found: {len(self.scraped_data)}")
                
                # Auto-save data
                if self.scraped_data:
                    self.save_scraped_data()
            else:
                self.log_message("Scraping stopped by user.")
        
        except Exception as e:
            self.log_message(f"Scraping error: {str(e)}")
        
        finally:
            # Clean up
            # No close() method for AirbnbScraper
            
            # Update UI state
            self.root.after(0, self.scraping_finished)
    
    def scraping_finished(self):
        """Called when scraping is finished"""
        self.is_scraping = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.scraped_data:
            self.export_btn.config(state=tk.NORMAL)
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_scraping = False
        self.log_message("Stopping scraping...")
    
    def save_scraped_data(self):
        """Save scraped data to files"""
        if not self.scraped_data:
            return
        
        try:
            create_output_folder()
            
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            output_format = self.output_format_var.get()
            
            if output_format in ["csv", "both"]:
                csv_filename = f"airbnb_listings_{timestamp}.csv"
                save_to_csv(self.scraped_data, csv_filename)
                self.log_message(f"Data saved to CSV: {csv_filename}")
            
            if output_format in ["excel", "both"]:
                excel_filename = f"airbnb_listings_{timestamp}.xlsx"
                save_to_excel(self.scraped_data, excel_filename)
                self.log_message(f"Data saved to Excel: {excel_filename}")
            
        except Exception as e:
            self.log_message(f"Error saving data: {str(e)}")
    
    def export_data(self):
        """Export scraped data to user-selected location"""
        if not self.scraped_data:
            messagebox.showwarning("No Data", "No data available to export.")
            return
        
        output_format = self.output_format_var.get()
        
        try:
            if output_format == "csv":
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Save CSV file"
                )
                if filename:
                    df = pd.DataFrame(self.scraped_data)
                    df.to_csv(filename, index=False, encoding='utf-8')
                    self.log_message(f"Data exported to: {filename}")
            
            elif output_format == "excel":
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Save Excel file"
                )
                if filename:
                    df = pd.DataFrame(self.scraped_data)
                    df.to_excel(filename, index=False, engine='openpyxl')
                    self.log_message(f"Data exported to: {filename}")
            
            elif output_format == "both":
                # Save CSV
                csv_filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Save CSV file"
                )
                if csv_filename:
                    df = pd.DataFrame(self.scraped_data)
                    df.to_csv(csv_filename, index=False, encoding='utf-8')
                    self.log_message(f"CSV exported to: {csv_filename}")
                
                # Save Excel
                excel_filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Save Excel file"
                )
                if excel_filename:
                    df = pd.DataFrame(self.scraped_data)
                    df.to_excel(excel_filename, index=False, engine='openpyxl')
                    self.log_message(f"Excel exported to: {excel_filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set application icon (optional)
    try:
        # You can add an icon file here if you have one
        # root.iconbitmap("icon.ico")
        pass
    except:
        pass
    
    app = AirbnbScraperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_scraping:
            if messagebox.askokcancel("Quit", "Scraping is in progress. Do you want to quit?"):
                app.stop_scraping()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

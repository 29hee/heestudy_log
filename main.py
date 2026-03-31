from app import StyledDashboard, tk

if __name__ == "__main__":
    root = tk.Tk()
    app = StyledDashboard(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # Allow terminal Ctrl+C to exit without traceback spam.
        try:
            app.on_close()
        except Exception:
            pass



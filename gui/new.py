from app import StyledDashboard, tk

__all__ = ["tk", "StyledDashboard"]


if __name__ == "__main__":
    root = tk.Tk()
    app = StyledDashboard(root)
    root.mainloop()


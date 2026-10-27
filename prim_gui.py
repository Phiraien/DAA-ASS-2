import tkinter as tk
from tkinter import ttk
import heapq

# ---------------- GRAPH DATA ----------------
graph = {
    "A": [("B", 2), ("C", 3)],
    "B": [("A", 2), ("C", 1), ("D", 4)],
    "C": [("A", 3), ("B", 1), ("D", 5), ("E", 6)],
    "D": [("B", 4), ("C", 5), ("E", 2)],
    "E": [("C", 6), ("D", 2)]
}

positions = {
    "A": (90, 80),
    "B": (290, 60),
    "C": (190, 210),
    "D": (410, 180),
    "E": (490, 320)
}


class PrimVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Prim's Algorithm Visualizer")
        self.root.geometry("950x650")
        self.root.minsize(800, 580)
        self.root.configure(bg="#0b1020")

        self.visited = set()
        self.mst = []
        self.heap = []
        self.total = 0
        self.running = False
        self.after_id = None

        self.build_gui()
        self.reset()

    def build_gui(self):
        title = tk.Label(
            self.root, text="Prim's Algorithm Visualizer",
            font=("Segoe UI", 22, "bold"),
            fg="#4de0bd", bg="#0b1020"
        )
        title.pack(pady=(15, 3))

        subtitle = tk.Label(
            self.root, text="Minimum Spanning Tree · Greedy Algorithm",
            font=("Segoe UI", 10), fg="#91a0ba", bg="#0b1020"
        )
        subtitle.pack(pady=(0, 12))

        main = tk.Frame(self.root, bg="#0b1020")
        main.pack(fill="both", expand=True, padx=18, pady=5)

        self.canvas = tk.Canvas(
            main, width=580, height=410,
            bg="#121a2b", highlightthickness=1,
            highlightbackground="#29364d"
        )
        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 12))

        side = tk.Frame(main, bg="#121a2b", width=260)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)

        tk.Label(
            side, text="CONTROL PANEL", font=("Segoe UI", 10, "bold"),
            fg="#4de0bd", bg="#121a2b"
        ).pack(anchor="w", padx=15, pady=(17, 8))

        row = tk.Frame(side, bg="#121a2b")
        row.pack(fill="x", padx=15, pady=5)

        tk.Label(row, text="Start vertex", fg="#cbd5e1",
                 bg="#121a2b").pack(side="left")

        self.start_var = tk.StringVar(value="A")
        self.start_box = ttk.Combobox(
            row, textvariable=self.start_var, values=list(graph),
            state="readonly", width=5
        )
        self.start_box.pack(side="right")

        self.step_button = tk.Button(
            side, text="Step  →", command=self.step,
            bg="#1d3445", fg="white", activebackground="#28566a",
            activeforeground="white", relief="flat", font=("Segoe UI", 10, "bold")
        )
        self.step_button.pack(fill="x", padx=15, pady=(12, 5), ipady=5)

        self.play_button = tk.Button(
            side, text="▶  Play", command=self.toggle_play,
            bg="#4de0bd", fg="#071a1a", activebackground="#76efd2",
            relief="flat", font=("Segoe UI", 10, "bold")
        )
        self.play_button.pack(fill="x", padx=15, pady=5, ipady=5)

        tk.Button(
            side, text="↻  Reset", command=self.reset,
            bg="#263248", fg="white", activebackground="#354761",
            activeforeground="white", relief="flat",
            font=("Segoe UI", 10, "bold")
        ).pack(fill="x", padx=15, pady=5, ipady=5)

        tk.Label(
            side, text="LIVE RESULTS", font=("Segoe UI", 10, "bold"),
            fg="#4de0bd", bg="#121a2b"
        ).pack(anchor="w", padx=15, pady=(20, 8))

        self.weight_label = self.make_info(side, "Total MST weight", "0")
        self.edge_label = self.make_info(side, "Edges selected", "0 / 4")
        self.vertex_label = self.make_info(side, "Visited vertices", "1 / 5")

        tk.Label(
            side, text="CURRENT STEP", font=("Segoe UI", 10, "bold"),
            fg="#4de0bd", bg="#121a2b"
        ).pack(anchor="w", padx=15, pady=(18, 7))

        self.message = tk.Label(
            side, text="Ready to start.",
            fg="#cbd5e1", bg="#121a2b", wraplength=220,
            justify="left", font=("Segoe UI", 10)
        )
        self.message.pack(anchor="w", padx=15)

        bottom = tk.Frame(self.root, bg="#0b1020")
        bottom.pack(fill="x", padx=20, pady=(7, 14))

        tk.Label(
            bottom, text="MST EDGES", font=("Segoe UI", 10, "bold"),
            fg="#4de0bd", bg="#0b1020"
        ).pack(anchor="w")

        self.result_text = tk.Label(
            bottom, text="No edges selected yet.",
            fg="#d5deee", bg="#0b1020", font=("Consolas", 10),
            justify="left", anchor="w"
        )
        self.result_text.pack(fill="x", pady=(4, 0))

    def make_info(self, parent, title, value):
        frame = tk.Frame(parent, bg="#0c1423", highlightbackground="#29364d",
                         highlightthickness=1)
        frame.pack(fill="x", padx=15, pady=4)
        tk.Label(frame, text=title, fg="#91a0ba", bg="#0c1423",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=9, pady=(6, 0))
        value_label = tk.Label(frame, text=value, fg="#4de0bd",
                               bg="#0c1423", font=("Segoe UI", 16, "bold"))
        value_label.pack(anchor="w", padx=9, pady=(0, 6))
        return value_label

    def reset(self):
        self.stop_play()
        self.visited = set()
        self.mst = []
        self.heap = []
        self.total = 0

        start = self.start_var.get()
        heapq.heappush(self.heap, (0, start, None))
        self.message.config(text=f"Start at vertex {start}. Choose the lowest-weight edge leading to an unvisited vertex.")
        self.update_view()

    def step(self):
        if not self.heap:
            self.message.config(text="Algorithm complete! All vertices are connected.")
            self.update_view()
            self.stop_play()
            return

        weight, node, parent = heapq.heappop(self.heap)

        while node in self.visited:
            if not self.heap:
                self.message.config(text="Algorithm complete.")
                self.update_view()
                self.stop_play()
                return
            weight, node, parent = heapq.heappop(self.heap)

        self.visited.add(node)

        if parent is not None:
            self.mst.append((parent, node, weight))
            self.total += weight
            self.message.config(
                text=f"Selected edge {parent} - {node} with weight {weight}.\n\n"
                     f"Vertex {node} is now visited. Total weight = {self.total}."
            )
        else:
            self.message.config(text=f"Starting vertex {node} is now visited.")

        for neighbor, cost in graph[node]:
            if neighbor not in self.visited:
                heapq.heappush(self.heap, (cost, neighbor, node))

        self.update_view()

        if len(self.visited) == len(graph):
            self.message.config(
                text=f"MST complete! Total minimum weight = {self.total}."
            )
            self.stop_play()

    def toggle_play(self):
        if self.running:
            self.stop_play()
        else:
            if len(self.visited) == len(graph):
                self.reset()
            self.running = True
            self.play_button.config(text="Ⅱ  Pause")
            self.auto_step()

    def auto_step(self):
        if not self.running:
            return
        self.step()
        if self.running and len(self.visited) < len(graph):
            self.after_id = self.root.after(1000, self.auto_step)
        else:
            self.stop_play()

    def stop_play(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if hasattr(self, "play_button"):
            self.play_button.config(text="▶  Play")

    def update_view(self):
        self.canvas.delete("all")

        # Draw all graph edges and their weights.
        for u in graph:
            for v, weight in graph[u]:
                if u < v:  # Draw each undirected edge once.
                    x1, y1 = positions[u]
                    x2, y2 = positions[v]
                    selected = any(
                        {a, b} == {u, v} for a, b, _ in self.mst
                    )
                    color = "#4de0bd" if selected else "#53617a"
                    width = 4 if selected else 2
                    self.canvas.create_line(
                        x1, y1, x2, y2, fill=color, width=width
                    )
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    self.canvas.create_rectangle(
                        mx - 12, my - 12, mx + 12, my + 12,
                        fill="#121a2b", outline=""
                    )
                    self.canvas.create_text(
                        mx, my, text=str(weight),
                        fill="#e5edf8", font=("Segoe UI", 11, "bold")
                    )

        # Draw vertices on top of the edges.
        for node, (x, y) in positions.items():
            if node in self.visited:
                fill, outline = "#123d3a", "#4de0bd"
            else:
                fill, outline = "#1a2941", "#70819f"

            self.canvas.create_oval(
                x - 24, y - 24, x + 24, y + 24,
                fill=fill, outline=outline, width=3
            )
            self.canvas.create_text(
                x, y, text=node, fill="white",
                font=("Segoe UI", 14, "bold")
            )

        self.weight_label.config(text=str(self.total))
        self.edge_label.config(text=f"{len(self.mst)} / {len(graph) - 1}")
        self.vertex_label.config(text=f"{len(self.visited)} / {len(graph)}")

        if self.mst:
            text = "    ".join(
                f"{u}-{v} ({w})" for u, v, w in self.mst
            )
            self.result_text.config(text=text)
        else:
            self.result_text.config(text="No edges selected yet.")

        if len(self.visited) == len(graph):
            self.step_button.config(state="disabled")
        else:
            self.step_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = PrimVisualizer(root)
    root.mainloop()

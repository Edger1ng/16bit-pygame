import pygame
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random

# Configuration
TILE_SIZE = 20
MAP_COLS = 25
MAP_ROWS = 15
WALL_COLOR = (60, 60, 80)
PATH_COLOR = (40, 40, 50)

class MapEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tilemap Editor")
        self.root.geometry("1200x800")
        
        # Map data
        self.map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.traps = set()
        self.portals = []
        
        # Drawing state
        self.current_tool = "wall"  
        self.drawing = False
        

        pygame.init()
        
        self.setup_ui()
        
    def setup_ui(self):

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        

        tools_frame = ttk.LabelFrame(left_panel, text="Tools")
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tool_var = tk.StringVar(value="wall")
        tools = [
            ("Wall", "wall", WALL_COLOR),
            ("Path", "path", PATH_COLOR),
            ("Trap", "trap", (200, 0, 0)),
            ("Portal", "portal", (100, 255, 255))
        ]
        
        for name, value, color in tools:
            rb = ttk.Radiobutton(tools_frame, text=name, variable=self.tool_var, value=value)
            rb.pack(anchor=tk.W, padx=5, pady=2)
        

        ops_frame = ttk.LabelFrame(left_panel, text="Map Operations")
        ops_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(ops_frame, text="Clear All", command=self.clear_map).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(ops_frame, text="Fill Walls", command=self.fill_walls).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(ops_frame, text="Generate Maze", command=self.generate_maze).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(ops_frame, text="Random Traps", command=self.add_random_traps).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(ops_frame, text="Random Portals", command=self.add_random_portals).pack(fill=tk.X, padx=5, pady=2)
        

        code_frame = ttk.LabelFrame(left_panel, text="Code Generation")
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(code_frame, text="Generate Code", command=self.generate_code).pack(fill=tk.X, padx=5, pady=2)
        

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        

        map_frame = ttk.LabelFrame(right_panel, text="Map Editor")
        map_frame.pack(fill=tk.X, pady=(0, 10))
        

        self.map_canvas = tk.Canvas(map_frame, width=MAP_COLS*TILE_SIZE, height=MAP_ROWS*TILE_SIZE, bg='black')
        self.map_canvas.pack(padx=10, pady=10)
        
        self.map_canvas.bind("<Button-1>", self.on_click)
        self.map_canvas.bind("<B1-Motion>", self.on_drag)
        self.map_canvas.bind("<ButtonRelease-1>", self.on_release)

        code_output_frame = ttk.LabelFrame(right_panel, text="Generated Code")
        code_output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.code_text = scrolledtext.ScrolledText(code_output_frame, height=15, font=("Consolas", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        

        self.draw_map()
        
    def get_tile_from_coords(self, x, y):
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        if 0 <= tile_x < MAP_COLS and 0 <= tile_y < MAP_ROWS:
            return tile_x, tile_y
        return None, None
    
    def on_click(self, event):
        self.drawing = True
        self.apply_tool(event.x, event.y)
    
    def on_drag(self, event):
        if self.drawing:
            self.apply_tool(event.x, event.y)
    
    def on_release(self, event):
        self.drawing = False
    
    def apply_tool(self, x, y):
        tile_x, tile_y = self.get_tile_from_coords(x, y)
        if tile_x is None:
            return
        
        tool = self.tool_var.get()
        
        if tool == "wall":
            self.map_data[tile_y][tile_x] = 1
            self.traps.discard((tile_x, tile_y))
            if (tile_x, tile_y) in self.portals:
                self.portals.remove((tile_x, tile_y))
        elif tool == "path":
            self.map_data[tile_y][tile_x] = 0
        elif tool == "trap":
            if self.map_data[tile_y][tile_x] == 0:  
                self.traps.add((tile_x, tile_y))
                if (tile_x, tile_y) in self.portals:
                    self.portals.remove((tile_x, tile_y))
        elif tool == "portal":
            if self.map_data[tile_y][tile_x] == 0:  
                if (tile_x, tile_y) not in self.portals:
                    self.portals.append((tile_x, tile_y))
                self.traps.discard((tile_x, tile_y))
        
        self.draw_map()
    
    def draw_map(self):
        self.map_canvas.delete("all")
        
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                x1, y1 = x * TILE_SIZE, y * TILE_SIZE
                x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
                
                if self.map_data[y][x] == 1: 
                    color = "#3c3c50"
                    self.map_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#505064")
                else:  
                    color = "#282832"
                    self.map_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#404040")
                

                if (x, y) in self.traps:
                    center_x, center_y = x1 + TILE_SIZE//2, y1 + TILE_SIZE//2
                    self.map_canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5, 
                                              fill="#c80000", outline="#ff0000")
                

                if (x, y) in self.portals:
                    center_x, center_y = x1 + TILE_SIZE//2, y1 + TILE_SIZE//2
                    self.map_canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5, 
                                              fill="#64ffff", outline="#00ffff")
    
    def clear_map(self):
        self.map_data = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.traps.clear()
        self.portals.clear()
        self.draw_map()
    
    def fill_walls(self):
        self.map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.traps.clear()
        self.portals.clear()
        self.draw_map()
    
    def generate_maze(self):
        self.map_data = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.traps.clear()
        self.portals.clear()
        
        def carve_passages(cx, cy):
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < MAP_COLS-1 and 0 < ny < MAP_ROWS-1:
                    if self.map_data[ny][nx] == 1:
                        self.map_data[cy + dy//2][cx + dx//2] = 0
                        self.map_data[ny][nx] = 0
                        carve_passages(nx, ny)
        
        self.map_data[1][1] = 0
        carve_passages(1, 1)
        self.map_data[MAP_ROWS-2][MAP_COLS-2] = 0
        
        self.draw_map()
    
    def get_free_tiles(self):
        free_tiles = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map_data[y][x] == 0:
                    free_tiles.append((x, y))
        return free_tiles
    
    def add_random_traps(self):
        free_tiles = self.get_free_tiles()
        if len(free_tiles) > 10:
            self.traps = set(random.sample(free_tiles, k=min(10, len(free_tiles))))
            # Remove portals that conflict with traps
            self.portals = [p for p in self.portals if p not in self.traps]
            self.draw_map()
    
    def add_random_portals(self):
        free_tiles = [t for t in self.get_free_tiles() if t not in self.traps]
        if len(free_tiles) > 4:
            self.portals = random.sample(free_tiles, k=min(4, len(free_tiles)))
            self.draw_map()
    
    def generate_code(self):
        map_str = "[\n" + ",\n".join(["    " + str(row) for row in self.map_data]) + "\n]"

        traps_str = "{" + ", ".join([f"({x}, {y})" for (x, y) in self.traps]) + "}"

        portals_str = "[" + ", ".join([f"({x}, {y})" for (x, y) in self.portals]) + "]"

        code = f'''# ---- Generated TileMap class ----'''
        print(map_str)
        print(traps_str)
        print(portals_str)
        
if __name__ == "__main__":
    editor = MapEditor()
    editor.root.mainloop()

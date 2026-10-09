import ezdxf
import math

class LandscapeLayout:
    def __init__(self, width, length):
        self.width = width
        self.length = length
        self.path_width = max(1.0, min(3.0, width * 0.15))
        
        # 1. Grass Boundary (Full area)
        self.grass_boundary = [(0,0), (width,0), (width,length), (0,length)]
        
        # 2. Seating / Pool Area (Center)
        sw = min(width * 0.5, 6.0)
        sl = min(length * 0.3, 6.0)
        self.seating_rect = [
            (width/2 - sw/2, length/2 - sl/2),
            (width/2 + sw/2, length/2 - sl/2),
            (width/2 + sw/2, length/2 + sl/2),
            (width/2 - sw/2, length/2 + sl/2)
        ]
        
        # 3. Main Pathway (Bottom to Seating, Seating to Top)
        self.path_rects = []
        # Bottom path
        self.path_rects.append([
            (width/2 - self.path_width/2, 0),
            (width/2 + self.path_width/2, 0),
            (width/2 + self.path_width/2, length/2 - sl/2),
            (width/2 - self.path_width/2, length/2 - sl/2)
        ])
        # Top path
        self.path_rects.append([
            (width/2 - self.path_width/2, length/2 + sl/2),
            (width/2 + self.path_width/2, length/2 + sl/2),
            (width/2 + self.path_width/2, length),
            (width/2 - self.path_width/2, length)
        ])
        
        # 4. Trees (Distributed along edges)
        self.trees = []
        tree_radius = max(0.5, min(1.5, width * 0.05))
        num_trees_side = max(3, int(length / 4))
        for i in range(1, num_trees_side):
            y = (length / num_trees_side) * i
            if y < length - 1:
                self.trees.append((tree_radius + 0.5, y, tree_radius)) # Left trees
                self.trees.append((width - tree_radius - 0.5, y, tree_radius)) # Right trees

def create_dxf(output_path, width, length):
    layout = LandscapeLayout(width, length)
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create layers with colors
    doc.layers.add("Grass", color=3)         # Green
    doc.layers.add("Pathways", color=8)      # Grey
    doc.layers.add("Seating", color=4)       # Cyan
    doc.layers.add("Trees", color=94)        # Dark Green

    # Draw Grass
    msp.add_lwpolyline(layout.grass_boundary, close=True, dxfattribs={'layer': 'Grass'})

    # Draw Pathways
    for rect in layout.path_rects:
        msp.add_lwpolyline(rect, close=True, dxfattribs={'layer': 'Pathways'})
        # Add hatch to pathways
        hatch = msp.add_hatch(color=8, dxfattribs={'layer': 'Pathways'})
        hatch.paths.add_polyline_path(rect, is_closed=True)

    # Draw Seating
    msp.add_lwpolyline(layout.seating_rect, close=True, dxfattribs={'layer': 'Seating'})
    hatch = msp.add_hatch(color=4, dxfattribs={'layer': 'Seating'})
    hatch.paths.add_polyline_path(layout.seating_rect, is_closed=True)
    
    # Draw Inner pool/table placeholder
    inner_seating = [
        (layout.seating_rect[0][0]+1, layout.seating_rect[0][1]+1),
        (layout.seating_rect[1][0]-1, layout.seating_rect[1][1]+1),
        (layout.seating_rect[2][0]-1, layout.seating_rect[2][1]-1),
        (layout.seating_rect[3][0]+1, layout.seating_rect[3][1]-1),
    ]
    msp.add_lwpolyline(inner_seating, close=True, dxfattribs={'layer': 'Seating'})

    # Draw Trees
    for tx, ty, r in layout.trees:
        msp.add_circle((tx, ty), radius=r, dxfattribs={'layer': 'Trees'})
        msp.add_circle((tx, ty), radius=r*0.2, dxfattribs={'layer': 'Trees'}) # trunk

    doc.saveas(output_path)
    return output_path

class OBJBuilder:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.current_group = "default"
        
    def set_group(self, name):
        self.current_group = name
        
    def add_vertex(self, x, y, z):
        self.vertices.append((x, y, z))
        return len(self.vertices)
        
    def add_face(self, v_indices):
        self.faces.append((self.current_group, v_indices))
        
    def add_box(self, x_min, x_max, y_min, y_max, z_min, z_max):
        v1 = self.add_vertex(x_min, y_min, z_min)
        v2 = self.add_vertex(x_max, y_min, z_min)
        v3 = self.add_vertex(x_max, y_max, z_min)
        v4 = self.add_vertex(x_min, y_max, z_min)
        v5 = self.add_vertex(x_min, y_min, z_max)
        v6 = self.add_vertex(x_max, y_min, z_max)
        v7 = self.add_vertex(x_max, y_max, z_max)
        v8 = self.add_vertex(x_min, y_max, z_max)
        
        self.add_face([v1, v2, v3, v4]) # bottom
        self.add_face([v5, v6, v7, v8]) # top
        self.add_face([v1, v2, v6, v5]) # front
        self.add_face([v2, v3, v7, v6]) # right
        self.add_face([v3, v4, v8, v7]) # back
        self.add_face([v4, v1, v5, v8]) # left

    def add_cylinder(self, cx, cy, z_min, z_max, radius, segments=8):
        bottom_vs = []
        top_vs = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            bottom_vs.append(self.add_vertex(x, y, z_min))
            top_vs.append(self.add_vertex(x, y, z_max))
            
        self.add_face(bottom_vs[::-1]) # bottom
        self.add_face(top_vs) # top
        for i in range(segments):
            next_i = (i + 1) % segments
            self.add_face([bottom_vs[i], bottom_vs[next_i], top_vs[next_i], top_vs[i]])

    def add_cone(self, cx, cy, z_min, z_max, radius, segments=8):
        bottom_vs = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            bottom_vs.append(self.add_vertex(x, y, z_min))
            
        top_v = self.add_vertex(cx, cy, z_max)
        self.add_face(bottom_vs[::-1]) # bottom
        for i in range(segments):
            next_i = (i + 1) % segments
            self.add_face([bottom_vs[i], bottom_vs[next_i], top_v])

    def export(self, path):
        with open(path, "w") as f:
            f.write("# Al-Qannas Landscape - 3D Export\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")
            
            curr_g = None
            for g, face in self.faces:
                if g != curr_g:
                    f.write(f"g {g}\n")
                    curr_g = g
                f.write("f " + " ".join(str(idx) for idx in face) + "\n")

def create_obj(output_path, width, length):
    layout = LandscapeLayout(width, length)
    obj = OBJBuilder()
    
    # Grass (Ground)
    obj.set_group("Grass")
    obj.add_box(0, width, 0, length, 0.0, 0.02)
    
    # Pathways
    obj.set_group("Pathways")
    for rect in layout.path_rects:
        x_min = rect[0][0]
        x_max = rect[1][0]
        y_min = rect[0][1]
        y_max = rect[2][1]
        obj.add_box(x_min, x_max, y_min, y_max, 0.02, 0.05)
        
    # Seating Area
    obj.set_group("Seating_Area")
    x_min = layout.seating_rect[0][0]
    x_max = layout.seating_rect[1][0]
    y_min = layout.seating_rect[0][1]
    y_max = layout.seating_rect[2][1]
    # Platform
    obj.add_box(x_min, x_max, y_min, y_max, 0.02, 0.2)
    
    # Inner block (Table or Pool)
    obj.set_group("Seating_Furniture")
    obj.add_box(x_min+1, x_max-1, y_min+1, y_max-1, 0.2, 0.7)
    
    # Trees
    for i, (tx, ty, r) in enumerate(layout.trees):
        # Trunk
        obj.set_group(f"Tree_Trunk_{i}")
        obj.add_cylinder(tx, ty, 0.0, 1.5, r*0.2, segments=8)
        # Leaves (Cone)
        obj.set_group(f"Tree_Leaves_{i}")
        obj.add_cone(tx, ty, 1.0, 3.5, r, segments=12)

    obj.export(output_path)
    return output_path

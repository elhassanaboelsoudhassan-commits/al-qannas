import ezdxf
import os

def create_dxf(output_path, width, length):
    """
    Generate a DXF file with standard layers.
    For demonstration, we draw simple boundary and placeholder shapes on layers.
    """
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create layers
    doc.layers.add("Walkways", color=7)      # الممرات
    doc.layers.add("Trees", color=3)         # الأشجار
    doc.layers.add("Grass", color=3)         # العشب
    doc.layers.add("Seating_Areas", color=1) # الجلسات

    # Draw boundary
    msp.add_lwpolyline([(0, 0), (width, 0), (width, length), (0, length), (0, 0)])

    # Add placeholder walkway (الممرات)
    msp.add_line((width * 0.1, 0), (width * 0.1, length), dxfattribs={'layer': 'Walkways'})
    msp.add_line((width * 0.2, 0), (width * 0.2, length), dxfattribs={'layer': 'Walkways'})

    # Add placeholder grass (العشب)
    msp.add_lwpolyline([(width * 0.3, length * 0.1), (width * 0.9, length * 0.1), 
                        (width * 0.9, length * 0.4), (width * 0.3, length * 0.4)], 
                       close=True, dxfattribs={'layer': 'Grass'})

    # Add placeholder seating area (الجلسات)
    msp.add_lwpolyline([(width * 0.4, length * 0.6), (width * 0.8, length * 0.6), 
                        (width * 0.8, length * 0.9), (width * 0.4, length * 0.9)], 
                       close=True, dxfattribs={'layer': 'Seating_Areas'})

    # Add placeholder trees (الأشجار)
    msp.add_circle((width * 0.5, length * 0.25), radius=width*0.05, dxfattribs={'layer': 'Trees'})
    msp.add_circle((width * 0.7, length * 0.25), radius=width*0.05, dxfattribs={'layer': 'Trees'})

    doc.saveas(output_path)
    return output_path

def create_obj(output_path, width, length):
    """
    Generate an OBJ file for 3D compatibility in SketchUp and Planner 5D.
    For demonstration, creates a 3D plane (ground) and some basic blocks for elements.
    """
    # Simple OBJ structure
    obj_content = []
    obj_content.append("# Al-Qannas Landscape - 3D Export")
    obj_content.append("o LandscapeModel")
    
    # Ground plane (Grass) - y is up in OBJ typically, but we use z as up for Sketchup
    # V: x, y, z
    obj_content.append(f"v 0.0 0.0 0.0")
    obj_content.append(f"v {width} 0.0 0.0")
    obj_content.append(f"v {width} {length} 0.0")
    obj_content.append(f"v 0.0 {length} 0.0")
    
    # Simple block for Seating area (Extruded)
    h = 2.0 # height
    obj_content.append(f"v {width*0.4} {length*0.6} 0.0")
    obj_content.append(f"v {width*0.8} {length*0.6} 0.0")
    obj_content.append(f"v {width*0.8} {length*0.9} 0.0")
    obj_content.append(f"v {width*0.4} {length*0.9} 0.0")
    
    obj_content.append(f"v {width*0.4} {length*0.6} {h}")
    obj_content.append(f"v {width*0.8} {length*0.6} {h}")
    obj_content.append(f"v {width*0.8} {length*0.9} {h}")
    obj_content.append(f"v {width*0.4} {length*0.9} {h}")

    # Faces
    obj_content.append("g Grass")
    obj_content.append("f 1 2 3 4") # Ground
    
    obj_content.append("g Seating_Area")
    # Bottom (5,6,7,8), Top (9,10,11,12)
    obj_content.append("f 5 6 7 8")
    obj_content.append("f 9 10 11 12")
    obj_content.append("f 5 6 10 9")
    obj_content.append("f 6 7 11 10")
    obj_content.append("f 7 8 12 11")
    obj_content.append("f 8 5 9 12")

    with open(output_path, "w") as f:
        f.write("\n".join(obj_content))
    
    return output_path

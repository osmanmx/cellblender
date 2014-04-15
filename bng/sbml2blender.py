'''
Spatial SBML importer
Rohan Arepally
Jose Juan Tapia
'''

from cellblender.utils import preserve_selection_use_operator
 
import sys
import bpy
import os
import xml.etree.ElementTree as ET
import shutil

# Read all of the CSG Object types in a SBML file 
def readSMBLFileCSGObject(filePath):
    tree = ET.parse(filePath)
    root = tree.getroot()
    objects = []
    ns = {'spatial': 'http://www.sbml.org/sbml/level3/version1/spatial/version1'}
    
    for object in root.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}csgObject'):
        id = object.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}spatialId')
        
        for csgPrimitive in object.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}csgPrimitive'):
            type        = csgPrimitive.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}primitiveType')
        
        for csgScale in object.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}csgScale'):
            scaleX      = csgScale.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}scaleX')
            scaleY      = csgScale.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}scaleY')
            scaleZ      = csgScale.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}scaleZ')
        
        for csgRotation in object.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}csgRotation'):
            rotateAxisX = csgRotation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}rotateAxisX')
            rotateAxisY = csgRotation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}rotateAxisY')
            rotateAxisZ = csgRotation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}rotateAxisZ')
        
        for csgTranslation in object.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}csgTranslation'):
            translateX  = csgTranslation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}translateX')
            translateY  = csgTranslation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}translateY')
            translateZ  = csgTranslation.get('{http://www.sbml.org/sbml/level3/version1/spatial/version1}translateZ')
        '''
        print("id: "          + id)
        print("type: "        + type)
        print("scaleX: "      + scaleX)
        print("scaleY: "      + scaleY)
        print("scaleZ: "      + scaleZ)
        print("rotateAxisX: " + rotateAxisX)
        print("rotateAxisY: " + rotateAxisY)
        print("rotateAxisZ: " + rotateAxisZ)
        print("translateX: "  + translateX)
        print("translateY: "  + translateY)
        print("translateZ: "  + translateZ)
	'''
        objects += [[id, type, scaleX, scaleY, scaleZ, rotateAxisX, rotateAxisY, rotateAxisZ,translateX, translateY, translateZ]]
    return objects

# read parametric object data
def readSMBLFileParametricObject(filepath):
    print("\n")
    print("reading parametric SBML\n")
    tree = ET.parse(filepath)
    root = tree.getroot()
    objects = []
    ns = {'spatial': 'http://www.sbml.org/sbml/level3/version1/spatial/version1'}
    
    for object in root.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}ParaObject'):
        id = object.get('spatialID')
        
        for polygonObject in object.iter('{http://www.sbml.org/sbml/level3/version1/spatial/version1}PolygonObject'):
            faces        = polygonObject.get('faces')
            vertices     = polygonObject.get('pointIndex')
        
        print("id: "       + id)
        
        #print("faces: "    + faces)
        #print("vertices: " + vertices)
        faces = faces[1:-1]
        faces = faces.split(";")
        temp = []
        for element in faces:
            face = element.split()
            for i in range(0,len(face)):
                face[i] = int(face[i])-1
            temp += [face]
        faces = temp
    
        vertices = vertices[1:-1]
        vertices = vertices.split(";")
        temp = []
        for element in vertices:
            vertice = element.split()
            for i in range(0, len(vertice)):
                vertice[i] = float(vertice[i])
            temp += [vertice]
        vertices = temp
    
        objects += [[id, faces, vertices]]
    return objects

# all objects in blender scene are deleted. Should leave empty blender scene.
def resetScene():
    obj_list = [item.name for item in bpy.data.objects if item.type == "MESH"]
    
    for obj in obj_list:
    	bpy.data.objects[obj].select = True
    
    bpy.ops.object.delete()

# calculate the volume of a mesh 
def mesh_vol(mesh, t_mat):
    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co * t_mat
        tv1 = mesh.vertices[f.vertices[1]].co * t_mat
        tv2 = mesh.vertices[f.vertices[2]].co * t_mat
        x0 = tv0.x
        y0 = tv0.y
        z0 = tv0.z
        x1 = tv1.x
        y1 = tv1.y
        z1 = tv1.z
        x2 = tv2.x
        y2 = tv2.y
        z2 = tv2.z
        det = x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
        volume = volume + det
    
    volume = volume/6.0
    return(volume)

# a sphere with dimensions x,y,z is added to the blender scene
def generateSphere(name, size, loc, rot):
    pi = 3.1415
    bpy.ops.mesh.primitive_uv_sphere_add(location=(float(loc[0]),float(loc[1]),float(loc[2])), \
                                         rotation=(float(rot[0]),float(rot[1]),float(rot[2]) ))
    obj = bpy.data.objects[bpy.context.active_object.name]
    scn = bpy.context.scene
    me = obj.data
    obj.scale = (float(size[0])*0.25,float(size[1])*0.25,float(size[2])*0.2)
    obj.name = name    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

# generates a cube in blender scene with dimensions x,y,z
def generateCube(x,y,z):
    pi = 3.1415
    bpy.ops.mesh.primitive_cube_add(location=(float(loc[0]),float(loc[1]),float(loc[2])), \
                                    rotation=(float(rot[0])*(pi/180),float(rot[1])*(pi/180),float(rot[2])*(pi/180) ))
    obj = bpy.data.objects[bpy.context.active_object.name]
    scn = bpy.context.scene
    me = obj.data
    obj.scale = (float(size[0]),float(size[1]),float(size[2]))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all()
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.name = name
    return obj

# Approximation of the surface area of a sphere (Knud Thomsen's formula)
# dimensions x,y,z are in microns
def surface_area_sphere(x,y,z):
    p = 1.6075
    a = abs(x)
    b = abs(y)
    c = abs(z)
    first  = pow(a,p)*pow(b,p)
    second = pow(a,p)*pow(c,p)
    third  = pow(b,p)*pow(c,p)
    val    = ( (first + second + third)/3.0 )
    val    = pow(val, 1.0/p)
    return 4*(3.14)*val

# imports a mesh into the scene and returns the volume
def importMesh(name,directory):
    bpy.ops.import_scene.obj(filepath=directory)
    imported = bpy.context.selected_objects[0]
    imported.name = name
    imported.scale = (0.2, 0.2, 0.25)
    imported.rotation_euler = (0,0,0)
    return mesh_vol(imported.data, imported.matrix_world)

#generates mesh in blender using SBML file data
def generateMesh(objectData):
    verts = objectData[2]
    faces = objectData[1]
    id    = objectData[0]
    
    mesh_data = bpy.data.meshes.new(id)
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update(calc_edges=True)
    
    obj = bpy.data.objects.new(id, mesh_data)
    
    scene = bpy.context.scene
    scene.objects.link(obj)
    obj.select = True
    obj.rotation_euler = (0,0,0)
    obj.scale = (0.05, 0.05, 0.04)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

# saves filename.blend to the directory specified
def saveBlendFile(directory,filename):
    print(filename)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(directory, filename + ".blend"))

# given SBML file create blender file of geometries described in SBML file
def sbml2blender(inputFilePath,addObjects):
    print("loading .xml file... " + inputFilePath)
    #extrapolate object data from smbl file
    csgObjects  = readSMBLFileCSGObject(inputFilePath)
    paramObject = readSMBLFileParametricObject(inputFilePath)
    
    print("length of objects: " + str(len(csgObjects)))
    #generates sphere or bounding box in Blender
    
    #track average endosome size
    sum_size = 0.0 #sum of volumes
    n_size   = 0.0 #number of endosomes
    
    #track average endosome surface area
    sum_surf = 0.0
    n_surf   = 0.0
    
    for object in csgObjects:
        if( object[1] == 'SOLID_SPHERE' or object[1] == 'sphere'):
            name      = object[0]
            size      = [float(object[2]), float(object[3]), float(object[4])]
            location  = [float(object[8]), float(object[9]), float(object[10])]
            rotation  = [float(object[5]), float(object[6]), float(object[7])]
            obj = generateSphere(name,size,location,rotation)
            sum_size += (4.0/3.0)*(3.14)*(size[0])*(size[1])*(size[2])
            n_size   += 1
            sum_surf += surface_area_sphere(size[0],size[1],size[2])
            n_surf += 1
        else:
            obj = generateCube(float(object[2]), float(object[3]), float(object[4]))
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)
    
    print("The average endosome size is: " + str((sum_size/(n_size*1.0))))
    print("The average endosome surface area is " + str((sum_surf/(n_surf*1.0))))
    
    for object in paramObject:
        obj = generateMesh(object)
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)

# main function, reads arguments and runs sbml2blender
if __name__ == '__main__':
    filenames = sys.argv[5:]
    resetScene()
    xml = filenames[0]
    try:
        print(filenames[1])
        print(filenames[2])
        # reset initial conditions
        importMesh('cell', os.path.join(os.getcwd(),filenames[0]))
        importMesh('nuc', os.path.join(os.getcwd(),filenames[1]))
    except:
        print('No meshes imported')
    sbml2blender(os.path.join(os.getcwd(), xml))

    outputFilePath = 'demo_sbml2blender'
    shutil.copyfile("test.blend", outputFilePath + ".blend")
    print('saving blend file to {0}'.format(outputFilePath))
    saveBlendFile(os.getcwd(), outputFilePath)


#!/usr/bin/env python3
# rovsimlibs.py>

import os
import numpy as np
from vtkmodules.all import *

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify


# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------
renderer        = vtkRenderer()
renderWindow    = vtkRenderWindow()
camera          = vtkCamera()
colors          = vtkNamedColors()
lut             = vtkLookupTable()
orientation_marker = True

# Painting colors
sea_color        = colors.GetColor3d("midnightblue")
rov_color        = colors.GetColor3d("lightsteelblue")
rov_cone_color   = colors.GetColor3d("gold")
rx_color         = colors.GetColor3d("salmon")
test_color       = colors.GetColor3d("mint")
unseen, seen, hole, fouling_low, fouling_mid, fouling_high = range(0,6)

# Cage params
cage_h      = 20
cage_w      = 2*cage_h
cage_l      = 2*cage_h
real_h      = 20.0
real_w      = 2*real_h
real_l      = 2*real_h
tile_factor = 1
step        = 1
cage_ap_filter  = vtkAppendFilter()
cage_seen       = vtkAppendFilter()
cage_assembly   = vtkAssembly()

# Rov params
# rovFileName    = rovsimPath + "/images/Insy300.stl"
rov_bounds     = np.zeros(6)
rov_pos        = np.zeros(3)
rov_rot        = np.zeros(3)
rov_initpos    = (cage_w/2,cage_l/2,cage_h-0.5)
rov_initrot    = np.zeros(3)
rov_cam_aperture = 60.0    # camera aperture in degree
real_visibillity = 5.0    # visibility in meters
rov_visibillity  = real_visibillity*(cage_w/real_w)
# enable_telemetry   = true
# enable_position    = true
rov_actor       = vtkActor()  
cone_tf_filter  = vtkTransformPolyDataFilter()
cone_tf         = vtkTransform()


# -----------------------------------------------------------------------------
# Cage3D
# -----------------------------------------------------------------------------

def CreateCage():      
    for i in range(4):
        dim = (cage_w,cage_h,1)
        wall_surface = vtkDataSetSurfaceFilter()
        tf           = vtkTransform()
        wall_tf      = vtkTransformFilter()
        
        if(i == 0):
            grid = CreateStructuredGrid(dim)
            wall_surface.SetInputData(grid)

            tf.RotateX(90)
            tf.Translate(0,0,0)

            wall_tf.SetInputConnection(wall_surface.GetOutputPort())
            wall_tf.SetTransform(tf)

            cage_ap_filter.AddInputConnection(wall_tf.GetOutputPort())
            # cage_ap_filter.update()
        
        # if(i == 1):
        #     grid = CreateStructuredGrid(dim)
        
        # if(i == 2):
        #     grid = CreateStructuredGrid(dim)
        
        # if(i == 3):
        #     grid = CreateStructuredGrid(dim)
        
        # if(i == 4):
        #     dim = (cage_w,cage_l,1)
        #     grid = CreateStructuredGrid(dim)
    
    cage_seen.AddInputConnection(cage_ap_filter.GetOutputPort())
    # mapper
    cage_seen_mapper = vtkDataSetMapper()
    cage_seen_mapper.SetInputData(cage_seen.GetOutput())
    cage_seen_mapper.ScalarVisibilityOn()
    cage_seen_mapper.SetScalarModeToUseCellData()
    cage_seen_mapper.SetScalarRange(unseen, fouling_high)
    cage_seen_mapper.SetLookupTable(lut)
    cage_seen_mapper.StaticOff()       
    # actor
    cage_seen_actor = vtkActor()
    cage_seen_actor.SetMapper(cage_seen_mapper)
    cage_seen_actor.GetProperty().SetSpecular(0.6)
    cage_seen_actor.GetProperty().SetSpecularPower(30)
    cage_seen_actor.GetProperty().SetOpacity(0.5)
    # add actor to cage_assembly part 
    # cage_assembly.AddPart(cage_seen_actor)

    renderer.AddActor(cage_seen_actor)
        
def SetWallStructuredGrid(dimensions, spacing=(step, step, 1)):
    """Create an explicit structured grid.

    Parameters
    ----------
    dimensions : tuple(int, int, int)
        The number of points in the I, J and K directions.
    spacing : tuple(int, int, int)
        The spacing between points in the I, J and K directions.

    Returns
    -------
    grid : vtkExplicitStructuredGrid
        An explicit structured grid.

    """
    ni, nj, nk = dimensions
    si, sj, sk = spacing

    points = vtkPoints()
    for z in range(0, nk * sk, sk):
        for y in range(0, nj * sj, sj):
            for x in range(0, ni * si, si):
                points.InsertNextPoint((x, y, z))

    cells = vtkCellArray()
    for k in range(0, nk - 1):
        for j in range(0, nj - 1):
            for i in range(0, ni - 1):
                multi_index = ([i, i + 1, i + 1, i, i, i + 1, i + 1, i],
                               [j, j, j + 1, j + 1, j, j, j + 1, j + 1],
                               [k, k, k, k, k + 1, k + 1, k + 1, k + 1])
                pts = np.ravel_multi_index(multi_index, dimensions, order='F')
                cells.InsertNextCell(8, pts)

    grid = vtkExplicitStructuredGrid()
    grid.SetDimensions(ni, nj, nk)
    grid.SetPoints(points)
    grid.SetCells(cells)

    return grid


# -----------------------------------------------------------------------------
# Rov3D
# -----------------------------------------------------------------------------
def SetRov3DCone(first=False):
    # cone source
    rov_cone = vtkConeSource()
    rov_cone.SetHeight(rov_visibillity)
    rov_cone.SetCenter(-rov_visibillity/2, 0, 0)
    rov_cone.SetAngle(rov_cam_aperture/2) # the cone's angle it's the half of the camera aperture angle
    rov_cone.SetResolution(4)
    rov_cone.CappingOn()

    if(first):
        # transform filter
        cone_tf_filter.SetInputConnection(rov_cone.GetOutputPort())
        # cone mapper
        cone_mapper = vtkPolyDataMapper()
        cone_mapper.SetInputConnection(cone_tf_filter.GetOutputPort())
        cone_mapper.ScalarVisibilityOff()
        # cone actor
        cone_actor = vtkActor()
        cone_actor.SetMapper(cone_mapper)
        cone_actor.GetProperty().SetDiffuseColor(rov_cone_color)
        cone_actor.GetProperty().SetDiffuse(0.8)
        cone_actor.GetProperty().SetOpacity(0.5)
    
        renderer.AddActor(cone_actor)
    
def CreateRov3D():
    filename = os.path.abspath("data/Insy108.stl")
    
    # 3D model
    reader = vtkSTLReader()
    reader.SetFileName(filename)
    # rov mapper and actor
    rov_mapper = vtkPolyDataMapper()
    rov_mapper.SetInputConnection(reader.GetOutputPort())
    # rov actor
    rov_actor.SetMapper(rov_mapper)
    rov_actor.GetProperty().SetDiffuse(0.8)
    rov_actor.GetProperty().SetDiffuseColor(rov_color)
    rov_actor.GetProperty().SetSpecular(0.3)
    rov_actor.GetProperty().SetSpecularPower(60.0)
    renderer.AddActor(rov_actor)

    # vision cone
    SetRov3DCone(True)

    # Rov's init pose
    SetRov3DPose()

def SetRov3DPose(pos = (0,0,0) , rot = (0,0,0)):
    # Rov actor
    x, y, z = pos
    roll, pitch, yaw = rot
    tf = vtkTransform()
    tf.PostMultiply()
    tf.RotateX(roll) 
    tf.RotateY(pitch)
    tf.RotateZ(yaw)
    tf.Translate(x,y,z)
    # transformed rov for rendering
    rov_actor.SetUserTransform(tf)

    # # data for animation
    # rov_rot[0] = roll
    # rov_rot[1] = pitch
    # rov_rot[2] = yaw
    # rov_pos[0] = x
    # rov_pos[1] = y
    # rov_pos[2] = z

    # Rov cone
    if(cone_tf.GetNumberOfConcatenatedTransforms() > 0): cone_tf.Identity()
    cone_tf.SetInput(tf)
    cone_tf.RotateX(45)

    # transformed cone polydata for further use
    cone_tf_filter.SetTransform(cone_tf)

def SetRovVisibillity(distance):
    real_visibillity = distance
    rov_visibillity  = real_visibillity*(cage_w/real_w)
    SetRov3DCone()


# -----------------------------------------------------------------------------
# Generic VTK functions
# -----------------------------------------------------------------------------
def SetCamera():
    camera.SetPosition(cage_w*2.05, cage_l*2.05, cage_h*4.2)
    camera.SetFocalPoint(cage_w/2, cage_l/2, cage_h/2)
    camera.SetViewUp(0, 0, 1)
    renderer.SetActiveCamera(camera)

def MakeLUT(tableSize=6):
    """
    Make a lookup table from a set of named colors.
    :param: tableSize - The table size
    :return: The lookup table.
    """
    nc = vtkNamedColors()
    # lut = vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()
    # Fill in a few known colors, the rest will be generated if needed
    lut.SetTableValue(0, nc.GetColor4d("gray"))
    lut.SetTableValue(1, nc.GetColor4d("lime"))
    lut.SetTableValue(2, nc.GetColor4d("red"))
    lut.SetTableValue(3, nc.GetColor4d("yellow"))
    lut.SetTableValue(4, nc.GetColor4d("magenta"))
    lut.SetTableValue(5, nc.GetColor4d("cyan"))
    # lut.SetTableValue(8, nc.GetColor4d("mint"))

    # return lut

def SetWidgets():
    # Widgets
    axesActor = vtkAnnotatedCubeActor()
    axesActor.SetYMinusFaceText("W")
    axesActor.SetXPlusFaceText ("S")
    axesActor.SetYPlusFaceText ("E")
    axesActor.SetXMinusFaceText("N")
    axesActor.SetZMinusFaceText("D")
    axesActor.SetZPlusFaceText("")
    axesActor.GetTextEdgesProperty().SetColor(colors.GetColor3d("yellow"))
    axesActor.GetTextEdgesProperty().SetLineWidth(2)
    axesActor.GetCubeProperty().SetColor(colors.GetColor3d("gray"))
    axes = vtkOrientationMarkerWidget()
    axes.SetOrientationMarker(axesActor)
    axes.SetInteractor(renderWindowInteractor)
    axes.InteractiveOff()
    if(orientation_marker): axes.EnabledOn()
    else: axes.EnabledOff() 

# -----------------------------------------------------------------------------
# test functions
# -----------------------------------------------------------------------------
def CreateCone(): 
    cone = vtkConeSource()
    cone.SetResolution(60)
    cone.SetCenter(-2,0,0)

    # Create a mapper and actor
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cone.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetDiffuseColor(test_color)    
    renderer.AddActor(actor)


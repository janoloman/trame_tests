#!/usr/bin/env python3
# rovsimlibs.py>

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

from vtkmodules.all import *


# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------
renderer        = vtkRenderer()
renderWindow    = vtkRenderWindow()

cage_ap_filter  = vtkAppendFilter()
cage_seen       = vtkAppendFilter()
cage_assembly   = vtkAssembly()

# Painting colors
colors = vtkNamedColors()
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
tile_factor = 1
step        = 1


def MakeLUT(tableSize=6):
    """
    Make a lookup table from a set of named colors.
    :param: tableSize - The table size
    :return: The lookup table.
    """
    nc = vtkNamedColors()
    lut = vtkLookupTable()
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

    return lut

def CreateCage():
    dim = (cage_w,cage_h,1)
    wall_surface = vtkDataSetSurfaceFilter()
    tf           = vtkTransform()
    wall_tf      = vtkTransformFilter()
        
    grid = CreateStructuredGrid(dim)
    wall_surface.SetInputData(grid)

    tf.RotateX(90)
    tf.Translate(0,0,0)

    wall_tf.SetInputConnection(wall_surface.GetOutputPort())
    wall_tf.SetTransform(tf)

    cage_ap_filter.AddInputConnection(wall_tf.GetOutputPort())
        
    # for i in range(4):
    #     dim = (cage_w,cage_h,1)
    #     wall_surface = vtkDataSetSurfaceFilter()
    #     tf           = vtkTransform()
    #     wall_tf      = vtkTransformFilter()
        
    #     if(i == 0):
    #         grid = CreateStructuredGrid(dim)
    #         wall_surface.SetInputData(grid)

    #         tf.RotateX(90)
    #         tf.Translate(0,0,0)

    #         wall_tf.SetInputConnection(wall_surface.GetOutputPort())
    #         wall_tf.SetTransform(tf)

    #         cage_ap_filter.AddInputConnection(wall_tf.GetOutputPort())
    #         # cage_ap_filter.update()
        
    #     # if(i == 1):
    #     #     grid = CreateStructuredGrid(dim)
        
    #     # if(i == 2):
    #     #     grid = CreateStructuredGrid(dim)
        
    #     # if(i == 3):
    #     #     grid = CreateStructuredGrid(dim)
        
    #     # if(i == 4):
    #     #     dim = (cage_w,cage_l,1)
    #     #     grid = CreateStructuredGrid(dim)
    
    # cage_seen.AddInputConnection(cage_ap_filter.GetOutputPort())
    # # mapper
    # cage_seen_mapper = vtkDataSetMapper()
    # cage_seen_mapper.SetInputData(cage_seen.GetOutput())
    # cage_seen_mapper.ScalarVisibilityOn()
    # cage_seen_mapper.SetScalarModeToUseCellData()
    # cage_seen_mapper.SetScalarRange(unseen, fouling_high)
    # cage_seen_mapper.SetLookupTable(lut)
    # cage_seen_mapper.StaticOff();       
    # # actor
    # cage_seen_actor = vtkActor()
    # cage_seen_actor.SetMapper(cage_seen_mapper)
    # cage_seen_actor.GetProperty().SetSpecular(0.6)
    # cage_seen_actor.GetProperty().SetSpecularPower(30)
    # cage_seen_actor.GetProperty().SetOpacity(0.5)
    # # add actor to cage_assembly part 
    # # cage_assembly.AddPart(cage_seen_actor)

    # renderer.AddActor(cage_seen_actor)
        

def CreateStructuredGrid(dimensions, spacing=(step, step, 1)):
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

    # begin test
    mapper = vtkDataSetMapper()
    mapper.SetInputData(grid)
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().LightingOff()
    actor.GetProperty().SetColor(colors.GetColor3d('Seashell'))
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('DarkSlateGray'))
    # end test

    return grid

    
def CreateCone():
    
    coneSource = vtkConeSource()
    coneSource.SetResolution(60)
    coneSource.SetCenter(-2,0,0)

    # Create a mapper and actor
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(coneSource.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetDiffuseColor(test_color)
    
    renderer.AddActor(actor)


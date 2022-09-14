#!/usr/bin/env python3

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

from rovsimlibs import *

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

lut = MakeLUT()


# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------
def InitVTK():
    # CreateStructuredGrid((cage_w,cage_h,1))
    # CreateCage()    
    CreateCone()    
    
    # Visualize
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderer.SetBackground(sea_color)
    renderer.ResetCamera()


# -----------------------------------------------------------------------------
# trame
# -----------------------------------------------------------------------------
server = get_server()
ctrl = server.controller
def InitTrame():
    with SinglePageLayout(server) as layout:
        layout.title.set_text("rovsim trame test")

        with layout.content:
            with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
            ):
                view = vtk.VtkLocalView(renderWindow)
                ctrl.on_server_ready.add(view.update)
    server.start()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    InitVTK()
    InitTrame()
#!/usr/bin/env python3

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

from rovsimlibs import *
from testlibs import *

# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------
def InitVTK():
    MakeLUT()
    
    # CreateCone()
    # CreateRov3D()
    # CreateStructuredGrid((cage_w,cage_h,1))
    # CreateCage() 
    CreateWall()

    # Renderer
    renderer.SetBackground(sea_color)
    renderer.ResetCamera()
    # setCamera()
    
    # RendererWindow
    renderWindow.AddRenderer(renderer)

    # RendererWindowInteractor
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    # renderWindowInteractor.Initialize()
  

    # renderWindowInteractor.Start()


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
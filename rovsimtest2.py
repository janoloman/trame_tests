#!/usr/bin/env python3

import numpy as np
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.all import *


# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------


def create_explicit_structured_grid(dimensions, spacing=(1, 1, 1)):
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


def convert_to_unstructured_grid(grid):
    """Convert explicit structured grid to unstructured grid.

    Parameters
    ----------
    grid : vtkExplicitStructuredGrid
        An explicit structured grid.

    Returns
    -------
    vtkUnstructuredGrid
        An unstructured grid.

    """
    converter = vtkExplicitStructuredGridToUnstructuredGrid()
    converter.SetInputData(grid)
    converter.Update()
    return converter.GetOutput()


def convert_to_explicit_structured_grid(grid):
    """Convert unstructured grid to explicit structured grid.

    Parameters
    ----------
    grid : UnstructuredGrid
        An unstructured grid.

    Returns
    -------
    vtkExplicitStructuredGrid
        An explicit structured grid. The ``'BLOCK_I'``, ``'BLOCK_J'`` and
        ``'BLOCK_K'`` cell arrays are required.

    """
    converter = vtkUnstructuredGridToExplicitStructuredGrid()
    converter.SetInputData(grid)
    converter.SetInputArrayToProcess(0, 0, 0, 1, 'BLOCK_I')
    converter.SetInputArrayToProcess(1, 0, 0, 1, 'BLOCK_J')
    converter.SetInputArrayToProcess(2, 0, 0, 1, 'BLOCK_K')
    converter.Update()
    return converter.GetOutput()




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
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    grid = create_explicit_structured_grid((5, 6, 7), (20, 10, 1))
    grid = convert_to_unstructured_grid(grid)
    grid = convert_to_explicit_structured_grid(grid)

    mapper = vtkDataSetMapper()
    mapper.SetInputData(grid)

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().LightingOff()
    colors = vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d('Seashell'))

    
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('DarkSlateGray'))
    renderer.ResetCamera()


    InitTrame()
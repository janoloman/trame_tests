#!/usr/bin/env python3

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

from rovsimlibs import *
from rovsimtest import *


def CreateWall():
    grid1 = create_explicit_structured_grid((5, 6, 7), (20, 10, 1))
    grid2 = convert_to_unstructured_grid(grid1)
    grid3 = convert_to_explicit_structured_grid(grid2)

    mapper = vtkDataSetMapper()
    mapper.SetInputData(grid3)

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().LightingOff()
    actor.GetProperty().SetColor(colors.GetColor3d('Seashell'))

    renderer.AddActor(actor)   
        
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

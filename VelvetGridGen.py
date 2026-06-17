"""This file acts as the main module for this script."""

import traceback
import adsk.core
import adsk.fusion
import adsk.cam

# Initialize the global variables for the Application and UserInterface objects.
app = adsk.core.Application.get()
ui = app.userInterface

handlers = []

maxCount = 100


def run(_context: str):
    """This function is called by Fusion when the script is run."""

    try:

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        # SAFELY CLEAN UP EXPIRED BUTTON DEFINITIONS FROM PREVIOUS RUN CRASHES
        existingDef = cmdDefs.itemById("CreateVelvetGrid")
        if existingDef:
            existingDef.deleteMe()
        # Create a button command definition.
        makeGridButton = cmdDefs.addButtonDefinition(
            "CreateVelvetGrid",
            "Create Velvet Grid Layout",
            "Dynamically make the grid.",
        )
        # Connect to the command created event.
        makeGridCommandCreated = MakeGridCommandCreatedEventHandler()
        makeGridButton.commandCreated.add(makeGridCommandCreated)
        handlers.append(makeGridCommandCreated)
        # Execute the command.
        makeGridButton.execute()

        # Keep the script running.
        adsk.autoTerminate(False)

    except:  # pylint:disable=bare-except
        # Write the error message to the TEXT COMMANDS window.
        app.log(f"Failed:\n{traceback.format_exc()}")


# Event handler for the commandCreated event.
class MakeGridCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs

        inputs.addDistanceValueCommandInput(
            "baseThickness",
            "Base Thickness",
            adsk.core.ValueInput.createByReal(1),
        )
        inputs.addDistanceValueCommandInput(
            "deviderHeight",
            "Divider Height",
            adsk.core.ValueInput.createByReal(0.5),
        )
        inputs.addIntegerSpinnerCommandInput("rowCount", "Row Count", 1, maxCount, 1, 3)
        inputs.addIntegerSpinnerCommandInput(
            "columnCount", "Column Count", 1, maxCount, 1, 3
        )

        inputs.addDistanceValueCommandInput(
            "rowheight",
            "Row Height",
            adsk.core.ValueInput.createByReal(1),
        )
        inputs.addDistanceValueCommandInput(
            "columnWidth",
            "Column Width",
            adsk.core.ValueInput.createByReal(1),
        )

        inputs.addDistanceValueCommandInput(
            "innerOffset",
            "Inner Spacing",
            adsk.core.ValueInput.createByReal(0.25),
        )
        inputs.addDistanceValueCommandInput(
            "outerOffset",
            "Outer Spacing",
            adsk.core.ValueInput.createByReal(1),
        )

        #
        customSizes = inputs.addBoolValueInput(
            "customSizes", "customSizes", True, "", False
        )

        rowsTable = inputs.addTableCommandInput("rowsTable", "Rows", 2, "1:1")
        columnsTable = inputs.addTableCommandInput("columnsTable", "Columns", 2, "1:1")

        add_button_rows = inputs.addBoolValueInput("rowsTable_AddButton", "➕", False)
        add_button_columns = inputs.addBoolValueInput(
            "columnsTable_AddButton", "➕", False
        )

        rowsTable.addToolbarCommandInput(add_button_rows)
        columnsTable.addToolbarCommandInput(add_button_columns)

        row_number = inputs.addIntegerSpinnerCommandInput(
            "row_number_0", "Row Number", 1, maxCount, 1, 1
        )
        column_number = inputs.addIntegerSpinnerCommandInput(
            "column_number_0", "Column Number", 1, maxCount, 1, 1
        )
        row_height = inputs.addDistanceValueCommandInput(
            "row_height_0",
            "Row 1 Height",
            adsk.core.ValueInput.createByReal(1),
        )
        column_width = inputs.addDistanceValueCommandInput(
            "column_width_0",
            "Column 1 Width",
            adsk.core.ValueInput.createByReal(1),
        )

        rowsTable.addCommandInput(row_number, 0, 0,)
        columnsTable.addCommandInput(column_number, 0, 0)
        rowsTable.addCommandInput(row_height, 0, 1)
        columnsTable.addCommandInput(column_width, 0, 1)

        # Initially hide the custom size tables until the user checks the customSizes box
        rowsTable.isVisible = False
        columnsTable.isVisible = False

        rowsTable.isVisible = True
        columnsTable.isVisible = True
        rowsTable.isVisible = False
        columnsTable.isVisible = False

        #
        customGrid = inputs.addBoolValueInput(
            "customGrid", "customGrid", True, "", False
        )

        table = inputs.addTableCommandInput("rectanglesTable", "Table", 5, "1:1")

        table.isVisible = False

        table.tablePresentationStyle = (
            adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
        )

        add_button_rectangles = inputs.addBoolValueInput(
            "rectanglesTable_AddButton", "➕", False
        )
        table.addToolbarCommandInput(add_button_rectangles)

        for i in range(4):
            cord_input = inputs.addIntegerSpinnerCommandInput(
                f"cord_{i}_0", f"Cord {i},0", 0, maxCount, 1, 0
            )
            table.addCommandInput(cord_input, 0, i)

        # for each one should it be filled or a pocket
        # Create a drop-down input and add it to the first row and second column.
        pocketOrFill = inputs.addDropDownCommandInput(
            "dropList_0", "", adsk.core.DropDownStyles.LabeledIconDropDownStyle
        )
        pocketOrFill.listItems.add("pocket", True, "Resources/Icons/pocket")
        pocketOrFill.listItems.add("filled", False, "Resources/Icons/filled")
        table.addCommandInput(pocketOrFill, 0, 5)


        inputs.addDistanceValueCommandInput(
            "innerFilletRadius",
            "Inner Fillet Radius",
            adsk.core.ValueInput.createByReal(0.25),
        )
        inputs.addDistanceValueCommandInput(
            "outerFilletRadius",
            "Outer Fillet Radius",
            adsk.core.ValueInput.createByReal(1),
        )
        

        # Connect to the execute event.
        onExecute = MakeGridCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        # Connect to the inputChanged event.
        onInputChanged = MakeGridCommandInputChangedHandler()
        cmd.inputChanged.add(onInputChanged)
        handlers.append(onInputChanged)


# Event handler for the execute event.
class MakeGridCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        inputs = eventArgs.command.commandInputs
        
        columnCount = inputs.itemById("columnCount").value
        rowCount = inputs.itemById("rowCount").value
        defaultRowHeight = inputs.itemById("rowheight").value
        defaultColumnWidth = inputs.itemById("columnWidth").value
        innerOffset = inputs.itemById("innerOffset").value
        outerOffset = inputs.itemById("outerOffset").value
        customSizes = inputs.itemById("customSizes").value
        customGrid = inputs.itemById("customGrid").value
        baseThickness = inputs.itemById("baseThickness").value
        deviderHeight = inputs.itemById("deviderHeight").value
        innerFillet = inputs.itemById("innerFilletRadius").value
        outerFillet = inputs.itemById("outerFilletRadius").value

        overallWidth = outerOffset
        columnWidthList = [defaultColumnWidth for _ in range(columnCount)]
        overallWidth_until = []
        overallHeight = outerOffset
        rowHeightList = [defaultRowHeight for _ in range(rowCount)]
        overallHeight_until = []

        normalRows = rowCount
        normalColumns = columnCount

        #TODO: fix this
        if customSizes:
            rowHeightsTable = inputs.itemById("rowsTable")
            for i in range(rowHeightsTable.rowCount):
                overallWidth_until.append(overallWidth)
                column_width = inputs.itemById(f"column_width_{i}")
                if column_width:
                    columnWidthList[i] = column_width.value
                overallWidth += columnWidthList[i] + innerOffset

            for i in range(rowCount):
                overallHeight_until.append(overallHeight)
                row_height = inputs.itemById(f"row_height_{i}")
                if row_height:
                    rowHeightList[i] = row_height.value
                overallHeight += rowHeightList[i] + innerOffset
        
        overallHeight += normalRows * (defaultRowHeight+innerOffset)
        overallWidth += normalColumns * (defaultColumnWidth+innerOffset)

        overallWidth += outerOffset - innerOffset #the right outer offset, and the there isn't inner offset after the last column
        overallHeight += outerOffset - innerOffset

        rectanglesType = [[0 for _ in range(columnCount)] for _ in range(rowCount)] #0 normal rectangles, 1 coustome pockets, 2 coustome filled
        coustome_pockets = dict() # (x1,y1) to (x2,y2)
        if customGrid:
            rectanglesTable = inputs.itemById("rectanglesTable")
            for i in range(rectanglesTable.rowCount):
                x1 = rectanglesTable.getInputAtPosition(i, 0).value
                y1 = rectanglesTable.getInputAtPosition(i, 1).value
                x2 = rectanglesTable.getInputAtPosition(i, 2).value
                y2 = rectanglesTable.getInputAtPosition(i, 3).value
                pocketOrFill = rectanglesTable.getInputAtPosition(i, 5)

                if pocketOrFill.selectedItem.name == "pocket":
                    coustome_pockets[(x1, y1)] = (x2, y2)
                
                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        if pocketOrFill.selectedItem.name == "pocket":
                            rectanglesType[y][x] = 1
                        else:
                            rectanglesType[y][x] = 2

        #generating the part

        desgin = adsk.fusion.Design.cast(app.activeProduct)
        root_Component = desgin.rootComponent
        sketches = root_Component.sketches

        xy_plane = root_Component.xYConstructionPlane
        base_sketch = sketches.add(xy_plane)
        base_lines = base_sketch.sketchCurves.sketchLines
        
        # Draw the base rectangle of the tray
        p_origin = adsk.core.Point3D.create(0, 0, 0)
        p_base_corner = adsk.core.Point3D.create(overallWidth, overallHeight, 0)
        base_lines.addTwoPointRectangle(p_origin, p_base_corner)

        # extrude the base rectangle
        prof = base_sketch.profiles.item(0)
        extrudes = root_Component.features.extrudeFeatures
        ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(baseThickness))
        
        base_plate_feature = extrudes.add(ext_input)

        base_body = base_plate_feature.bodies.item(0)
        base_face = base_plate_feature.endFaces.item(0) # the top face of the base rectangle, where the divider will be extruded from

        grid_sketch = sketches.add(base_face)
        grid_lines = grid_sketch.sketchCurves.sketchLines

        for i in range(columnCount):
            for j in range(rowCount):
                if rectanglesType[j][i] == 0:
                    # draw the rectangle
                    x1 = overallWidth_until[i]
                    y1 = overallHeight_until[j]
                    x2 = x1 + columnWidthList[i]
                    y2 = y1 + rowHeightList[j]

                    p1 = adsk.core.Point2D.create(x1, y1)
                    p2 = adsk.core.Point2D.create(x2, y2)
                    grid_lines.addTwoPointRectangle(p1, p2)
                elif coustome_pockets.get((i,j)):
                    # draw the rectangle
                    x1 = overallWidth_until[i]
                    y1 = overallHeight_until[j]
                    i2, j2 = coustome_pockets[(i,j)]
                    x2 = overallWidth_until[i2] + columnWidthList[i2]
                    y2 = overallHeight_until[j2] + rowHeightList[j2]
                    p1 = adsk.core.Point2D.create(x1, y1)
                    p2 = adsk.core.Point2D.create(x2, y2)
                    grid_lines.addTwoPointRectangle(p1, p2)

                # else it's 2 so a filled rectangle so we draw nothing
        
        # so we know that in 0<x,y<outerOffset there is no rectangle so we can chose there an get the outer rectangle / divider
        chosing_point = adsk.core.Point2D.create(outerOffset/2, outerOffset/2)
        diveder_profile = grid_sketch.profileAtPoint(chosing_point)
        
        #extrude the grid divider
        ext_input = extrudes.createInput(diveder_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ext_input.setDistanceExtent(False, deviderHeight)
        extrudes.add(ext_input)

        #add fillets to all the vertical edges
        fillets = root_Component.features.filletFeatures
        
        inner_edge_collection = adsk.core.ObjectCollection.create()
        outer_edge_collection = adsk.core.ObjectCollection.create()
        
        for edge in base_body.edges:
            line_geom = edge.geometry
            start_pt = line_geom.startPoint
            end_pt = line_geom.endPoint
            
            direction_x = abs(end_pt.x - start_pt.x)
            direction_y = abs(end_pt.y - start_pt.y)
            direction_z = abs(end_pt.z - start_pt.z)
            
            small_delta = 0.001
            if direction_x < small_delta and direction_y < small_delta and direction_z > small_delta:#check if vertical
                if abs(start_pt.z) < small_delta or abs(end_pt.z) < small_delta:#check if starts from base (so it's an outer edge) so from z=0
                    outer_edge_collection.add(edge)
                else:
                    inner_edge_collection.add(edge)
                        
        if outer_edge_collection.count > 0:
            outer_fillet_input = fillets.createInput()
            outer_radius = adsk.core.ValueInput.createByReal(outerFillet)
            outer_fillet_input.addConstantRadiusEdgeSet(outer_edge_collection, outer_radius, True)
            fillets.add(outer_fillet_input)
            
        if inner_edge_collection.count > 0:
            inner_fillet_input = fillets.createInput()
            inner_radius = adsk.core.ValueInput.createByReal(innerFillet)
            inner_fillet_input.addConstantRadiusEdgeSet(inner_edge_collection, inner_radius, True)
            fillets.add(inner_fillet_input)
        

    

class MakeGridCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)
        changedInput = eventArgs.input
        inputs = eventArgs.inputs

        partitionedId = changedInput.id.partition("_")
        if partitionedId[-1] == "AddButton":
            partitionedId = changedInput.id.partition("_")
            parentId = partitionedId[0]
            table = inputs.itemById(parentId)
            newRowIndex = table.rowCount
            if parentId == "rowsTable":
                row_number = inputs.addIntegerSpinnerCommandInput(
                    f"row_number_{newRowIndex}", f"Row Number", 1, maxCount, 1, 1
                )
                row_height = inputs.addDistanceValueCommandInput(
                    f"row_height_{newRowIndex}",
                    f"Row {newRowIndex} Height",
                    adsk.core.ValueInput.createByReal(10),
                )
                table.addCommandInput(
                    row_number,
                    newRowIndex,
                    0,
                )
                table.addCommandInput(row_height, newRowIndex, 1)
            elif parentId == "columnsTable":
                column_number = inputs.addIntegerSpinnerCommandInput(
                    f"column_number_{newRowIndex}", f"Column Number", 1, maxCount, 1, 1
                )
                column_width = inputs.addDistanceValueCommandInput(
                    f"column_width_{newRowIndex}",
                    f"Column {newRowIndex} Width",
                    adsk.core.ValueInput.createByReal(10),
                )
                table.addCommandInput(
                    column_number,
                    newRowIndex,
                    0,
                )
                table.addCommandInput(column_width, newRowIndex, 1)
            elif parentId == "rectanglesTable":
                for i in range(4):
                    cord_input = inputs.addIntegerSpinnerCommandInput(
                        f"cord_{i}_{newRowIndex}", f"Cord {i}", 0, maxCount, 1, 0
                    )
                    table.addCommandInput(cord_input, newRowIndex, i)

                pocketOrFill = inputs.addDropDownCommandInput(
                    f"dropList_{newRowIndex}",
                    "filled or pocket",
                    adsk.core.DropDownStyles.LabeledIconDropDownStyle,
                )
                pocketOrFill.listItems.add("pocket", True, "Resources/Icons/pocket")
                pocketOrFill.listItems.add("filled", False, "Resources/Icons/filled")
                table.addCommandInput(pocketOrFill, newRowIndex, 5)

        if changedInput.id == "customSizes":
            customSizes = inputs.itemById("customSizes").value
            rowsTable = inputs.itemById("rowsTable")
            columnsTable = inputs.itemById("columnsTable")
            rowsTable.isVisible = customSizes
            columnsTable.isVisible = customSizes
        elif changedInput.id == "customGrid":
            customGrid = inputs.itemById("customGrid").value
            table = inputs.itemById("rectanglesTable")
            table.isVisible = customGrid


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById("MyButtonDefIdPython")
        if cmdDef:
            cmdDef.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById("SolidScriptsAddinsPanel")
        cntrl = addinsPanel.controls.itemById("MyButtonDefIdPython")
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


# credit: Itay Levy, itay3.8.2010@gmail.com and autodesk fusion 360 api team

"""This file acts as the main module for this script."""

import traceback
import adsk.core
import adsk.fusion
import adsk.cam

# Initialize the global variables for the Application and UserInterface objects.
app = adsk.core.Application.get()
ui   = app.userInterface

handlers = []

maxCount = 100

def run(_context: str):
    """This function is called by Fusion when the script is run."""

    try:

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        # SAFELY CLEAN UP EXPIRED BUTTON DEFINITIONS FROM PREVIOUS RUN CRASHES
        existingDef = cmdDefs.itemById('CreateVelvetGrid')
        if existingDef:
             existingDef.deleteMe()
        # Create a button command definition.
        makeGridButton = cmdDefs.addButtonDefinition(
             'CreateVelvetGrid', 
             'Create Velvet Grid Layout', 
             'Dynamically make the grid.'
        )
        # Connect to the command created event.
        makeGridCommandCreated = MakeGridCommandCreatedEventHandler()
        makeGridButton.commandCreated.add(makeGridCommandCreated)
        handlers.append(makeGridCommandCreated)
        # Execute the command.
        makeGridButton.execute()
        
        # Keep the script running.
        adsk.autoTerminate(False)

    except:   #pylint:disable=bare-except
      # Write the error message to the TEXT COMMANDS window.
      app.log(f'Failed:\n{traceback.format_exc()}')


# Event handler for the commandCreated event.
class MakeGridCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
      super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs
        inputs.addIntegerSpinnerCommandInput('rowCount', 'Row Count', 1,maxCount,1, 3)
        inputs.addIntegerSpinnerCommandInput('columnCount', 'Column Count', 1,maxCount,1, 3)

        inputs.addDistanceValueCommandInput('rowheight', 'Row Height', adsk.core.ValueInput.createByReal(10),)
        inputs.addDistanceValueCommandInput('columnWidth', 'Column Width', adsk.core.ValueInput.createByReal(10),)

        inputs.addDistanceValueCommandInput('innerOffset', 'Inner Spacing', adsk.core.ValueInput.createByReal(5),)
        inputs.addDistanceValueCommandInput('outerOffset', 'Outer Spacing', adsk.core.ValueInput.createByReal(10),)

        #
        customSizes = inputs.addBoolValueInput('customSizes', 'customSizes',
                                                          True, '', False)
        

        rowsTable = inputs.addTableCommandInput('rowsTable', 'Rows', 2, '1:1')
        columnsTable = inputs.addTableCommandInput('columnsTable', 'Columns', 2, '1:1')

        add_button_rows = inputs.addBoolValueInput('rowsTable_AddButton',  '➕', False)
        add_button_columns = inputs.addBoolValueInput('columnsTable_AddButton',  '➕', False)

        rowsTable.addToolbarCommandInput(add_button_rows)
        columnsTable.addToolbarCommandInput(add_button_columns)

        row_number = inputs.addIntegerSpinnerCommandInput('row_number_0', 'Row Number', 1,maxCount,1, 1)
        column_number = inputs.addIntegerSpinnerCommandInput('column_number_0', 'Column Number', 1,maxCount,1, 1)
        row_height = inputs.addDistanceValueCommandInput('row_height_0', 'Row 1 Height', adsk.core.ValueInput.createByReal(10),)
        column_width = inputs.addDistanceValueCommandInput('column_width_0', 'Column 1 Width', adsk.core.ValueInput.createByReal(10),)

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
        customGrid = inputs.addBoolValueInput('customGrid', 'customGrid',
                                                          True, '', False)
        
        table = inputs.addTableCommandInput('rectanglesTable', 'Table', 5, '1:1')
        
        table.isVisible = False
        
        table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
        
        add_button_rectangles = inputs.addBoolValueInput('rectanglesTable_AddButton',  '➕', False)
        table.addToolbarCommandInput(add_button_rectangles)
        
        for i in range(4):
            cord_input = inputs.addIntegerSpinnerCommandInput(f'cord_{i}_0', f'Cord {i},0', 0, maxCount, 1, 0)
            table.addCommandInput(cord_input, 0, i)

        #for each one should it be filled or a pocket
        # Create a drop-down input and add it to the first row and second column.
        pocketOrFill = inputs.addDropDownCommandInput('dropList_0', '', adsk.core.DropDownStyles.TextListDropDownStyle)
        pocketOrFill.listItems.add('pocket', True, '')
        pocketOrFill.listItems.add('fill', False, '')
        table.addCommandInput(pocketOrFill, 0, 5)


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
      eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
      inputs = eventArgs.command.commandInputs
      columnCount = inputs.itemById('columnCount').value
      rowCount = inputs.itemById('rowCount').value

class MakeGridCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
      super().__init__()
    def notify(self, args):
      eventArgs = adsk.core.InputChangedEventArgs.cast(args)
      changedInput = eventArgs.input
      inputs = eventArgs.inputs

      partitionedId = changedInput.id.partition('_')
      if partitionedId[-1] == 'AddButton':
            partitionedId = changedInput.id.partition('_')
            parentId = partitionedId[0]
            table = inputs.itemById(parentId)
            newRowIndex = table.rowCount
            if parentId == 'rowsTable':
                  row_number = inputs.addIntegerSpinnerCommandInput(f'row_number_{newRowIndex}', f'Row Number', 1,maxCount,1, 1)
                  row_height = inputs.addDistanceValueCommandInput(f'row_height_{newRowIndex}', f'Row {newRowIndex} Height', adsk.core.ValueInput.createByReal(10),)
                  table.addCommandInput(row_number, newRowIndex, 0,)
                  table.addCommandInput(row_height, newRowIndex, 1)
            elif parentId == 'columnsTable':
                  column_number = inputs.addIntegerSpinnerCommandInput(f'column_number_{newRowIndex}', f'Column Number', 1,maxCount,1, 1)
                  column_width = inputs.addDistanceValueCommandInput(f'column_width_{newRowIndex}', f'Column {newRowIndex} Width', adsk.core.ValueInput.createByReal(10),)
                  table.addCommandInput(column_number, newRowIndex, 0,)
                  table.addCommandInput(column_width, newRowIndex, 1)
            elif parentId == 'rectanglesTable':
                for i in range(4):
                    cord_input = inputs.addIntegerSpinnerCommandInput(f'cord_{i}_{newRowIndex}', f'Cord {i}', 0, maxCount, 1, 0)
                    table.addCommandInput(cord_input, newRowIndex, i)

                pocketOrFill = inputs.addDropDownCommandInput(f'dropList_{newRowIndex}', '', adsk.core.DropDownStyles.TextListDropDownStyle)
                pocketOrFill.listItems.add('pocket', True, '')
                pocketOrFill.listItems.add('fill', False, '')
                table.addCommandInput(pocketOrFill, newRowIndex, 5)

      if changedInput.id == 'customSizes':
            customSizes = inputs.itemById('customSizes').value
            rowsTable = inputs.itemById('rowsTable')
            columnsTable = inputs.itemById('columnsTable')
            rowsTable.isVisible = customSizes
            columnsTable.isVisible = customSizes
      elif changedInput.id == 'customGrid':
            customGrid = inputs.itemById('customGrid').value
            table = inputs.itemById('rectanglesTable')
            table.isVisible = customGrid



def stop(context):
    try:
        app = adsk.core.Application.get()
        ui   = app.userInterface
          
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('MyButtonDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()
           
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('MyButtonDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 


# credit: Itay Levy, itay3.8.2010@gmail.com and autodesk fusion 360 api team
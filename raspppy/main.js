// Modules to control application life and create native browser window
const { app, BrowserWindow, Menu, dialog } = require('electron')
const path = require('path')

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'client/preload.js')
    }
  })

  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Patch',
          accelerator: 'CmdOrCtrl+O',
          click() {
            dialog.showOpenDialog({
              properties: ['openFile']
            })
              .then(function (fileObj) {
                // the fileObj has two props 
                if (!fileObj.canceled) {
                  mainWindow.webContents.send('OPEN_PATCH', fileObj.filePaths)
                }
              })
              .catch(function (err) {
                console.error(err)
              })
          }
        },
        {
          label: 'Save Patch',
          accelerator: 'CmdOrCtrl+S',
          click() {
            mainWindow.webContents.send('SAVE_PATCH', {})
          }
        },
        {
          label: 'Exit',
          click() {
            app.quit()
          }
        }
      ]
    },{
      label: 'Edit',
      submenu: [
        {
          label: 'Delete',
          accelerator: 'Backspace',
          click() {
            mainWindow.webContents.send('DELETE_OBJECT', {})
          }
        },
        {
          label: 'Delete (invisible)',
          accelerator: 'Delete',
          visible: false,
          acceleratorWorksWhenHidden: true,
          click() {
            mainWindow.webContents.send('DELETE_OBJECT', {})
          }
        },
        {
          label: 'Toggle Edit Mode',
          accelerator: 'CmdOrCtrl+E',
          click() {
            mainWindow.webContents.send('TOGGLE_EDIT_MODE', {})
          }
        },
      ]
    },{
      label: 'Put',
      submenu: [
        {
          label: 'Object',
          accelerator: 'CmdOrCtrl+1',
          click() {
            mainWindow.webContents.send('PUT_OBJECT', {})
          }
        },
      ]
    },
  ])
  Menu.setApplicationMenu(menu)

  // and load the index.html of the app.
  mainWindow.loadURL('http://localhost:8000/index.html');
  // Open the DevTools.
  mainWindow.webContents.openDevTools()

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) createWindow()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.


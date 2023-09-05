const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    openPatch: (callback) => ipcRenderer.on('OPEN_PATCH', callback),
    savePatch: (callback) => ipcRenderer.on('SAVE_PATCH', callback),

    deleteObject: (callback) => ipcRenderer.on('DELETE_OBJECT', callback),
})
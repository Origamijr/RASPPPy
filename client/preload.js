const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    openPatch: (callback) => ipcRenderer.on('OPEN_PATCH', callback)
})
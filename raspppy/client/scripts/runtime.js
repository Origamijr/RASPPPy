// where python and electron interfacing is relegated. Basically the "View" layer

const Runtime = (() => {
    // Retrieve one-time data from python, and load external scripts
    let CONFIG = {}
    let ALIASES = {}
    let DISPLAY_CLASSES = {};
    (async () => {
        CONFIG = await eel.config()()
        ALIASES = await eel.get_aliases()()
        display_scripts = await eel.get_display_scripts()()

        Object.keys(display_scripts).forEach(function(classname) {
            if (DISPLAY_CLASSES[classname]) return
            const scriptElement = document.createElement('script')
            scriptElement.textContent = display_scripts[classname].script
            document.body.appendChild(scriptElement)
            DISPLAY_CLASSES[classname] = eval(`${display_scripts[classname].display_class}`)
        });
    })();

    function aliases() {
        return ALIASES
    }

    function config() {
        return CONFIG
    }

    function displayClasses() {
        return DISPLAY_CLASSES
    }


    // Patch management callbacks

    let patches = {}
    
    window.electronAPI.openPatch(async (event, value) => {
        //console.log('got FILE_OPEN', event, value)
        let info = await eel.open_patch(value[0])()
        let patch = new RASPPPyPatch(info)
        patch.filename = value[0]
        patches[patch.id] = patch
        CanvasEditor.setPatch(patch)
        document.getElementById('properties_panel').innerHTML = patch.name
    })

    window.electronAPI.savePatch(async (event, value) => {
        await eel.save_patch(patches[0][1])() // TODO save is hard coded
    })

    document.getElementById("dsp_toggle").addEventListener("change", () => {
        if (document.getElementById("dsp_toggle").checked) {
            eel.toggle_dsp(true)
        } else {
            eel.toggle_dsp(false)
        }
    });

    let edit_mode = false
    document.getElementById("edit_toggle").addEventListener("change", () => {
        edit_mode = document.getElementById("edit_toggle").checked
    });
    window.electronAPI.toggleEditMode(async (event, value) => {
        document.getElementById("edit_toggle").checked = !document.getElementById("edit_toggle").checked
        edit_mode = document.getElementById("edit_toggle").checked
    })
    function editMode() {
        return edit_mode
    }

    window.electronAPI.deleteObject(async (event, value) => {
        CanvasEditor.getPatch().deleteSelection()
    })

    window.electronAPI.putObject(async (event, value) => {
        document.getElementById("edit_toggle").checked = edit_mode = true
        CanvasEditor.putObject()
    })


    // Functions to call modifications to python
    // Locks acquired to avoid concurrency issues

    function updateObjectProperties(patch_id, obj_ids, properties, callback) {
        navigator.locks.request('eel', () => {
            eel.update_object_properties(patch_id, obj_ids, properties)(callback);
        })
    }

    function removeObjects(patch_id, obj_ids, callback) {
        navigator.locks.request('eel', () => {
            eel.remove_objects(patch_id, obj_ids)(callback)
        })
    }

    function putObjects(patch_id, properties, callback) {
        navigator.locks.request('eel', () => {
            eel.put_objects(patch_id, properties)(callback)
        })
    }

    function bangObject(obj, port) {
        navigator.locks.request('eel', () => {
            eel.bang_object(obj.patch, obj.id, port)()
        })
    }

    function wire(patch_id, wires, connect, callback) {
        navigator.locks.request('eel', () => {
            eel.wire(patch_id, wires, connect)(callback)
        })
    }


    // Function to receive updates from python
    eel.expose(callObjectMethod)
    function callObjectMethod(patch_id, obj_id, f, args) {
        return patches[patch_id].objects[obj_id][f](...args)
    }
    
    return {
        config,
        aliases,
        displayClasses,
        editMode,

        updateObjectProperties,
        removeObjects,
        putObjects,
        bangObject,
        wire,
    }
})();
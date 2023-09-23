// where python and electron interfacing is relegated. Basically the "View" layer

const Runtime = (() => {
    // Retrieve one-time data from python, and load external scripts
    let CONFIG = {}
    let ALIASES = {}
    let DISPLAY_CLASSES = {};
    (async () => {
        CONFIG = await eel.config()()
        ALIASES = await eel.get_aliases()()

        // TODO Why am I iterating here? Do it in python and batch load the scripts...

        // Once both CONFIG and ALIASES are available, proceed to load the scripts
        async function load_scripts(directory) {
            const classNames = [...new Set(Object.values(ALIASES))]
            const scripts = await eel.get_js_scripts(directory)()
            for (let classname of classNames) {
                const filename = classname.toLowerCase() // We assume the file name is just the class name
                if (DISPLAY_CLASSES[classname] || !(filename in scripts)) continue // Skip if namespace already taken

                const scriptElement = document.createElement('script')
                scriptElement.textContent = scripts[filename]
                document.body.appendChild(scriptElement)
                DISPLAY_CLASSES[classname] = eval(`${classname}`)
            }
        }

        load_scripts(CONFIG.files.base_library)
        for (let dir of CONFIG.files.external_libraries) { load_scripts(dir) }
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
    // TODO ui update call from python to call arbitrary class instance method
    
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
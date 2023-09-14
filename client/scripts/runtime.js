// where python interfacing is relegated

const Runtime = (() => {
    // Retrieve one-time data from python, and load external scripts
    let CONFIG = {}
    let ALIASES = {}
    let DISPLAY_CLASSES = {};
    (async () => {
        CONFIG = await eel.config()()
        ALIASES = await eel.get_aliases()()

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


    // Patch management callbacks

    let patches = {} // TODO wrap into a class to avoid global scope

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
        //console.log('got FILE_SAVE', event, value)
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
    function editMode() {
        return edit_mode
    }


    // Functions to call modifications to python
    function bangObject(patch_id, object_id, port) {
        eel.bang_object(patch_id, object_id, port)()
    }
    
    return {
        CONFIG,
        ALIASES,
        DISPLAY_CLASSES,
        editMode,
        bangObject,
    }
})();
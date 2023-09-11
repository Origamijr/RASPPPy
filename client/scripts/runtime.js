// where python interfacing is relegated

// Retrieve one-time data from python, and load external scripts
let CONFIG = {};
let ALIASES = {};
(async () => {
    CONFIG = await eel.config()();
    ALIASES = await eel.get_aliases()();

    // Once both CONFIG and ALIASES are available, proceed to load the scripts
    const loadedScripts = new Set();
    async function load_scripts(directory) {
        const objectNames = [...new Set(Object.values(ALIASES))]
        const scripts = await eel.get_js_scripts(directory)()
        for (let objectName of objectNames) {
            const className = objectName.toLowerCase()
            if (loadedScripts.has(objectName) || !(className in scripts)) continue // Skip if namespace already taken

            const scriptElement = document.createElement('script')
            scriptElement.textContent = scripts[className];
            document.body.appendChild(scriptElement);
            loadedScripts.add(objectName)
        }
    }

    load_scripts(CONFIG.files.base_library)
    //CONFIG.files.external_libraries.foreach(dir => {load_scripts('../'+dir)})
})();


// Patch management callbacks

let patches = {} // TODO wrap into a class to avoid global scope

window.electronAPI.openPatch(async (event, value) => {
    //console.log('got FILE_OPEN', event, value)
    let info = await eel.open_patch(value[0])()
    let patch = new RASPPPyPatch(info)
    patch.filename = value[0]
    patches[patch.id] = patch
    curr_patch = patch
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
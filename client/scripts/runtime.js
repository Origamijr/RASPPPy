function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
  }

let patches = {}
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

let checkbox = document.getElementById("dsp_toggle");
checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
        eel.toggle_dsp(true)
    } else {
        eel.toggle_dsp(false)
    }
});
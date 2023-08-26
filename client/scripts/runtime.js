
function pick_file() {
    let input = document.getElementById('file_dialogue').click()
    return document.getElementById('file_dialogue').value
}

window.electronAPI.openPatch(async (event, value) => {
    console.log('got FILE_OPEN', event, value)
    let patch = await eel.open_patch(value[0])()
    console.log(patch)
    document.getElementById('file_content').innerHTML = patch.name
})

let checkbox = document.getElementById("dsp_toggle");
checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
        eel.toggle_dsp(true)
        console.log('hi')
    } else {
        eel.toggle_dsp(false)
    }
});

eel.expose(js_random);
function js_random() {
    return Math.random();
}
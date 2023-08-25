async function pick_file() {
    let folder = document.getElementById('input-box').value;
    let file_div = document.getElementById('file-name');

    // Call into Python so we can access the file system
    let random_filename = await eel.pick_file(folder)();
    file_div.innerHTML = JSON.stringify(random_filename);
}

let checkbox = document.getElementById("dsp_toggle");
checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
        eel.toggle_dsp(true)
        console.log('hi')
    } else {
        eel.toggle_dsp(false)
    }
});
let canvas = document.getElementById("main_canvas")
let context = canvas.getContext("2d")

let canvas_width = canvas.width
let canvas_height = canvas.height

let mouse_down = function(event) {
    event.preventDefault()
    console.log(event)
}
canvas.onmousedown = mouse_down
canvas.onmouseup = mouse_down
canvas.onmouseout = mouse_down
canvas.onmousemove = mouse_down



render = function() {
    context.clearRect(0, 0, canvas_width, canvas_height)
    // Draw stuff here
}

render()
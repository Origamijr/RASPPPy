let canvas = document.getElementById("main_canvas")
let context = canvas.getContext("2d")
let curr_patch = null
fitToContainer(canvas)

function fitToContainer(canvas){
  canvas.width  = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}

window.addEventListener('resize', function() {
    fitToContainer(canvas);
}, true);

let curr_obj = null
let curr_drag_offset = null
canvas.addEventListener('mousedown', function (event) {
    event.preventDefault()

    let mouseX = parseInt(event.offsetX)
    let mouseY = parseInt(event.offsetY)

    curr_obj = null
    let collision = curr_patch.mouse_collision(mouseX, mouseY)
    if (collision[0] != 0) {
        if (collision[0] == 1) {
            curr_obj = collision[2]
            curr_drag_offset = [curr_obj.x - mouseX, curr_obj.y - mouseY]
        }
    }
});

canvas.addEventListener('mouseup', function (event) {
    event.preventDefault()

    if (curr_drag_offset && curr_obj) {
        curr_drag_offset = null
    }
});

canvas.addEventListener('mousemove', function (event) {
    event.preventDefault()

    if (curr_drag_offset && curr_obj) {
        let mouseX = parseInt(event.offsetX)
        let mouseY = parseInt(event.offsetY)

        curr_obj.x = mouseX + curr_drag_offset[0]
        curr_obj.y = mouseY + curr_drag_offset[1]
    }
});

canvas.addEventListener('mouseout', function (event) {
    event.preventDefault()
    //console.log('mouseout');
    //console.log(event);
});

canvas.addEventListener('click', function (event) {
    event.preventDefault()
    //console.log('click');
    //console.log(event);
});

canvas.addEventListener('dblclick', function (event) {
    event.preventDefault()
    //console.log('dblclick');
    //console.log(event);
});

function render(ctx) {
    //fitToContainer(canvas); // This should be able to be moved outside, but idk
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (curr_patch) curr_patch.render(ctx)
}

// main update function
function update(dt, context) {
    if (curr_patch) curr_patch.update(dt, context)
}

let start, previousTimeStamp;
function animate(timeStamp) {
    if (start === undefined) {
        start = timeStamp;
    }
    const elapsed = timeStamp - start;

    if (previousTimeStamp !== timeStamp) {
        update(elapsed, context)
        render(context)
    }

    previousTimeStamp = timeStamp;

    window.requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
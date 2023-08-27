let canvas = document.getElementById("main_canvas")
let context = canvas.getContext("2d")
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
    Object.keys(objects).some(id => {
        obj = objects[id]
        const inside = obj.x <= mouseX && mouseX <= obj.x+obj.width 
                        && obj.y+3 <= mouseY && mouseY <= obj.y+obj.height-3
        if (inside) {
            curr_obj = obj
            curr_drag_offset = [obj.x - mouseX, obj.y - mouseY]
        }
        return inside
    })
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

let objects = {}

function add_object(obj) {
    objects[obj.id] = obj
}

add_object(new RASPPPyObject())

function render(ctx) {
    //fitToContainer(canvas); // This should be able to be moved outside, but idk
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    Object.keys(objects).forEach(id => {
        objects[id].render(ctx)
    });
}

// main update function
function update(dt) {
    Object.keys(objects).forEach(id => {
        objects[id].update(dt)
    });
}

let start, previousTimeStamp;
function animate(timeStamp) {
    if (start === undefined) {
        start = timeStamp;
    }
    const elapsed = timeStamp - start;

    if (previousTimeStamp !== timeStamp) {
        update(elapsed)
        render(context)
    }

    previousTimeStamp = timeStamp;

    window.requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
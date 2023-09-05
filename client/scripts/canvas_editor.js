// Where event handling and draw loop is relegated

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

let curr_collision = null
let curr_drag_offset = null
function get_collision(patch, x, y) {
    if (patch) {
        curr_collision = patch.mouse_collision(x, y)
        if (curr_collision[0] != 0) return
    }
    curr_collision = NO_COLLISION
}

canvas.addEventListener('mousedown', function (event) {
    event.preventDefault()

    let mouseX = parseInt(event.offsetX)
    let mouseY = parseInt(event.offsetY)

    if (!curr_patch) return
    switch (curr_collision.type) {
        case CollisionType.Object:
            curr_drag_offset = new Vec2(curr_collision.object.x - mouseX, curr_collision.object.y - mouseY)
            curr_patch.selected_objects = [curr_collision.object.id]
            break
        case CollisionType.Wire:
            curr_patch.selected_wire = curr_collision
            break
        case CollisionType.Output:
            curr_patch.dangling_wire = {
                src: curr_collision.object.outputs[curr_collision.port].location,
                dest: new Vec2(mouseX, mouseY),
                width: curr_collision.object.outputs[curr_collision.port].type == 'MESSAGE' ? 1 : 2,
                dest_id: null,
                dest_port: null
            }
        case CollisionType.None:
            curr_patch.selected_wire = null
            curr_patch.selected_objects = []
            break
    }
});

canvas.addEventListener('mouseup', function (event) {
    event.preventDefault()

    if (curr_drag_offset) {
        curr_drag_offset = null
        canvas.style.cursor = 'grab'
    }

    if (!curr_patch) return
    if (curr_patch.dangling_wire) {
        if (curr_patch.dangling_wire.dest_id !== null) {
            console.log('connected') // TODO
        }
        curr_patch.dangling_wire = null
    }
});

canvas.addEventListener('mousemove', function (event) {
    event.preventDefault()

    let mouseX = parseInt(event.offsetX)
    let mouseY = parseInt(event.offsetY)

    if (curr_drag_offset) {
        let mouseX = parseInt(event.offsetX)
        let mouseY = parseInt(event.offsetY)

        curr_collision.object.x = mouseX + curr_drag_offset.x
        curr_collision.object.y = mouseY + curr_drag_offset.y

        canvas.style.cursor = 'grabbing'

    } else if (curr_patch && curr_patch.dangling_wire) {
        curr_patch.dangling_wire.dest.set(mouseX, mouseY)
        get_collision(curr_patch, mouseX, mouseY)
        if (curr_collision.type == CollisionType.Input) {
            curr_patch.dangling_wire.dest_id = curr_collision.object.id
            curr_patch.dangling_wire.dest_port = curr_collision.port
        } else {
            curr_patch.dangling_wire.dest_id = null
            curr_patch.dangling_wire.dest_port = null
        }

    } else {
        get_collision(curr_patch, mouseX, mouseY)
        
        switch (curr_collision.type) {
            case CollisionType.Object:
                canvas.style.cursor = 'grab'
                break
            case CollisionType.Input:
            case CollisionType.Output:
                canvas.style.cursor = 'crosshair'
                break
            case CollisionType.Wire:
                canvas.style.cursor = 'cell'
                break
            default:
                canvas.style.cursor = 'default'
        }
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
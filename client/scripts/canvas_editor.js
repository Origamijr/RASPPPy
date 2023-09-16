// Where event handling and draw loop is relegated

const CanvasEditor = (() => {
    let canvas = document.getElementById("main_canvas")
    let context = canvas.getContext("2d")
    context.translate(0.5, 0.5)
    let curr_patch = null

    function setPatch(patch) {
        curr_patch = patch
    }

    function fitToContainer(canvas) {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }
    fitToContainer(canvas)

    window.addEventListener('resize', function () {
        fitToContainer(canvas);
    }, true);

    let curr_collision = null
    let curr_drag_offset = null
    function get_collision(patch, x, y) {
        let collision = NO_COLLISION
        if (patch) {
            collision = patch.mouse_collision(x, y)
        }
        return collision
    }

    canvas.addEventListener('mousedown', function (event) {
        event.preventDefault()

        let mouseX = parseInt(event.offsetX)
        let mouseY = parseInt(event.offsetY)

        if (!curr_patch) return
        switch (curr_collision.type) {
            case CollisionType.Object:
                if (Runtime.editMode()) {
                    curr_drag_offset = new Vec2(curr_collision.object.x - mouseX, curr_collision.object.y - mouseY)
                    curr_patch.select(curr_collision.object.id)
                } else if (typeof curr_collision.object.onmousedown === 'function') {
                    curr_collision.object.onmousedown(event)
                }
                break
            case CollisionType.Wire:
                if (Runtime.editMode()) {
                    curr_patch.select(curr_collision)
                }
                break
            case CollisionType.Output:
                if (Runtime.editMode()) {
                    curr_patch.dangling_wire = {
                        src_id: curr_collision.object.id,
                        src_port: curr_collision.port,
                        src: curr_collision.object.outputs[curr_collision.port].location,
                        dest: new Vec2(mouseX, mouseY),
                        type: curr_collision.object.outputs[curr_collision.port].type,
                        dest_id: null,
                        dest_port: null
                    }
                }
                break
            case CollisionType.None:
                if (Runtime.editMode()) {
                    curr_patch.select(null)
                }
                break
        }
    });

    canvas.addEventListener('mouseup', function (event) {
        event.preventDefault()

        if (!curr_patch) return

        if (curr_drag_offset) {
            Runtime.updateObjectProperties(curr_collision.object, (modified) => {
                curr_patch.update_objects(modified)
            });
            curr_drag_offset = null
            canvas.style.cursor = 'grab'
        }

        if (curr_patch.dangling_wire) {
            if (curr_patch.dangling_wire.dest_id !== null) {
                Runtime.wire(curr_patch.id, [curr_patch.dangling_wire], true, (modified) => {
                    curr_patch.update_objects(modified)
                    curr_patch.dangling_wire = null
                });
            } else {
                curr_patch.dangling_wire = null
            }
        }
    });

    canvas.addEventListener('mousemove', function (event) {
        event.preventDefault()

        let mouseX = parseInt(event.offsetX)
        let mouseY = parseInt(event.offsetY)

        if (curr_drag_offset) {
            // Case if dragging an object
            curr_collision.object.translate(mouseX + curr_drag_offset.x - curr_collision.object.x,
                mouseY + curr_drag_offset.y - curr_collision.object.y)
            canvas.style.cursor = 'grabbing'

        } else if (curr_patch && curr_patch.dangling_wire) {
            // Case if creating a wire
            curr_patch.dangling_wire.dest.set(mouseX, mouseY)
            curr_collision = get_collision(curr_patch, mouseX, mouseY)
            if (curr_collision.type == CollisionType.Input
                    && (curr_collision.object.inputs[curr_collision.port].type == 'ANYTHING'
                    || curr_patch.dangling_wire.type == 'BANG'
                    || curr_collision.object.inputs[curr_collision.port].type == curr_patch.dangling_wire.type)) {
                curr_patch.dangling_wire.dest_id = curr_collision.object.id
                curr_patch.dangling_wire.dest_port = curr_collision.port
                canvas.style.cursor = 'crosshair'
            } else {
                curr_patch.dangling_wire.dest_id = null
                curr_patch.dangling_wire.dest_port = null
                canvas.style.cursor = 'not-allowed'
            }

        } else {
            // Default case (check current mouse collision and update)
            curr_collision = get_collision(curr_patch, mouseX, mouseY)

            if (Runtime.editMode()) {
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
                        canvas.style.cursor = 'pointer'
                }
            } else {
                canvas.style.cursor = 'default'
            }
        }
    });

    canvas.addEventListener('mouseout', function (event) {
        event.preventDefault()
        //console.log('mouseout');
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
    function update(dt) {
        if (curr_patch) curr_patch.update(dt)
    }

    let start, previousTimeStamp;
    function animate(timeStamp) {
        if (start === undefined) {
            start = timeStamp;
            previousTimeStamp = start;
        }
        const dt = (timeStamp - previousTimeStamp)/1000;
        if (previousTimeStamp !== timeStamp) {
            update(dt);
            render(context);
        }

        previousTimeStamp = timeStamp;

        window.requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);

    return {
        setPatch,
    }
})();
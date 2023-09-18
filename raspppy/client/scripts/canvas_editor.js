// Where event handling and draw loop is relegated

const CanvasEditor = (() => {
    let canvas = document.getElementById("main_canvas")
    let context = canvas.getContext("2d")
    let curr_patch = null
    const EditorState = {
        Idle: 0,
        Dragging: 1,
        Wiring: 2,
        Putting: 3,
        Typing: 4,
    }
    let curr_state = EditorState.Idle

    let mouse_position = new Vec2(-1,-1)
    function setMouseFromEvent(event=null) {
        if (event != null) {
            mouse_position.set(parseInt(event.offsetX), parseInt(event.offsetY))
        } else {
            mouse_position.set(-1, -1)
        }
        return mouse_position
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
    function get_collision(patch, pos) {
        let collision = NO_COLLISION
        if (patch) {
            collision = patch.mouseCollision(pos.x, pos.y)
        }
        return collision
    }

    canvas.addEventListener('mousedown', function (event) {
        event.preventDefault()

        setMouseFromEvent(event)

        if (!curr_patch) return
        switch (curr_collision.type) {
            case CollisionType.Object:
                if (Runtime.editMode()) {
                    curr_drag_offset = new Vec2(curr_collision.object.x - mouse_position.x, curr_collision.object.y - mouse_position.y)
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
                        dest: mouse_position.cclone(),
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
            // Release object if dragging
            Runtime.updateObjectProperties(curr_collision.object, (modified) => {
                curr_patch.updateObjects(modified) // update position on response
            });
            curr_drag_offset = null
            canvas.style.cursor = 'grab'
        }

        if (curr_patch.dangling_wire) {
            // Wire if was creating wire
            if (curr_patch.dangling_wire.dest_id !== null) {
                Runtime.wire(curr_patch.id, [curr_patch.dangling_wire], true, (modified) => {
                    curr_patch.updateObjects(modified)
                    curr_patch.dangling_wire = null
                });
            } else {
                curr_patch.dangling_wire = null
            }
        }
    });

    canvas.addEventListener('mousemove', function (event) {
        event.preventDefault()

        setMouseFromEvent(event)

        if (curr_drag_offset) {
            // Case if dragging an object
            curr_collision.object.setPosition(mouse_position.x + curr_drag_offset.x, mouse_position.y + curr_drag_offset.y)
            canvas.style.cursor = 'grabbing'

        } else if (curr_patch && curr_patch.dangling_wire) {
            // Case if creating a wire
            curr_patch.dangling_wire.dest.copy(mouse_position)
            curr_collision = get_collision(curr_patch, mouse_position)
            if (curr_collision.type == CollisionType.Input
                    && (curr_collision.object.inputs[curr_collision.port].type == 'ANYTHING'
                    || curr_patch.dangling_wire.type == 'BANG'
                    || curr_collision.object.inputs[curr_collision.port].type == curr_patch.dangling_wire.type)) {
                curr_patch.dangling_wire.dest_id = curr_collision.object.id
                curr_patch.dangling_wire.dest_port = curr_collision.port
                canvas.style.cursor = 'crosshair'
            } else {
                console.log('hi')
                curr_patch.dangling_wire.dest_id = null
                curr_patch.dangling_wire.dest_port = null
                canvas.style.cursor = 'not-allowed'
            }

        } else {
            // Default case (check current mouse collision and update)
            curr_collision = get_collision(curr_patch, mouse_position)

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
        setMouseFromEvent()
    });

    canvas.addEventListener('mouseover', function (event) {
        event.preventDefault()
        setMouseFromEvent(event)
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

        console.log(mouse_position)

        previousTimeStamp = timeStamp;

        window.requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);


    // Interface functions

    function setPatch(patch) {
        curr_patch = patch
    }

    function getPatch() {
        return curr_patch
    }

    function putObject(klass=null) {
        if (curr_state != EditorState.Idle) return null
        curr_state = EditorState.Putting
        ids = []
        if (curr_patch.selected_objects.length == 1) {
            obj = curr_patch.addObject(null, klass)
            obj.setPosition(curr_patch.objects[obj_id].x, curr_patch.objects[obj_id].y)
        } else if (mouse_position.x >= 0 && mouse_position.y >= 0) {

        }
    }

    return {
        setPatch,
        getPatch,
        putObject,
    }
})();
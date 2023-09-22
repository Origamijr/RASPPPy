// Where event handling and draw loop is relegated

const CanvasEditor = (() => {
    let canvas = document.getElementById("main_canvas")
    let context = canvas.getContext("2d")
    let curr_patch = null
    const EditorState = { // TODO make rest of the interractions stateful
        Idle: 0,
        Dragging: 1, // Moving an object with the mouse held down
        Wiring: 2, // Creating a wire from an output with the mouse held down
        Putting: 3, // Moving an object without the mouse held down
        ObjectTyping: 4, // Editing the text in an object
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
    function getCollision(patch, pos) {
        let collision = NO_COLLISION
        if (patch) {
            collision = patch.mouseCollision(pos.x, pos.y)
        }
        return collision
    }

    // Text Input handling
    text_callback = null
    text_input_element = null
    function addTextInput(x, y, callback, resizeCallback=null, initialValue='') {
        input = text_input_element = document.createElement('div')
        text_input_element.contentEditable = true
    
        const canvasRect = canvas.getBoundingClientRect();
        text_input_element.style.position = 'fixed'
        text_input_element.style.left = (canvasRect.left + x + 6) + 'px'
        text_input_element.style.top = (canvasRect.top + y + 3) + 'px'
        text_input_element.style.color = 'white'
        text_input_element.style.fontSize = '12px' // This is hard-coded
        text_input_element.style.outline = 'none'
        text_input_element.style.overflow = 'auto'

        text_input_element.innerText  = initialValue
    
        text_input_element.onkeydown = event => {
            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' || event.key == 'Escape') {
                event.preventDefault()
                finishTextInput()
            }
            if (event.key === 'Tab') {
                event.preventDefault()
                document.execCommand('insertText', false, '  ') // Seems deprecated, but works
            }
        };

        text_input_element.oninput = () => {
            if (typeof resizeCallback === 'function') {
                resizeCallback(text_input_element.offsetWidth, text_input_element.offsetHeight);
            }
        }
    
        document.body.appendChild(text_input_element)
        document.body.addEventListener('mousedown', _textInputclickHandler)
        text_callback = callback
        text_input_element.focus()
    }
    function _textInputclickHandler(event) {
        if (event.target !== text_input_element) {
            finishTextInput();
        }
    }
    function finishTextInput() {
        const inputValue = text_input_element.innerText
        text_input_element.blur()
        document.body.removeChild(text_input_element)
        document.body.removeEventListener('mousedown', _textInputclickHandler)
        if (typeof text_callback === 'function') {
            text_callback(inputValue);
        }
    }

    function terminateActiveState() {
        switch (curr_state) {
            case EditorState.Dragging:
            case EditorState.Putting:
                // Release object if dragging
                Runtime.updateObjectProperties(curr_patch.id, 
                        curr_patch.selected_objects, 
                        curr_patch.getProperties(curr_patch.selected_objects)
                                  .map(props => ObjUtils.pick(props, ['position'])), 
                        (modified) => {
                    curr_patch.updateObjects(modified) // update position on response
                });
                if (curr_state == EditorState.Dragging) {
                    canvas.style.cursor = 'grab'
                    curr_drag_offset = null
                }
                break

            case EditorState.Wiring:
                // Wire if was creating wire
                if (curr_patch.dangling_wire.dest_id !== null) {
                    curr_patch.wire(curr_patch.dangling_wire)
                }
                curr_patch.dangling_wire = null
                break
        }
        curr_state = EditorState.Idle
    }

    canvas.addEventListener('mousedown', function (event) {
        event.preventDefault()

        setMouseFromEvent(event)

        if (!curr_patch) return
        switch (curr_state) {
            case EditorState.Putting:

                break
            default:
                switch (curr_collision.type) {
                    case CollisionType.Object:
                        if (Runtime.editMode()) {
                            curr_drag_offset = new Vec2(curr_collision.object.x - mouse_position.x, curr_collision.object.y - mouse_position.y)
                            curr_patch.select(curr_collision.object.id)
                            curr_state = EditorState.Dragging
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
                                dest: mouse_position.clone(),
                                type: curr_collision.object.outputs[curr_collision.port].type,
                                dest_id: null,
                                dest_port: null
                            }
                            curr_state = EditorState.Wiring
                        }
                        break
                    case CollisionType.None:
                        if (Runtime.editMode()) {
                            curr_patch.select(null)
                        }
                        break
                }
        }
    });

    canvas.addEventListener('mouseup', function (event) {
        event.preventDefault()

        if (!curr_patch) return

        terminateActiveState()
    });

    canvas.addEventListener('mousemove', function (event) {
        event.preventDefault()

        setMouseFromEvent(event)

        switch (curr_state) {
            case EditorState.Dragging:
                curr_collision.object.setPosition(mouse_position.x + curr_drag_offset.x, mouse_position.y + curr_drag_offset.y)
                canvas.style.cursor = 'grabbing'
                break
            case EditorState.Wiring:
                curr_patch.dangling_wire.dest.copy(mouse_position)
                curr_collision = getCollision(curr_patch, mouse_position)
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
                break
            default:
                // Default case (check current mouse collision and update)
                curr_collision = getCollision(curr_patch, mouse_position)
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
        console.log('dblclick');
        //console.log(event);
    });

    window.addEventListener('keydown', function(event) {
        switch (curr_state) {
            case EditorState.Putting:
                if (!event.ctrlKey && !event.metaKey && !event.altKey && event.key.length === 1) {
                    console.log(event.key)
                }
                break
        }
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


    // Interface functions

    function setPatch(patch) {
        curr_patch = patch
    }

    function getPatch() {
        return curr_patch
    }

    function putObject() {
        if (!curr_patch) return
        terminateActiveState()
        
        obj = curr_patch.addObject(null, null, true)
        if (curr_patch.selected_objects.length == 1) {
            // If exactly one object is selected, spawn an object below it
            selected_obj = curr_patch.objects[curr_patch.selected_objects[0]]
            position = new Vec2(selected_obj.x, selected_obj.y+selected_obj.height+10)
            obj.setPosition(position.x, position.y)
            curr_patch.wire(WireUtils.createWire(selected_obj.id, 0, obj.id, 0), true)
            curr_state = EditorState.ObjectTyping
            addTextInput(position.x, position.y, text => {
                obj.setText(text)
                curr_patch.putTempObjects()
            }, (w, h) => {
                obj.width = Math.max(w + 12, obj.width)
                obj.height = h + 6
            })
            return
        } 
        
        position = (mouse_position.x >= 0 && mouse_position.y >= 0) ? mouse_position : new Vec2(canvas.width / 2, canvas.height / 2)
        obj.setPosition(position.x, position.y)
        curr_state = EditorState.Putting
        curr_patch.select(obj)
    }

    return {
        setPatch,
        getPatch,
        putObject,
    }
})();
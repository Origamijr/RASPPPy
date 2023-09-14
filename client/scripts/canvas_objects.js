// Classes for UI elements are relegated here

class RASPPPyObject {
    constructor(obj=null, patch_id=null) {
        this.id = 0
        this.x = 0
        this.y = 0
        this.height = 20
        this.width = 32
        this.port_width = 8
        this.port_height = 3
        this.text = ''
        this.inputs = []
        this.outputs = []
        this.properties = {}
        this.width_set = false
        this.display_mode = false
        this.patch = patch_id
        if (obj) {
            this.load(obj)
        }
        console.log(this.patch)
    }

    load(obj) {
        this.id = obj.id
        this.inputs = JSON.parse(JSON.stringify(obj.inputs))
        this.outputs = JSON.parse(JSON.stringify(obj.outputs))
        this.properties = JSON.parse(JSON.stringify(obj.properties))
        this.text = this.properties.text
        this.x = this.properties.position[0]
        this.y = this.properties.position[1]
    }

    translate(x, y) {
        this.x += x
        this.y += y
        for (let input of this.inputs) {
            input.location.x += x
            input.location.y += y
        }
        for (let output of this.outputs) {
            output.location.x += x
            output.location.y += y
        }
    }

    getCollision(x, y) {
        if (x < this.x 
            || x > this.x+this.width 
            || y < this.y 
            || y > this.y+this.height) return NO_COLLISION

        for (let i=0; i < this.inputs.length; i++) {
            if (x < this.x+i*this.input_spacing) continue
            if (x > this.x+i*this.input_spacing+this.port_width) continue
            if (y > this.y+5) continue
            return {type: CollisionType.Input, object: this, port: i}
        }
        for (let i=0; i < this.outputs.length; i++) {
            if (x < this.x+i*this.output_spacing) continue
            if (x > this.x+i*this.output_spacing+this.port_width) continue
            if (y < this.y+this.height-5) continue
            return {type: CollisionType.Output, object: this, port: i}
        }
        return {type: CollisionType.Object, object: this}
    }

    _resize_box(ctx) {
        // Yeah, there's an easier way to calculate this, but it's 6am
        this.width = 32
        
        // Resize to text
        ctx.font = 'bold 12px "DejaVu Sans Mono"'
        this.width = Math.max(this.width, ctx.measureText(this.text).width + 12)
        
        // Get spacing between inputs and resize if necessary
        if (this.inputs.length > 1) {
            this.input_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.inputs.length-1))
            this.width = (this.inputs.length-1)*this.input_spacing+this.port_width
        } else {
            this.input_spacing = 0
        }

        // Get spacing between outputs and resize if necessary
        if (this.outputs.length > 1) {
            this.output_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.outputs.length-1))
            this.width = (this.outputs.length-1)*this.output_spacing+this.port_width
            if (this.inputs.length > 1) this.input_spacing = (this.width-this.port_width)/(this.inputs.length-1)
        } else {
            this.output_spacing = 0
        }

        // Get loctions of the ports
        for (let i=0; i < this.inputs.length; i++) {
            if (i > 0 && i == this.inputs.length-1) break
            this.inputs[i].location = new Vec2(this.x+i*this.input_spacing+this.port_width/2, this.y+this.port_height/2)
        }
        if (this.inputs.length > 1) {
            this.inputs[this.inputs.length-1].location = new Vec2(this.x+this.width-this.port_width/2, this.y+this.port_height/2)
        }
        for (let i=0; i < this.outputs.length; i++) {
            if (i > 0 && i == this.outputs.length-1) break
            this.outputs[i].location = new Vec2(this.x+i*this.output_spacing+this.port_width/2, this.y+this.height-this.port_height/2)
        }
        if (this.outputs.length > 1) {
            this.outputs[this.outputs.length-1].location = new Vec2(this.x+this.width-this.port_width/2, this.y+this.height-this.port_height/2)
        }
    }

    render(ctx, color) {
        if (!this.width_set) {
            this._resize_box(ctx)
            this.width_set = true
        }
        ctx.lineWidth = 1;
        ctx.strokeStyle = color
        ctx.fillStyle = color
        if (this.text === '') {
            ctx.setLineDash([5, 3])
            ctx.strokeRect(this.x, this.y, this.width, this.height)
        } else {
            // Render text
            ctx.font = 'bold 12px "DejaVu Sans Mono"'
            ctx.fillText(this.text, this.x+6, this.y+this.height-6)
            
            // Render box
            this._renderIO(ctx)
            ctx.strokeRect(this.x, this.y, this.width, this.height)
        }
    }

    _renderIO(ctx) {
        if (this.input_spacing === undefined) this.input_spacing = this.port_width + 2;
        if (this.output_spacing === undefined) this.output_spacing = this.port_width + 2;

        // Render inputs
        for (let i=0; i < this.inputs.length; i++) {
            if (i > 0 && i == this.inputs.length-1) break
            ctx.fillRect(this.inputs[i].location.x-this.port_width/2, this.inputs[i].location.y-this.port_height/2, this.port_width, this.port_height)
        }
        if (this.inputs.length > 1) {
            ctx.fillRect(this.inputs[this.inputs.length-1].location.x-this.port_width/2, this.inputs[this.inputs.length-1].location.y-this.port_height/2, this.port_width, this.port_height)
        }

        // Render outputs
        for (let i=0; i < this.outputs.length; i++) {
            if (i > 0 && i == this.outputs.length-1) break
            ctx.fillRect(this.outputs[i].location.x-this.port_width/2, this.outputs[i].location.y-this.port_height/2, this.port_width, this.port_height)
        }
        if (this.outputs.length > 1) {
            ctx.fillRect(this.outputs[this.outputs.length-1].location.x-this.port_width/2, this.outputs[this.outputs.length-1].location.y-this.port_height/2, this.port_width, this.port_height)
        }
    }

    update(dt) {
        // Nothing yet
    }
}

class RASPPPyPatch {
    constructor(patch) {
        this.id = patch.id
        this.name = patch.name
        this.filename = null
        this.objects = {}
        for (let obj of patch.objects) {this.add_object(obj)}
        this.mouse_position = null

        this.dangling_wire = null

        this.selected_wire = null
        this.selected_objects = []
    }

    add_object(obj) {
        let canv_obj = null;
        if ('class' in obj && obj.class in Runtime.DISPLAY_CLASSES) {
            canv_obj = new Runtime.DISPLAY_CLASSES[obj.class](obj, this.id)
        } else {
            canv_obj = new RASPPPyObject(obj, this.id)
        }
        this.objects[obj.id] = canv_obj
    }

    mouse_collision(x, y) {
        // Highly non-optimized. If an issue arises should be rewriten with like a sptial hash or something
        for (let id of Object.keys(this.objects)) {
            let collision = this.objects[id].getCollision(x, y)
            if (collision.type == CollisionType.None) continue
            collision.object = this.objects[id]
            return collision
        }
        for (let id of Object.keys(this.objects)) {
            let obj = this.objects[id]
            for (let [port, io] of obj.outputs.entries()) {
                if (!('location' in io)) continue
                let start = io.location
                for (let wire of io.wires) {
                    let other = this.objects[wire.id]
                    if (!('location' in other.inputs[wire.port])) continue
                    let end = other.inputs[wire.port].location
                    if (distToSegmentSquared(start, end, new Vec2(x, y)) < 4) {
                        return {
                            type: CollisionType.Wire,
                            src_id: obj.id,
                            src_port: port,
                            dest_id: other.id,
                            dest_port: wire.port
                        }
                    }
                }
            }
        }
        return NO_COLLISION
    }

    render(ctx) {
        for (let id of Object.keys(this.objects)) {
            // Render object
            let obj = this.objects[id]
            obj.render(ctx, this.selected_objects.includes(parseInt(id)) ? 'blue' : 'white')

            // Render output wires for the object
            for (let [port, io] of obj.outputs.entries()) {
                if (!('location' in io)) continue
                if (io.type == 'SIGNAL') {
                    ctx.lineWidth = 2;
                } else {
                    ctx.lineWidth = 1
                }

                for (let wire of io.wires) {
                    if (!(wire.id in this.objects)) continue
                    let other = this.objects[wire.id]
                    let other_port = other.inputs[wire.port]
                    if (!('location' in other_port)) continue // other object hasn't been rendered
                    if (this.selected_wire
                        && this.selected_wire.src_id == obj.id
                        && this.selected_wire.src_port == port
                        && this.selected_wire.dest_id == other.id
                        && this.selected_wire.dest_port == wire.port) {
                        ctx.strokeStyle = 'blue'
                    } else {
                        ctx.strokeStyle = 'white'
                    }
                    ctx.beginPath()
                    ctx.moveTo(io.location.x, io.location.y)
                    ctx.lineTo(other_port.location.x, other_port.location.y)
                    ctx.stroke()
                }
            }

            if (this.dangling_wire) {
                ctx.strokeStyle = 'white'
                ctx.lineWidth = this.dangling_wire.width
                ctx.beginPath()
                ctx.moveTo(this.dangling_wire.src.x, this.dangling_wire.src.y)
                ctx.lineTo(this.dangling_wire.dest.x, this.dangling_wire.dest.y)
                ctx.stroke()
            }
        }
    }

    update(dt) {
        for (let id of Object.keys(this.objects)) {
            this.objects[id].update(dt)
        }
    }
}

const CollisionType = {
    None: 0,
    Object: 1,
    Input: 2,
    Output: 3,
    Wire: 4,
}
const NO_COLLISION = {type: CollisionType.None}
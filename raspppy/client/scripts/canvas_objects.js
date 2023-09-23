// Classes for UI elements are relegated here

class RASPPPyObject {
    constructor(obj = null, patch_id = null) {
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
        this.properties = { position: [0, 0], text: '' }
        this.width_set = false
        this.display_mode = false
        this.patch = patch_id
        this.ctx = null
        if (obj) {
            this.load(obj)
        }
    }

    load(obj) {
        this.id = obj.id
        this.inputs = JSON.parse(JSON.stringify(obj.inputs))
        this.outputs = JSON.parse(JSON.stringify(obj.outputs))
        this.properties = JSON.parse(JSON.stringify(obj.properties))
        this.text = this.properties.text
        this.x = this.properties.position[0]
        this.y = this.properties.position[1]
        this.displayMode(this.display_mode)
        if (this.ctx) this._resize_box(this.ctx)
    }

    displayMode(use = true) {
        this.display_mode = false
        this.height = 20
        this.width = 32
        this.port_width = 8
        this.port_height = 3
    }

    translate(x, y) {
        this.x += x
        this.y += y
        this.properties.position[0] += x
        this.properties.position[1] += y

        // Port locations are absolute, so they must also be updated
        for (let input of this.inputs) {
            if (!('location' in input)) continue
            input.location.x += x
            input.location.y += y
        }
        for (let output of this.outputs) {
            if (!('location' in output)) continue
            output.location.x += x
            output.location.y += y
        }
    }

    setPosition(x, y) {
        this.translate(x - this.x, y - this.y)
    }

    setText(text) {
        this.text = text
        this.properties.text = text
    }

    getCollision(x, y) {
        // Check if outside
        if (x < this.x
            || x > this.x + this.width
            || y < this.y
            || y > this.y + this.height) return NO_COLLISION

        // Check input ports
        for (let i = 0; i < this.inputs.length; i++) {
            if (x < this.x + i * this.input_spacing) continue
            if (x > this.x + i * this.input_spacing + this.port_width) continue
            if (y > this.y + 6) continue
            return { type: CollisionType.Input, object: this, port: i }
        }
        // Check output ports
        for (let i = 0; i < this.outputs.length; i++) {
            if (x < this.x + i * this.output_spacing) continue
            if (x > this.x + i * this.output_spacing + this.port_width) continue
            if (y < this.y + this.height - 6) continue
            return { type: CollisionType.Output, object: this, port: i }
        }
        // Otherwise just colliding with object in general
        return { type: CollisionType.Object, object: this }
    }

    _resize_box(ctx) {
        // Yeah, there's an easier way to calculate this, but it's 6am
        this.width = 32

        // Resize to text
        ctx.font = 'bold 12px "DejaVu Sans Mono"'
        this.width = Math.max(this.width, ctx.measureText(this.text).width + 12)

        // Get spacing between inputs and resize if necessary
        if (this.inputs.length > 1) {
            this.input_spacing = Math.max(this.port_width + 2, (this.width - this.port_width) / (this.inputs.length - 1))
            this.width = (this.inputs.length - 1) * this.input_spacing + this.port_width
        } else {
            this.input_spacing = 0
        }

        // Get spacing between outputs and resize if necessary
        if (this.outputs.length > 1) {
            this.output_spacing = Math.max(this.port_width + 2, (this.width - this.port_width) / (this.outputs.length - 1))
            this.width = (this.outputs.length - 1) * this.output_spacing + this.port_width
            if (this.inputs.length > 1) this.input_spacing = (this.width - this.port_width) / (this.inputs.length - 1)
        } else {
            this.output_spacing = 0
        }

        // Get loctions of the ports
        for (let i = 0; i < this.inputs.length; i++) {
            if (i > 0 && i == this.inputs.length - 1) break
            this.inputs[i].location = new Vec2(this.x + i * this.input_spacing + this.port_width / 2, this.y + this.port_height / 2)
        }
        if (this.inputs.length > 1) {
            this.inputs[this.inputs.length - 1].location = new Vec2(this.x + this.width - this.port_width / 2, this.y + this.port_height / 2)
        }
        for (let i = 0; i < this.outputs.length; i++) {
            if (i > 0 && i == this.outputs.length - 1) break
            this.outputs[i].location = new Vec2(this.x + i * this.output_spacing + this.port_width / 2, this.y + this.height - this.port_height / 2)
        }
        if (this.outputs.length > 1) {
            this.outputs[this.outputs.length - 1].location = new Vec2(this.x + this.width - this.port_width / 2, this.y + this.height - this.port_height / 2)
        }
    }

    render(ctx, color) {
        this.ctx = ctx
        if (!this.width_set) {
            // Recompute width and port locations
            this._resize_box(ctx)
            this.width_set = true
        }
        ctx.lineWidth = 1;
        ctx.strokeStyle = color
        ctx.fillStyle = color
        if (this.text === '' || !(this.text.split(' ')[0] in Runtime.aliases())) {
            // Default case if no text
            ctx.setLineDash([5, 3])
            ctx.strokeRect(this.x, this.y, this.width, this.height)
            ctx.setLineDash([]);
        } else {
            // Render text
            ctx.font = 'bold 12px "DejaVu Sans Mono"'
            ctx.fillText(this.text, this.x + 6, this.y + this.height - 6)

            // Render box
            this._renderIO(ctx)
            ctx.strokeRect(this.x, this.y, this.width, this.height)
        }
    }

    _renderIO(ctx) {
        if (this.input_spacing === undefined) this.input_spacing = this.port_width + 2;
        if (this.output_spacing === undefined) this.output_spacing = this.port_width + 2;

        // Render inputs
        for (let i = 0; i < this.inputs.length; i++) {
            if (i > 0 && i == this.inputs.length - 1) break
            ctx.fillRect(this.inputs[i].location.x - this.port_width / 2, this.inputs[i].location.y - this.port_height / 2, this.port_width, this.port_height)
        }
        if (this.inputs.length > 1) {
            ctx.fillRect(this.inputs[this.inputs.length - 1].location.x - this.port_width / 2, this.inputs[this.inputs.length - 1].location.y - this.port_height / 2, this.port_width, this.port_height)
        }

        // Render outputs
        for (let i = 0; i < this.outputs.length; i++) {
            if (i > 0 && i == this.outputs.length - 1) break
            ctx.fillRect(this.outputs[i].location.x - this.port_width / 2, this.outputs[i].location.y - this.port_height / 2, this.port_width, this.port_height)
        }
        if (this.outputs.length > 1) {
            ctx.fillRect(this.outputs[this.outputs.length - 1].location.x - this.port_width / 2, this.outputs[this.outputs.length - 1].location.y - this.port_height / 2, this.port_width, this.port_height)
        }
    }

    update(dt) {
        // Nothing yet
    }
}
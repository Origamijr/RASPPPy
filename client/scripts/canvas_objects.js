class RASPPPyObject {
    constructor(obj=null) {
        this.id = 0
        this.x = 0
        this.y = 0
        this.height = 20
        this.width = 32
        this.text = ''
        this.inputs = []
        this.outputs = []
        this.ctx = null
        if (obj) {
            this.load(obj)
        }
    }

    load(obj) {
        this.id = obj.id
        this.inputs = JSON.parse(JSON.stringify(obj.inputs))
        this.outputs = JSON.parse(JSON.stringify(obj.outputs))
        this.text = obj.properties.text
        this.x = obj.properties.position[0]
        this.y = obj.properties.position[1]
    }

    get_collision(x, y) {
        if (x < this.x || x > this.x+this.width || y < this.y || y > this.y+this.height) return [0,0]
        for (let i=0; i < this.inputs.length; i++) {
            if (x < this.x+i*this.input_spacing) continue
            if (x > this.x+i*this.input_spacing+this.port_width) continue
            if (y > this.y+5) continue
            return [2, i]
        }
        for (let i=0; i < this.outputs.length; i++) {
            if (x < this.x+i*this.output_spacing) continue
            if (x > this.x+i*this.output_spacing+this.port_width) continue
            if (y < this.y+this.height-5) continue
            return [3, i]
        }
        return [1,0]
    }

    resize_box() {
        if (this.ctx) {
            this.port_width = 8
            // Yeah, there's an easier way to calculate this, but it's 6am
            this.width = 32
            this.ctx.font = 'bold 12px "DejaVu Sans Mono"'
            this.width = Math.max(this.width, this.ctx.measureText(this.text).width + 12)
            
            if (this.inputs.length > 1) {
                this.input_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.inputs.length-1))
                this.width = (this.inputs.length-1)*this.input_spacing+this.port_width
            } else {
                this.input_spacing = 0
            }

            if (this.outputs.length > 1) {
                this.output_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.outputs.length-1))
                this.width = (this.outputs.length-1)*this.output_spacing+this.port_width
                if (this.inputs.length > 1) this.input_spacing = (this.width-this.port_width)/(this.inputs.length-1)
            } else {
                this.output_spacing = 0
            }
        }
    }

    render(ctx) {
        if (!this.ctx) {
            this.ctx = ctx
            this.resize_box(ctx)
        }
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'black'
        if (this.text === '') {
            ctx.setLineDash([5, 3])
            ctx.strokeRect(this.x, this.y, this.width, this.height)
        } else {
            ctx.font = 'bold 12px "DejaVu Sans Mono"'
            ctx.fillText(this.text, this.x+6, this.y+this.height-6)
            
            for (let i=0; i < this.inputs.length; i++) {
                if (i > 0 && i == this.inputs.length-1) break
                ctx.fillRect(this.x+i*this.input_spacing, this.y, this.port_width, 3)
                this.inputs[i].location = [this.x+i*this.input_spacing+this.port_width/2, this.y+1]
            }
            if (this.inputs.length > 1) {
                ctx.fillRect(this.x+this.width-this.port_width, this.y, this.port_width, 3)
                this.inputs[this.inputs.length-1].location = [this.x+this.width-this.port_width/2, this.y+1]
            }

            
            for (let i=0; i < this.outputs.length; i++) {
                if (i > 0 && i == this.outputs.length-1) break
                ctx.fillRect(this.x+i*this.output_spacing, this.y+this.height-3, this.port_width, 3)
                this.outputs[i].location = [this.x+i*this.input_spacing+this.port_width/2, this.y+this.height-1]
            }
            if (this.outputs.length > 1) {
                ctx.fillRect(this.x+this.width-this.port_width, this.y+this.height-3, this.port_width, 3)
                this.outputs[this.outputs.length-1].location = [this.x+this.width+this.port_width/2, this.y+this.height-1]
            }

            ctx.strokeRect(this.x, this.y, this.width, this.height)
        }
    }

    update(dt, ctx) {
        //this.ctx = ctx
        //this.resize_box()
    }
}

class RASPPPyPatch {
    constructor(patch) {
        this.id = patch.id
        this.name = patch.name
        this.filename = null
        this.objects = {}
        for (let obj of patch.objects) {
            let canv_obj = new RASPPPyObject(obj)
            this.objects[canv_obj.id] = canv_obj
        }
    }

    mouse_collision(x, y) {
        for (let id of Object.keys(this.objects)) {
            let collision = this.objects[id].get_collision(x, y)
            if (collision[0] == 0) continue
            return [collision[0], collision[1], this.objects[id]]
        }
        return [0, null]
    }

    render(ctx) {
        for (let id of Object.keys(this.objects)) {
            let obj = this.objects[id]
            obj.render(ctx)

            for (let io of obj.outputs) {
                if (io.type == 'SIGNAL') {
                    ctx.lineWidth = 2;
                } else {
                    ctx.lineWidth = 1
                }

                for (let wire of io.wires) {
                    if (!(wire.id in this.objects)) continue
                    let other = this.objects[wire.id].inputs[wire.port]
                    if (!('location' in other)) continue
                    ctx.beginPath()
                    ctx.moveTo(io.location[0], io.location[1])
                    ctx.lineTo(other.location[0], other.location[1])
                    ctx.stroke()
                }
            }
        }
    }

    update(dt, ctx) {
        for (let id of Object.keys(this.objects)) {
            this.objects[id].update(dt)
        }
    }
}
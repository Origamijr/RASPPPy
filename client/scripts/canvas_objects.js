function load_obj() {

}

class RASPPPyObject {
    constructor() {
        this.id = 0
        this.x = 0
        this.y = 0
        this.height = 20
        this.width = 32
        this.content = 'Testing'
        this.num_inputs = 3
        this.num_outputs = 10
        this.ctx = null
    }

    resize_box(ctx) {
        if (this.ctx) {
            this.port_width = 8
            // Yeah, there's an easier way to calculate this, but it's 6am
            this.width = Math.max(this.width, ctx.measureText(this.content).width + 12)

            this.input_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.num_inputs-1))
            this.width = (this.num_inputs-1)*this.input_spacing+this.port_width

            this.output_spacing = Math.max(this.port_width+2, (this.width-this.port_width)/(this.num_outputs-1))
            this.width = (this.num_outputs-1)*this.output_spacing+this.port_width
            this.input_spacing = (this.width-this.port_width)/(this.num_inputs-1)
        }
    }

    render(ctx) {
        if (!this.ctx) {
            this.ctx = ctx
            this.resize_box(ctx)
        }
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'black'
        if (this.content === '') {
            ctx.setLineDash([5, 3])
            ctx.strokeRect(this.x, this.y, this.width, this.height)
        } else {
            ctx.font = 'bold 12px "DejaVu Sans Mono"'
            ctx.fillText(this.content, this.x+6, this.y+this.height-6)
            
            for (let i=0; i < this.num_inputs-1; i++) {
                ctx.fillRect(this.x+i*this.input_spacing, this.y, this.port_width, 3)
            }
            if (this.num_inputs > 1) ctx.fillRect(this.x+this.width-this.port_width, this.y, this.port_width, 3)

            
            for (let i=0; i < this.num_outputs-1; i++) {
                ctx.fillRect(this.x+i*this.output_spacing, this.y+this.height-3, this.port_width, 3)
            }
            if (this.num_outputs > 1) ctx.fillRect(this.x+this.width-this.port_width, this.y+this.height-3, this.port_width, 3)

            ctx.strokeRect(this.x, this.y, this.width, this.height)
        }
    }

    update(dt) {
        //this.resize_box()
    }
}
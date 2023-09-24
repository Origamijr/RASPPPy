class Bang extends RASPPPyObject {
    constructor(obj=null, patch_id=null) {
        super(obj, patch_id)
        this.displayMode()
        this.press_time = 0
        this.press_duration = 'press_duration' in this.properties ? this.properties.press_duration : 0.2
    }

    displayMode(use=true) {
        this.display_mode = use

        if (this.display_mode) {
            this.height = 20
            this.width = 20
            this.port_height = 2
            this.inputs[0].location = new Vec2(this.x+this.port_width/2, this.y+this.port_height/2)
            this.outputs[0].location = new Vec2(this.x+this.port_width/2, this.y+this.height-this.port_height/2)
        } else {
            super.displayMode()
        }
    }

    bang() {
        this.press_time = this.press_duration
    }

    onmousedown(event) {
        Runtime.bangObject(this, 1)
        this.bang()
    }

    render(ctx, color) {
        if (!this.display_mode) return super.render(ctx)

        ctx.lineWidth = 1;
        ctx.strokeStyle = color
        ctx.fillStyle = color

        ctx.beginPath();
        ctx.arc(this.x+this.width/2, this.y+this.height/2, this.width/2-2, 0, 2 * Math.PI);
        if (this.press_time > 0) ctx.fill();
        else ctx.stroke();

        this._renderIO(ctx)
        ctx.strokeRect(this.x, this.y, this.width, this.height)
    }

    update(dt) {
        if (!this.display_mode) return super.update(dt)
        this.press_time = Math.max(0, this.press_time - dt)
    }
}
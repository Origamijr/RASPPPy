class Bang extends RASPPPyObject {
    constructor(obj=null, patch_id=null) {
        super(obj, patch_id)
        this.display_mode = true

        this.height = 20
        this.width = 20
        this.inputs[0].location = new Vec2(this.x+this.port_width/2, this.y+this.port_height/2)
        this.outputs[0].location = new Vec2(this.x+this.port_width/2, this.y+this.height-this.port_height/2)

        this.press_time = 0
        this.press_duration = 'press_duration' in this.properties ? this.properties.press_duration : 1
    }

    getCollision(x, y) {
        if (!this.display_mode) return super.getCollision(x, y)
        if (x < this.x 
            || x > this.x+this.width 
            || y < this.y 
            || y > this.y+this.height) return NO_COLLISION

        return {type: CollisionType.Object, object: this}
    }

    onmousedown(event) {
        Runtime.bangObject(this.patch, this.id, 0)
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
        this.press_time = Math.max(0, this.press_time - this.press_duration)
    }
}
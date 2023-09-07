class Bang extends RASPPPyObject {
    constructor(obj=null) {
        super(obj)
        this.display_mode = true

        this.display_height = 20
        this.display_width = 20

        this.pressed = true
        this.press_duration = 'press_duration' in self.properties ? self.properties.press_duration : 1
    }

    get_collision(x, y) {
        if (!this.display_mode) return super.get_collision(x, y)
        if (x < this.x 
            || x > this.x+this.display_width 
            || y < this.y 
            || y > this.y+this.display_height) return NO_COLLISION

        // TODO

        return {type: CollisionType.Object, object: this}
    }

    render(ctx) {
        if (!this.display_mode) return super.render(ctx)
    }

    update(dt) {
        if (!this.display_mode) return super.render(dt)
    }
}
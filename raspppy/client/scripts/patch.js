
class RASPPPyPatch {
    constructor(patch) {
        this.id = patch.id
        this.name = patch.name
        this.filename = null
        this.objects = {}
        for (let obj of patch.objects) { this.addObject(obj, obj.class) }
        this.mouse_position = null

        this.dangling_wire = null

        this.selected_wires = []
        this.selected_objects = []

        this.temp_counter = -1
        this.temp_wires = []
    }

    addObject(obj=null, klass=null, temp=false) {
        let canv_obj = null;
        if (klass != null && klass in Runtime.displayClasses()) {
            canv_obj = new (Runtime.displayClasses()[obj.class])(obj, this.id)
        } else {
            canv_obj = new RASPPPyObject(obj, this.id)
        }
        if (temp) {
            canv_obj.id = this.temp_counter
            this.temp_counter--
        }
        this.objects[canv_obj.id] = canv_obj
        return canv_obj
    }

    wire(wires, temp=false) {
        if (temp) {
            if (Array.isArray(wires)) {
                this.temp_wires.push(...wires);
            } else if (WireUtils.isWire(wires)) {
                this.temp_wires.push(wires);
            }
            return
        }
        if (WireUtils.isWire(wires)) {
            wires = [wires]
        } else if (!Array.isArray(wires)) {
            return
        }
        Runtime.wire(this.id, wires, true, (modified) => {
            this.updateObjects(modified)
        });
    }

    clearTempObjects() {
        Object.keys(this.objects)
            .filter(id => parseInt(id) < 0)
            .forEach(id => delete dictionary[id]);
        this.temp_counter = -1
    }

    putTempObjects() {
        let ids = Object.keys(this.objects).filter(id => parseInt(id) < 0)
        let properties = ids.map(id => this.objects[id].properties)
        let temp_wires = JSON.parse(JSON.stringify(this.temp_wires))
        if (ids.length > 0) {
            Runtime.putObjects(this.id, properties, (added) => {
                for (let i=0; i < added.length; i++) {
                    // For each added object, replace the temp object, then replace the temp id with real id in temp_wires
                    this.addObject(added[i], added[i].class)
                    delete this.objects[ids[i]]
                    for (let wire of temp_wires) {
                        if (wire.src_id == ids[i]) wire.src_id = added[i].id
                        if (wire.dest_id == ids[i]) wire.dest_id = added[i].id
                    }
                }
                // Try wiring after creating the objects
                this.wire(temp_wires)
            })
        } else {
            this.wire(temp_wires)
        }
        this.temp_counter = -1
    }

    updateObjects(objs) {
        for (let obj of objs) {
            this.objects[obj.id].load(obj)
        }
    }

    getProperties(obj_ids) {
        if (typeof obj_ids === 'number') {
            return this.objects[obj_ids].properties;
        } else if (Array.isArray(obj_ids)) {
            return obj_ids.map(id => this.objects[id].properties);
        }
    }

    select(selection = null, keep = false) {
        if (!keep) {
            this.selected_objects = []
            this.selected_wires = []
        }
        if (selection == null) return
        if (!Array.isArray(selection)) selection = [selection]
        for (let s of selection) {
            if (Number.isInteger(s)) {
                this.selected_objects.push(s)
            } else if (s instanceof RASPPPyObject) {
                this.selected_objects.push(s.id);
            } else if (WireUtils.isWire(s)) {
                this.selected_wires.push(s)
            }
        }
    }

    deleteSelection() {
        Runtime.wire(this.id, this.selected_wires, false, (modified_from_wires) => {
            Runtime.removeObjects(this.id, this.selected_objects, (modified_from_remove) => {
                let combinedList = modified_from_wires
                    .filter(obj1 => !modified_from_remove[1].some(obj2 => obj2.id === obj1.id))
                    .filter(obj => !modified_from_remove[0].includes(obj.id))
                    .concat(modified_from_remove[1]);
                this.updateObjects(combinedList);

                for (let key of modified_from_remove[0]) delete this.objects[key]
                this.selected_wires = []
                this.selected_objects = []
            })
        })
    }

    mouseCollision(x, y) {
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
            obj.render(ctx, this.selected_objects.includes(parseInt(id)) ? 'aqua' : 'white')

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
                    if (WireUtils.wireInList({ src_id: obj.id, src_port: port, dest_id: other.id, dest_port: wire.port }, this.selected_wires)) {
                        ctx.strokeStyle = 'aqua'
                    } else {
                        ctx.strokeStyle = 'white'
                    }
                    ctx.beginPath()
                    ctx.moveTo(io.location.x, io.location.y)
                    ctx.lineTo(other_port.location.x, other_port.location.y)
                    ctx.stroke()
                }
            }

            // Render wire being created
            if (this.dangling_wire) {
                if (this.dangling_wire.type == 'SIGNAL') {
                    ctx.lineWidth = 2;
                } else {
                    ctx.lineWidth = 1
                }
                ctx.strokeStyle = 'white'
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

class WireUtils {
    static createWire(src_id, src_port, dest_id, dest_port, obj={}) {
        obj.src_id = src_id
        obj.src_port = src_port
        obj.dest_id = dest_id
        obj.dest_port = dest_port
        return obj
    }

    static isWire(w) {
        return !Array.isArray(w) && ['src_id', 'src_port', 'dest_id', 'dest_port'].every(key => key in w)
    }

    static areWiresEqual(wire1, wire2) {
        return (
            wire1.src_id === wire2.src_id &&
            wire1.src_port === wire2.src_port &&
            wire1.dest_id === wire2.dest_id &&
            wire1.dest_port === wire2.dest_port
        );
    }

    static wireInList(wire, wires) {
        for (const w of wires) {
            if (WireUtils.areWiresEqual(w, wire))
                return true
        }
        return false;
    }
}

const CollisionType = {
    None: 0,
    Object: 1,
    Input: 2,
    Output: 3,
    Wire: 4,
}
const NO_COLLISION = { type: CollisionType.None }
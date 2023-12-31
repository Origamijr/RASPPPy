// Where stateless functions that are useful without context are relegated

function distToSegmentSquared(a, b, p) {
    function sqr(x) { return x * x }
    function dist2(v, w) { return sqr(v.x - w.x) + sqr(v.y - w.y) }

    var l2 = dist2(a, b); // length squared of segment
    if (l2 == 0) return dist2(a, p); // single point case
    // projection onto parameterized line a+t(b-a)
    var t = ((b.x - a.x) * (p.x - a.x) + (b.y - a.y) * (p.y - a.y)) / l2;
    t = Math.max(0, Math.min(1, t)); // clamp projection to segment
    return dist2(p, {
        x: a.x + t * (b.x - a.x),
        y: a.y + t * (b.y - a.y)
    }); // return squared distance to projection
}

class Vec2 {
    constructor(x = 0, y = 0) {
        this.x = x
        this.y = y
    }
    clone() {
        return new Vec2(this.x, this.y)
    }
    copy(other) {
        this.x = other.x
        this.y = other.y
    }
    set(x, y) {
        this.x = x
        this.y = y
    }
}

const ObjUtils = (() => {
    const pick = (obj, keys) => Object.fromEntries(
        keys.filter(key => key in obj)
            .map(key => [key, obj[key]])
    );
    
    const inclusivePick = (obj, keys) => Object.fromEntries(
        keys.map(key => [key, obj[key]])
    );
    
    const omit = (obj, keys) => Object.fromEntries(
        Object.entries(obj).filter(([key]) => !keys.includes(key))
    );
    
    return {
        pick,
        inclusivePick,
        omit,
    }
})();

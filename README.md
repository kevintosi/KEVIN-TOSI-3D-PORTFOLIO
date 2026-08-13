# Portfolio V2

Port of the `3js_test` portfolio onto a new Blender-built world. Same app, new world.

```bash
python3 server.py
```

Then open http://localhost:8000. Add `?debug=1` for the console helpers
(`__world.tp(x, z)` teleports, `__world.look(x, y, z)` aims the camera).

A plain static server is required — `file://` won't work, because ES modules, the GLB
fetch and the CSS3D video embeds all need a real origin.

## What carried over unchanged

Every system is world-agnostic and was ported as-is:

- Theater carousel — Vimeo + YouTube via keyless oEmbed, CSS3D hole-punch iframes,
  scroll to browse, auto-advance on end
- Octree + Capsule physics, step-up (0.5), head bob, super-jump with SFX
- Mobile: touch look-joystick, movement buttons, TAP-to-interact
- Welcome screen with animated gradient-blob background
- Doors that swing open on approach, dust particles, idle timer, lighting dimmer
- The Blender naming conventions: `NOCOLLIDE`, `COLLISION`, `door*`

Your content is untouched: the 20 Vimeo IDs, `FILM_ORDER`, and all eight
`PROJECT_ROOMS` with their YouTube IDs and Orangina images.

## What is world-specific

Everything tied to the old house/rooms model is marked `WORLD CONFIG` in
`index.html`, with the previous values kept in comments as `OLD:`. Search for
`WORLD CONFIG` to find all of them:

| What | Where | Now |
| --- | --- | --- |
| Model path | `GLTFLoader().load` | `./PORTFOLIO V2.glb` |
| Player size | `EYE_OFFSET` / `PLAYER_RADIUS` | 0.30 / 0.15 — eye at 0.45 |
| Spawn + initial aim | `SPAWN` / `SPAWN_LOOK` | approach walkway, z 14.10, facing the vault |
| Door slide direction | `DOOR_SLIDE_INWARD` | inward, toward x=0 |
| Collision exclusions | `DECORATIVE` | `/^(sphere\|text)/i` |
| Bulbs | `pointLightsConfig` | four flanking the end wall |
| Theater screen | `masterScreen.position` / `SCREEN_SCALE` | end wall, 2.40 × 1.35 |
| Project walls | `EAST_WALL` / `WEST_WALL` / `WEST_WALL_FACING` | x = +1.20 / −1.20 / −0.04 |
| Project spans | `PROJECT_ROOMS[].span` | refitted to z −10.20 … 1.50 |
| Slavic TV | `setupSlavicTv()` | west face of the divider |
| Local video | `LOCAL_VIDEO_SCREENS` | west wall, z −9.00 |

To reposition anything: walk to the spot, read the coordinates off the HUD
(top-left), paste them in.

## The trap that would have broken collision

The old world's `DECORATIVE` regex excluded any mesh whose name starts with
`circle` from the collision octree. In **this** model `Circle` is the vault — the
curved wall-and-ceiling shell that provides all the side containment. Copying that
regex over would have let you walk straight out through the walls, silently, with
nothing in the console.

It's now `/^(sphere|text)/i`, matching only the door handles and door labels. At
7.8k triangles this model has no octree cost worth optimising, so prefer tagging
meshes `NOCOLLIDE` in Blender over growing that regex — explicit beats
pattern-matching that can catch the wrong thing.

Verified after the change: floor supports at spawn, the vault blocks at x = ±1.30
(inside the floor edge at ±1.34), the divider stops you at x = 0.12 with a 0.13
capsule radius, and the end wall stops you at z = 1.48.

## Doors

The doors slide horizontally rather than swinging. The original code rotated them about
`rotation.y`, but these panels have their origin at the panel centre rather than at a
hinge edge, so they spun in place through the wall.

Each now slides along **world X** by 1.02× its own width, which fully clears its opening.
Direction is inward, toward x=0, because the geometry requires it: the panels are 0.42
wide with outer edges at x = ∓0.942 while the end wall only reaches ±1.30, so sliding
outward leaves 0.358 of room and the door would overhang the wall edge into the vault.
The 1.06 span of solid wall between the two doors is ample. Flip `DOOR_SLIDE_INWARD` to
reverse it.

The offset is computed in world space and converted to parent space via the inverse
parent matrix, so it survives Blender's Z-up conversion and any parent rotation or
scale — nudging local `.x` would send them sideways-and-through the floor.

Because the wall is a single thin plane there's no pocket to disappear into, so the
panel slides across the wall face like a barn door. It sits 2cm proud of the wall, so no
z-fighting.

### Trigger

Each door opens when the player comes within `TRIGGER_DIST` (1.2) of it, **from either
side** — the test is an unsigned distance, so there's no front/back special-casing.

The anchor is the door's world **bounding-box centre**, not its object origin. That
distinction matters here: these meshes have their origin at (0,0,0) with the offset
baked into the vertices, so `getWorldPosition()` returns the world origin — 1.83 away
from the actual door. The inherited code used exactly that, which meant the doors fired
when you walked past the middle of the corridor and never when you stood in front of
them. If you re-export with origins applied, the bbox centre stays correct either way.

The two doors are 1.48 apart, so at 1.2 they stay fully independent; raise
`TRIGGER_DIST` past ~0.74 of that spacing and they start opening as a pair.

Verified symmetric: standing at door_1 reads 0.38 from the corridor and 0.39 from the
apron; 1.0m out reads 1.01 and 1.02.

## Known issues with the current model

These are model-side. All are quick fixes in Blender:

0. **There is a 0.56m hole in the floor at z ≈ 7.0 — the route from spawn is broken.**
   The main floor (`Plane`) ends at z 6.77 and the new approach walkway (`Plane.003`)
   starts at z 7.33. Walking from the spawn toward the vault, you drop through the seam.
   Sweeping the whole centre line from z 24 to −10.6 finds exactly one gap, right there.
   **And this app has no fall-reset** — it was inherited from `3js_test`, which never
   needed one — so a visitor who falls keeps falling forever with no way back. Closing
   the gap in Blender fixes it; say the word if you'd also like a respawn safety net,
   which is about two lines.

   Related: the walkway is 0.70 wide with no railings — you lose floor at x = ±0.5 — so
   it's easy to walk off the side as well.


1. **The apron is sealed off.** The end wall (`Plane.001`) is solid across the full
   2.68 width and 2.46 height, and the doors on it are decorative panels rather than
   openings. So the 5m space beyond it (z 1.66 … 6.77) can't be reached from the
   spawn. Two project rooms and the local video screen initially landed out there
   and were moved back into the corridor — **anything you place past z 1.60 is
   invisible to visitors** until you cut a real opening.

2. **The divider wall blocks the theater.** `Plane.002` runs down the middle of the
   corridor (x = 0) from z 1.65 to −3.36, directly in front of the end wall where the
   theater screen hangs. From the centre line it's edge-on and barely there, but from
   either lane it occludes half the screen. Either shorten the divider or move the
   theater into one lane.

3. **The corridor is tight for this much work.** Eight project rooms plus the theater
   are competing for 11.7m of reachable wall, which puts the screens at ~0.45m wide.
   Readable at the 1.2m viewing distance the corridor forces, but there's no room to
   grow. The old world gave each project its own room.

## Blender conventions

- `NOCOLLIDE` in a mesh name — stays visible, no collision. Case, spaces,
  underscores, hyphens and `.001` suffixes are all ignored.
- `COLLISION` in a mesh name — hidden, still collides. An invisible blocker.
- Name starting with `door` — gets double-sided material and swings open when you
  come within 1.2m. Currently `door_1` and `door_2`.

## Notes

- Three.js r164 via unpkg importmap, matching `3js_test`. No build step, no
  `node_modules`.
- Only the 10 referenced assets were copied from `3js_test` (21MB), not the full
  227MB of Blender source textures and unused videos.
- The temp `__probe()` diagnostic block was dropped — it was explicitly marked for
  removal in the source and fired 404s on every load.

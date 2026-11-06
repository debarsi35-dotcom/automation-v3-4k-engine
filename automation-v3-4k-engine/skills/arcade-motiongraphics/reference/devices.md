# Device library (each one has a kit call in `kit/arcade.js`)

Coordinates are screen px on the 1080×1920 canvas. `t` is global time. `w(i)` is the onset of shown word i.

## Worlds (backgrounds)
| device | from | call |
|---|---|---|
| Pixel sky with drifting clouds, stepped horizon bands | A 0.4 s | `A.makeCloud(seed,w,h)` cached, drawn ×P; `A.C.sky` |
| Halftone (square dots growing toward the bottom) | A 9.8 s / 15.8 s | `A.halftone(top,bottom,dotColour,cell)` |
| Wood-panel stripes (crew wall) | A 3 s | `A.stripes(c1,c2,band)` |
| Navy graph paper | own | `A.graph(bg,line,cell)` |
| Stepped red bands (end card) | A 28 s | `A.bands(top,bottom,n)` |
| CRT glass: scanlines + vignette + reflection | B | `A.crtGlass(ctx,k)` |

## Pixel art
| device | call |
|---|---|
| Sprite from strings + palette | `A.defSprite(name, rows, pal)`, `A.drawSpr(ctx,name,x,y,scale,{anchor:'c'|'bc',flip,outline,ow})` |
| Reveal a sprite pixel by pixel (build-up) | `A.drawCells(ctx, rows, pal, x, y, cell, keep(i,j))` |
| Chunky dark outline around a sprite or cut-out | `A.silhouette(img,colour)` drawn at ±8 px offsets under the image |
| Real photo → pixel art | `A.pixelate(img, cellsWide, levels, sat)`, drawn nearest-neighbour |
| Coin, ? block, brick, ground, pipe, hill, girder, ladder, barrel, cabinet, flame, car | `example/film.js` (copy and edit) |

## Type
| device | call |
|---|---|
| Pixel fire type (REF-A "MAXIMUM FLAVOUR"): Press Start 2P mask → gradient rows + 1 px extrusion + dark outline | `A.ptext(ctx,str,x,y,cell,'fire'|'gold'|'white'|'red'|'cyan'|'plainWhite'|...)` |
| Pop-in with stepped integer growth | `A.popCell(t,t0,cell,k,dur)` or the film helper `pop(ctx,t,t0,str,x,y,cell,style,{out,reveal})` |
| Word-by-word reveal of one line (monospaced) | `A.ptext(...,{reveal:nChars})` |
| Display title slam (heavy face, extrusion, flies in rotated with smear copies, elastic settle) | `A.slam(t,t0)` → `A.title(ctx,str,x,y,size,{rot,scale,alpha})` |
| RPG dialog box + typewriter + squash + bubble pop | `A.dialog(ctx,x,y,w,h,lines,{t,tail,squash})`, `A.type(str,t,t0,t1)`, `A.ring` + `A.puff` |
| Dark label tag ("HAIR? TOO HARD") | film helper `tag(ctx,str,x,y,cell)` |

## HUD + garnish
| device | call |
|---|---|
| Heart + segmented health bar + coin counter (REF-B) | `A.hud(ctx,{health,coins,label,alpha})` |
| Crosshair that locks on (flies in big and spinning, settles) | `A.lockOn(ctx,x,y,r,t,t0,t1)` |
| White pixel plus-sparks | `A.sparks(ctx,cx,cy,rad,t,n,seed,{squash,rise})` |
| Manga radial speed lines | `A.speedLines(ctx,cx,cy,t,seed,{color,n,r0,speed})` |
| 8-bit smoke puff / impact ring | `A.puff(ctx,x,y,p,{r,n,cell,size,squash})`, `A.ring(ctx,x,y,r,cell,colour,alpha)` |
| 3 motion lines above a falling thing | `A.motionLines(ctx,x,y,w,len)` |
| Screen shake (snapped to the pixel grid) | film helper `shake(t,t0,amp,dur,seed)` |

## Transitions (aim for 5–7 kinds per film; each needs a cause)
| transition | from | call |
|---|---|---|
| Knit / stitch dissolve | A 0.0 s & 7.9 s | `A.knit(ctx,src,k,t,{base,tint,stitch,ta})` (k 1→0 to resolve) |
| Pinwheel wedge wipe centred on the next subject | A 2.44 s | `A.pinwheel(ctx,from,to,p,cx,cy,8)` |
| White starburst cut | A 8.12 s | `A.flash` for 2 frames + `A.starburst(ctx,cx,cy,p,seed)` |
| Stripe scan real ↔ pixel | A 17.5 s | `A.scanConvert(ctx,drawA,drawB,box,p,seed)` |
| CRT vertical-line glitch | A 9.44 s | `A.glitchV(ctx,src,k,t,seed)` |
| Bayer dither dissolve (pixel crossfade) | own | `A.dither(ctx,from,to,p,cell)` |
| Circle iris close/open | Mario canon | `A.iris(ctx,cx,cy,r,cell)` |
| CRT power-on | B | `A.crtOn(ctx,src,p)` |
| Shutter down / roll up | own (warehouse door) | `shutter(ctx,edge)` in example |
| Pull back into a real cabinet / screen | B + real photo | `SC.end` in example (draw content into the photo's screen opening) |

## Scene contract
`SC.name = (ctx, t) => { ... }` draws a full opaque frame. `SPANS` says which scene owns each time. `TR` lists the
transition windows `[t0, t1, fn]`, where fn draws the scenes it needs into buffers with `S(id,t,'b1')` and composites them.
`F.render(ctx,t)` = the transition if one is active, else the scene, then the HUD on top.

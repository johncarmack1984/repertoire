//! A data map drawn by mln-rs: style.json over the files the levers wrote to
//! data/, in a window, or offscreen with `--snapshot out.png`, which also
//! writes out.report.json for `datamap.py check --png`.
//!
//! cargo run --release -- [--snapshot PNG] [--size WxH] [--pixel-ratio N] [--live JSON]

use std::error::Error;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use mln_rs::feature::{Identifier, Value};
use mln_rs::mln_map::RenderMode;
use mln_rs::mln_style::image::Impl as StyleImage;
use mln_rs::mln_util::image::PremultipliedImage;
use mln_rs::mln_util::size::Size;
use mln_rs::{
    AttachOptions, DemandMode, FeatureState, FeatureStateSelector, FrameDemand, FrameDisposition, Map, MapOptions,
    RenderSession, RenderTarget, Runtime, RuntimeOptions,
};
use serde_json::{Value as Json, json};

mod window;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

/// The project folder, fixed at build time. Projects that share a target folder
/// and this package name share one binary, so give each project a name of its own.
const PROJECT: &str = env!("CARGO_MANIFEST_DIR");
/// The arrowhead's length in its image, in logical pixels. style.json's
/// icon-size divides `dm_arrow` by it.
const ARROW_PX: f64 = 16.0;
/// The transparent margin around the arrowhead, in logical pixels. style.json's
/// icon-offset takes it back, then sets the tip back `dm_setback` pixels from
/// the node center, at any zoom.
const ARROW_MARGIN: f64 = 4.0;

struct Args {
    snapshot: Option<PathBuf>,
    size: Size,
    pixel_ratio: f32,
    live: Option<PathBuf>,
}

fn main() -> Result<()> {
    let args = parse_args()?;
    let runtime = Runtime::new(&RuntimeOptions::default())?;
    let options = mln_rs::mln_map::MapOptions { size: args.size, pixel_ratio: args.pixel_ratio, ..Default::default() };
    let (map, created) = runtime.create_map(MapOptions { map: options, ..Default::default() })?;
    created.wait()?;
    map.set_style_json(style(&Path::new(PROJECT).join("data"))?)?.wait()?;
    // A new style drops its images, so add the arrow after each set_style_json.
    map.set_style_image(arrow()?)?.wait()?;
    if let Some(path) = &args.live {
        update(&map, &Flows::read(path)?)?;
    }
    let shown = match &args.snapshot {
        Some(png) => snapshot(&map, &args, png),
        None => window::show(&map, args.size),
    };
    // The session goes first (snapshot and show release theirs), then the map, then the runtime.
    map.release()?.wait()?;
    runtime.release()?.wait()?;
    shown
}

fn parse_args() -> Result<Args> {
    let mut args = Args { snapshot: None, size: Size::new(1200, 800), pixel_ratio: 1.0, live: None };
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = || it.next().ok_or_else(|| format!("{flag} needs a value"));
        match flag.as_str() {
            "--snapshot" => args.snapshot = Some(value()?.into()),
            "--size" => {
                let text = value()?;
                let (w, h) = text.split_once('x').ok_or("--size is WIDTHxHEIGHT")?;
                args.size = Size::new(w.parse()?, h.parse()?);
            }
            "--pixel-ratio" => args.pixel_ratio = value()?.parse()?,
            "--live" => args.live = Some(value()?.into()),
            other => return Err(format!("unknown flag {other}: try --snapshot, --size, --pixel-ratio or --live").into()),
        }
    }
    Ok(args)
}

/// The style in style.json, with `{{DATA}}` replaced by `data_dir`. A source
/// whose file is missing is left out with its layers, and named on stdout, so
/// the style draws whichever layers the levers wrote.
fn style(data_dir: &Path) -> Result<String> {
    let text = std::fs::read_to_string(Path::new(PROJECT).join("style.json"))?;
    let mut style: Json = serde_json::from_str(&text.replace("{{DATA}}", &data_dir.to_string_lossy()))?;
    let sources = style["sources"].as_object_mut().ok_or("style.json has no sources")?;
    let missing: Vec<(String, String)> = (sources.iter())
        .filter_map(|(id, source)| {
            let url = source["data"].as_str().or(source["url"].as_str())?;
            let path = url.split_once("file://")?.1;
            (!Path::new(path).exists()).then(|| (id.clone(), path.to_owned()))
        })
        .collect();
    for (id, path) in &missing {
        println!("left out source {id} and its layers: no file at {path}");
        sources.remove(id);
    }
    let layers = style["layers"].as_array_mut().ok_or("style.json has no layers")?;
    layers.retain(|layer| !missing.iter().any(|(id, _)| layer["source"] == id.as_str()));
    Ok(style.to_string())
}

/// An arrowhead that points up with its tip at the top, as a signed distance
/// field, so that style.json colors it with icon-color.
fn arrow() -> Result<StyleImage> {
    const SCALE: f64 = 4.0;
    let half = ARROW_PX * 0.45;
    let tip = (ARROW_MARGIN + half, ARROW_MARGIN);
    let corners = [tip, (tip.0 + half, tip.1 + ARROW_PX), (tip.0 - half, tip.1 + ARROW_PX)];
    let size = Size::new(((half + ARROW_MARGIN) * 2.0 * SCALE) as u32, ((ARROW_PX + ARROW_MARGIN * 2.0) * SCALE) as u32);
    let mut pixels = Vec::new();
    for y in 0..size.height {
        for x in 0..size.width {
            let distance = signed_distance(((f64::from(x) + 0.5) / SCALE, (f64::from(y) + 0.5) / SCALE), &corners);
            // MapLibre draws an SDF's edge at 0.75, falling by 1/8 for each logical pixel, as in its glyphs.
            let alpha = ((0.75 - distance / 8.0).clamp(0.0, 1.0) * 255.0).round() as u8;
            pixels.extend([alpha; 4]);
        }
    }
    let image = PremultipliedImage::from_vec(size, pixels);
    Ok(StyleImage::new("dm-arrow".into(), image, SCALE as f32, true, vec![], vec![], None, None, None)?)
}

/// The distance from `p` to a clockwise triangle's edges, negative inside.
fn signed_distance(p: (f64, f64), corners: &[(f64, f64); 3]) -> f64 {
    let mut nearest = f64::MAX;
    let mut inside = true;
    for (i, a) in corners.iter().enumerate() {
        let b = corners[(i + 1) % 3];
        let (ex, ey, px, py) = (b.0 - a.0, b.1 - a.1, p.0 - a.0, p.1 - a.1);
        let t = ((px * ex + py * ey) / (ex * ex + ey * ey)).clamp(0.0, 1.0);
        nearest = nearest.min((px - t * ex).hypot(py - t * ey));
        inside &= ex * py - ey * px >= 0.0;
    }
    if inside { -nearest } else { nearest }
}

/// Live flow values by the `id` each flow has in data/flows.geojson, in the
/// legend's unit, with the legend's width scale, so live widths keep the
/// legend true.
struct Flows {
    values: Vec<(u64, f64)>,
    px_per_unit: f64,
    min_px: f64,
}

impl Flows {
    /// Reads `{"id": value, ...}` from `path`, and the scale from the flows
    /// layer's `width` in data/legend.json.
    fn read(path: &Path) -> Result<Flows> {
        let live: serde_json::Map<String, Json> = serde_json::from_str(&std::fs::read_to_string(path)?)?;
        let legend: Json = serde_json::from_str(&std::fs::read_to_string(Path::new(PROJECT).join("data/legend.json"))?)?;
        let width = &legend["layers"]["flows"]["width"];
        let number = |key: &str| width[key].as_f64().ok_or(format!("legend.json has no layers.flows.width.{key}"));
        let values = live
            .iter()
            .map(|(id, value)| Ok((id.parse()?, value.as_f64().ok_or(format!("live value {id} isn't a number"))?)))
            .collect::<Result<_>>()?;
        Ok(Flows { values, px_per_unit: number("max_px")? / number("vmax")?, min_px: number("min_px")? })
    }
}

/// Sets each flow's width from its live value through feature-state, which
/// the next frame draws without reloading or re-tiling data/flows.geojson.
fn update(map: &Map, flows: &Flows) -> Result<()> {
    for &(id, value) in &flows.values {
        let width = (value * flows.px_per_unit).max(flows.min_px);
        let state: FeatureState = [("dm_width".to_owned(), Value::Double(width))].into_iter().collect();
        map.set_feature_state(&FeatureStateSelector::feature("flows", Identifier::Uint(id)), state)?.wait()?;
    }
    Ok(())
}

/// Renders offscreen once everything has loaded, and writes the PNG and its
/// report beside it.
fn snapshot(map: &Map, args: &Args, png: &Path) -> Result<()> {
    let started = Instant::now();
    let target = RenderTarget::Offscreen { size: args.size, device: None };
    let (session, attached) = map.attach(target, AttachOptions::default())?;
    attached.wait()?;
    let frames = render_loaded(&session)?;
    let image = session.read_texture()?.wait()?;
    session.release()?.wait()?;
    std::fs::write(png, mln_rs::mln_image::encode_png(&image))?;
    let report = png.with_extension("report.json");
    std::fs::write(&report, serde_json::to_string_pretty(&report_of(map, args)?)?)?;
    let ms = started.elapsed().as_millis();
    println!("wrote {} and {} after {frames} frames, {ms} ms", png.display(), report.display());
    Ok(())
}

/// Renders frames until one shows everything loaded with nothing left to
/// animate, and returns how many that took.
fn render_loaded(session: &RenderSession) -> Result<u64> {
    let deadline = Instant::now() + Duration::from_secs(60);
    let mut token = 0;
    loop {
        token += 1;
        session.demand_frame(FrameDemand::new(DemandMode::Force, token))?;
        let frame = loop {
            if let Some(frame) = session.drain_frame_results()?.into_iter().find(|f| f.token == Some(token)) {
                break frame;
            }
            if Instant::now() > deadline {
                return Err("the map didn't finish loading in 60 s".into());
            }
            std::thread::sleep(Duration::from_millis(1));
        };
        if frame.disposition != FrameDisposition::Rendered {
            return Err(format!("frame {token} was {:?}: {:?}", frame.disposition, session.snapshot()?).into());
        }
        if frame.mode == RenderMode::Full && !frame.needs_repaint {
            return Ok(token);
        }
    }
}

/// What `datamap.py check --png` judges beside the PNG: the camera, the
/// layers with their sources, and the sources with their URLs.
fn report_of(map: &Map, args: &Args) -> Result<Json> {
    let camera = map.camera()?.wait()?.camera;
    let bounds = map.snapshot()?.bounds;
    let projection: Json = match map.style_root_property("projection")?.wait()? {
        Some(json) => serde_json::from_str(&json)?,
        None => json!({"type": "mercator"}),
    };
    let layers: Vec<Json> = (map.style_layers()?.wait()?.into_iter())
        .map(|layer| json!({"id": layer.id, "type": layer.layer_type, "source": layer.source_id}))
        .collect();
    let sources: Vec<Json> = (map.style_sources()?.wait()?.into_iter())
        .map(|source| json!({"id": source.id, "type": format!("{:?}", source.kind).to_lowercase(), "url": source.url}))
        .collect();
    Ok(json!({
        "projection": projection["type"], "pitch": camera.pitch, "bearing": camera.bearing, "zoom": camera.zoom,
        "center": [camera.center.longitude(), camera.center.latitude()],
        "minZoom": bounds.min_zoom, "maxZoom": bounds.max_zoom, "controls": [], "moving": false,
        "size": {"width": args.size.width, "height": args.size.height}, "scale": args.pixel_ratio,
        "layers": layers, "sources": sources,
    }))
}

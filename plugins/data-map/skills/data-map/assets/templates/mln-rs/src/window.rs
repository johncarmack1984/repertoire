//! The map in a window: winit's event loop drives the render session on its
//! own thread, where macOS makes the window's surface.

use std::error::Error;
use std::sync::Arc;

use mln_rs::mln_util::size::Size;
use mln_rs::{
    AttachOptions, DemandMode, Driver, DriverWork, FrameDemand, FrameDisposition, LogicalExtent, Map, RenderSession,
    RenderTarget, Surface,
};
use winit::application::ApplicationHandler;
use winit::dpi::LogicalSize;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, EventLoop, EventLoopProxy};
use winit::window::{Window, WindowId};

use crate::Result;

/// Shows the map in a window until it closes.
pub fn show(map: &Map, size: Size) -> Result<()> {
    let event_loop = EventLoop::<Ask>::with_user_event().build()?;
    let mut host = Host { map, size, proxy: event_loop.create_proxy(), open: None, error: None };
    event_loop.run_app(&mut host)?;
    if let Some(open) = host.open.take() {
        let released = open.session.release()?;
        while !released.is_complete() {
            open.driver.service()?;
        }
    }
    host.error.map_or(Ok(()), Err)
}

/// What the render session asks of the window's thread.
#[derive(Clone, Copy, Debug)]
enum Ask {
    Service,
    DrainFrames,
    Redraw,
}

struct Host<'a> {
    map: &'a Map,
    size: Size,
    proxy: EventLoopProxy<Ask>,
    open: Option<Open>,
    error: Option<Box<dyn Error>>,
}

/// The window and the session that draws into it.
struct Open {
    window: Arc<Window>,
    session: RenderSession,
    driver: DriverWork,
    token: u64,
}

impl Host<'_> {
    fn open(&self, event_loop: &ActiveEventLoop) -> Result<Open> {
        let attributes = Window::default_attributes()
            .with_title("data map")
            .with_inner_size(LogicalSize::new(self.size.width, self.size.height));
        let window = Arc::new(event_loop.create_window(attributes)?);
        let ask = |ask: Ask| {
            let proxy = self.proxy.clone();
            Some(Arc::new(move || {
                let _ = proxy.send_event(ask);
            }) as mln_rs::Wake)
        };
        let options = AttachOptions {
            driver: Driver::CallerThread,
            driver_work_wake: ask(Ask::Service),
            frame_wake: ask(Ask::DrainFrames),
            redraw_wake: ask(Ask::Redraw),
            ..AttachOptions::default()
        };
        self.map.resize(LogicalExtent::new(self.size, window.scale_factor()))?.wait()?;
        let target = RenderTarget::Surface { size: self.size, surface: Surface::window(Arc::clone(&window)), device: None };
        let (session, attached) = self.map.attach(target, options)?;
        let driver = session.take_driver_work()?;
        while !attached.is_complete() {
            driver.service()?;
        }
        attached.wait()?;
        session.demand_frame(FrameDemand::new(DemandMode::Force, 0))?;
        Ok(Open { window, session, driver, token: 0 })
    }

    fn answer(&mut self, ask: Ask) -> Result<()> {
        let Some(open) = &self.open else { return Ok(()) };
        match ask {
            Ask::Service => open.driver.service()?,
            Ask::Redraw => open.window.request_redraw(),
            Ask::DrainFrames => {
                for frame in open.session.drain_frame_results()? {
                    if frame.disposition == FrameDisposition::Failed {
                        return Err(format!("a frame failed: {:?}", open.session.snapshot()?).into());
                    }
                    if frame.needs_repaint {
                        open.window.request_redraw();
                    }
                }
            }
        }
        Ok(())
    }

    fn handle(&mut self, event: WindowEvent, event_loop: &ActiveEventLoop) -> Result<()> {
        let Some(open) = &mut self.open else { return Ok(()) };
        match event {
            WindowEvent::RedrawRequested => {
                open.token += 1;
                open.session.demand_frame(FrameDemand::new(DemandMode::Force, open.token))?;
            }
            // A window that macOS hasn't shown yet takes no frame, so draw again once it shows.
            WindowEvent::Occluded(false) => open.window.request_redraw(),
            WindowEvent::Resized(physical) => {
                let logical = physical.to_logical::<u32>(open.window.scale_factor());
                if logical.width > 0 && logical.height > 0 {
                    let extent = LogicalExtent::new(Size::new(logical.width, logical.height), open.window.scale_factor());
                    // Never wait on a session's completion here: this thread runs its work.
                    drop(open.session.resize(extent)?);
                }
            }
            WindowEvent::CloseRequested => event_loop.exit(),
            _ => {}
        }
        Ok(())
    }

    fn fail(&mut self, error: Box<dyn Error>, event_loop: &ActiveEventLoop) {
        self.error.get_or_insert(error);
        event_loop.exit();
    }
}

impl ApplicationHandler<Ask> for Host<'_> {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        if self.open.is_none() {
            match self.open(event_loop) {
                Ok(open) => self.open = Some(open),
                Err(error) => self.fail(error, event_loop),
            }
        }
    }

    fn user_event(&mut self, event_loop: &ActiveEventLoop, ask: Ask) {
        if let Err(error) = self.answer(ask) {
            self.fail(error, event_loop);
        }
    }

    fn window_event(&mut self, event_loop: &ActiveEventLoop, _: WindowId, event: WindowEvent) {
        if let Err(error) = self.handle(event, event_loop) {
            self.fail(error, event_loop);
        }
    }
}

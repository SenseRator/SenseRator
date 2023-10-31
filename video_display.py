import sdl2
import sdl2.ext

class Display(object):
    def __init__(self, W, H):
        sdl2.ext.init()

        # Create an SDL_DisplayMode structure
        mode = sdl2.SDL_DisplayMode()

        # Pass the structure when calling SDL_GetDesktopDisplayMode
        sdl2.SDL_GetDesktopDisplayMode(0, mode)
        
        center_x = (mode.w - W) // 2
        center_y = (mode.h - H) // 2

        self._W, self._H = W, H
        self._window = sdl2.ext.Window("Video Display", size=(W, H), position=(center_x, center_y))
        self._window.show()

    def paint(self, img):
        self._handle_events()
        self._draw(img)

    def _handle_events(self):
        """Handle window events."""
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.close()

    def _draw(self, img):
        """Draw the given image on the window."""
        surf = sdl2.ext.pixels3d(self._window.get_surface())
        surf[:, :, 0:3] = img.swapaxes(0, 1)
        self._window.refresh()

    def close(self):
        sdl2.ext.quit()


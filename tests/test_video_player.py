import unittest
import sys
import os
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

# Add the parent directory to the sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from video_player import VideoPlayer

class TestVideoPlayer(unittest.TestCase):
    def setUp(self):
        self.frames = ["frame1.jpg", "frame2.jpg"]
        self.folder = "test_folder"
        self.resize = (600, 450)
        self.object_results = [Mock(), Mock()]  # Mock results for two frames
        self.seg_paths = ["seg1.jpg", "seg2.jpg"]
        self.window = Mock()

        # Mocking the __getitem__ method
        self.window.__getitem__ = Mock()
        self.window.__getitem__.side_effect = lambda key: Mock()

        # Creating the VideoPlayer instance for testing
        self.player = VideoPlayer(self.frames, self.window, self.folder, self.resize, self.object_results, self.seg_paths)


    @patch('image_processing.read_and_resize_image')
    def test_play_video(self, mock_read_and_resize_image):
        # Mock read_and_resize_image to return a dummy image
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_read_and_resize_image.return_value = dummy_image

        # Mock the window.read method to return a stop signal after the first call
        self.window.read.side_effect = [(None, None)]
        self.player.play_video()
        self.assertTrue(self.player.paused)

    def test_pause_video(self):
        self.player.pause_video()
        self.assertTrue(self.player.paused)

    def test_restart_video(self):
        self.player.cur_frame = 1
        self.player.restart_video()
        self.assertEqual(self.player.cur_frame, 0)
        self.assertTrue(self.player.paused)

    def test_update_slider(self):
        self.player.cur_frame = 1

if __name__ == '__main__':
    unittest.main()